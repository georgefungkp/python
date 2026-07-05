"""IBKR Client Portal Web API client.

Handles HTTP calls to the Client Portal Gateway (default: localhost:5000),
transient-failure retries, contract search + conid scoring, market data,
and portfolio position fetching (with pagination).
"""

import logging
import time
from typing import Dict, List, Optional

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class IBKRClientPortalAPI:
    """Client for IBKR Client Portal Web API. Gateway must be running locally."""

    MAX_RETRIES = 5
    RETRY_BACKOFF_SECONDS = 1.0  # exponential: 1s, 2s, 4s, 8s, ...
    POSITIONS_PAGE_SIZE = 30
    POSITIONS_MAX_PAGES = 100

    def __init__(self, base_url: str = "https://localhost:5000/v1/api", timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout

        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'User-Agent': 'IBKR-Python-Client/1.0',
            'Content-Type': 'application/json',
        })

        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        self._conid_cache: Dict[str, str] = {}

    # ------------------------------------------------------------------
    # HTTP layer
    # ------------------------------------------------------------------

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """HTTP call with retry on connection errors / timeouts / 5xx. 4xx is not retried."""
        url = f"{self.base_url}{endpoint}"
        last_error = None

        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.session.request(method, url, timeout=self.timeout, **kwargs)

                if response.status_code == 200:
                    return response.json()

                if 500 <= response.status_code < 600:
                    last_error = f"HTTP {response.status_code} - {response.text}"
                    self.logger.warning(
                        f"API {endpoint} returned {response.status_code}, "
                        f"retry {attempt + 1}/{self.MAX_RETRIES}")
                else:
                    self.logger.error(f"API request failed: {response.status_code} - {response.text}")
                    return None

            except requests.exceptions.ConnectionError as e:
                last_error = f"ConnectionError: {e}"
                self.logger.warning(f"Connection error on {endpoint}, retry {attempt + 1}/{self.MAX_RETRIES}")

            except requests.exceptions.Timeout as e:
                last_error = f"Timeout: {e}"
                self.logger.warning(f"Timeout on {endpoint}, retry {attempt + 1}/{self.MAX_RETRIES}")

            except Exception as e:
                self.logger.error(f"Request error: {e}")
                return None

            if attempt < self.MAX_RETRIES - 1:
                time.sleep(self.RETRY_BACKOFF_SECONDS * (2 ** attempt))

        self.logger.error(f"API request failed after {self.MAX_RETRIES} attempts: {last_error}")
        if "ConnectionError" in (last_error or ""):
            self.logger.info("Please ensure Client Portal Gateway is running")
        return None

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    def check_authentication(self) -> bool:
        """Return True if the gateway reports an authenticated session."""
        result = self._make_request('GET', '/iserver/auth/status')
        if result and result.get('authenticated'):
            self.logger.info("Session is authenticated")
            return True
        self.logger.warning("Session not authenticated")
        return False

    # ------------------------------------------------------------------
    # Contract search & conid resolution
    # ------------------------------------------------------------------

    def search_contract(self, symbol: str, sec_type: str = "STK",
                        exchange: str = "SMART", currency: str = "USD") -> Optional[List[Dict]]:
        """GET /iserver/secdef/search — returns matching contracts or None."""
        params = {'symbol': symbol, 'secType': sec_type, 'exchange': exchange, 'currency': currency}
        result = self._make_request('GET', '/iserver/secdef/search', params=params)

        if result is None:
            return None
        if not isinstance(result, list):
            self.logger.error(f"Unexpected response type for {symbol}: {type(result).__name__}")
            return None
        self.logger.info(f"Found {len(result)} contracts for {symbol}")
        return result

    @staticmethod
    def _score_contract(contract: dict, exchange: str, stock_name: Optional[str]) -> int:
        """Rank a search hit against the requested exchange and (optionally) stock name."""
        score = 0
        company_name = (contract.get('companyName') or '').upper()
        description = (contract.get('description') or '').upper()

        if stock_name:
            name_upper = stock_name.upper()
            if name_upper in company_name:
                score += 30
            elif name_upper in description:
                score += 15

        if any(kw in company_name for kw in ('ORDINARY', 'COMMON', 'SHARE')):
            score += 15
        if any(kw in description for kw in ('ORDINARY', 'COMMON', 'SHARE')):
            score += 10

        if any(kw in company_name for kw in ('WARRANT', 'OPTION', 'FUTURE')):
            score -= 50
        if any(kw in description for kw in ('WARRANT', 'OPTION', 'FUTURE')):
            score -= 30

        for section in contract.get('sections', []):
            if exchange in str(section.get('exchange', '')):
                score += 20

        return score

    def get_conid(self, symbol: str, sec_type: str = "STK",
                  exchange: str = "SMART", currency: str = "USD",
                  stock_name: Optional[str] = None) -> Optional[str]:
        """Resolve a symbol to a conid via search + scoring, with caching."""
        cache_key = f"{symbol}|{sec_type}|{exchange}|{currency}"
        if cache_key in self._conid_cache:
            return self._conid_cache[cache_key]

        contracts = self.search_contract(symbol, sec_type, exchange, currency)
        if not contracts:
            self.logger.error(f"No contract found for {symbol}")
            return None

        if len(contracts) == 1:
            best = contracts[0]
            self.logger.info(f"Single contract: {symbol} → {best.get('conid')}")
        else:
            best = max(contracts, key=lambda c: self._score_contract(c, exchange, stock_name))
            desc = best.get('description', best.get('companyName', 'N/A'))
            self.logger.info(f"Best match: {symbol} → {best.get('conid')} ({desc[:30]})")

        conid = str(best.get('conid'))
        self._conid_cache[cache_key] = conid
        return conid

    # ------------------------------------------------------------------
    # Market data
    # ------------------------------------------------------------------

    def get_market_data_snapshot(self, conids: List[str],
                                 fields: Optional[List[str]] = None) -> Optional[List[Dict]]:
        """GET /iserver/marketdata/snapshot for one-or-many conids.

        Common field IDs: 31=last, 84=bid, 85=ask, 70/71=high/low, 72=close, 73=open.
        """
        if fields is None:
            fields = ["31", "84", "85", "86", "87", "88", "70", "71", "72", "73"]
        params = {'conids': ','.join(conids), 'fields': ','.join(fields)}
        return self._make_request('GET', '/iserver/marketdata/snapshot', params=params)

    def get_historical_data(self, conid: str, period: str = "1d",
                            bar: str = "1min") -> Optional[Dict]:
        """GET /iserver/marketdata/history — returns OHLCV bars in `data`."""
        params = {'conid': conid, 'period': period, 'bar': bar}
        return self._make_request('GET', '/iserver/marketdata/history', params=params)

    # ------------------------------------------------------------------
    # Portfolio
    # ------------------------------------------------------------------

    def get_portfolio_accounts(self) -> Optional[List[Dict]]:
        result = self._make_request('GET', '/portfolio/accounts')
        if result:
            self.logger.info(f"Retrieved {len(result)} account(s)")
        return result

    def get_portfolio_positions(self, account_id: str) -> Optional[List[Dict]]:
        """Paginated fetch of all positions for an account (30/page)."""
        all_positions: List[Dict] = []

        for page in range(self.POSITIONS_MAX_PAGES):
            result = self._make_request('GET', f'/portfolio/{account_id}/positions/{page}')
            if not result:
                break
            all_positions.extend(result)
            if len(result) < self.POSITIONS_PAGE_SIZE:
                break
        else:
            self.logger.warning(f"Hit POSITIONS_MAX_PAGES={self.POSITIONS_MAX_PAGES}")

        if all_positions:
            self.logger.info(f"Retrieved {len(all_positions)} position(s) for account {account_id}")
        return all_positions or None
