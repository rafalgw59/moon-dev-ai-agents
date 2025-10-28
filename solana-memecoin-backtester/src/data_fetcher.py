"""
Moralis API Integration for Solana Token Data
Fetches OHLCV data, metadata, and price information
"""

import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import os
import json

try:
    from . import config
except ImportError:
    import config


class MoralisDataFetcher:
    """Fetch Solana token data from Moralis API"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Moralis data fetcher

        Args:
            api_key: Moralis API key (if None, reads from config)
        """
        self.api_key = api_key or config.MORALIS_API_KEY

        if not self.api_key:
            raise ValueError("Moralis API key not provided. Set MORALIS_API_KEY in .env file")

        self.base_url = 'https://solana-gateway.moralis.io'
        self.headers = {
            'accept': 'application/json',
            'X-API-Key': self.api_key
        }

        # Create data directory if it doesn't exist
        os.makedirs(config.DOWNLOADED_DATA_DIR, exist_ok=True)

    def get_token_metadata(self, token_address: str) -> Dict:
        """
        Get token metadata (name, symbol, decimals, etc.)

        Args:
            token_address: Solana token address

        Returns:
            Dictionary with token metadata
        """
        url = f'{self.base_url}/token/mainnet/{token_address}/metadata'

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching metadata for {token_address}: {e}")
            return {}

    def get_token_price(self, token_address: str) -> Optional[float]:
        """
        Get current token price

        Args:
            token_address: Solana token address

        Returns:
            Current price in USD or None if failed
        """
        url = f'{self.base_url}/token/mainnet/{token_address}/price'

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return float(data.get('usdPrice', 0))
        except requests.exceptions.RequestException as e:
            print(f"Error fetching price for {token_address}: {e}")
            return None

    def get_ohlcv_data(
        self,
        token_address: str,
        date_start: str,
        date_end: str,
        timeframe: str = '15min',
        save_to_csv: bool = True
    ) -> pd.DataFrame:
        """
        Fetch OHLCV (candlestick) data for a token

        Args:
            token_address: Solana token address
            date_start: Start date (YYYY-MM-DD)
            date_end: End date (YYYY-MM-DD)
            timeframe: Candle timeframe (1min, 5min, 15min, 30min, 1hour, 4hour, 1day)
            save_to_csv: Save data to CSV file

        Returns:
            DataFrame with columns: datetime, open, high, low, close, volume
        """
        # Convert dates to timestamps
        start_dt = datetime.strptime(date_start, '%Y-%m-%d')
        end_dt = datetime.strptime(date_end, '%Y-%m-%d')

        # Moralis API endpoint
        url = f'{self.base_url}/token/mainnet/{token_address}/ohlcv'

        all_candles = []
        current_start = start_dt

        print(f"Fetching OHLCV data for {token_address[:8]}...")
        print(f"  Date range: {date_start} to {date_end}")
        print(f"  Timeframe: {timeframe}")

        while current_start < end_dt:
            # Calculate end time for this batch (Moralis limits response size)
            current_end = min(current_start + timedelta(days=30), end_dt)

            params = {
                'from': int(current_start.timestamp()),
                'to': int(current_end.timestamp()),
                'interval': timeframe
            }

            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()

                if isinstance(data, list):
                    all_candles.extend(data)
                    print(f"  Fetched {len(data)} candles ({current_start.date()} to {current_end.date()})")
                elif isinstance(data, dict) and 'result' in data:
                    all_candles.extend(data['result'])
                    print(f"  Fetched {len(data['result'])} candles ({current_start.date()} to {current_end.date()})")

                # Move to next batch
                current_start = current_end

                # Rate limiting - be nice to the API
                time.sleep(0.5)

            except requests.exceptions.RequestException as e:
                print(f"Error fetching data batch: {e}")
                current_start = current_end
                time.sleep(1)

        # Convert to DataFrame
        if not all_candles:
            print(f"⚠ No data returned for {token_address}")
            return pd.DataFrame()

        df = self._process_ohlcv_data(all_candles)

        print(f"✓ Total candles fetched: {len(df)}")

        # Save to CSV
        if save_to_csv and not df.empty:
            filename = self._generate_filename(token_address, date_start, date_end, timeframe)
            filepath = os.path.join(config.DOWNLOADED_DATA_DIR, filename)
            df.to_csv(filepath, index=False)
            print(f"✓ Saved to: {filepath}")

        return df

    def _process_ohlcv_data(self, candles: List[Dict]) -> pd.DataFrame:
        """
        Process raw OHLCV data into proper DataFrame format

        Args:
            candles: List of candle dictionaries from Moralis

        Returns:
            Cleaned DataFrame with proper column names
        """
        df = pd.DataFrame(candles)

        if df.empty:
            return df

        # Moralis response format varies, handle different structures
        column_mapping = {
            'timestamp': 'datetime',
            'time': 'datetime',
            'date': 'datetime',
            'openPrice': 'open',
            'o': 'open',
            'highPrice': 'high',
            'h': 'high',
            'lowPrice': 'low',
            'l': 'low',
            'closePrice': 'close',
            'c': 'close',
            'volume': 'volume',
            'v': 'volume'
        }

        # Rename columns
        df = df.rename(columns=column_mapping)

        # Ensure required columns exist
        required_cols = ['datetime', 'open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in df.columns:
                print(f"⚠ Warning: Missing column '{col}', available columns: {df.columns.tolist()}")

        # Convert datetime
        if 'datetime' in df.columns:
            # Handle timestamp (Unix epoch)
            if df['datetime'].dtype in ['int64', 'float64']:
                df['datetime'] = pd.to_datetime(df['datetime'], unit='s')
            else:
                df['datetime'] = pd.to_datetime(df['datetime'])

        # Convert price/volume columns to numeric
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Remove any rows with NaN values
        df = df.dropna()

        # Sort by datetime
        if 'datetime' in df.columns:
            df = df.sort_values('datetime').reset_index(drop=True)

        # Select only required columns
        available_cols = [col for col in required_cols if col in df.columns]
        df = df[available_cols]

        return df

    def _generate_filename(self, token_address: str, date_start: str, date_end: str, timeframe: str) -> str:
        """Generate CSV filename for downloaded data"""
        short_addr = token_address[:8]
        filename = f"{short_addr}_{date_start}_to_{date_end}_{timeframe}.csv"
        return filename

    def load_data_from_csv(self, filepath: str) -> pd.DataFrame:
        """
        Load OHLCV data from CSV file

        Args:
            filepath: Path to CSV file

        Returns:
            DataFrame with OHLCV data
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        df = pd.read_csv(filepath)

        # Convert datetime column
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'])

        return df

    def prepare_for_backtesting(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare DataFrame for backtesting.py library
        Requires: datetime index, capitalized column names (Open, High, Low, Close, Volume)

        Args:
            df: DataFrame with lowercase column names

        Returns:
            DataFrame ready for backtesting.py
        """
        if df.empty:
            return df

        # Make a copy
        bt_df = df.copy()

        # Capitalize column names (backtesting.py requirement)
        bt_df.columns = [col.capitalize() for col in bt_df.columns]

        # Set datetime as index
        if 'Datetime' in bt_df.columns:
            bt_df = bt_df.set_index('Datetime')

        return bt_df

    def get_multiple_tokens(
        self,
        token_addresses: List[str],
        date_start: str,
        date_end: str,
        timeframe: str = '15min'
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch OHLCV data for multiple tokens

        Args:
            token_addresses: List of Solana token addresses
            date_start: Start date (YYYY-MM-DD)
            date_end: End date (YYYY-MM-DD)
            timeframe: Candle timeframe

        Returns:
            Dictionary mapping token_address -> DataFrame
        """
        results = {}

        for i, address in enumerate(token_addresses, 1):
            print(f"\n[{i}/{len(token_addresses)}] Processing {address[:8]}...")

            df = self.get_ohlcv_data(address, date_start, date_end, timeframe)

            if not df.empty:
                results[address] = df
            else:
                print(f"⚠ Skipping {address[:8]} (no data)")

            # Rate limiting between tokens
            time.sleep(1)

        print(f"\n✓ Successfully fetched data for {len(results)}/{len(token_addresses)} tokens")
        return results


def test_fetcher():
    """Test the Moralis data fetcher"""
    print("=" * 70)
    print("MORALIS DATA FETCHER - Test Mode")
    print("=" * 70)

    # Validate config
    errors = config.validate_config()
    if errors:
        print("\n❌ Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        return

    # Initialize fetcher
    try:
        fetcher = MoralisDataFetcher()
        print("\n✓ Moralis fetcher initialized")
    except ValueError as e:
        print(f"\n❌ {e}")
        return

    # Test token (SOL wrapped token - well-known address)
    test_token = "So11111111111111111111111111111111111111112"  # Wrapped SOL

    print(f"\nTest Token: {test_token}")

    # Test 1: Get metadata
    print("\n" + "=" * 70)
    print("TEST 1: Fetch Token Metadata")
    print("=" * 70)
    metadata = fetcher.get_token_metadata(test_token)
    if metadata:
        print(f"  Name: {metadata.get('name', 'N/A')}")
        print(f"  Symbol: {metadata.get('symbol', 'N/A')}")
        print(f"  Decimals: {metadata.get('decimals', 'N/A')}")
    else:
        print("  ⚠ No metadata returned")

    # Test 2: Get current price
    print("\n" + "=" * 70)
    print("TEST 2: Fetch Current Price")
    print("=" * 70)
    price = fetcher.get_token_price(test_token)
    if price:
        print(f"  Current Price: ${price:.4f}")
    else:
        print("  ⚠ No price returned")

    # Test 3: Get OHLCV data (small date range for testing)
    print("\n" + "=" * 70)
    print("TEST 3: Fetch OHLCV Data")
    print("=" * 70)
    df = fetcher.get_ohlcv_data(
        token_address=test_token,
        date_start='2024-01-01',
        date_end='2024-01-07',
        timeframe='1hour',
        save_to_csv=True
    )

    if not df.empty:
        print(f"\nDataFrame Info:")
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {df.columns.tolist()}")
        print(f"\nFirst 3 rows:")
        print(df.head(3))
        print(f"\nLast 3 rows:")
        print(df.tail(3))
        print(f"\nData types:")
        print(df.dtypes)

        # Test preparing for backtesting
        print("\n" + "=" * 70)
        print("TEST 4: Prepare for Backtesting")
        print("=" * 70)
        bt_df = fetcher.prepare_for_backtesting(df)
        print(f"  Columns: {bt_df.columns.tolist()}")
        print(f"  Index: {bt_df.index.name}")
        print(f"\nReady for backtesting.py ✓")
    else:
        print("  ⚠ No OHLCV data returned")

    print("\n" + "=" * 70)
    print("✓ All tests completed!")
    print("=" * 70)


if __name__ == '__main__':
    test_fetcher()
