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


@dataclass
class Config:
    """Application configuration."""
    excel_file_path: str = r"C:\Users\George\Documents\asset allocation.xlsx"
    default_sheet_name: str = "Stock"
    max_header_search_rows: int = 20
    max_end_marker_search_cols: int = 15
    price_batch_size: int = 20

    # Chinese header names
    header_symbol: str = "編號"
    header_quantity: str = "股數"
    header_price: str = "市價"
    header_name: str = "股票名稱"
    end_marker: str = "佔投資組合持股市值"


@dataclass
class ColumnMapping:
    """Excel column indices for data fields."""
    symbol: Optional[int] = None
    quantity: Optional[int] = None
    price: Optional[int] = None
    name: Optional[int] = None

    def is_complete(self) -> bool:
        """Check if all required columns are found."""
        return all([self.symbol, self.quantity, self.price])

    def get_missing(self, config: Config) -> List[str]:
        """Get list of missing column names."""
        missing = []
        if self.symbol is None:
            missing.append(config.header_symbol)
        if self.quantity is None:
            missing.append(config.header_quantity)
        if self.price is None:
            missing.append(config.header_price)
        return missing


@dataclass
class UpdateStatistics:
    """Statistics for update operations."""
    qty_updated: int = 0
    qty_not_in_portfolio: int = 0
    price_updated: int = 0
    price_failed: int = 0
    skipped: int = 0
    qty_changes: List[Tuple[str, float, float]] = field(default_factory=list)
    symbols_in_excel: set = field(default_factory=set)


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


class SymbolValidator:
    """Validates and normalizes security symbols."""

    @staticmethod
    def is_valid_symbol(value: str, config: Config) -> bool:
        """
        Validate if a cell value is a valid security symbol.

        Valid: AAPL, 939, US91282CJV46, BRK.B
        Invalid: Empty, Chinese characters, percentages, formulas
        """
        if not value:
            return False

        value = str(value).strip()

        if not value or value == config.header_symbol:
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

    @staticmethod
    def is_isin(symbol: str) -> bool:
        """Check if symbol is in ISIN format (12 chars, 2-letter country code)."""
        if not symbol or len(symbol) != 12:
            return False

        symbol = str(symbol).strip()
        return (symbol[:2].isalpha() and
                symbol[-1].isdigit() and
                symbol[2:11].isalnum())

    @staticmethod
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

        # Remove date suffixes for bonds
        normalized = re.sub(r'\s+\d{1,2}[/-]\d{1,2}[/-]\d{2,4}$', '', normalized)
        normalized = re.sub(r'\s+\d{4}[/-]\d{1,2}[/-]\d{1,2}$', '', normalized)

        return normalized.strip()


class MarketDetector:
    """Detects market information from symbols."""

    @staticmethod
    def detect_market_info(symbol: str) -> Tuple[str, str, str]:
        """
        Detect security type, exchange, and currency from symbol.

        Returns: (sec_type, exchange, currency)
        """
        symbol = str(symbol).strip()

        # ISIN → Bond
        if SymbolValidator.is_isin(symbol):
            return ("BOND", "SMART", "USD")

        # Has letters → US stock
        if any(c.isalpha() for c in symbol):
            return ("STK", "SMART", "USD")

        # All digits → HK stock
        if symbol.isdigit():
            return ("STK", "SEHK", "HKD")

        return ("STK", "SMART", "USD")


class PriceUtils:
    """Utilities for price handling."""

    @staticmethod
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


class WorksheetAnalyzer:
    """Analyzes Excel worksheet structure."""

    def __init__(self, config: Config):
        self.config = config

    def find_header_columns(self, ws) -> ColumnMapping:
        """Find column indices for all headers in the worksheet."""
        columns = ColumnMapping()

        for row in range(1, self.config.max_header_search_rows + 1):
            for col in range(1, 15):
                cell_value = ws.cell(row, col).value

                if cell_value == self.config.header_symbol:
                    columns.symbol = col
                elif cell_value == self.config.header_quantity:
                    columns.quantity = col
                elif cell_value == self.config.header_price:
                    columns.price = col
                elif cell_value == self.config.header_name:
                    columns.name = col

            # Early exit if all found
            if all([columns.symbol, columns.quantity, columns.price, columns.name]):
                break

        return columns

    def find_data_tables(self, ws, symbol_col: int) -> List[Tuple[int, int]]:
        """Find all data tables in the worksheet."""
        if symbol_col is None:
            raise ValueError(
                f"symbol_col cannot be None. The symbol column ({self.config.header_symbol}) is required but was not found.")

        tables = []
        current_start = None

        for row in range(1, ws.max_row + 1):
            # Check for table header
            cell_value = ws.cell(row, symbol_col).value
            if cell_value and str(cell_value).strip() == self.config.header_symbol:
                current_start = row
                continue

            # Check for end marker
            if self._has_end_marker(ws, row) and current_start:
                end_row = row - 2
                if end_row >= current_start:
                    tables.append((current_start, end_row))
                current_start = None

        return tables

    def _has_end_marker(self, ws, row: int) -> bool:
        """Check if row contains the end marker."""
        for col in range(1, self.config.max_end_marker_search_cols):
            cell_value = ws.cell(row, col).value
            if cell_value and self.config.end_marker in str(cell_value):
                return True
        return False


class PortfolioManager:
    """Manages portfolio data fetching and processing."""

    def __init__(self, api: IBKRClientPortalAPI):
        self.api = api

    def fetch_portfolio(self) -> Dict[str, Dict]:
        """Fetch portfolio positions from IBKR."""
        print("\n" + "=" * 80)
        print("📊 FETCHING PORTFOLIO DATA")
        print("=" * 80 + "\n")

        accounts = self.api.get_portfolio_accounts()
        if not accounts:
            print("⚠️  Could not retrieve portfolio accounts")
            return {}

        print(f"✅ Found {len(accounts)} account(s)")

        account_id = accounts[0].get('accountId')
        print(f"📊 Using account: {account_id}")

        positions = self.api.get_portfolio_positions(account_id)
        if not positions:
            print("⚠️  No positions found")
            return {}

        print(f"✅ Found {len(positions)} position(s)\n")

        return self._process_positions(positions)

    def _process_positions(self, positions: List[Dict]) -> Dict[str, Dict]:
        """Process raw positions into normalized portfolio dictionary."""
        portfolio = {}

        for pos in positions:
            ticker = pos.get('ticker', '').strip().upper() if pos.get('ticker') else ''
            if ticker:
                normalized_ticker = SymbolValidator.normalize_symbol(ticker)

                portfolio[normalized_ticker] = {
                    'quantity': pos.get('position', 0),
                    'conid': str(pos.get('conid', '')),
                    'currency': pos.get('currency', 'USD'),
                    'description': pos.get('contractDesc', ''),
                    'original_ticker': ticker
                }
                print(f"  • {ticker}: {portfolio[normalized_ticker]['quantity']} shares")

        print()
        return portfolio


class QuantityUpdater:
    """Handles quantity updates for securities."""

    @staticmethod
    def update_quantity(ws, row: int, col: int, symbol: str, portfolio: Dict,
                        stats: UpdateStatistics, errors: ErrorTracker, stock_name: Optional[str]):
        """Update quantity for a single security."""
        normalized_symbol = SymbolValidator.normalize_symbol(symbol)

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


class PriceUpdater:
    """Handles batch price updates for securities."""

    def __init__(self, api: IBKRClientPortalAPI, fetcher: IBKRPriceFetcher, config: Config):
        self.api = api
        self.fetcher = fetcher
        self.config = config

    def batch_update_prices(self, ws, symbols_to_update: List[Tuple[int, str, Optional[str]]],
                            portfolio: Dict, columns: ColumnMapping, stats: UpdateStatistics,
                            errors: ErrorTracker):
        """Update prices in batches for better network performance."""
        if not symbols_to_update:
            return

        print(
            f"\n💹 Batch processing {len(symbols_to_update)} price updates (batch size: {self.config.price_batch_size})...")

        # Process in batches
        for i in range(0, len(symbols_to_update), self.config.price_batch_size):
            batch = symbols_to_update[i:i + self.config.price_batch_size]
            batch_num = i // self.config.price_batch_size + 1

            print(f"   Batch {batch_num}: {', '.join([s[1] for s in batch])[:60]}...")

            self._process_batch(ws, batch, portfolio, columns, stats, errors)

    def _process_batch(self, ws, batch: List[Tuple[int, str, Optional[str]]],
                       portfolio: Dict, columns: ColumnMapping,
                       stats: UpdateStatistics, errors: ErrorTracker):
        """Process a single batch of symbols."""
        # Phase 1: Bulk contract lookup with caching
        conid_map = self._build_conid_map(batch, portfolio)

        # Phase 2: Bulk market data fetch
        if conid_map:
            self._fetch_and_update_prices(ws, conid_map, columns, stats, errors)

        # Handle symbols where conid lookup failed
        self._handle_failed_lookups(batch, conid_map, stats, errors)

    def _build_conid_map(self, batch: List[Tuple[int, str, Optional[str]]],
                         portfolio: Dict) -> Dict[str, Tuple]:
        """Build mapping of symbols to contract IDs."""
        conid_map = {}

        for row, symbol, stock_name in batch:
            normalized_symbol = SymbolValidator.normalize_symbol(symbol)

            # First, try to get conid from portfolio (more reliable)
            conid = None
            if normalized_symbol in portfolio:
                conid = portfolio[normalized_symbol].get('conid')
                if conid:
                    sec_type = "STK"
                    exchange = "SMART"
                    currency = portfolio[normalized_symbol].get('currency', 'USD')
                    conid_map[symbol] = (conid, row, stock_name, sec_type, exchange, currency, normalized_symbol)
                    continue

            # If not in portfolio, search for contract
            sec_type, exchange, currency = MarketDetector.detect_market_info(normalized_symbol)
            conid = self.fetcher.get_conid(normalized_symbol, sec_type, exchange, currency, stock_name)

            if conid:
                conid_map[symbol] = (conid, row, stock_name, sec_type, exchange, currency, normalized_symbol)

        return conid_map

    def _fetch_and_update_prices(self, ws, conid_map: Dict, columns: ColumnMapping,
                                 stats: UpdateStatistics, errors: ErrorTracker):
        """Fetch market data and update prices."""
        conids_list = [info[0] for info in conid_map.values()]

        # Make a SINGLE API call for all contracts in this batch
        # Request both last price (31) and closing price (72)
        market_data = self.api.get_market_data_snapshot(conids_list, fields=["31", "72"])

        if not market_data:
            return

        # Map responses back to symbols
        for data_item in market_data:
            conid_str = str(data_item.get('conid', ''))

            # Find which symbol this conid belongs to
            for symbol, (conid, row, stock_name, sec_type, exchange, currency, normalized) in conid_map.items():
                if conid == conid_str:
                    self._update_single_price(ws, data_item, symbol, row, stock_name,
                                              exchange, currency, normalized, columns, stats, errors)
                    break

    def _update_single_price(self, ws, data_item: Dict, symbol: str, row: int,
                             stock_name: Optional[str], exchange: str, currency: str,
                             normalized: str, columns: ColumnMapping,
                             stats: UpdateStatistics, errors: ErrorTracker):
        """Update a single price from market data."""
        # Try to get latest market price (Field 31)
        last_price = data_item.get('31')

        # If no latest price, try closing price (Field 72)
        if last_price is None:
            last_price = data_item.get('72')

        if last_price is not None:
            price = PriceUtils.clean_price(last_price)
            ws.cell(row, columns.price).value = price
            display_symbol = f"{symbol} ({normalized})" if normalized != symbol else symbol
            print(f"  ✅ {display_symbol}: {currency} {price:.2f}")
            stats.price_updated += 1
        else:
            print(f"  ❌ {symbol}: No price data")
            stats.price_failed += 1
            errors.no_market_data.append(
                ErrorRecord(row, symbol, stock_name, f"{exchange}/{currency}")
            )

    def _handle_failed_lookups(self, batch: List[Tuple[int, str, Optional[str]]],
                               conid_map: Dict, stats: UpdateStatistics, errors: ErrorTracker):
        """Handle symbols where conid lookup failed."""
        for row, symbol, stock_name in batch:
            if symbol not in conid_map:
                normalized_symbol = SymbolValidator.normalize_symbol(symbol)
                sec_type, exchange, currency = MarketDetector.detect_market_info(normalized_symbol)
                display_symbol = f"{symbol} ({normalized_symbol})" if normalized_symbol != symbol else symbol
                print(f"  ❌ {display_symbol}: Contract not found")
                stats.price_failed += 1
                errors.contract_not_found.append(
                    ErrorRecord(row, symbol, stock_name, f"{exchange}/{currency}",
                                "Failed to resolve contract ID")
                )


class ReportGenerator:
    """Generates reports and summaries."""

    @staticmethod
    def print_column_mapping(columns: ColumnMapping, config: Config):
        """Print found columns."""
        print("=" * 80)
        print("COLUMN MAPPING")
        print("=" * 80)
        print(f"✅ {config.header_symbol}: Column {columns.symbol}")

        if columns.quantity:
            print(f"✅ {config.header_quantity}: Column {columns.quantity}")
        else:
            print(f"⚠️  {config.header_quantity}: Not found - quantities will not be updated")

        if columns.price:
            print(f"✅ {config.header_price}: Column {columns.price}")
        else:
            print(f"⚠️  {config.header_price}: Not found - prices will not be updated")

        if columns.name:
            print(f"✅ {config.header_name}: Column {columns.name}")

    @staticmethod
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
        ReportGenerator._print_portfolio_analysis(stats, portfolio)

    @staticmethod
    def _print_portfolio_analysis(stats: UpdateStatistics, portfolio: Dict[str, Dict]):
        """Print portfolio analysis section."""
        if not portfolio:
            return

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

    @staticmethod
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


class WorkbookManager:
    """Manages Excel workbook operations."""

    def __init__(self, config: Config):
        self.config = config

    def setup_workbook(self, file_path: str):
        """Load and configure workbook. Returns (wb, ws) or (None, None) on error."""
        try:
            wb = openpyxl.load_workbook(file_path)
            wb.calculation.calcMode = 'auto'
            wb.calculation.fullCalcOnLoad = True

            if self.config.default_sheet_name in wb.sheetnames:
                wb.active = wb[self.config.default_sheet_name]
                print(f"✅ Using sheet: '{self.config.default_sheet_name}'\n")

            return wb, wb.active
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            return None, None
        except Exception as e:
            print(f"❌ Error loading file: {e}")
            return None, None

    @staticmethod
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

    @staticmethod
    def create_backup(file_path: str) -> Optional[str]:
        """Create a backup of the Excel file with timestamp."""
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


class AssetAllocationUpdater:
    """Main orchestrator for asset allocation updates."""

    def __init__(self, config: Config):
        self.config = config
        self.api = IBKRClientPortalAPI()
        self.fetcher = IBKRPriceFetcher()
        self.portfolio_manager = PortfolioManager(self.api)
        self.workbook_manager = WorkbookManager(config)
        self.worksheet_analyzer = WorksheetAnalyzer(config)
        self.price_updater = PriceUpdater(self.api, self.fetcher, config)

    def run(self, file_path: Optional[str] = None):
        """Execute the asset allocation update process."""
        if file_path is None:
            file_path = self.config.excel_file_path

        # Print header
        self._print_header(file_path)

        # Create backup
        backup_path = self.workbook_manager.create_backup(file_path)
        if not backup_path:
            print("❌ Cannot proceed without backup. Exiting.")
            return

        # Authenticate
        if not self._authenticate():
            return

        # Fetch portfolio
        portfolio = self.portfolio_manager.fetch_portfolio()

        # Load workbook
        wb, ws = self.workbook_manager.setup_workbook(file_path)
        if not wb:
            return

        try:
            # Analyze worksheet structure
            columns = self.worksheet_analyzer.find_header_columns(ws)

            # Validate structure
            if not self._validate_structure(columns):
                return

            # Print column mapping
            ReportGenerator.print_column_mapping(columns, self.config)

            # Find data tables
            tables = self.worksheet_analyzer.find_data_tables(ws, columns.symbol)

            if not tables:
                print("\n❌ No data tables found")
                return

            self._print_tables_info(tables)

            # Initialize tracking
            stats = UpdateStatistics()
            errors = ErrorTracker()

            # Process all tables
            self._process_tables(ws, tables, columns, portfolio, stats, errors)

            # Save workbook
            self.workbook_manager.save_workbook(wb, file_path)

            # Print reports
            ReportGenerator.print_summary(stats, portfolio)
            ReportGenerator.print_error_report(errors)

            print(f"\n💾 Backup saved at: {backup_path}")

        finally:
            wb.close()

    def _print_header(self, file_path: str):
        """Print application header."""
        print("\n" + "=" * 80)
        print("📊 IBKR ASSET ALLOCATION UPDATER")
        print("=" * 80 + "\n")
        print(f"📂 File: {file_path}\n")
        print("💾 Creating backup...")

    def _authenticate(self) -> bool:
        """Authenticate with IBKR API."""
        if not self.api.check_authentication():
            print("❌ Not authenticated. Please start Client Portal Gateway.")
            return False
        print("✅ Authenticated\n")
        return True

    def _validate_structure(self, columns: ColumnMapping) -> bool:
        """Validate worksheet structure has required columns."""
        missing_columns = columns.get_missing(self.config)

        if missing_columns:
            print("\n" + "=" * 80)
            print("❌ CRITICAL ERROR: Required columns not found")
            print("=" * 80)
            print(f"\nThe following required columns are missing from your Excel file:")
            for col_name in missing_columns:
                print(f"   ❌ {col_name}")
            print("\n💡 Please verify:")
            print(f"   1. Your Excel file has a header row with all required columns")
            print(f"   2. The headers are in the first {self.config.max_header_search_rows} rows")
            print("   3. The column names are spelled correctly (including Chinese characters)")
            print(
                f"\n📋 Required columns: {self.config.header_symbol}, {self.config.header_quantity}, {self.config.header_price}")
            print("\n❌ Update aborted.\n")
            return False

        return True

    def _print_tables_info(self, tables: List[Tuple[int, int]]):
        """Print information about found data tables."""
        print(f"\n✅ Found {len(tables)} data table(s)")
        for i, (start, end) in enumerate(tables, 1):
            print(f"   Table {i}: Rows {start + 1} to {end}")

    def _process_tables(self, ws, tables: List[Tuple[int, int]], columns: ColumnMapping,
                        portfolio: Dict, stats: UpdateStatistics, errors: ErrorTracker):
        """Process all data tables with optimized batch price updates."""
        print("\n" + "=" * 80)
        print("UPDATING POSITIONS")
        print("=" * 80 + "\n")

        symbols_for_batch_price_update = []

        for table_num, (start_row, end_row) in enumerate(tables, 1):
            print(f"📋 Table {table_num}:\n")

            for row in range(start_row + 1, end_row + 1):
                symbol_value = ws.cell(row, columns.symbol).value

                if not SymbolValidator.is_valid_symbol(symbol_value, self.config):
                    if symbol_value:
                        stats.skipped += 1
                    continue

                symbol = str(symbol_value).strip().upper()
                stock_name = self._get_stock_name(ws, row, columns)

                # Track this symbol as being in Excel (use normalized form)
                normalized_symbol = SymbolValidator.normalize_symbol(symbol)
                stats.symbols_in_excel.add(normalized_symbol)

                print(f"Row {row}: {symbol}")

                # Update quantity immediately (fast, no network call)
                if columns.quantity:
                    QuantityUpdater.update_quantity(ws, row, columns.quantity, symbol, portfolio,
                                                    stats, errors, stock_name)

                # Collect for batch price update
                if columns.price:
                    symbols_for_batch_price_update.append((row, symbol, stock_name))

                print()

        # Batch update all prices
        if columns.price and symbols_for_batch_price_update:
            self.price_updater.batch_update_prices(ws, symbols_for_batch_price_update,
                                                   portfolio, columns, stats, errors)

    def _get_stock_name(self, ws, row: int, columns: ColumnMapping) -> Optional[str]:
        """Extract stock name from worksheet if available."""
        if not columns.name:
            return None

        name_value = ws.cell(row, columns.name).value
        return str(name_value).strip() if name_value else None


def update_asset_allocation(file_path: Optional[str] = None) -> None:
    """Main function to update asset allocation Excel file."""
    config = Config()
    updater = AssetAllocationUpdater(config)
    updater.run(file_path)


if __name__ == "__main__":
    update_asset_allocation()