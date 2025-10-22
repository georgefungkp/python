"""
IBKR Price Fetcher - High-Level Market Data Interface
======================================================
A user-friendly wrapper around IBKRClientPortalAPI for fetching security prices.

This module provides simplified methods for common market data operations:
- Getting current prices for single or multiple securities
- Retrieving historical price data
- Automatic authentication management
- Symbol to contract ID mapping with caching

Architecture:
    This is the high-level API layer. It wraps IBKRClientPortalAPI and provides:
    - Simplified interfaces for common operations
    - Automatic conid resolution and caching
    - Data transformation into SecurityPrice objects
    - Authentication state management

Usage:
    fetcher = IBKRPriceFetcher()
    price = fetcher.get_price("AAPL")
    if price:
        print(f"AAPL: ${price.last_price}")
"""

import time
from typing import Optional, Dict, List

from IBKRClientPortalAPI import IBKRClientPortalAPI, SecurityPrice


class IBKRPriceFetcher:
    """
    High-level interface for fetching security prices from IBKR.
    
    This class simplifies common market data operations by:
    - Handling authentication automatically
    - Caching symbol-to-conid mappings
    - Converting raw API data to SecurityPrice objects
    - Supporting bulk operations for multiple securities
    
    Attributes:
        api (IBKRClientPortalAPI): Low-level API client
        conid_cache (dict): Cache of symbol to conid mappings for performance
    """
    
    # Common security types mapping for user convenience
    # Maps friendly names to IBKR security type codes
    SECURITY_TYPES = {
        "stock": "STK",      # Common stocks
        "option": "OPT",     # Options contracts
        "future": "FUT",     # Futures contracts
        "forex": "CASH",     # Foreign exchange
        "index": "IND",      # Market indices
        "bond": "BOND"       # Bonds
    }
    
    # Market data field mappings
    # Maps IBKR field IDs to SecurityPrice attribute names
    FIELD_MAP = {
        "31": "last_price",          # Most recent trade price
        "84": "bid_price",           # Current bid price
        "85": "ask_price",           # Current ask price
        "86": "change",              # Absolute price change
        "87": "change_percentage",   # Percentage change
        "88": "volume",              # Trading volume
        "70": "high",                # Day's high price
        "71": "low",                 # Day's low price
        "72": "close_price",         # Closing price
        "73": "open_price",          # Opening price
        "74": "previous_close"       # Previous day's close
    }
    
    def __init__(self, base_url: str = "https://localhost:5000/v1/api"):
        """
        Initialize the price fetcher.
        
        Args:
            base_url: Base URL for the IBKR Client Portal Gateway
        """
        # Initialize the low-level API client
        self.api = IBKRClientPortalAPI(base_url)
        
        # Cache for symbol to conid mappings to avoid repeated lookups
        # Key format: "SYMBOL_SECTYPE_EXCHANGE_CURRENCY"
        self.conid_cache = {}
        
    def ensure_authenticated(self) -> bool:
        """
        Ensure we have a valid authenticated session with IBKR.
        
        This method checks the current authentication status and attempts
        to authenticate if necessary. It should be called before any
        market data operations.
        
        Returns:
            True if authenticated (already or after successful authentication)
            False if authentication failed
        """
        # Check if already authenticated
        if not self.api.check_authentication():
            self.api.logger.info("Attempting to authenticate...")
            
            # Initiate authentication
            if not self.api.sso_validate():
                self.api.logger.error(
                    "Authentication failed. Please check Client Portal Gateway."
                )
                return False
            
            # Wait for authentication to complete
            # SSO validation needs time to process
            time.sleep(5)
            
            # Verify authentication succeeded
            return self.api.check_authentication()
        
        return True
    
    def _score_contract(self, contract: dict, symbol: str, exchange: str, 
                       currency: str, stock_name: str = None) -> int:
        """Calculate match score for a contract."""
        score = 0
        description = (contract.get('description') or '').upper()
        company_name = (contract.get('companyName') or '').upper()
        
        # If we have stock name from Excel, check if company name contains it
        if stock_name:
            stock_name_upper = stock_name.upper()
            if stock_name_upper in company_name:
                score += 30  # Strong match!
            elif stock_name_upper in description:
                score += 15
        
        # Prefer stocks with ORDINARY/COMMON in company name or description
        if any(kw in company_name for kw in ['ORDINARY', 'COMMON', 'SHARE']):
            score += 15
        if any(kw in description for kw in ['ORDINARY', 'COMMON', 'SHARE']):
            score += 10
        
        # Strong penalty for derivatives
        if any(kw in company_name for kw in ['WARRANT', 'OPTION', 'FUTURE']):
            score -= 50
        if any(kw in description for kw in ['WARRANT', 'OPTION', 'FUTURE']):
            score -= 30
        
        # Check sections for exchange match
        sections = contract.get('sections', [])
        for section in sections:
            section_exchange = str(section.get('exchange', ''))
            if exchange in section_exchange:
                score += 20
        
        return score
    
    def get_conid(self, symbol: str, sec_type: str = "STK", 
                  exchange: str = "SMART", currency: str = "USD",
                  stock_name: str = None) -> Optional[str]:
        """Get contract ID with intelligent matching."""
        
        cache_key = f"{symbol}_{sec_type}_{exchange}_{currency}"
        if cache_key in self.conid_cache:
            return self.conid_cache[cache_key]
        
        contracts = self.api.search_contract(symbol, sec_type, exchange, currency)
        if not contracts:
            self.api.logger.error(f"No contract found for {symbol}")
            return None
        
        # Single contract - use it
        if len(contracts) == 1:
            conid = str(contracts[0].get('conid'))
            self.api.logger.info(f"Single contract: {symbol} → {conid}")
            self.conid_cache[cache_key] = conid
            return conid
        
        # Multiple contracts - find best match
        best = max(contracts, key=lambda c: self._score_contract(
            c, symbol, exchange, currency, stock_name
        ))
        conid = str(best.get('conid'))
        score = self._score_contract(best, symbol, exchange, currency, stock_name)
        company = best.get('companyName', 'N/A')
        
        self.api.logger.info(
            f"Best match: {symbol} → {conid} ({company[:30]}, score: {score})"
        )
        self.conid_cache[cache_key] = conid
        return conid
    
    def get_price(self, symbol: str, sec_type: str = "STK", 
                  exchange: str = "SMART", currency: str = "USD",
                  stock_name: str = None) -> Optional[SecurityPrice]:
        """Get current price data for a single security."""
        
        if not self.ensure_authenticated():
            return None
        
        conid = self.get_conid(symbol, sec_type, exchange, currency, stock_name)
        if not conid:
            return None
        
        # Request market data snapshot from API
        market_data = self.api.get_market_data_snapshot([conid])
        if not market_data or len(market_data) == 0:
            self.api.logger.error(f"No market data received for {symbol}")
            return None
        
        # Extract first (and only) result
        data = market_data[0]
        
        # Create SecurityPrice object to hold the data
        price_data = SecurityPrice(symbol=symbol, conid=conid)
        
        # Map field IDs from API response to SecurityPrice attributes
        for field_id, attr_name in self.FIELD_MAP.items():
            if field_id in data and data[field_id] is not None:
                try:
                    # Try to convert to float (most fields are numeric)
                    setattr(price_data, attr_name, float(data[field_id]))
                except (TypeError, ValueError):
                    # If conversion fails, store raw value
                    setattr(price_data, attr_name, data[field_id])
        
        return price_data
    
    def get_prices(
        self, 
        symbols: List[str], 
        sec_type: str = "STK",
        exchange: str = "SMART", 
        currency: str = "USD"
    ) -> Dict[str, SecurityPrice]:
        """
        Get current prices for multiple securities in a single request.
        
        This is more efficient than calling get_price() multiple times
        because it batches the API requests.
        
        Args:
            symbols: List of ticker symbols (e.g., ["AAPL", "MSFT", "GOOG"])
            sec_type: Security type for all symbols (default: "STK")
            exchange: Exchange for all symbols (default: "SMART")
            currency: Currency for all symbols (default: "USD")
            
        Returns:
            Dictionary mapping symbols to SecurityPrice objects
            Empty dictionary if request fails or no data retrieved
            
        Example:
            fetcher = IBKRPriceFetcher()
            prices = fetcher.get_prices(["AAPL", "MSFT", "GOOG"])
            for symbol, price in prices.items():
                print(f"{symbol}: ${price.last_price}")
        """
        # Ensure we have valid authentication
        if not self.ensure_authenticated():
            return {}
        
        # Build list of conids and mapping from conid back to symbol
        conids = []
        symbol_to_conid = {}
        
        # Look up conid for each symbol
        for symbol in symbols:
            conid = self.get_conid(symbol, sec_type, exchange, currency)
            if conid:
                conids.append(conid)
                symbol_to_conid[conid] = symbol
        
        # If no valid conids found, return empty result
        if not conids:
            return {}
        
        # Get bulk market data for all contracts
        market_data = self.api.get_market_data_snapshot(conids)
        if not market_data:
            return {}
        
        # Build results dictionary
        results = {}
        
        # Process each contract's market data
        for data in market_data:
            conid = str(data.get('conid'))
            symbol = symbol_to_conid.get(conid)
            
            if symbol:
                # Create SecurityPrice object for this symbol
                price_data = SecurityPrice(symbol=symbol, conid=conid)
                
                # Map field IDs to attributes
                for field_id, attr_name in self.FIELD_MAP.items():
                    if field_id in data and data[field_id] is not None:
                        try:
                            # Try to convert to float
                            setattr(price_data, attr_name, float(data[field_id]))
                        except (TypeError, ValueError):
                            # Store raw value if conversion fails
                            setattr(price_data, attr_name, data[field_id])
                
                # Add to results
                results[symbol] = price_data
        
        return results
