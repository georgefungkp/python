"""
Comprehensive test suite for IBKR modules:
- IBKRClientPortalAPI.py
- IBKRPriceFetcher.py  
- stock_updater.py
"""

import unittest
from unittest.mock import MagicMock, patch

from IBKRClientPortalAPI import IBKRClientPortalAPI, SecurityPrice
from IBKRPriceFetcher import IBKRPriceFetcher
from stock_updater import (
    ColumnMapping, UpdateStatistics, ErrorTracker, AppContext
)


# ============================================================================
# Tests for IBKRClientPortalAPI.py
# ============================================================================

class TestSecurityPrice(unittest.TestCase):
    """Tests for SecurityPrice dataclass."""

    def test_security_price_creation(self):
        """Test creating SecurityPrice with all fields."""
        price = SecurityPrice(
            symbol="AAPL",
            conid="265598",
            last_price=150.25,
            bid_price=150.20,
            ask_price=150.30,
            change=2.5,
            change_percentage=1.69,
            volume=50000000,
            high=151.50,
            low=149.00,
            open_price=149.50,
            close_price=147.75
        )
        
        self.assertEqual(price.symbol, "AAPL")
        self.assertEqual(price.conid, "265598")
        self.assertEqual(price.last_price, 150.25)
        self.assertEqual(price.bid_price, 150.20)
        self.assertEqual(price.ask_price, 150.30)

    def test_security_price_optional_fields(self):
        """Test SecurityPrice with optional fields as None."""
        price = SecurityPrice(
            symbol="TSLA",
            conid="76792991",
            last_price=250.00,
            bid_price=None,
            ask_price=None,
            change=None,
            change_percentage=None,
            volume=None,
            high=None,
            low=None,
            open_price=None,
            close_price=None
        )
        
        self.assertEqual(price.symbol, "TSLA")
        self.assertIsNone(price.bid_price)
        self.assertIsNone(price.volume)


class TestIBKRClientPortalAPI(unittest.TestCase):
    """Tests for IBKRClientPortalAPI class."""

    def setUp(self):
        """Set up test fixtures."""
        self.api = IBKRClientPortalAPI(base_url="https://localhost:5000", timeout=10)

    @patch('requests.Session')
    def test_init(self, mock_session):
        """Test API initialization."""
        api = IBKRClientPortalAPI(base_url="https://test.com", timeout=15)
        self.assertEqual(api.base_url, "https://test.com")
        self.assertEqual(api.timeout, 15)

    @patch.object(IBKRClientPortalAPI, '_make_request')
    def test_check_authentication_success(self, mock_request):
        """Test successful authentication check."""
        mock_request.return_value = {
            'authenticated': True,
            'competing': False,
            'connected': True
        }
        
        result = self.api.check_authentication()
        self.assertTrue(result)
        mock_request.assert_called_once_with('GET', '/iserver/auth/status')

    @patch.object(IBKRClientPortalAPI, '_make_request')
    def test_check_authentication_failure(self, mock_request):
        """Test failed authentication check."""
        mock_request.return_value = {
            'authenticated': False,
            'competing': False,
            'connected': False
        }
        
        result = self.api.check_authentication()
        self.assertFalse(result)

    @patch.object(IBKRClientPortalAPI, '_make_request')
    def test_search_contract_success(self, mock_request):
        """Test successful contract search."""
        mock_request.return_value = [
            {
                'conid': '265598',
                'symbol': 'AAPL',
                'description': 'APPLE INC',
                'exchange': 'NASDAQ',
                'currency': 'USD',
                'instrumentType': 'STK'
            }
        ]
        
        result = self.api.search_contract('AAPL', 'STK', 'SMART', 'USD')
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['symbol'], 'AAPL')
        self.assertEqual(result[0]['conid'], '265598')

    @patch.object(IBKRClientPortalAPI, '_make_request')
    def test_search_contract_no_results(self, mock_request):
        """Test contract search with no results."""
        mock_request.return_value = []
        
        result = self.api.search_contract('INVALID', 'STK', 'SMART', 'USD')
        
        self.assertEqual(len(result), 0)

    @patch.object(IBKRClientPortalAPI, '_make_request')
    def test_get_market_data_snapshot(self, mock_request):
        """Test getting market data snapshot."""
        mock_request.return_value = [
            {
                'conid': '265598',
                '31': '150.25',  # Last price
                '84': '150.20',  # Bid
                '85': '150.30',  # Ask
                '86': '2.5',     # Change
                '87': '1.69',    # Change %
                '88': '50000000' # Volume
            }
        ]
        
        result = self.api.get_market_data_snapshot(['265598'])
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['conid'], '265598')
        self.assertEqual(result[0]['31'], '150.25')

    @patch.object(IBKRClientPortalAPI, '_make_request')
    def test_get_portfolio_accounts(self, mock_request):
        """Test getting portfolio accounts."""
        mock_request.return_value = [
            {
                'accountId': 'U1234567',
                'accountVan': 'U1234567',
                'accountTitle': 'Test Account',
                'displayName': 'Test Account',
                'accountAlias': None,
                'accountStatus': 1234567890,
                'currency': 'USD',
                'type': 'INDIVIDUAL'
            }
        ]
        
        result = self.api.get_portfolio_accounts()
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['accountId'], 'U1234567')

    @patch.object(IBKRClientPortalAPI, '_make_request')
    def test_get_portfolio_positions(self, mock_request):
        """Test getting portfolio positions."""
        mock_request.return_value = [
            {
                'acctId': 'U1234567',
                'conid': 265598,
                'contractDesc': 'AAPL',
                'position': 100.0,
                'mktPrice': 150.25,
                'mktValue': 15025.0,
                'currency': 'USD',
                'avgCost': 145.0,
                'avgPrice': 145.0,
                'realizedPnl': 0.0,
                'unrealizedPnl': 525.0
            }
        ]
        
        result = self.api.get_portfolio_positions('U1234567')
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['contractDesc'], 'AAPL')
        self.assertEqual(result[0]['position'], 100.0)


# ============================================================================
# Tests for IBKRPriceFetcher.py
# ============================================================================

class TestIBKRPriceFetcher(unittest.TestCase):
    """Tests for IBKRPriceFetcher class."""

    def setUp(self):
        """Set up test fixtures."""
        with patch.object(IBKRPriceFetcher, 'ensure_authenticated'):
            self.fetcher = IBKRPriceFetcher()

    @patch.object(IBKRClientPortalAPI, 'check_authentication')
    def test_ensure_authenticated_success(self, mock_check):
        """Test successful authentication check."""
        mock_check.return_value = True
        fetcher = IBKRPriceFetcher()
        fetcher.ensure_authenticated()
        self.assertTrue(fetcher._auth_checked)

    @patch.object(IBKRClientPortalAPI, 'check_authentication')
    def test_ensure_authenticated_failure(self, mock_check):
        """Test failed authentication."""
        mock_check.return_value = False
        fetcher = IBKRPriceFetcher()
        
        with self.assertRaises(ConnectionError):
            fetcher.ensure_authenticated()

    def test_score_contract_exact_match(self):
        """Test contract scoring with exact symbol match."""
        contract = {
            'symbol': 'AAPL',
            'description': 'APPLE INC',
            'exchange': 'NASDAQ',
            'currency': 'USD'
        }
        
        score = self.fetcher._score_contract(contract, 'AAPL', 'NASDAQ', 'USD', None)
        
        # Exact symbol match should give high score
        self.assertGreater(score, 50)

    def test_score_contract_with_stock_name(self):
        """Test contract scoring with stock name matching."""
        contract = {
            'symbol': 'AAPL',
            'description': 'APPLE INC',
            'companyName': 'Apple Inc.',
            'exchange': 'NASDAQ',
            'currency': 'USD'
        }
        
        score = self.fetcher._score_contract(contract, 'AAPL', 'NASDAQ', 'USD', 'Apple Inc.')
        
        # Should get bonus points for name match
        self.assertGreater(score, 60)

    @patch.object(IBKRClientPortalAPI, 'search_contract')
    def test_get_conid_success(self, mock_search):
        """Test successful CONID retrieval."""
        mock_search.return_value = [
            {
                'conid': '265598',
                'symbol': 'AAPL',
                'description': 'APPLE INC',
                'exchange': 'NASDAQ',
                'currency': 'USD'
            }
        ]
        
        conid = self.fetcher.get_conid('AAPL', 'STK', 'SMART', 'USD')
        
        self.assertEqual(conid, '265598')

    @patch.object(IBKRClientPortalAPI, 'search_contract')
    def test_get_conid_cached(self, mock_search):
        """Test CONID retrieval from cache."""
        # First call - should search
        mock_search.return_value = [
            {'conid': '265598', 'symbol': 'AAPL', 'exchange': 'NASDAQ', 'currency': 'USD'}
        ]
        
        conid1 = self.fetcher.get_conid('AAPL', 'STK', 'SMART', 'USD')
        
        # Second call - should use cache
        conid2 = self.fetcher.get_conid('AAPL', 'STK', 'SMART', 'USD')
        
        self.assertEqual(conid1, conid2)
        # Should only call search once
        self.assertEqual(mock_search.call_count, 1)

    @patch.object(IBKRClientPortalAPI, 'search_contract')
    def test_get_conid_not_found(self, mock_search):
        """Test CONID retrieval when contract not found."""
        mock_search.return_value = []
        
        conid = self.fetcher.get_conid('INVALID', 'STK', 'SMART', 'USD')
        
        self.assertIsNone(conid)

    @patch.object(IBKRPriceFetcher, 'get_conid')
    @patch.object(IBKRClientPortalAPI, 'get_market_data_snapshot')
    def test_get_price_success(self, mock_snapshot, mock_conid):
        """Test successful price retrieval."""
        mock_conid.return_value = '265598'
        mock_snapshot.return_value = [
            {
                'conid': '265598',
                '31': 'C150.25',  # Last price
                '84': 'C150.20',  # Bid
                '85': 'C150.30'   # Ask
            }
        ]
        
        price = self.fetcher.get_price('AAPL', 'STK', 'SMART', 'USD')
        
        self.assertIsNotNone(price)
        self.assertEqual(price.symbol, 'AAPL')
        self.assertEqual(price.last_price, 150.25)

    @patch.object(IBKRPriceFetcher, 'get_conid')
    def test_get_price_no_conid(self, mock_conid):
        """Test price retrieval when CONID not found."""
        mock_conid.return_value = None
        
        price = self.fetcher.get_price('INVALID', 'STK', 'SMART', 'USD')
        
        self.assertIsNone(price)

    @patch.object(IBKRPriceFetcher, 'get_price')
    def test_get_prices_batch(self, mock_get_price):
        """Test batch price retrieval."""
        mock_get_price.side_effect = [
            SecurityPrice('AAPL', '265598', 150.25, None, None, None, None, None, None, None, None, None),
            SecurityPrice('TSLA', '76792991', 250.00, None, None, None, None, None, None, None, None, None)
        ]
        
        symbols = ['AAPL', 'TSLA']
        prices = self.fetcher.get_prices(symbols)
        
        self.assertEqual(len(prices), 2)
        self.assertEqual(prices[0].symbol, 'AAPL')
        self.assertEqual(prices[1].symbol, 'TSLA')



class TestAppContext(unittest.TestCase):
    """Tests for AppContext dataclass."""

    def test_app_context_creation(self):
        """Test creating AppContext."""
        api = MagicMock()
        fetcher = MagicMock()
        portfolio = {'AAPL': 100.0}
        columns = ColumnMapping(0, 1, 2, 3)
        stats = UpdateStatistics()
        errors = ErrorTracker()
        
        context = AppContext(
            api=api,
            fetcher=fetcher,
            portfolio=portfolio,
            columns=columns,
            stats=stats,
            errors=errors
        )
        
        self.assertEqual(context.api, api)
        self.assertEqual(context.fetcher, fetcher)
        self.assertEqual(context.portfolio, portfolio)
        self.assertEqual(context.columns, columns)
        self.assertEqual(context.stats, stats)
        self.assertEqual(context.errors, errors)


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete workflow."""

    @patch.object(IBKRClientPortalAPI, 'check_authentication')
    @patch.object(IBKRClientPortalAPI, 'search_contract')
    @patch.object(IBKRClientPortalAPI, 'get_market_data_snapshot')
    def test_full_price_fetch_workflow(self, mock_snapshot, mock_search, mock_auth):
        """Test complete workflow from authentication to price fetch."""
        # Setup mocks
        mock_auth.return_value = True
        mock_search.return_value = [
            {'conid': '265598', 'symbol': 'AAPL', 'exchange': 'NASDAQ', 'currency': 'USD'}
        ]
        mock_snapshot.return_value = [
            {'conid': '265598', '31': 'C150.25'}
        ]
        
        # Execute workflow
        fetcher = IBKRPriceFetcher()
        price = fetcher.get_price('AAPL', 'STK', 'SMART', 'USD')
        
        # Verify
        self.assertIsNotNone(price)
        self.assertEqual(price.symbol, 'AAPL')
        self.assertEqual(price.last_price, 150.25)


if __name__ == '__main__':
    unittest.main(verbosity=2)
