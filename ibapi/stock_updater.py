"""
IBKR Asset Allocation Updater
==============================
Updates asset allocation Excel with quantities from IBKR portfolio and current market prices.

Features:
- Fetches portfolio positions from IBKR
- Updates quantities for holdings in portfolio
- Updates market prices for all securities
- Provides detailed error reporting

Usage:
    python stock_updater.py
"""

from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass, field
import openpyxl
from IBKRPriceFetcher import IBKRPriceFetcher
from IBKRClientPortalAPI import IBKRClientPortalAPI
from datetime import datetime
import shutil
from pathlib import Path


# Constants
EXCEL_FILE_PATH = r"C:\Users\George\Documents\asset allocation.xlsx"
DEFAULT_SHEET_NAME = "stock"
MAX_HEADER_SEARCH_ROWS = 20
MAX_END_MARKER_SEARCH_COLS = 15

# Chinese header names
HEADER_SYMBOL = "編號"
HEADER_QUANTITY = "股數"
HEADER_PRICE = "市價"
HEADER_NAME = "股票名稱"
END_MARKER = "佔投資組合持股市值"


@dataclass
class ColumnMapping:
    """Excel column indices for data fields."""
    symbol: Optional[int] = None
    quantity: Optional[int] = None
    price: Optional[int] = None
    name: Optional[int] = None


@dataclass
class UpdateStatistics:
    """Statistics for update operations."""
    qty_updated: int = 0
    qty_not_in_portfolio: int = 0
    price_updated: int = 0
    price_failed: int = 0
    skipped: int = 0
    qty_changes: List[Tuple[str, float, float]] = field(default_factory=list)


@dataclass
class ErrorRecord:
    """Record of a failed operation."""
    row: int
    symbol: str
    name: Optional[str] = None
    market: Optional[str] = None
    error: Optional[str] = None


class ErrorTracker:
    """Tracks errors during update process."""

    def __init__(self):
        self.not_in_portfolio: List[ErrorRecord] = []
        self.contract_not_found: List[ErrorRecord] = []
        self.no_market_data: List[ErrorRecord] = []
        self.price_failed: List[ErrorRecord] = []

    def has_errors(self) -> bool:
        """Check if any errors were tracked."""
        return any([
            self.not_in_portfolio,
            self.contract_not_found,
            self.no_market_data,
            self.price_failed
        ])


def is_valid_symbol(value: str) -> bool:
    """
    Validate if a cell value is a valid security symbol.

    Valid: AAPL, 939, US91282CJV46, BRK.B
    Invalid: Empty, Chinese characters, percentages, formulas
    """
    if not value:
        return False

    value = str(value).strip()

    if not value or value == HEADER_SYMBOL:
        return False

    # Skip Chinese characters
    if any('\u4e00' <= c <= '\u9fff' for c in value):
        return False

    # Skip decimal-only numbers (0.15, 1.5)
    if '.' in value and value.replace('.', '').isdigit():
        return False

    # Skip special characters except . and / (for stocks/bonds)
    invalid_chars = {'%', '$', '=', ':', '（', '）'}
    if any(char in value for char in invalid_chars):
        return False

    # Must have letters or be all digits
    has_letter = any(c.isalpha() for c in value)
    all_digits = value.isdigit()

    return has_letter or all_digits


def is_isin(symbol: str) -> bool:
    """Check if symbol is in ISIN format (12 chars, 2-letter country code)."""
    if not symbol or len(symbol) != 12:
        return False

    symbol = str(symbol).strip()
    return (symbol[:2].isalpha() and
            symbol[-1].isdigit() and
            symbol[2:11].isalnum())


def detect_market_info(symbol: str) -> Tuple[str, str, str]:
    """
    Detect security type, exchange, and currency from symbol.

    Returns: (sec_type, exchange, currency)
    """
    symbol = str(symbol).strip()

    # ISIN → Bond
    if is_isin(symbol):
        return ("BOND", "SMART", "USD")

    # Has letters → US stock
    if any(c.isalpha() for c in symbol):
        return ("STK", "SMART", "USD")

    # All digits → HK stock
    if symbol.isdigit():
        return ("STK", "SEHK", "HKD")

    return ("STK", "SMART", "USD")


def find_header_columns(ws, max_rows: int = MAX_HEADER_SEARCH_ROWS) -> ColumnMapping:
    """Find column indices for all headers in the worksheet."""
    columns = ColumnMapping()

    for row in range(1, max_rows + 1):
        for col in range(1, 15):
            cell_value = ws.cell(row, col).value

            if cell_value == HEADER_SYMBOL:
                columns.symbol = col
            elif cell_value == HEADER_QUANTITY:
                columns.quantity = col
            elif cell_value == HEADER_PRICE:
                columns.price = col
            elif cell_value == HEADER_NAME:
                columns.name = col

        # Early exit if all found
        if all([columns.symbol, columns.quantity, columns.price, columns.name]):
            break

    return columns


def find_data_tables(ws, symbol_col: int) -> List[Tuple[int, int]]:
    """Find all data tables in the worksheet."""
    tables = []
    current_start = None

    for row in range(1, ws.max_row + 1):
        # Check for table header
        cell_value = ws.cell(row, symbol_col).value
        if cell_value and str(cell_value).strip() == HEADER_SYMBOL:
            current_start = row
            continue

        # Check for end marker
        has_end_marker = False
        for col in range(1, MAX_END_MARKER_SEARCH_COLS):
            cell_value = ws.cell(row, col).value
            if cell_value and END_MARKER in str(cell_value):
                has_end_marker = True
                break

        if has_end_marker and current_start:
            end_row = row - 2
            if end_row >= current_start:
                tables.append((current_start, end_row))
            current_start = None

    return tables


def clean_price(value) -> Optional[float]:
    """Clean IBKR price values (removes letter prefixes like C, H, L)."""
    if value is None:
        return None

    try:
        if isinstance(value, (int, float)):
            return float(value)

        value_str = str(value).strip()

        # Remove letter prefix if present
        if value_str and value_str[0].isalpha():
            value_str = value_str[1:]

        return float(value_str)
    except (TypeError, ValueError) as e:
        print(f"Could not convert price value '{value}': {e}")
        return None


def fetch_portfolio(api: IBKRClientPortalAPI) -> Dict[str, Dict]:
    """Fetch portfolio positions from IBKR."""
    print("\n" + "=" * 80)
    print("📊 FETCHING PORTFOLIO DATA")
    print("=" * 80 + "\n")

    accounts = api.get_portfolio_accounts()
    if not accounts:
        print("⚠️  Could not retrieve portfolio accounts")
        return {}

    print(f"✅ Found {len(accounts)} account(s)")

    account_id = accounts[0].get('accountId')
    print(f"📊 Using account: {account_id}")

    positions = api.get_portfolio_positions(account_id)
    if not positions:
        print("⚠️  No positions found")
        return {}

    print(f"✅ Found {len(positions)} position(s)\n")

    portfolio = {}
    for pos in positions:
        ticker = pos.get('ticker', '').strip().upper() if pos.get('ticker') else ''
        if ticker:
            portfolio[ticker] = {
                'quantity': pos.get('position', 0),
                'conid': str(pos.get('conid', '')),
                'currency': pos.get('currency', 'USD'),
                'description': pos.get('contractDesc', '')
            }
            print(f"  • {ticker}: {portfolio[ticker]['quantity']} shares")

    print()
    return portfolio


def update_quantity(ws, row: int, col: int, symbol: str, portfolio: Dict,
                    stats: UpdateStatistics, errors: ErrorTracker, stock_name: Optional[str]):
    """Update quantity for a single security."""
    if symbol in portfolio:
        old_qty = ws.cell(row, col).value or 0
        new_qty = portfolio[symbol]['quantity']
        
        ws.cell(row, col).value = new_qty
        print(f"  ✅ Quantity: {new_qty}")
        stats.qty_updated += 1
        
        # Track if quantity changed
        if old_qty != new_qty:
            stats.qty_changes.append((symbol, old_qty, new_qty))
    else:
        print(f"  ⚠️  Quantity: Not in portfolio")
        stats.qty_not_in_portfolio += 1
        errors.not_in_portfolio.append(ErrorRecord(row, symbol, stock_name))


def update_price(ws, row: int, col: int, symbol: str, stock_name: Optional[str],
                fetcher: IBKRPriceFetcher, stats: UpdateStatistics, errors: ErrorTracker):
    """Update price for a single security."""
    sec_type, exchange, currency = detect_market_info(symbol)

    try:
        price_data = fetcher.get_price(symbol, sec_type, exchange, currency, stock_name)

        if price_data and price_data.last_price is not None:
            price = clean_price(price_data.last_price)
            ws.cell(row, col).value = price
            print(f"  ✅ Price: {currency} {price:.2f}")
            stats.price_updated += 1
        else:
            print(f"  ❌ Price: No data available")
            stats.price_failed += 1
            errors.no_market_data.append(
                ErrorRecord(row, symbol, stock_name, f"{exchange}/{currency}")
            )
    except Exception as e:
        error_msg = str(e)
        print(f"  ❌ Price: {error_msg[:50]}")
        stats.price_failed += 1

        # Categorize error
        if 'contract' in error_msg.lower():
            errors.contract_not_found.append(
                ErrorRecord(row, symbol, stock_name, f"{exchange}/{currency}", error_msg[:100])
            )
        else:
            errors.price_failed.append(
                ErrorRecord(row, symbol, stock_name, f"{exchange}/{currency}", error_msg[:100])
            )


def print_column_mapping(columns: ColumnMapping):
    """Print found columns."""
    print("=" * 80)
    print("COLUMN MAPPING")
    print("=" * 80)
    print(f"✅ {HEADER_SYMBOL}: Column {columns.symbol}")

    if columns.quantity:
        print(f"✅ {HEADER_QUANTITY}: Column {columns.quantity}")
    else:
        print(f"⚠️  {HEADER_QUANTITY}: Not found - quantities will not be updated")

    if columns.price:
        print(f"✅ {HEADER_PRICE}: Column {columns.price}")
    else:
        print(f"⚠️  {HEADER_PRICE}: Not found - prices will not be updated")

    if columns.name:
        print(f"✅ {HEADER_NAME}: Column {columns.name}")


def print_summary(stats: UpdateStatistics, portfolio_size: int):
    """Print update summary."""
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\n📊 Quantities:")
    print(f"   ✅ Updated: {stats.qty_updated}")
    
    if stats.qty_changes:
        print(f"\n   🔄 Changed quantities ({len(stats.qty_changes)}):")
        for symbol, old_qty, new_qty in stats.qty_changes:
            diff = new_qty - old_qty
            sign = "+" if diff > 0 else ""
            print(f"      • {symbol}: {old_qty} → {new_qty} ({sign}{diff})")
    else:
        print(f"   ℹ️  No quantity changes detected")
    
    print(f"\n   ⚠️  Not in portfolio: {stats.qty_not_in_portfolio}")
    print(f"\n💰 Prices:")
    print(f"   ✅ Updated: {stats.price_updated}")
    print(f"   ❌ Failed: {stats.price_failed}")
    print(f"\n⏭️  Skipped: {stats.skipped}")

    if portfolio_size > 0:
        print(f"\n📝 Portfolio had {portfolio_size} positions")


def print_error_report(errors: ErrorTracker):
    """Print detailed error report."""
    print("\n" + "=" * 80)
    print("DETAILED ERROR REPORT")
    print("=" * 80)
    
    if not errors.has_errors():
        print("\n✅ No errors detected! All securities updated successfully.")
        print("\n" + "=" * 80)
        return
    
    # Define error categories with their display info
    error_categories = [
        {
            'errors': errors.not_in_portfolio,
            'icon': '❌',
            'title': 'NOT IN PORTFOLIO',
            'description': 'These symbols are in Excel but not in your IBKR portfolio:',
            'tip': 'Check if you still hold these or remove from Excel',
            'show_market': False,
            'show_error': False
        },
        {
            'errors': errors.contract_not_found,
            'icon': '❌',
            'title': 'CONTRACTS NOT FOUND',
            'description': 'IBKR could not find these symbols:',
            'tip': 'Verify symbols are correct for the market',
            'show_market': True,
            'show_error': True
        },
        {
            'errors': errors.no_market_data,
            'icon': '⚠️',
            'title': 'NO MARKET DATA',
            'description': 'Contract found but no price available:',
            'tip': 'Market may be closed or data subscription required',
            'show_market': True,
            'show_error': False
        },
        {
            'errors': errors.price_failed,
            'icon': '❌',
            'title': 'OTHER ERRORS',
            'description': 'Unexpected errors while fetching prices:',
            'tip': None,
            'show_market': False,
            'show_error': True
        }
    ]
    
    # Print each category
    for category in error_categories:
        error_list = category['errors']
        if not error_list:
            continue
        
        # Header
        print(f"\n{category['icon']} {category['title']} ({len(error_list)})")
        print("-" * 80)
        print(f"{category['description']}\n")
        
        # Error entries
        for err in error_list:
            name_str = f" - {err.name}" if err.name else ""
            print(f"  Row {err.row:3d}: {err.symbol}{name_str}")
            
            if category['show_market'] and err.market:
                print(f"           Market: {err.market}")
            
            if category['show_error'] and err.error:
                print(f"           Error: {err.error}")
            
            if category['show_market'] or category['show_error']:
                print()
        
        # Tip
        if category['tip']:
            print(f"💡 {category['tip']}")
    
    print("\n" + "=" * 80)


@dataclass
class AppContext:
    """Application context holding all shared state."""
    api: IBKRClientPortalAPI
    fetcher: IBKRPriceFetcher
    portfolio: Dict[str, Dict]
    columns: ColumnMapping
    stats: UpdateStatistics
    errors: ErrorTracker


def setup_workbook(file_path: str):
    """Load and configure workbook. Returns (wb, ws) or (None, None) on error."""
    try:
        wb = openpyxl.load_workbook(file_path)
        wb.calculation.calcMode = 'auto'
        wb.calculation.fullCalcOnLoad = True
        
        if DEFAULT_SHEET_NAME in wb.sheetnames:
            wb.active = wb[DEFAULT_SHEET_NAME]
            print(f"✅ Using sheet: '{DEFAULT_SHEET_NAME}'\n")
        
        return wb, wb.active
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return None, None
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return None, None


def validate_workbook_structure(ws, columns: ColumnMapping, tables: List[Tuple[int, int]]) -> bool:
    """Validate workbook has required structure. Returns True if valid."""
    if not columns.symbol:
        print(f"❌ Could not find '{HEADER_SYMBOL}' column")
        return False
    
    if not tables:
        print("\n❌ No data tables found")
        return False
    
    return True


def get_stock_name(ws, row: int, columns: ColumnMapping) -> Optional[str]:
    """Extract stock name from worksheet if available."""
    if not columns.name:
        return None
    
    name_value = ws.cell(row, columns.name).value
    return str(name_value).strip() if name_value else None


def process_row(ws, row: int, symbol: str, ctx: AppContext):
    """Process a single row (update quantity and price)."""
    print(f"Row {row}: {symbol}")
    stock_name = get_stock_name(ws, row, ctx.columns)
    
    # Update quantity if column exists
    if ctx.columns.quantity:
        update_quantity(ws, row, ctx.columns.quantity, symbol, ctx.portfolio,
                       ctx.stats, ctx.errors, stock_name)
    
    # Update price if column exists
    if ctx.columns.price:
        update_price(ws, row, ctx.columns.price, symbol, stock_name,
                    ctx.fetcher, ctx.stats, ctx.errors)
    
    print()


def process_tables(ws, tables: List[Tuple[int, int]], ctx: AppContext):
    """Process all data tables in the worksheet."""
    print("\n" + "=" * 80)
    print("UPDATING POSITIONS")
    print("=" * 80 + "\n")
    
    for table_num, (start_row, end_row) in enumerate(tables, 1):
        print(f"📋 Table {table_num}:\n")
        
        for row in range(start_row + 1, end_row + 1):
            symbol_value = ws.cell(row, ctx.columns.symbol).value
            
            # Skip invalid symbols
            if not is_valid_symbol(symbol_value):
                if symbol_value:
                    ctx.stats.skipped += 1
                continue
            
            symbol = str(symbol_value).strip().upper()
            process_row(ws, row, symbol, ctx)


def save_workbook(wb, file_path: str) -> bool:
    """Save workbook with error handling. Returns True if successful."""
    print("=" * 80)
    print("SAVING FILE")
    print("=" * 80 + "\n")
    
    try:
        for sheet in wb.worksheets:
            sheet.sheet_view.tabSelected = False
        wb.save(file_path)
        print("✅ File saved successfully!\n")
        return True
    except Exception as e:
        print(f"❌ Error saving: {e}")
        return False


def update_asset_allocation(file_path: str = EXCEL_FILE_PATH) -> None:
    """Main function to update asset allocation Excel file."""
    # Print header
    print("\n" + "=" * 80)
    print("📊 IBKR ASSET ALLOCATION UPDATER")
    print("=" * 80 + "\n")
    print(f"📂 File: {file_path}\n")
    
    # Initialize APIs
    api = IBKRClientPortalAPI()
    fetcher = IBKRPriceFetcher()
    
    # Authenticate
    if not api.check_authentication():
        print("❌ Not authenticated. Please start Client Portal Gateway.")
        return
    print("✅ Authenticated\n")
    
    # Fetch portfolio
    portfolio = fetch_portfolio(api)
    
    # Load workbook
    wb, ws = setup_workbook(file_path)
    if not wb:
        return
    
    try:
        # Find structure
        columns = find_header_columns(ws)
        print_column_mapping(columns)
        
        tables = find_data_tables(ws, columns.symbol)
        
        # Validate structure
        if not validate_workbook_structure(ws, columns, tables):
            return
        
        print(f"\n✅ Found {len(tables)} data table(s)")
        for i, (start, end) in enumerate(tables, 1):
            print(f"   Table {i}: Rows {start + 1} to {end}")
        
        # Create context
        ctx = AppContext(
            api=api,
            fetcher=fetcher,
            portfolio=portfolio,
            columns=columns,
            stats=UpdateStatistics(),
            errors=ErrorTracker()
        )
        
        # Process all tables
        process_tables(ws, tables, ctx)
        
        # Save workbook
        save_workbook(wb, file_path)
        
        # Print reports
        print_summary(ctx.stats, len(portfolio))
        print_error_report(ctx.errors)
        
    finally:
        wb.close()


if __name__ == "__main__":
    update_asset_allocation()