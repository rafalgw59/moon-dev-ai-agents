"""
Backtest Runner
Executes trading strategies and collects performance statistics
"""

import os
import sys
import pandas as pd
import importlib.util
from datetime import datetime
from typing import Dict, Optional, List
import traceback

try:
    from . import config
    from .data_fetcher import MoralisDataFetcher
except ImportError:
    import config
    from data_fetcher import MoralisDataFetcher


class BacktestRunner:
    """Execute backtests and collect statistics"""

    def __init__(self):
        """Initialize backtest runner"""
        # Create results directory
        os.makedirs(config.RESULTS_DIR, exist_ok=True)

        # Initialize results CSV if it doesn't exist
        if not os.path.exists(config.RESULTS_CSV):
            self._init_results_csv()

        self.data_fetcher = MoralisDataFetcher()

    def _init_results_csv(self):
        """Initialize empty results CSV with headers"""
        headers = [
            'timestamp',
            'strategy_name',
            'token_address',
            'return_pct',
            'buy_hold_pct',
            'vs_buy_hold_pct',
            'sharpe_ratio',
            'sortino_ratio',
            'max_drawdown_pct',
            'avg_drawdown_pct',
            'num_trades',
            'win_rate_pct',
            'best_trade_pct',
            'worst_trade_pct',
            'expectancy',
            'exposure_time_pct',
            'timeframe',
            'date_start',
            'date_end',
            'initial_capital',
            'final_equity',
            'passed_filters'
        ]

        df = pd.DataFrame(columns=headers)
        df.to_csv(config.RESULTS_CSV, index=False)
        print(f"✓ Initialized results CSV: {config.RESULTS_CSV}")

    def run_backtest_from_file(
        self,
        strategy_file: str,
        data_file: str,
        save_results: bool = True
    ) -> Optional[Dict]:
        """
        Run a backtest from a strategy Python file

        Args:
            strategy_file: Path to strategy .py file
            data_file: Path to OHLCV CSV file
            save_results: Save results to CSV

        Returns:
            Dictionary with backtest statistics or None if failed
        """
        print("=" * 70)
        print(f"Running backtest: {os.path.basename(strategy_file)}")
        print("=" * 70)

        try:
            # Load data
            print(f"\n1. Loading data from: {data_file}")
            df = self.data_fetcher.load_data_from_csv(data_file)

            if df.empty:
                print("❌ Data file is empty")
                return None

            print(f"   ✓ Loaded {len(df)} candles")
            print(f"   Date range: {df['datetime'].min()} to {df['datetime'].max()}")

            # Prepare data for backtesting
            bt_df = self.data_fetcher.prepare_for_backtesting(df)

            # Load strategy dynamically
            print(f"\n2. Loading strategy from: {strategy_file}")
            strategy_class = self._load_strategy_class(strategy_file)

            if not strategy_class:
                print("❌ Failed to load strategy class")
                return None

            print(f"   ✓ Strategy loaded: {strategy_class.__name__}")

            # Run backtest
            print(f"\n3. Executing backtest...")
            from backtesting import Backtest

            bt = Backtest(
                bt_df,
                strategy_class,
                cash=config.INITIAL_CAPITAL,
                commission=config.COMMISSION
            )

            stats = bt.run()
            print("   ✓ Backtest completed")

            # Extract statistics
            results = self._extract_stats(stats, strategy_file, data_file)

            # Check if meets saving criteria
            passed_filters = self._check_filters(results)
            results['passed_filters'] = passed_filters

            # Display results
            self._display_results(results)

            # Save to CSV
            if save_results and (config.SAVE_ALL_BACKTESTS or passed_filters):
                self._save_to_csv(results)
                print(f"\n✓ Results saved to: {config.RESULTS_CSV}")
            elif not passed_filters:
                print(f"\n⚠ Results not saved (didn't meet minimum criteria)")

            return results

        except Exception as e:
            print(f"\n❌ Backtest failed: {e}")
            traceback.print_exc()
            return None

    def run_backtest_with_token(
        self,
        strategy_file: str,
        token_address: str,
        date_start: Optional[str] = None,
        date_end: Optional[str] = None,
        timeframe: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Run backtest by fetching data for a specific token

        Args:
            strategy_file: Path to strategy .py file
            token_address: Solana token address
            date_start: Start date (YYYY-MM-DD) or None for config default
            date_end: End date (YYYY-MM-DD) or None for config default
            timeframe: Timeframe or None for config default

        Returns:
            Dictionary with backtest statistics or None if failed
        """
        # Use config defaults if not specified
        date_start = date_start or config.DATE_START
        date_end = date_end or config.DATE_END
        timeframe = timeframe or config.TIMEFRAME

        print("=" * 70)
        print(f"Running backtest with live data fetch")
        print("=" * 70)
        print(f"Token: {token_address}")
        print(f"Date Range: {date_start} to {date_end}")
        print(f"Timeframe: {timeframe}")

        # Fetch data
        df = self.data_fetcher.get_ohlcv_data(
            token_address=token_address,
            date_start=date_start,
            date_end=date_end,
            timeframe=timeframe,
            save_to_csv=True
        )

        if df.empty:
            print("❌ No data fetched for token")
            return None

        # Get the saved data file path
        filename = self.data_fetcher._generate_filename(token_address, date_start, date_end, timeframe)
        data_file = os.path.join(config.DOWNLOADED_DATA_DIR, filename)

        # Run backtest with the data file
        return self.run_backtest_from_file(strategy_file, data_file)

    def batch_run_strategies(
        self,
        strategy_files: List[str],
        data_file: str
    ) -> List[Dict]:
        """
        Run multiple strategies on the same dataset

        Args:
            strategy_files: List of strategy file paths
            data_file: Path to OHLCV CSV file

        Returns:
            List of result dictionaries
        """
        results = []

        print("=" * 70)
        print(f"BATCH BACKTEST: {len(strategy_files)} strategies")
        print("=" * 70)

        for i, strategy_file in enumerate(strategy_files, 1):
            print(f"\n[{i}/{len(strategy_files)}] {os.path.basename(strategy_file)}")
            print("-" * 70)

            result = self.run_backtest_from_file(strategy_file, data_file)

            if result:
                results.append(result)

            print()

        # Summary
        print("=" * 70)
        print("BATCH BACKTEST SUMMARY")
        print("=" * 70)
        print(f"Total strategies: {len(strategy_files)}")
        print(f"Successful: {len(results)}")
        print(f"Failed: {len(strategy_files) - len(results)}")

        if results:
            passed = sum(1 for r in results if r['passed_filters'])
            print(f"Passed filters: {passed}")

            avg_return = sum(r['return_pct'] for r in results) / len(results)
            print(f"Average return: {avg_return:.2f}%")

        return results

    def _load_strategy_class(self, filepath: str):
        """Dynamically load strategy class from Python file"""
        try:
            # Load module from file
            spec = importlib.util.spec_from_file_location("strategy_module", filepath)
            module = importlib.util.module_from_spec(spec)
            sys.modules["strategy_module"] = module
            spec.loader.exec_module(module)

            # Find Strategy class (looks for subclass of backtesting.Strategy)
            from backtesting import Strategy

            for name in dir(module):
                obj = getattr(module, name)
                try:
                    if isinstance(obj, type) and issubclass(obj, Strategy) and obj is not Strategy:
                        return obj
                except TypeError:
                    continue

            print("⚠ No Strategy class found in file")
            return None

        except Exception as e:
            print(f"❌ Error loading strategy: {e}")
            traceback.print_exc()
            return None

    def _extract_stats(self, stats, strategy_file: str, data_file: str) -> Dict:
        """Extract key statistics from backtesting.py stats object"""

        # Get strategy name from file
        strategy_name = os.path.splitext(os.path.basename(strategy_file))[0]

        # Try to extract token address from data file name
        data_filename = os.path.basename(data_file)
        token_address = data_filename.split('_')[0] if '_' in data_filename else 'unknown'

        # Extract timeframe and dates from data file if available
        parts = data_filename.replace('.csv', '').split('_')
        timeframe = parts[-1] if len(parts) > 1 else config.TIMEFRAME

        date_start = parts[1] if len(parts) > 3 else config.DATE_START
        date_end = parts[3] if len(parts) > 3 else config.DATE_END

        return {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'strategy_name': strategy_name,
            'token_address': token_address,
            'return_pct': float(stats['Return [%]']) if 'Return [%]' in stats else 0.0,
            'buy_hold_pct': float(stats['Buy & Hold Return [%]']) if 'Buy & Hold Return [%]' in stats else 0.0,
            'vs_buy_hold_pct': float(stats.get('Return vs. Buy Hold [%]', 0.0)),
            'sharpe_ratio': float(stats.get('Sharpe Ratio', 0.0)),
            'sortino_ratio': float(stats.get('Sortino Ratio', 0.0)),
            'max_drawdown_pct': float(stats.get('Max. Drawdown [%]', 0.0)),
            'avg_drawdown_pct': float(stats.get('Avg. Drawdown [%]', 0.0)),
            'num_trades': int(stats.get('# Trades', 0)),
            'win_rate_pct': float(stats.get('Win Rate [%]', 0.0)),
            'best_trade_pct': float(stats.get('Best Trade [%]', 0.0)),
            'worst_trade_pct': float(stats.get('Worst Trade [%]', 0.0)),
            'expectancy': float(stats.get('Expectancy [%]', 0.0)),
            'exposure_time_pct': float(stats.get('Exposure Time [%]', 0.0)),
            'timeframe': timeframe,
            'date_start': date_start,
            'date_end': date_end,
            'initial_capital': config.INITIAL_CAPITAL,
            'final_equity': float(stats.get('Equity Final [$]', config.INITIAL_CAPITAL)),
        }

    def _check_filters(self, results: Dict) -> bool:
        """Check if results meet minimum criteria for saving"""

        if config.SAVE_ALL_BACKTESTS:
            return True

        checks = [
            results['return_pct'] >= config.MIN_RETURN_PCT,
            results['sharpe_ratio'] >= config.MIN_SHARPE_RATIO,
            results['win_rate_pct'] >= config.MIN_WIN_RATE,
            abs(results['max_drawdown_pct']) <= config.MAX_DRAWDOWN_PCT
        ]

        return all(checks)

    def _display_results(self, results: Dict):
        """Display backtest results in a nice format"""

        print("\n" + "=" * 70)
        print("BACKTEST RESULTS")
        print("=" * 70)

        print(f"\nStrategy: {results['strategy_name']}")
        print(f"Token: {results['token_address']}")
        print(f"Period: {results['date_start']} to {results['date_end']} ({results['timeframe']})")

        print(f"\n📊 Performance:")
        print(f"  Return: {results['return_pct']:.2f}%")
        print(f"  Buy & Hold: {results['buy_hold_pct']:.2f}%")
        print(f"  vs. Buy & Hold: {results['vs_buy_hold_pct']:.2f}%")

        print(f"\n📈 Risk Metrics:")
        print(f"  Sharpe Ratio: {results['sharpe_ratio']:.3f}")
        print(f"  Sortino Ratio: {results['sortino_ratio']:.3f}")
        print(f"  Max Drawdown: {results['max_drawdown_pct']:.2f}%")
        print(f"  Avg Drawdown: {results['avg_drawdown_pct']:.2f}%")

        print(f"\n💰 Trading Stats:")
        print(f"  Total Trades: {results['num_trades']}")
        print(f"  Win Rate: {results['win_rate_pct']:.2f}%")
        print(f"  Best Trade: {results['best_trade_pct']:.2f}%")
        print(f"  Worst Trade: {results['worst_trade_pct']:.2f}%")
        print(f"  Expectancy: {results['expectancy']:.2f}%")

        print(f"\n💵 Capital:")
        print(f"  Initial: ${results['initial_capital']:,.2f}")
        print(f"  Final: ${results['final_equity']:,.2f}")
        print(f"  Profit: ${results['final_equity'] - results['initial_capital']:,.2f}")

        # Filter status
        if results['passed_filters']:
            print(f"\n✅ PASSED - Meets minimum criteria")
        else:
            print(f"\n⚠️  FAILED - Does not meet minimum criteria")

    def _save_to_csv(self, results: Dict):
        """Append results to CSV file"""

        # Read existing data
        df_existing = pd.read_csv(config.RESULTS_CSV)

        # Append new result
        df_new = pd.DataFrame([results])
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)

        # Save back to CSV
        df_combined.to_csv(config.RESULTS_CSV, index=False)

    def get_top_strategies(self, n: int = 10, sort_by: str = 'return_pct') -> pd.DataFrame:
        """
        Get top performing strategies from results

        Args:
            n: Number of top strategies to return
            sort_by: Column to sort by

        Returns:
            DataFrame with top strategies
        """
        if not os.path.exists(config.RESULTS_CSV):
            return pd.DataFrame()

        df = pd.read_csv(config.RESULTS_CSV)

        if df.empty:
            return df

        # Filter only passed strategies
        df_passed = df[df['passed_filters'] == True].copy()

        if df_passed.empty:
            return df_passed

        # Sort and get top N
        df_top = df_passed.sort_values(sort_by, ascending=False).head(n)

        return df_top


def test_runner():
    """Test the backtest runner"""
    print("=" * 70)
    print("BACKTEST RUNNER - Test Mode")
    print("=" * 70)

    runner = BacktestRunner()

    print("\n✓ Backtest runner initialized")
    print(f"✓ Results CSV: {config.RESULTS_CSV}")

    # Check if there are any strategies to test
    strategies_dir = config.STRATEGIES_DIR
    if os.path.exists(strategies_dir):
        strategy_files = [
            os.path.join(strategies_dir, f)
            for f in os.listdir(strategies_dir)
            if f.endswith('.py') and not f.startswith('_')
        ]

        if strategy_files:
            print(f"\n✓ Found {len(strategy_files)} strategies to test")
        else:
            print(f"\n⚠ No strategy files found in {strategies_dir}")
    else:
        print(f"\n⚠ Strategies directory doesn't exist: {strategies_dir}")

    # Check for data files
    data_dir = config.DOWNLOADED_DATA_DIR
    if os.path.exists(data_dir):
        data_files = [
            os.path.join(data_dir, f)
            for f in os.listdir(data_dir)
            if f.endswith('.csv')
        ]

        if data_files:
            print(f"✓ Found {len(data_files)} data files")
        else:
            print(f"⚠ No data files found in {data_dir}")
    else:
        print(f"⚠ Data directory doesn't exist: {data_dir}")

    print("\n" + "=" * 70)
    print("Ready to run backtests!")
    print("=" * 70)


if __name__ == '__main__':
    test_runner()
