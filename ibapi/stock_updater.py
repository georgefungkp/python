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
import re


# Constants
EXCEL_FILE_PATH = r"C:\Users\George\Documents\asset allocation.xlsx"
DEFAULT_SHEET_NAME = "Stock"
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
    symbols_in_excel: set = field(default_factory=set)  # Track symbols we found in Excel


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
    # Validate symbol_col is not None
    if symbol_col is None:
        raise ValueError("symbol_col cannot be None. The symbol column (編號) is required but was not found.")
    
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


def normalize_symbol(symbol: str) -> str:
    """
    Normalize symbol for portfolio matching.

    Handles variations like:
    - "BRK.B" → "BRK B" (dots to spaces)
    - "US-T 31/01/26" → "US-T" (remove date suffixes)
    - Strips whitespace and converts to uppercase
    """
    if not symbol:
        return ""

    normalized = str(symbol).strip().upper()

    # Replace dots with spaces (BRK.B → BRK B)
    normalized = normalized.replace('.', ' ')

    # Remove date suffixes for bonds (e.g., "US-T 31/01/26" → "US-T")
    # Match patterns like: "31/01/26", "01/31/26", "2026-01-31", etc.
    import re
    # Remove common date patterns at the end
    normalized = re.sub(r'\s+\d{1,2}[/-]\d{1,2}[/-]\d{2,4}$', '', normalized)
    normalized = re.sub(r'\s+\d{4}[/-]\d{1,2}[/-]\d{1,2}$', '', normalized)

    return normalized.strip()


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
            # Store with normalized key for better matching
            normalized_ticker = normalize_symbol(ticker)

            portfolio[normalize_symbol(ticker)] = {
                'quantity': pos.get('position', 0),
                'conid': str(pos.get('conid', '')),
                'currency': pos.get('currency', 'USD'),
                'description': pos.get('contractDesc', ''),
                'original_ticker': ticker  # Keep original for display
            }
            print(f"  • {ticker}: {portfolio[normalized_ticker]['quantity']} shares")

    print()
    return portfolio


def update_quantity(ws, row: int, col: int, symbol: str, portfolio: Dict,
                    stats: UpdateStatistics, errors: ErrorTracker, stock_name: Optional[str]):
    """Update quantity for a single security."""
    # Normalize symbol for portfolio lookup
    normalized_symbol = normalize_symbol(symbol)
    
    if normalized_symbol in portfolio:
        old_qty = ws.cell(row, col).value or 0
        new_qty = portfolio[normalized_symbol]['quantity']
        
        ws.cell(row, col).value = new_qty
        print(f"  ✅ Quantity: {new_qty}")
        stats.qty_updated += 1
        
        # Track if quantity changed
        if old_qty != new_qty:
            stats.qty_changes.append((symbol, old_qty, new_qty))
    else:
        print(f"  ⚠️  Quantity: Not in portfolio")
        print(f"     Reason: Symbol '{symbol}' (normalized: '{normalized_symbol}') not found in your IBKR holdings")
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


def print_summary(stats: UpdateStatistics, portfolio: Dict[str, Dict]):
    """Print concise update summary."""
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    # Quantities section
    if stats.qty_updated > 0:
        print(f"\n📊 Quantities: {stats.qty_updated} updated")
        if stats.qty_changes:
            print(f"   Changed: {len(stats.qty_changes)}")
            for symbol, old_qty, new_qty in stats.qty_changes:
                diff = new_qty - old_qty
                sign = "+" if diff > 0 else ""
                print(f"      {symbol}: {old_qty} → {new_qty} ({sign}{diff})")
    
    if stats.qty_not_in_portfolio > 0:
        print(f"   Not in portfolio: {stats.qty_not_in_portfolio} (see details below)")
    
    # Prices section
    print(f"\n💰 Prices: {stats.price_updated} updated")
    if stats.price_failed > 0:
        print(f"   Failed: {stats.price_failed} (see details below)")
    
    if stats.skipped > 0:
        print(f"\n⏭️  Skipped: {stats.skipped} invalid symbols")
    
    # Portfolio analysis
    if portfolio:
        print(f"\n📝 Portfolio: {len(portfolio)} positions")
        
        # Find positions not in Excel
        missing_in_excel = []
        for normalized_symbol, position_data in portfolio.items():
            if normalized_symbol not in stats.symbols_in_excel:
                original_ticker = position_data.get('original_ticker', normalized_symbol)
                quantity = position_data.get('quantity', 0)
                missing_in_excel.append((original_ticker, quantity))
        
        if missing_in_excel:
            print(f"\n⚠️  Positions NOT in Excel: {len(missing_in_excel)}")
            print("   The following positions are in your IBKR portfolio but not found in Excel:")
            for ticker, qty in sorted(missing_in_excel):
                print(f"      {ticker}: {qty} shares")
        else:
            print("   ✅ All portfolio positions are in Excel")


def print_error_report(errors: ErrorTracker):
    """Print clean, concise error report."""
    print("\n" + "=" * 80)
    print("ISSUES FOUND")
    print("=" * 80)
    
    if not errors.has_errors():
        print("\n✅ No issues - all updates successful")
        return
    
    # Group errors by type with clean output
    if errors.not_in_portfolio:
        print(f"\n❌ NOT IN PORTFOLIO ({len(errors.not_in_portfolio)})")
        print("   Quantities not updated - symbols not in your IBKR account:")
        for err in errors.not_in_portfolio:
            print(f"      {err.symbol} (row {err.row})")
    
    if errors.contract_not_found:
        print(f"\n❌ SYMBOL NOT FOUND ({len(errors.contract_not_found)})")
        print("   Prices not updated - IBKR couldn't find these symbols:")
        for err in errors.contract_not_found:
            print(f"      {err.symbol} at {err.market} (row {err.row})")
    
    if errors.no_market_data:
        print(f"\n⚠️  NO PRICE DATA ({len(errors.no_market_data)})")
        print("   Market closed or data unavailable:")
        for err in errors.no_market_data:
            print(f"      {err.symbol} (row {err.row})")
    
    if errors.price_failed:
        print(f"\n❌ OTHER ERRORS ({len(errors.price_failed)})")
        for err in errors.price_failed:
            print(f"      {err.symbol}: {err.error[:50]} (row {err.row})")


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


def batch_update_prices(ws, symbols_to_update: List[Tuple[int, str, Optional[str]]], 
                       ctx: AppContext, batch_size: int = 10):
    """
    Update prices in batches for better network performance.
    
    Args:
        ws: Worksheet
        symbols_to_update: List of (row, symbol, stock_name) tuples
        ctx: Application context
        batch_size: Number of symbols to process in each batch
    """
    if not symbols_to_update:
        return
    
    print(f"\n💹 Batch processing {len(symbols_to_update)} price updates (batch size: {batch_size})...")
    
    # Process in batches
    for i in range(0, len(symbols_to_update), batch_size):
        batch = symbols_to_update[i:i + batch_size]
        batch_num = i // batch_size + 1
        
        print(f"   Batch {batch_num}: {', '.join([s[1] for s in batch])[:60]}...")
        
        # Phase 1: Bulk contract lookup with caching
        conid_map = {}  # symbol -> (conid, row, stock_name, sec_type, exchange, currency, normalized_symbol)
        
        for row, symbol, stock_name in batch:
            # Normalize symbol for IBKR API lookup and portfolio lookup
            normalized_symbol = normalize_symbol(symbol)
            
            # First, try to get conid from portfolio (more reliable)
            conid = None
            if normalized_symbol in ctx.portfolio:
                conid = ctx.portfolio[normalized_symbol].get('conid')
                if conid:
                    # Use portfolio conid - most reliable
                    sec_type = "STK"  # Most portfolio items are stocks
                    exchange = "SMART"
                    currency = ctx.portfolio[normalized_symbol].get('currency', 'USD')
                    conid_map[symbol] = (conid, row, stock_name, sec_type, exchange, currency, normalized_symbol)
                    continue
            
            # If not in portfolio, search for contract
            sec_type, exchange, currency = detect_market_info(normalized_symbol)
            conid = ctx.fetcher.get_conid(normalized_symbol, sec_type, exchange, currency, stock_name)
            
            if conid:
                conid_map[symbol] = (conid, row, stock_name, sec_type, exchange, currency, normalized_symbol)
        
        # Phase 2: Bulk market data fetch (if we have valid conids)
        if conid_map:
            conids_list = [info[0] for info in conid_map.values()]
            
            # Make a SINGLE API call for all contracts in this batch
            market_data = ctx.api.get_market_data_snapshot(conids_list, fields=["31"])
            
            if market_data:
                # Map responses back to symbols
                for data_item in market_data:
                    conid_str = str(data_item.get('conid', ''))
                    
                    # Find which symbol this conid belongs to
                    for symbol, (conid, row, stock_name, sec_type, exchange, currency, normalized) in conid_map.items():
                        if conid == conid_str:
                            # Extract price
                            last_price = data_item.get('31')  # Field 31 = Last Price
                            
                            if last_price is not None:
                                price = clean_price(last_price)
                                ws.cell(row, ctx.columns.price).value = price
                                if normalized != symbol:
                                    print(f"  ✅ {symbol} ({normalized}): {currency} {price:.2f}")
                                else:
                                    print(f"  ✅ {symbol}: {currency} {price:.2f}")
                                ctx.stats.price_updated += 1
                            else:
                                print(f"  ❌ {symbol}: No price data")
                                ctx.stats.price_failed += 1
                                ctx.errors.no_market_data.append(
                                    ErrorRecord(row, symbol, stock_name, f"{exchange}/{currency}")
                                )
                            break
        
        # Handle symbols where conid lookup failed
        for row, symbol, stock_name in batch:
            if symbol not in conid_map:
                normalized_symbol = normalize_symbol(symbol)
                sec_type, exchange, currency = detect_market_info(normalized_symbol)
                if normalized_symbol != symbol:
                    print(f"  ❌ {symbol} ({normalized_symbol}): Contract not found")
                else:
                    print(f"  ❌ {symbol}: Contract not found")
                ctx.stats.price_failed += 1
                ctx.errors.contract_not_found.append(
                    ErrorRecord(row, symbol, stock_name, f"{exchange}/{currency}", 
                               "Failed to resolve contract ID")
                )


def process_tables(ws, tables: List[Tuple[int, int]], ctx: AppContext):
    """Process all data tables with optimized batch price updates."""
    print("\n" + "=" * 80)
    print("UPDATING POSITIONS")
    print("=" * 80 + "\n")
    
    symbols_for_batch_price_update = []
    
    for table_num, (start_row, end_row) in enumerate(tables, 1):
        print(f"📋 Table {table_num}:\n")
        
        for row in range(start_row + 1, end_row + 1):
            symbol_value = ws.cell(row, ctx.columns.symbol).value
            
            if not is_valid_symbol(symbol_value):
                if symbol_value:
                    ctx.stats.skipped += 1
                continue
            
            symbol = str(symbol_value).strip().upper()
            stock_name = get_stock_name(ws, row, ctx.columns)
            
            # Track this symbol as being in Excel (use normalized form)
            normalized_symbol = normalize_symbol(symbol)
            ctx.stats.symbols_in_excel.add(normalized_symbol)
            
            print(f"Row {row}: {symbol}")
            
            # Update quantity immediately (fast, no network call)
            if ctx.columns.quantity:
                update_quantity(ws, row, ctx.columns.quantity, symbol, ctx.portfolio,
                              ctx.stats, ctx.errors, stock_name)
            
            # Collect for batch price update
            if ctx.columns.price:
                symbols_for_batch_price_update.append((row, symbol, stock_name))
            
            print()
    
    # Batch update all prices (MUCH faster with bulk API calls!)
    if ctx.columns.price and symbols_for_batch_price_update:
        batch_update_prices(ws, symbols_for_batch_price_update, ctx, batch_size=20)  # Increased to 20


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
    
    # Create backup first
    print("💾 Creating backup...")
    backup_path = create_backup(file_path)
    if not backup_path:
        print("❌ Cannot proceed without backup. Exiting.")
        return
    
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
        
        # Validate ALL required columns are found
        missing_columns = []
        if columns.symbol is None:
            missing_columns.append(HEADER_SYMBOL)
        if columns.quantity is None:
            missing_columns.append(HEADER_QUANTITY)
        if columns.price is None:
            missing_columns.append(HEADER_PRICE)
        
        if missing_columns:
            print("\n" + "=" * 80)
            print("❌ CRITICAL ERROR: Required columns not found")
            print("=" * 80)
            print(f"\nThe following required columns are missing from your Excel file:")
            for col_name in missing_columns:
                print(f"   ❌ {col_name}")
            print("\n💡 Please verify:")
            print(f"   1. Your Excel file has a header row with all required columns")
            print(f"   2. The headers are in the first {MAX_HEADER_SEARCH_ROWS} rows")
            print("   3. The column names are spelled correctly (including Chinese characters)")
            print(f"\n📋 Required columns: {HEADER_SYMBOL}, {HEADER_QUANTITY}, {HEADER_PRICE}")
            print("\n❌ Update aborted.\n")
            return
        
        # All columns found - print mapping
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
        print_summary(ctx.stats, portfolio)
        print_error_report(ctx.errors)
        
        print(f"\n💾 Backup saved at: {backup_path}")
        
    finally:
        wb.close()


def create_backup(file_path: str) -> Optional[str]:
    """
    Create a backup of the Excel file with timestamp.

    Returns:
        Path to backup file if successful, None otherwise
    """
    try:
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            print(f"⚠️  File not found: {file_path}")
            return None

        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path_obj.stem}_backup_{timestamp}{file_path_obj.suffix}"
        backup_path = file_path_obj.parent / backup_name

        # Copy file to backup location
        shutil.copy2(file_path, backup_path)
        print(f"✅ Backup created: {backup_path.name}\n")

        return str(backup_path)

    except Exception as e:
        print(f"❌ Failed to create backup: {e}")
        return None


if __name__ == "__main__":
    update_asset_allocation()