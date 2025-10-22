"""
IBKR Last Price Fetcher
=======================
Updates asset allocation Excel with current prices from IBKR.

Rules:
- Contains English letters → US market (SMART/USD)
- All digits only → Hong Kong market (SEHK/HKD)

Usage:
    python stock_updater.py
"""

from typing import Optional, Tuple, List
import openpyxl
from IBKRPriceFetcher import IBKRPriceFetcher


def is_valid_symbol(value: str) -> bool:
    """
    Check if a cell value is a valid stock symbol.
    
    Valid symbols:
    - Contains letters (US stocks: AAPL, MSFT, BRK.B, etc.)
    - All digits (HK stocks: 939, 3033, etc.)
    - ISIN format (Bonds: US91282CJV46 - 12 chars starting with 2-letter country code)
    
    Invalid:
    - Empty or None
    - Chinese characters (headers/labels)
    - Special characters like %, $, =
    - Numbers with decimal point only (0.15, 1.5%, etc.)
    - Common header text like "編號"
    
    Args:
        value: Cell value to check
        
    Returns:
        True if valid symbol, False otherwise
    """
    if not value:
        return False
    
    value = str(value).strip()
    
    # Skip empty or very short values
    if len(value) == 0:
        return False
    
    # Skip header text
    if value == "編號":
        return False
    
    # Skip if contains Chinese characters
    if any('\u4e00' <= c <= '\u9fff' for c in value):
        return False
    
    # Skip if ONLY contains decimal and digits (like 0.15, 1.5)
    # But allow symbols with dots like BRK.B
    if '.' in value and value.replace('.', '').isdigit():
        return False
    
    # Skip if contains special characters (but allow . and / for stocks and bonds)
    if any(char in value for char in ['%', '$', '=', ':', '（', '）']):
        return False
    
    # Valid patterns:
    # 1. Contains letters (US stocks: AAPL, BRK.B, US-T)
    # 2. All digits (HK stocks: 939, 3033)
    # 3. ISIN format (12 characters, starts with 2 letters)
    has_letter = any(c.isalpha() for c in value)
    all_digits = value.isdigit()
    
    return has_letter or all_digits


def is_isin(symbol: str) -> bool:
    """
    Check if a symbol is in ISIN format.
    
    ISIN format: 12 characters
    - First 2 characters: Country code (letters)
    - Next 9 characters: National security identifier (alphanumeric)
    - Last 1 character: Check digit (digit)
    
    Examples:
        US91282CJV46 - US Treasury Bond
        US0378331005 - Apple Inc.
        GB0002374006 - UK security
    
    Args:
        symbol: Symbol to check
        
    Returns:
        True if symbol matches ISIN format, False otherwise
    """
    if not symbol:
        return False
    
    symbol = str(symbol).strip()
    
    # ISIN must be exactly 12 characters
    if len(symbol) != 12:
        return False
    
    # First 2 characters must be letters (country code)
    if not symbol[:2].isalpha():
        return False
    
    # Last character must be a digit (check digit)
    if not symbol[-1].isdigit():
        return False
    
    # Middle 9 characters must be alphanumeric
    if not symbol[2:11].isalnum():
        return False
    
    return True


def detect_security_type(symbol: str) -> str:
    """
    Detect security type based on symbol format.
    
    Rules:
    - ISIN format (12 chars, starts with country code) → BOND
    - Contains letters but not ISIN → STK (stock)
    - All digits → STK (Hong Kong stocks)
    
    Args:
        symbol: Symbol to analyze
        
    Returns:
        Security type: "BOND" or "STK"
    """
    symbol = str(symbol).strip()
    
    # Check if it's an ISIN (bond identifier)
    if is_isin(symbol):
        return "BOND"
    
    # Otherwise, it's a stock
    return "STK"


def detect_exchange_and_currency(symbol: str, sec_type: str = None) -> Tuple[str, str, str]:
    """
    Detect exchange, currency, and security type based on symbol pattern.
    
    Rules:
    - ISIN format → BOND/SMART/USD
    - Contains English letter → Stock/SMART/USD
    - All digits only → Stock/SEHK/HKD
    
    Args:
        symbol: Symbol to analyze
        sec_type: Optional override for security type
        
    Returns:
        (sec_type, exchange, currency) tuple
    """
    symbol = str(symbol).strip()
    
    # Determine security type if not provided
    if sec_type is None:
        sec_type = detect_security_type(symbol)
    
    # Bonds always use SMART/USD
    if sec_type == "BOND":
        return ("BOND", "SMART", "USD")
    
    # For stocks: check if it contains letters or is all digits
    has_letter = any(c.isalpha() for c in symbol)
    
    if has_letter:
        return ("STK", "SMART", "USD")
    elif symbol.isdigit():
        return ("STK", "SEHK", "HKD")
    else:
        return ("STK", "SMART", "USD")


def find_all_tables(ws, symbol_col: int) -> List[Tuple[int, int]]:
    """
    Find all data tables in the worksheet.
    
    Each table:
    - Starts with a row containing "編號" 
    - Ends 2 rows before "佔投資組合持股市值"
    
    Args:
        ws: Worksheet object
        symbol_col: Column index for symbols
        
    Returns:
        List of (start_row, end_row) tuples for each table
    """
    tables = []
    current_start = None
    
    for row in range(1, ws.max_row + 1):
        # Check symbol column for "編號" header
        symbol_cell_value = ws.cell(row, symbol_col).value
        
        if symbol_cell_value:
            value_str = str(symbol_cell_value).strip()
            
            # Found a table header
            if value_str == "編號":
                current_start = row
                continue
        
        # Check all columns in this row for end marker
        row_has_end_marker = False
        for col in range(1, 15):  # Check columns A through N
            cell_value = ws.cell(row, col).value
            if cell_value and "佔投資組合持股市值" in str(cell_value):
                row_has_end_marker = True
                break
        
        # Found end marker for current table
        if row_has_end_marker and current_start:
            # Table ends 2 rows before this marker
            end_row = row - 2
            if end_row >= current_start:
                tables.append((current_start, end_row))
            current_start = None
    
    return tables


def find_header_columns(ws, max_search_rows: int = 20) -> Tuple[Optional[int], Optional[int]]:
    """
    Find the column indices for "編號" and "市價".
    
    Args:
        ws: Worksheet object
        max_search_rows: Maximum rows to search for headers
        
    Returns:
        (symbol_col, price_col) tuple
    """
    symbol_col = None
    price_col = None
    
    for row in range(1, max_search_rows + 1):
        for col in range(1, 10):
            cell_value = ws.cell(row, col).value
            if cell_value == "編號":
                symbol_col = col
            if cell_value == "市價":
                price_col = col
        
        if symbol_col and price_col:
            break
    
    return symbol_col, price_col


# Helper function to clean and convert price values
def clean_price(value) -> Optional[float]:
    """
    Clean IBKR price values that may have prefixes like 'C', 'H', 'L'.

    Examples:
        "'C19.80'" -> 19.80
        "19.80" -> 19.80
        "'H20.50'" -> 20.50
    """
    if value is None:
        return None

    try:
        # If already a number, return it
        if isinstance(value, (int, float)):
            return float(value)

        # Convert to string
        value_str = str(value).strip()

        # Check if starts with a letter prefix (C, H, L, O, etc.)
        if value_str and value_str[0].isalpha():
            # Remove the first character (the prefix letter)
            value_str = value_str[1:]

        # Convert to float
        return float(value_str)
    except (TypeError, ValueError) as e:
        print(f"Could not convert price value '{value}': {e}")
        return None

def update_asset_allocation(file_path: str = "asset allocation.xlsx") -> None:
    """
    Update asset allocation Excel with current prices.
    
    Reads symbols from "編號" column and updates "市價" column.
    Processes all tables in the worksheet, skipping summary sections.
    Supports stocks (by ticker or HK number) and bonds (by ISIN).
    
    Args:
        file_path: Path to Excel file
    """
    print(f"📊 Opening Excel file: {file_path}")
    
    # Load workbook
    try:
        wb = openpyxl.load_workbook(file_path)
        # Set calculation properties
        wb.calculation.calcMode = 'auto'
        wb.calculation.fullCalcOnLoad = True
        if "stock" in wb.sheetnames:
            wb.active = wb["stock"]
        ws = wb.active
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return
    
    # Find column indices
    symbol_col, price_col = find_header_columns(ws)
    
    if not symbol_col or not price_col:
        print("❌ Could not find '編號' or '市價' columns")
        wb.close()
        return
    
    # Find stock name column (股票名稱)
    stock_name_col = None
    for row in range(1, 20):
        for col in range(1, 10):
            cell_value = ws.cell(row, col).value
            if cell_value == "股票名稱":
                stock_name_col = col
                break
        if stock_name_col:
            break
    
    print(f"✅ Found: 編號=Column {symbol_col}, 市價=Column {price_col}")
    if stock_name_col:
        print(f"✅ Found: 股票名稱=Column {stock_name_col}")
    
    # Find all data tables
    tables = find_all_tables(ws, symbol_col)
    
    if not tables:
        print("❌ No data tables found")
        wb.close()
        return
    
    print(f"✅ Found {len(tables)} tables to process")
    for i, (start, end) in enumerate(tables, 1):
        print(f"   Table {i}: Rows {start + 1} to {end}")
    
    print("-" * 80)
    
    # Initialize fetcher
    fetcher = IBKRPriceFetcher()
    
    # Track statistics
    updated_count = 0
    failed_count = 0
    skipped_count = 0
    bond_count = 0
    stock_count = 0
    
    # Process each table
    for table_num, (start_row, end_row) in enumerate(tables, 1):
        print(f"\n📋 Processing Table {table_num} (rows {start_row + 1} to {end_row}):")
        
        # Process rows in this table (skip header row)
        for row in range(start_row + 1, end_row + 1):
            symbol_value = ws.cell(row, symbol_col).value
            
            # Validate if it's a valid symbol
            if not is_valid_symbol(symbol_value):
                if symbol_value:  # Only count non-empty skips
                    skipped_count += 1
                continue
            
            symbol = str(symbol_value).strip()
            
            # Detect security type and market
            sec_type, exchange, currency = detect_exchange_and_currency(symbol)
            
            # Track security types
            if sec_type == "BOND":
                bond_count += 1
                security_label = "BOND/ISIN"
            else:
                stock_count += 1
                security_label = "STOCK"
            
            # Get stock/bond name from Excel if available
            stock_name = None
            if stock_name_col:
                stock_name_value = ws.cell(row, stock_name_col).value
                if stock_name_value:
                    stock_name = str(stock_name_value).strip()
            
            # Get price
            print(f"Row {row}: {symbol} [{security_label}] ({exchange}/{currency})...", end=" ")
            
            try:
                price_data = fetcher.get_price(
                    symbol, 
                    sec_type=sec_type,
                    exchange=exchange, 
                    currency=currency,
                    stock_name=stock_name  # Pass name for matching
                )
                
                if price_data and price_data.last_price is not None:
                    # Update the cell
                    price_data.last_price = clean_price(price_data.last_price)
                    print(f"✅ {currency} ${price_data.last_price:.2f}")
                    ws.cell(row, price_col).value = price_data.last_price
                    updated_count += 1
                else:
                    print(f"❌ No price available")
                    failed_count += 1
                    
            except Exception as e:
                print(f"❌ Error: {str(e)[:50]}")
                failed_count += 1
    
    # Save the workbook
    print("-" * 80)
    print(f"💾 Saving changes...")

    # Additionally, mark all sheets as needing recalculation
    for sheet in wb.worksheets:
        sheet.sheet_view.tabSelected = False
    try:
        wb.save(file_path)
        print(f"✅ File saved successfully!")
        print(f"\n📊 Summary:")
        print(f"   ✅ Updated: {updated_count}")
        print(f"   ❌ Failed:  {failed_count}")
        print(f"   ⏭️  Skipped: {skipped_count}")
        print(f"   📈 Stocks:  {stock_count}")
        print(f"   📜 Bonds:   {bond_count}")
        print(f"   📝 Total:   {updated_count + failed_count + skipped_count}")
    except Exception as e:
        print(f"❌ Error saving file: {e}")
    finally:
        wb.close()


if __name__ == "__main__":
    # Update the asset allocation spreadsheet
    update_asset_allocation("asset allocation.xlsx")
