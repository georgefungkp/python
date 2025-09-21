import pandas as pd
import numpy as np
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.common import TickerId
from ibapi.ticktype import TickType
import threading
import time
import os


class IBApi(EWrapper, EClient):
    """Interactive Brokers API client for fetching stock prices"""

    def __init__(self):
        EClient.__init__(self, self)
        self.prices = {}
        self.req_id = 0
        self.connected = False
        self.data_received = {}

    def error(self, reqId, errorCode, errorString):
        print(f"Error {errorCode}: {errorString}")

    def connectAck(self):
        print("Connected to IB Gateway/TWS")
        self.connected = True

    def tickPrice(self, reqId, tickType, price, attrib):
        """Handle incoming price data"""
        if tickType == TickType.LAST or tickType == TickType.CLOSE:
            symbol = list(self.data_received.keys())[list(self.data_received.values()).index(reqId)]
            self.prices[symbol] = price
            print(f"Received price for {symbol}: ${price:.2f}")

    def get_stock_price(self, symbol, exchange="SMART", currency="USD"):
        """Get current stock price for a symbol"""
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = exchange
        contract.currency = currency

        self.req_id += 1
        self.data_received[symbol] = self.req_id

        self.reqMktData(self.req_id, contract, "", False, False, [])
        return self.req_id


class StockPriceUpdater:
    """Main class to handle Excel file operations and price updates"""

    def __init__(self, excel_file="asset allocation.xlsx"):
        self.excel_file = excel_file
        self.ib_api = IBApi()
        self.df = None

    def load_spreadsheet(self):
        """Load the CSV spreadsheet"""
        try:
            self.df = pd.read_excel(self.excel_file)
            print(f"Successfully loaded {self.excel_file}")
            print("Columns:", self.df.columns.tolist())
            print("Shape:", self.df.shape)
            return True
        except FileNotFoundError:
            print(f"File {self.excel_file} not found!")
            return False
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            return False

    def connect_to_ib(self, host="127.0.0.1", port=7497, client_id=1):
        """Connect to Interactive Brokers API"""
        print("Connecting to IB Gateway/TWS...")
        self.ib_api.connect(host, port, client_id)

        # Start the socket in a separate thread
        api_thread = threading.Thread(target=self.ib_api.run, daemon=True)
        api_thread.start()

        # Wait for connection
        time.sleep(2)
        return self.ib_api.connected

    def extract_stock_symbols(self):
        """Extract stock symbols from the spreadsheet"""
        symbols = []

        # Based on the image, it looks like there are stock symbols in the data
        # We need to identify the column containing symbols
        if self.df is not None:
            # Look for columns that might contain stock symbols
            for col in self.df.columns:
                print(f"Column '{col}' sample values:")
                print(self.df[col].head())
                print("-" * 30)

            # You may need to adjust this based on actual column names
            # Common column names for symbols: 'Symbol', 'Ticker', 'Code', etc.
            symbol_columns = [col for col in self.df.columns
                              if any(keyword in col.lower()
                                     for keyword in ['symbol', 'ticker', 'code', '代碼', '編號'])]

            if symbol_columns:
                symbols = self.df[symbol_columns[0]].dropna().tolist()
                print(f"Found symbols in column '{symbol_columns[0]}': {symbols}")
            else:
                print("Could not automatically identify symbol column.")
                print("Available columns:", self.df.columns.tolist())

        return symbols

    def update_prices(self, symbols):
        """Update prices for given symbols"""
        if not self.ib_api.connected:
            print("Not connected to IB API!")
            return

        print(f"Requesting prices for {len(symbols)} symbols...")

        # Request prices for all symbols
        for symbol in symbols:
            self.ib_api.get_stock_price(symbol)
            time.sleep(0.1)  # Small delay to avoid overwhelming the API

        # Wait for price data
        print("Waiting for price data...")
        time.sleep(5)

        return self.ib_api.prices

    def update_spreadsheet(self, prices):
        """Update the spreadsheet with new prices"""
        if self.df is None:
            print("No spreadsheet loaded!")
            return

        # Find price column (adjust based on actual column names)
        price_columns = [col for col in self.df.columns
                         if any(keyword in col.lower()
                                for keyword in ['price', 'value', '市價', '價格', '現價'])]

        if not price_columns:
            print("Could not find price column. Available columns:")
            print(self.df.columns.tolist())
            return

        price_col = price_columns[0]
        symbol_col = None

        # Find symbol column
        symbol_columns = [col for col in self.df.columns
                          if any(keyword in col.lower()
                                 for keyword in ['symbol', 'ticker', 'code', '代碼', '編號'])]

        if symbol_columns:
            symbol_col = symbol_columns[0]

        if symbol_col:
            # Update prices based on symbols
            for idx, row in self.df.iterrows():
                symbol = row[symbol_col]
                if symbol in prices:
                    self.df.at[idx, price_col] = prices[symbol]
                    print(f"Updated {symbol}: {prices[symbol]}")

        # Calculate portfolio values and percentages if needed
        self.calculate_portfolio_metrics()

    def calculate_portfolio_metrics(self):
        """Calculate portfolio values and allocation percentages"""
        # Look for quantity and price columns to calculate values
        qty_columns = [col for col in self.df.columns
                       if any(keyword in col.lower()
                              for keyword in ['quantity', 'shares', '股數', '數量'])]

        price_columns = [col for col in self.df.columns
                         if any(keyword in col.lower()
                                for keyword in ['price', 'value', '市價', '價格', '現價'])]

        if qty_columns and price_columns:
            qty_col = qty_columns[0]
            price_col = price_columns[0]

            # Calculate market value
            self.df['Market Value'] = self.df[qty_col] * self.df[price_col]

            # Calculate allocation percentages
            total_value = self.df['Market Value'].sum()
            self.df['Allocation %'] = (self.df['Market Value'] / total_value * 100).round(2)

            print(f"Total Portfolio Value: ${total_value:,.2f}")

    def save_spreadsheet(self, output_file=None):
        """Save the updated spreadsheet"""
        if output_file is None:
            output_file = self.excel_file.replace('.xlsx', '_updated.xlsx')

        try:
            self.df.to_excel(output_file, index=False)
            print(f"Updated spreadsheet saved as: {output_file}")
        except Exception as e:
            print(f"Error saving file: {e}")

    def disconnect_ib(self):
        """Disconnect from IB API"""
        if self.ib_api.connected:
            self.ib_api.disconnect()
            print("Disconnected from IB API")


def main():
    """Main function to run the asset allocation updater"""
    print("=== Asset Allocation Updater ===")

    # Initialize the updater
    updater = StockPriceUpdater("C:\\Users\\George\\Documents\\asset allocation.xlsx")

    try:
        # 1. Load the spreadsheet
        if not updater.load_spreadsheet():
            return

        # 2. Connect to IB API
        print("\nNote: Make sure IB Gateway or TWS is running!")
        print("Default connection: localhost:7497")

        if updater.connect_to_ib():
            print("Successfully connected to IB API")

            # 3. Extract stock symbols
            symbols = updater.extract_stock_symbols()

            if symbols:
                # 4. Update prices
                prices = updater.update_prices(symbols)

                if prices:
                    print(f"\nReceived prices: {prices}")

                    # 5. Update spreadsheet
                    updater.update_spreadsheet(prices)

                    # 6. Save updated file
                    updater.save_spreadsheet()
                else:
                    print("No price data received")
            else:
                print("No symbols found to update")

        else:
            print("Failed to connect to IB API")
            print("Please ensure IB Gateway or TWS is running and accessible")

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Clean up
        updater.disconnect_ib()


if __name__ == "__main__":
    main()