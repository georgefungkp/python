"""
IBKR Client Portal Web API Client
==================================
A Python client for interacting with Interactive Brokers' Client Portal Web API.
This module provides low-level API access for authentication, contract search, 
and market data retrieval.

Documentation: https://ibkrcampus.com/campus/ibkr-api-page/cpapi-v1/

Requirements:
    - IBKR Client Portal Gateway must be running (default: localhost:5000)
    - SSL warnings are disabled for localhost connections
    - Active IBKR account with proper permissions

Architecture:
    This is the base API layer that handles direct HTTP communication with IBKR.
    For higher-level operations, use IBKRPriceFetcher which wraps this class.
"""

import requests
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import urllib3

# Disable SSL warnings for localhost connections
# This is safe because we're connecting to localhost (Client Portal Gateway)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@dataclass
class SecurityPrice:
    """
    Data class representing comprehensive security price information.
    
    This class holds all relevant price data for a security, including
    real-time quotes, daily statistics, and trading volume.
    
    Attributes:
        symbol (str): Ticker symbol of the security (e.g., "AAPL", "MSFT")
        conid (str): IBKR contract identifier - unique ID for the contract
        last_price (float, optional): Most recent trade price
        bid_price (float, optional): Current highest bid price
        ask_price (float, optional): Current lowest ask price
        change (float, optional): Absolute price change from previous close
        change_percentage (float, optional): Percentage change from previous close
        volume (float, optional): Total trading volume for the day
        high (float, optional): Highest price of the current trading day
        low (float, optional): Lowest price of the current trading day
        open_price (float, optional): Opening price of the trading day
        close_price (float, optional): Closing price (for completed trading days)
    """
    symbol: str
    conid: str
    last_price: Optional[float] = None
    bid_price: Optional[float] = None
    ask_price: Optional[float] = None
    change: Optional[float] = None
    change_percentage: Optional[float] = None
    volume: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    open_price: Optional[float] = None
    close_price: Optional[float] = None


class IBKRClientPortalAPI:
    """
    Low-level client for IBKR Client Portal Web API.
    
    This class provides direct access to IBKR's REST API endpoints for:
    - Session authentication and management
    - Contract search and information retrieval
    - Real-time and historical market data
    
    The Client Portal Gateway must be running locally for this to work.
    
    Attributes:
        base_url (str): Base URL for API endpoints
        timeout (int): Request timeout in seconds
        session (requests.Session): Persistent HTTP session for connection pooling
        logger (logging.Logger): Logger instance for operation tracking
    """
    
    def __init__(self, base_url: str = "https://localhost:5000/v1/api", timeout: int = 30):
        """
        Initialize the IBKR Client Portal API client.
        
        Args:
            base_url: Base URL for the API (default: https://localhost:5000/v1/api)
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = base_url
        self.timeout = timeout
        
        # Initialize session with persistent connection and SSL disabled for localhost
        self.session = requests.Session()
        self.session.verify = False  # Safe for localhost connections
        self.session.headers.update({
            'User-Agent': 'IBKR-Python-Client/1.0',
            'Content-Type': 'application/json'
        })
        
        # Configure logging for debugging and monitoring
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """
        Make an HTTP request to the IBKR API with error handling.
        
        This is a private helper method that centralizes request logic and
        provides consistent error handling across all API calls.
        
        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            endpoint: API endpoint path (e.g., '/iserver/auth/status')
            **kwargs: Additional arguments passed to requests.request()
            
        Returns:
            JSON response as dictionary if successful (status 200)
            None if request fails or encounters an error
            
        Error Handling:
            - ConnectionError: Cannot connect to Client Portal Gateway
            - Timeout: Request took longer than specified timeout
            - Other exceptions: Logged and returns None
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            # Make the HTTP request with timeout
            response = self.session.request(
                method, 
                url, 
                timeout=self.timeout,
                **kwargs
            )
            
            # Check if request was successful
            if response.status_code == 200:
                return response.json()
            else:
                # Log non-200 responses for debugging
                self.logger.error(
                    f"API request failed: {response.status_code} - {response.text}"
                )
                return None
                
        except requests.exceptions.ConnectionError:
            # Client Portal Gateway is not running or not accessible
            self.logger.error(f"Connection error: Cannot connect to {self.base_url}")
            self.logger.info("Please ensure Client Portal Gateway is running")
            return None
            
        except requests.exceptions.Timeout:
            # Request took too long
            self.logger.error("Request timeout")
            return None
            
        except Exception as e:
            # Catch-all for unexpected errors
            self.logger.error(f"Request error: {e}")
            return None
    
    def check_authentication(self) -> bool:
        """
        Check if the current session is authenticated with IBKR.
        
        This should be called before making other API requests to ensure
        the session is valid. If not authenticated, call sso_validate().
        
        Endpoint: GET /iserver/auth/status
        
        Returns:
            True if session is authenticated and valid
            False if session is not authenticated or check failed
        """
        result = self._make_request('GET', '/iserver/auth/status')
        
        if result and result.get('authenticated'):
            self.logger.info("Session is authenticated")
            return True
        else:
            self.logger.warning("Session not authenticated")
            return False
    
    def sso_validate(self) -> bool:
        """
        Initiate Single Sign-On (SSO) authentication flow.
        
        This triggers the authentication process with IBKR. After calling this,
        wait a few seconds and then check authentication status again.
        
        Note: The Client Portal Gateway must be properly configured and running
        for this to work.
        
        Endpoint: POST /sso/validate
        
        Returns:
            True if SSO validation was initiated successfully
            False if request failed
        """
        result = self._make_request('POST', '/sso/validate')
        
        if result:
            self.logger.info("SSO validation initiated")
            return True
        return False
    
    def tickle(self) -> bool:
        """
        Keep the session alive by sending a tickle request.
        
        IBKR sessions can timeout due to inactivity. Call this method
        periodically (e.g., every few minutes) to prevent session expiration.
        This is especially important for long-running applications.
        
        Endpoint: POST /tickle
        
        Returns:
            True if tickle was successful
            False if request failed
        """
        result = self._make_request('POST', '/tickle')
        return result is not None
    
    def search_contract(
        self, 
        symbol: str, 
        sec_type: str = "STK", 
        exchange: str = "SMART", 
        currency: str = "USD"
    ) -> Optional[List[Dict]]:  # Fixed return type: List[Dict] instead of Dict
        """
        Search for a contract by symbol and get its contract ID (conid).
        
        The conid is required for most market data operations. This method
        searches IBKR's database for matching contracts.
        
        Endpoint: GET /iserver/secdef/search
        
        Args:
            symbol: Ticker symbol to search for (e.g., "AAPL", "MSFT")
            sec_type: Security type - STK (stock), OPT (option), FUT (future),
                     CASH (forex), IND (index), BOND (bond)
            exchange: Exchange to search on - SMART for smart routing (recommended),
                     or specific exchanges like NYSE, NASDAQ, etc.
            currency: Currency for the contract (e.g., "USD", "EUR")
            
        Returns:
            List of matching contracts with details including conid
            None if search fails or no results found
            
        Example:
            contracts = api.search_contract("AAPL", "STK", "SMART", "USD")
            if contracts:
                conid = contracts[0]['conid']
        """
        params = {
            'symbol': symbol,
            'secType': sec_type,
            'exchange': exchange,
            'currency': currency
        }
        
        result = self._make_request('GET', '/iserver/secdef/search', params=params)
        
        # Validate that result is a list (if not None)
        if result is not None:
            if not isinstance(result, list):
                self.logger.error(f"Unexpected API response format for {symbol}: {type(result).__name__}")
                self.logger.debug(f"Response content: {result}")
                return None
            self.logger.info(f"Found {len(result)} contracts for {symbol}")
        
        return result
    
    def get_contract_info(self, conid: str) -> Optional[Dict]:
        """
        Get detailed information for a specific contract by conid.
        
        Returns comprehensive contract details including:
        - Full contract specifications
        - Trading hours
        - Margin requirements
        - Contract multipliers (for derivatives)
        
        Endpoint: GET /iserver/contract/{conid}/info
        
        Args:
            conid: Contract identifier from search_contract()
            
        Returns:
            Dictionary with detailed contract information
            None if request fails or contract not found
        """
        return self._make_request('GET', f'/iserver/contract/{conid}/info')
    
    def get_market_data_snapshot(
        self, 
        conids: List[str], 
        fields: List[str] = None
    ) -> Optional[List[Dict]]:
        """
        Get real-time market data snapshot for one or more contracts.
        
        This is the primary method for getting current price data. It supports
        bulk requests for multiple contracts simultaneously.
        
        Endpoint: GET /iserver/marketdata/snapshot
        
        Common field IDs (what data to retrieve):
            31: Last Price - Most recent trade price
            55: Bid Size - Number of shares at bid
            84: Bid Price - Current highest bid
            85: Ask Price - Current lowest ask
            86: Change - Absolute price change from previous close
            87: Change Percentage - Percentage change from previous close
            88: Volume - Total trading volume
            70: High - Day's highest price
            71: Low - Day's lowest price
            72: Close - Previous day's closing price
            73: Open - Opening price
            74: Previous Close - Previous trading day's close
            
        Args:
            conids: List of contract identifiers to retrieve data for
            fields: List of field IDs to retrieve (defaults to common fields)
            
        Returns:
            List of dictionaries containing market data for each contract
            None if request fails
            
        Example:
            data = api.get_market_data_snapshot(["265598"], ["31", "84", "85"])
            last_price = data[0]['31']  # Access last price
        """
        # Use default fields if none specified - covers most common use cases
        if fields is None:
            fields = ["31", "84", "85", "86", "87", "88", "70", "71", "72", "73"]
        
        # Build query parameters - API expects comma-separated strings
        params = {
            'conids': ','.join(conids),
            'fields': ','.join(fields)
        }
        
        return self._make_request('GET', '/iserver/marketdata/snapshot', params=params)
    
    def get_historical_data(
        self, 
        conid: str, 
        period: str = "1d", 
        bar: str = "1min", 
        exchange: str = ""
    ) -> Optional[Dict]:
        """
        Get historical market data (OHLCV bars) for a contract.
        
        Returns time-series data with Open, High, Low, Close, and Volume
        for the specified period and bar size.
        
        Endpoint: GET /iserver/marketdata/history
        
        Available periods:
            1d: One day
            1w: One week
            1m: One month
            1y: One year
            5y: Five years
            
        Available bar sizes:
            1min, 2min, 5min, 15min, 30min: Intraday bars
            1h, 2h, 4h: Hourly bars
            1d: Daily bars
            
        Args:
            conid: Contract identifier
            period: Time period for historical data
            bar: Bar size/interval for the data
            exchange: Optional exchange specification (usually not needed)
            
        Returns:
            Dictionary with 'data' key containing list of historical bars
            Each bar has: 't' (timestamp), 'o' (open), 'h' (high), 
                         'l' (low), 'c' (close), 'v' (volume)
            None if request fails
            
        Example:
            history = api.get_historical_data("265598", period="1w", bar="1d")
            if history and 'data' in history:
                for bar in history['data']:
                    print(f"Date: {bar['t']}, Close: {bar['c']}")
        """
        # Build query parameters
        params = {
            'conid': conid,
            'period': period,
            'bar': bar
        }
        
        # Add exchange if specified (optional for most use cases)
        if exchange:
            params['exchange'] = exchange
            
        return self._make_request('GET', '/iserver/marketdata/history', params=params)
    
    def get_portfolio_accounts(self) -> Optional[List[Dict]]:
        """
        Get list of portfolio accounts.
        
        Returns information about all brokerage accounts linked to the session.
        
        Endpoint: GET /portfolio/accounts
        
        Returns:
            List of account dictionaries with account IDs and metadata
            None if request fails
            
        Example:
            accounts = api.get_portfolio_accounts()
            if accounts:
                account_id = accounts[0]['accountId']
        """
        result = self._make_request('GET', '/portfolio/accounts')
        
        if result:
            self.logger.info(f"Retrieved {len(result)} account(s)")
        
        return result
    
    def get_portfolio_positions(self, account_id: str) -> Optional[List[Dict]]:
        """
        Get all positions for a specific account.
        
        Returns detailed information about all open positions including
        contract details, position size, market value, and P&L.
        
        Endpoint: GET /portfolio/{accountId}/positions/0
        
        Args:
            account_id: Account identifier from get_portfolio_accounts()
            
        Returns:
            List of position dictionaries with holdings information
            None if request fails
            
        Position fields include:
            - conid: Contract identifier
            - contractDesc: Contract description
            - position: Number of shares/contracts
            - mktPrice: Current market price
            - mktValue: Current market value
            - currency: Position currency
            - avgCost: Average cost basis
            - avgPrice: Average purchase price
            - unrealizedPnl: Unrealized profit/loss
            - ticker: Ticker symbol (if available)
            
        Example:
            positions = api.get_portfolio_positions("U1234567")
            for pos in positions:
                print(f"{pos['contractDesc']}: {pos['position']} @ ${pos['mktPrice']}")
        """
        result = self._make_request('GET', f'/portfolio/{account_id}/positions/0')
        
        if result:
            self.logger.info(f"Retrieved {len(result)} position(s) for account {account_id}")
        
        return result