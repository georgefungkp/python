"""
Test script for debugging IBKR symbol lookups and prices.
"""

from IBKRPriceFetcher import IBKRPriceFetcher
from IBKRClientPortalAPI import IBKRClientPortalAPI
from typing import List, Tuple, Optional


def display_contract_details(contract: dict, index: int = None):
    """Display detailed information about a contract."""
    # Validate that contract is actually a dictionary
    if not isinstance(contract, dict):
        print(f"  ⚠️  Error: Expected dictionary but got {type(contract).__name__}: {contract}")
        return
    
    prefix = f"Contract {index}: " if index else ""

    print(f"{prefix}")
    print(f"  Conid: {contract.get('conid')}")
    print(f"  Symbol: {contract.get('symbol')}")
    print(f"  Description: {contract.get('description')}")
    print(f"  Exchange: {contract.get('exchange')}")
    print(f"  Currency: {contract.get('currency')}")
    print(f"  Instrument Type: {contract.get('instrumentType')}")
    if contract.get('companyName'):
        print(f"  Company: {contract.get('companyName')}")
    print()


def display_market_data(data: dict, currency: str = "USD", contract: dict = None):
    """Display market data fields."""
    field_names = {
        '31': 'Last Price',
        '84': 'Bid Price',
        '85': 'Ask Price',
        '86': 'Change',
        '87': 'Change % / Yield',
        '88': 'Volume',
        '70': 'High',
        '71': 'Low',
        '72': 'Close',
        '73': 'Open'
    }

    # Display contract identification info if available
    if contract:
        print("  Contract Info:")
        print(f"    Symbol: {contract.get('symbol', 'N/A')}")
        print(f"    Name: {contract.get('companyName') or contract.get('description', 'N/A')}")
        print(f"    Exchange: {contract.get('exchange', 'N/A')}")
        print(f"    Currency: {contract.get('currency', 'N/A')}")
        print(f"    Conid: {contract.get('conid', data.get('conid', 'N/A'))}")
        print()

    print("  Available fields:")
    for field_id, field_value in data.items():
        if field_id not in ['conid', 'server_id']:
            field_name = field_names.get(field_id, f'Field {field_id}')
            print(f"    {field_name}: {field_value}")

    # Try to extract and display price
    last_price = data.get('31') or data.get('84') or data.get('85') or data.get('72')
    if last_price:
        price_str = str(last_price)
        if price_str and price_str[0].isalpha():
            price_str = price_str[1:]
        try:
            price = float(price_str)
            print(f"  💰 Price: {currency} ${price:.2f}")
        except:
            print(f"  ⚠️  Raw price value: {last_price}")
    else:
        print("  ❌ No price data available")


def search_and_display_contracts(api: IBKRClientPortalAPI, symbol: str,
                                 sec_type: str, exchange: str, currency: str) -> Optional[List[dict]]:
    """Search for contracts and display them."""
    print(f"🔍 Searching for {sec_type} contracts matching '{symbol}'...")
    contracts = api.search_contract(symbol, sec_type, exchange, currency)

    if not contracts:
        print(f"❌ No contracts found for {symbol}")
        return None

    # Validate that contracts is a list
    if not isinstance(contracts, list):
        print(f"❌ Unexpected response format. Expected list but got {type(contracts).__name__}")
        print(f"   Response: {contracts}")
        return None

    print(f"✅ Found {len(contracts)} contract(s):\n")

    for i, contract in enumerate(contracts, 1):
        # Additional validation for each contract item
        if not isinstance(contract, dict):
            print(f"Contract {i}: ⚠️  Invalid format (expected dict, got {type(contract).__name__}): {contract}\n")
            continue
        display_contract_details(contract, i)

    return contracts


def fetch_and_display_prices(api: IBKRClientPortalAPI, contracts: List[dict], currency: str = "USD"):
    """Fetch and display market data for contracts."""
    print("-" * 80)
    print("📊 Fetching prices for each contract:\n")

    for i, contract in enumerate(contracts, 1):
        conid = str(contract.get('conid'))
        exchange_name = contract.get('exchange', 'N/A')

        print(f"Contract {i} (Conid: {conid}, Exchange: {exchange_name}):")

        market_data = api.get_market_data_snapshot([conid])

        if market_data and len(market_data) > 0:
            display_market_data(market_data[0], currency, contract)
        else:
            print("  ❌ No market data received")

        print()


def test_security(symbol: str, sec_type: str = "STK", exchange: str = "SMART", currency: str = "USD"):
    """
    Test a security by searching and fetching its price.

    Args:
        symbol: Security symbol
        sec_type: Security type (STK, BOND, etc.)
        exchange: Exchange (SMART, SEHK, etc.)
        currency: Currency (USD, HKD, etc.)
    """
    print("=" * 80)
    print(f"Testing {sec_type}: {symbol}")
    print(f"Exchange: {exchange}, Currency: {currency}")
    print("=" * 80)

    api = IBKRClientPortalAPI()

    if not api.check_authentication():
        print("❌ Not authenticated. Please start Client Portal Gateway.")
        return

    print("✅ Authenticated\n")

    # Search and display contracts
    contracts = search_and_display_contracts(api, symbol, sec_type, exchange, currency)

    if contracts:
        # Fetch and display prices
        fetch_and_display_prices(api, contracts, currency)

    print("=" * 80)


def test_multiple_securities():
    """Test multiple securities to compare results."""
    test_cases = [
        ("3478", "STK", "SEHK", "HKD"),      # Hong Kong stock
        ("939", "STK", "SEHK", "HKD"),       # Hong Kong stock
        ("AAPL", "STK", "SMART", "USD"),     # US stock
        ("PTBD", "STK", "SMART", "USD"),     # US stock
        ("US91282CJV46", "BOND", "SMART", "USD")  # US Bond (ISIN)
    ]

    for symbol, sec_type, exchange, currency in test_cases:
        test_security(symbol, sec_type, exchange, currency)
        print("\n")


def test_bond_by_identifier():
    """Interactive test to search bonds by ISIN or CUSIP."""
    print("\n" + "=" * 80)
    print("Bond Search by ISIN/CUSIP")
    print("=" * 80)

    api = IBKRClientPortalAPI()

    if not api.check_authentication():
        print("❌ Not authenticated. Please start Client Portal Gateway.")
        return

    print("✅ Authenticated\n")

    print("Enter bond identifier:")
    print("  - ISIN (e.g., US91282CJV46)")
    print("  - CUSIP (e.g., 912828C57)")
    identifier = input("Identifier: ").strip()

    if not identifier:
        print("⚠️  No identifier provided. Exiting.")
        return

    print(f"\n🔍 Searching for bond: {identifier}...\n")

    contracts = api.search_contract(identifier, "BOND", "SMART", "USD")

    if not contracts or len(contracts) == 0:
        print(f"❌ No contracts found for {identifier}")
        print("\n💡 Tips:")
        print("  - Verify the identifier is correct")
        print("  - Try both ISIN and CUSIP formats")
        print("  - Check if bond is available on IBKR")
        return

    print(f"✅ Found {len(contracts)} contract(s):\n")

    for i, contract in enumerate(contracts, 1):
        display_contract_details(contract, i)

    # Get market data for first contract
    if contracts:
        conid = str(contracts[0].get('conid'))
        print(f"📊 Fetching market data for CONID {conid}...\n")

        market_data = api.get_market_data_snapshot([conid])

        if market_data and len(market_data) > 0:
            print("💰 Market Data:")
            display_market_data(market_data[0], "USD")
        else:
            print("❌ No market data available")

    print("\n" + "=" * 80)


def test_with_fetcher(symbol: str, sec_type: str = "STK",
                     exchange: str = "SMART", currency: str = "USD",
                     stock_name: str = None):
    """Test using the high-level IBKRPriceFetcher interface."""
    print("\n" + "=" * 80)
    print(f"Testing with IBKRPriceFetcher: {symbol}")
    print("=" * 80)

    fetcher = IBKRPriceFetcher()

    print(f"\n🔍 Fetching data for '{symbol}'...")

    price_data = fetcher.get_price(
        symbol=symbol,
        sec_type=sec_type,
        exchange=exchange,
        currency=currency,
        stock_name=stock_name
    )

    if price_data and price_data.last_price:
        print(f"✅ Price: ${price_data.last_price:.2f}")
        if price_data.bid_price:
            print(f"   Bid: ${price_data.bid_price:.2f}")
        if price_data.ask_price:
            print(f"   Ask: ${price_data.ask_price:.2f}")
    else:
        print("❌ Could not retrieve price")

    print("=" * 80)


if __name__ == "__main__":
    # Test individual stock
    # test_security("BRK.B", "STK", "NYSE", "USD")
    # test_security("BRK-B", "STK", "NYSE", "USD")
    # test_security("BRK", "STK", "NYSE", "USD")
    test_security("3033", "STK", "SEHK", "HKD")
    test_security("PTLC", "STK", "SMART", "USD")
    test_security("2806", "STK", "SEHK", "HKD")
    test_security("2807", "STK", "SEHK", "HKD")
    test_security("3439", "STK", "SEHK", "HKD")
    test_security("ARKQ", "STK", "SEHK", "HKD")
    test_security("GLD", "STK", "SEHK", "HKD")

    print("\n\n")

    # Test bond with ISIN
    # test_security("US91282CJV46", "BOND", "SMART", "USD")

    print("\n\n")

    # Interactive bond test
    # test_bond_by_identifier()

    # Test multiple securities
    # test_multiple_securities()

    # Test with fetcher
    # test_with_fetcher("AAPL", "STK", "SMART", "USD")