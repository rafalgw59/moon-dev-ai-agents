"""
Swarm Runner - Parallel AI Agent System for Strategy Discovery
Implements anti-overfitting measures and cost optimization
"""

import os
import time
import hashlib
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, Semaphore
from queue import Queue
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd
from termcolor import cprint

try:
    from . import config
    from .data_fetcher import MoralisDataFetcher
    from .strategy_builder import AIStrategyBuilder
    from .backtest_runner import BacktestRunner
except ImportError:
    import config
    from data_fetcher import MoralisDataFetcher
    from strategy_builder import AIStrategyBuilder
    from backtest_runner import BacktestRunner


class SwarmRunner:
    """
    Parallel AI agent swarm for strategy discovery

    Features:
    - Multi-threaded strategy generation and testing
    - Anti-overfitting: walk-forward analysis, out-of-sample testing
    - Cost optimization: use cheaper models for initial passes
    - Multi-token testing
    - Thread-safe operations
    """

    def __init__(self, max_threads: int = None, cost_optimized: bool = True):
        """
        Initialize swarm runner

        Args:
            max_threads: Maximum parallel threads (default from config)
            cost_optimized: Use cheaper AI models to save costs
        """
        self.max_threads = max_threads or config.SWARM_MAX_THREADS
        self.cost_optimized = cost_optimized

        # Thread safety
        self.console_lock = Lock()
        self.file_lock = Lock()
        self.api_lock = Lock()
        self.rate_limiter = Semaphore(self.max_threads)

        # Initialize components
        self.data_fetcher = MoralisDataFetcher()
        self.backtest_runner = BacktestRunner()

        # Stats tracking
        self.stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'passed_filters': 0,
            'active_threads': 0
        }

        # Thread colors for console output
        self.thread_colors = {
            0: "cyan", 1: "magenta", 2: "yellow", 3: "green",
            4: "blue", 5: "white", 6: "cyan", 7: "magenta"
        }

        # Create swarm data directories
        self.swarm_dir = Path(config.DATA_DIR) / 'swarm'
        self.swarm_dir.mkdir(parents=True, exist_ok=True)

        self.processed_log = self.swarm_dir / 'processed_ideas.log'
        self.swarm_results_csv = self.swarm_dir / 'swarm_results.csv'

    def thread_print(self, message: str, thread_id: int, color: str = None, attrs: List = None):
        """Thread-safe colored console output"""
        if color is None:
            color = self.thread_colors.get(thread_id % 8, "white")

        with self.console_lock:
            prefix = f"[Swarm-{thread_id:02d}]"
            cprint(f"{prefix} {message}", color, attrs=attrs)

    def get_idea_hash(self, idea: str) -> str:
        """Generate unique hash for an idea"""
        return hashlib.md5(idea.encode('utf-8')).hexdigest()

    def is_idea_processed(self, idea: str) -> bool:
        """Check if idea already processed"""
        if not self.processed_log.exists():
            return False

        idea_hash = self.get_idea_hash(idea)

        with self.file_lock:
            with open(self.processed_log, 'r') as f:
                processed = [line.split(',')[0] for line in f if line.strip()]

        return idea_hash in processed

    def log_processed_idea(self, idea: str, strategy_name: str, thread_id: int):
        """Log idea as processed"""
        idea_hash = self.get_idea_hash(idea)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self.file_lock:
            if not self.processed_log.exists():
                with open(self.processed_log, 'w') as f:
                    f.write("# Swarm Runner - Processed Ideas Log\n")
                    f.write("# Format: hash,timestamp,thread_id,strategy_name\n")

            with open(self.processed_log, 'a') as f:
                f.write(f"{idea_hash},{timestamp},T{thread_id:02d},{strategy_name}\n")

    def get_ai_model_config(self, phase: str) -> str:
        """
        Get AI model for specific phase (cost optimized)

        Args:
            phase: 'research', 'backtest', 'debug'

        Returns:
            Model type string
        """
        if not self.cost_optimized:
            return config.STRATEGY_AI_MODEL

        # Cost optimization: use cheaper models for initial passes
        cheap_models = {
            'research': 'deepseek',      # Cheap and fast
            'backtest': 'anthropic',      # Need quality code
            'debug': 'deepseek'           # Can use cheaper for debugging
        }

        return cheap_models.get(phase, config.STRATEGY_AI_MODEL)

    def split_data_for_walkforward(self, df: pd.DataFrame, train_pct: float = 0.7) -> tuple:
        """
        Split data into training and testing periods (walk-forward)

        Anti-overfitting measure: train on earlier data, test on later

        Args:
            df: OHLCV DataFrame
            train_pct: Percentage for training (0.7 = 70% train, 30% test)

        Returns:
            (train_df, test_df)
        """
        split_idx = int(len(df) * train_pct)

        train_df = df.iloc[:split_idx].copy()
        test_df = df.iloc[split_idx:].copy()

        return train_df, test_df

    def run_walkforward_analysis(
        self,
        strategy_file: str,
        data_file: str,
        thread_id: int
    ) -> Dict:
        """
        Run walk-forward analysis on strategy

        Tests strategy on both training and out-of-sample data

        Returns:
            Dict with train_results, test_results, walkforward_ratio
        """
        self.thread_print("Starting walk-forward analysis...", thread_id, "cyan")

        # Load full data
        df = self.data_fetcher.load_data_from_csv(data_file)

        if df.empty:
            return {'error': 'Empty data file'}

        # Split into train/test
        train_df, test_df = self.split_data_for_walkforward(df, train_pct=0.7)

        # Save temporary train/test files
        train_file = str(Path(data_file).parent / f"train_{Path(data_file).name}")
        test_file = str(Path(data_file).parent / f"test_{Path(data_file).name}")

        train_df.to_csv(train_file, index=False)
        test_df.to_csv(test_file, index=False)

        # Run backtest on training data
        self.thread_print(f"Testing on TRAINING data ({len(train_df)} candles)...", thread_id)
        train_results = self.backtest_runner.run_backtest_from_file(
            strategy_file=strategy_file,
            data_file=train_file,
            save_results=False
        )

        # Run backtest on testing data (out-of-sample)
        self.thread_print(f"Testing on OUT-OF-SAMPLE data ({len(test_df)} candles)...", thread_id)
        test_results = self.backtest_runner.run_backtest_from_file(
            strategy_file=strategy_file,
            data_file=test_file,
            save_results=False
        )

        # Cleanup temp files
        os.remove(train_file)
        os.remove(test_file)

        # Calculate walk-forward ratio (test return / train return)
        # Closer to 1.0 = less overfitting
        # < 0.5 = likely overfitted
        # > 0.8 = good generalization
        if train_results and test_results:
            train_return = train_results.get('return_pct', 0)
            test_return = test_results.get('return_pct', 0)

            if train_return > 0:
                walkforward_ratio = test_return / train_return
            else:
                walkforward_ratio = 0

            # Assess overfitting
            if walkforward_ratio > 0.8:
                assessment = "GOOD - Low overfitting risk"
                color = "green"
            elif walkforward_ratio > 0.5:
                assessment = "MODERATE - Some overfitting"
                color = "yellow"
            else:
                assessment = "BAD - Likely overfitted"
                color = "red"

            self.thread_print(
                f"Walk-Forward Ratio: {walkforward_ratio:.2f} ({assessment})",
                thread_id,
                color,
                attrs=['bold']
            )

            return {
                'train_results': train_results,
                'test_results': test_results,
                'walkforward_ratio': walkforward_ratio,
                'assessment': assessment,
                'overfitting_risk': 'low' if walkforward_ratio > 0.8 else 'high'
            }

        return {'error': 'Backtest failed'}

    def test_on_multiple_tokens(
        self,
        strategy_file: str,
        token_addresses: List[str],
        thread_id: int
    ) -> List[Dict]:
        """
        Test strategy on multiple tokens (anti-overfitting)

        Args:
            strategy_file: Path to strategy .py file
            token_addresses: List of token addresses to test
            thread_id: Thread ID

        Returns:
            List of backtest results for each token
        """
        self.thread_print(f"Testing on {len(token_addresses)} tokens...", thread_id, "cyan")

        results = []

        for i, token_address in enumerate(token_addresses, 1):
            self.thread_print(f"[{i}/{len(token_addresses)}] Testing {token_address[:8]}...", thread_id)

            # Fetch data for this token
            df = self.data_fetcher.get_ohlcv_data(
                token_address=token_address,
                date_start=config.DATE_START,
                date_end=config.DATE_END,
                timeframe=config.TIMEFRAME,
                save_to_csv=True
            )

            if df.empty:
                self.thread_print(f"No data for {token_address[:8]}, skipping", thread_id, "yellow")
                continue

            # Get saved data file
            filename = self.data_fetcher._generate_filename(
                token_address,
                config.DATE_START,
                config.DATE_END,
                config.TIMEFRAME
            )
            data_file = os.path.join(config.DOWNLOADED_DATA_DIR, filename)

            # Run backtest
            result = self.backtest_runner.run_backtest_from_file(
                strategy_file=strategy_file,
                data_file=data_file,
                save_results=False
            )

            if result:
                result['token_address'] = token_address
                results.append(result)
                self.thread_print(
                    f"✓ {token_address[:8]}: {result.get('return_pct', 0):.2f}%",
                    thread_id,
                    "green" if result.get('passed_filters') else "yellow"
                )

            # Rate limiting
            time.sleep(1)

        # Summary statistics
        if results:
            avg_return = sum(r.get('return_pct', 0) for r in results) / len(results)
            passed_count = sum(1 for r in results if r.get('passed_filters'))

            self.thread_print(
                f"Multi-token summary: {avg_return:.2f}% avg, {passed_count}/{len(results)} passed",
                thread_id,
                "green" if passed_count > 0 else "yellow",
                attrs=['bold']
            )

        return results

    def process_single_idea(self, idea: str, thread_id: int) -> Dict:
        """
        Process one strategy idea through full pipeline

        Pipeline:
        1. Generate strategy with AI
        2. Backtest on training data
        3. Walk-forward analysis
        4. Multi-token testing (optional)
        5. Save if passes anti-overfitting checks

        Args:
            idea: Strategy idea text
            thread_id: Thread ID

        Returns:
            Results dictionary
        """
        start_time = time.time()

        try:
            self.thread_print("=" * 60, thread_id)
            self.thread_print(f"Processing: {idea[:60]}...", thread_id, attrs=['bold'])
            self.thread_print("=" * 60, thread_id)

            # Phase 1: Generate strategy
            self.thread_print("Phase 1: AI Strategy Generation", thread_id, "cyan", attrs=['bold'])

            # Use cost-optimized model
            model_type = self.get_ai_model_config('research')
            builder = AIStrategyBuilder(model_type=model_type)

            strategy_result = builder.generate_strategy(idea)
            strategy_name = strategy_result['name']
            strategy_file = strategy_result['code_file']

            self.log_processed_idea(idea, strategy_name, thread_id)
            self.thread_print(f"✓ Generated: {strategy_name}", thread_id, "green")

            # Phase 2: Initial backtest
            self.thread_print("Phase 2: Initial Backtest", thread_id, "cyan", attrs=['bold'])

            # Use example data for quick test
            data_files = [
                f for f in os.listdir(config.DOWNLOADED_DATA_DIR)
                if f.endswith('.csv')
            ]

            if not data_files:
                self.thread_print("No data files found! Fetch data first.", thread_id, "red")
                return {'success': False, 'error': 'No data files'}

            # Use first available data file
            data_file = os.path.join(config.DOWNLOADED_DATA_DIR, data_files[0])

            initial_results = self.backtest_runner.run_backtest_from_file(
                strategy_file=strategy_file,
                data_file=data_file,
                save_results=False
            )

            if not initial_results:
                self.thread_print("Initial backtest failed", thread_id, "red")
                return {'success': False, 'error': 'Initial backtest failed'}

            initial_return = initial_results.get('return_pct', 0)
            self.thread_print(f"✓ Initial return: {initial_return:.2f}%", thread_id, "green")

            # Phase 3: Walk-forward analysis (anti-overfitting)
            self.thread_print("Phase 3: Walk-Forward Analysis", thread_id, "cyan", attrs=['bold'])

            walkforward_results = self.run_walkforward_analysis(
                strategy_file=strategy_file,
                data_file=data_file,
                thread_id=thread_id
            )

            if 'error' in walkforward_results:
                self.thread_print(f"Walk-forward failed: {walkforward_results['error']}", thread_id, "red")
                return {'success': False, 'error': 'Walk-forward failed'}

            # Check overfitting risk
            overfitting_risk = walkforward_results.get('overfitting_risk', 'high')
            walkforward_ratio = walkforward_results.get('walkforward_ratio', 0)

            if overfitting_risk == 'high':
                self.thread_print(
                    f"⚠ HIGH OVERFITTING RISK (WF ratio: {walkforward_ratio:.2f}) - NOT SAVING",
                    thread_id,
                    "red",
                    attrs=['bold']
                )

                # Log but don't save
                return {
                    'success': True,
                    'strategy_name': strategy_name,
                    'initial_return': initial_return,
                    'walkforward_ratio': walkforward_ratio,
                    'overfitting_risk': 'high',
                    'saved': False
                }

            # Phase 4: Multi-token testing (if configured)
            multi_token_results = None
            if config.SWARM_MULTI_TOKEN_TEST and len(config.SWARM_TEST_TOKENS) > 0:
                self.thread_print("Phase 4: Multi-Token Testing", thread_id, "cyan", attrs=['bold'])

                multi_token_results = self.test_on_multiple_tokens(
                    strategy_file=strategy_file,
                    token_addresses=config.SWARM_TEST_TOKENS,
                    thread_id=thread_id
                )

            # Phase 5: Final evaluation and saving
            self.thread_print("Phase 5: Final Evaluation", thread_id, "cyan", attrs=['bold'])

            test_results = walkforward_results['test_results']
            test_return = test_results.get('return_pct', 0)

            # Check if passes filters
            if test_results.get('passed_filters'):
                self.thread_print("✅ PASSED ALL FILTERS!", thread_id, "green", attrs=['bold'])

                # Save to results CSV
                self.save_to_swarm_csv(
                    strategy_name=strategy_name,
                    initial_results=initial_results,
                    walkforward_results=walkforward_results,
                    multi_token_results=multi_token_results,
                    thread_id=thread_id
                )

                elapsed = time.time() - start_time
                self.thread_print(
                    f"🎉 SUCCESS in {elapsed:.1f}s! Return: {test_return:.2f}% (WF: {walkforward_ratio:.2f})",
                    thread_id,
                    "green",
                    attrs=['bold']
                )

                return {
                    'success': True,
                    'strategy_name': strategy_name,
                    'initial_return': initial_return,
                    'test_return': test_return,
                    'walkforward_ratio': walkforward_ratio,
                    'overfitting_risk': 'low',
                    'saved': True,
                    'elapsed_time': elapsed
                }
            else:
                self.thread_print(f"Did not pass filters (return: {test_return:.2f}%)", thread_id, "yellow")

                return {
                    'success': True,
                    'strategy_name': strategy_name,
                    'initial_return': initial_return,
                    'test_return': test_return,
                    'walkforward_ratio': walkforward_ratio,
                    'saved': False
                }

        except Exception as e:
            self.thread_print(f"ERROR: {str(e)}", thread_id, "red", attrs=['bold'])
            import traceback
            traceback.print_exc()

            return {
                'success': False,
                'error': str(e),
                'thread_id': thread_id
            }

    def save_to_swarm_csv(
        self,
        strategy_name: str,
        initial_results: Dict,
        walkforward_results: Dict,
        multi_token_results: List[Dict],
        thread_id: int
    ):
        """Save swarm results to CSV with anti-overfitting metrics"""

        with self.file_lock:
            # Create CSV if doesn't exist
            if not self.swarm_results_csv.exists():
                df = pd.DataFrame(columns=[
                    'timestamp', 'thread_id', 'strategy_name',
                    'initial_return_%', 'train_return_%', 'test_return_%',
                    'walkforward_ratio', 'overfitting_risk',
                    'sharpe_ratio', 'sortino_ratio', 'max_drawdown_%',
                    'num_trades', 'win_rate_%',
                    'multi_token_avg_%', 'multi_token_passed_count'
                ])
                df.to_csv(self.swarm_results_csv, index=False)

            # Prepare row data
            test_results = walkforward_results['test_results']
            train_results = walkforward_results['train_results']

            # Multi-token stats
            if multi_token_results and len(multi_token_results) > 0:
                multi_avg = sum(r.get('return_pct', 0) for r in multi_token_results) / len(multi_token_results)
                multi_passed = sum(1 for r in multi_token_results if r.get('passed_filters'))
            else:
                multi_avg = None
                multi_passed = None

            row = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'thread_id': f"T{thread_id:02d}",
                'strategy_name': strategy_name,
                'initial_return_%': initial_results.get('return_pct', 0),
                'train_return_%': train_results.get('return_pct', 0),
                'test_return_%': test_results.get('return_pct', 0),
                'walkforward_ratio': walkforward_results.get('walkforward_ratio', 0),
                'overfitting_risk': walkforward_results.get('overfitting_risk', 'unknown'),
                'sharpe_ratio': test_results.get('sharpe_ratio', 0),
                'sortino_ratio': test_results.get('sortino_ratio', 0),
                'max_drawdown_%': test_results.get('max_drawdown_pct', 0),
                'num_trades': test_results.get('num_trades', 0),
                'win_rate_%': test_results.get('win_rate_pct', 0),
                'multi_token_avg_%': multi_avg,
                'multi_token_passed_count': multi_passed
            }

            # Append to CSV
            df = pd.read_csv(self.swarm_results_csv)
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
            df.to_csv(self.swarm_results_csv, index=False)

            self.thread_print(f"💾 Saved to swarm CSV", thread_id, "green")

    def run_swarm(self, ideas: List[str]):
        """
        Run swarm on list of ideas

        Args:
            ideas: List of strategy idea texts
        """
        print("=" * 70)
        print("🚀 STARTING AI SWARM - STRATEGY DISCOVERY")
        print("=" * 70)
        print(f"Ideas to process: {len(ideas)}")
        print(f"Max parallel threads: {self.max_threads}")
        print(f"Cost optimized: {self.cost_optimized}")
        print(f"Walk-forward analysis: ENABLED")
        print(f"Multi-token testing: {'ENABLED' if config.SWARM_MULTI_TOKEN_TEST else 'DISABLED'}")
        print("=" * 70)
        print()

        # Filter already processed ideas
        ideas_to_process = [idea for idea in ideas if not self.is_idea_processed(idea)]

        if len(ideas_to_process) < len(ideas):
            skipped = len(ideas) - len(ideas_to_process)
            cprint(f"⏭ Skipping {skipped} already processed ideas", "yellow")

        if not ideas_to_process:
            cprint("✓ All ideas already processed!", "green")
            return

        print(f"\n🎯 Processing {len(ideas_to_process)} new ideas...\n")

        # Process in parallel
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = {
                executor.submit(self.process_single_idea, idea, i): (idea, i)
                for i, idea in enumerate(ideas_to_process)
            }

            for future in as_completed(futures):
                idea, thread_id = futures[future]

                try:
                    result = future.result()

                    # Update stats
                    self.stats['total_processed'] += 1

                    if result.get('success'):
                        self.stats['successful'] += 1
                        if result.get('saved'):
                            self.stats['passed_filters'] += 1
                    else:
                        self.stats['failed'] += 1

                except Exception as e:
                    cprint(f"Thread {thread_id} failed: {e}", "red")
                    self.stats['failed'] += 1

        # Final summary
        print("\n" + "=" * 70)
        print("🎉 SWARM COMPLETED")
        print("=" * 70)
        print(f"Total processed: {self.stats['total_processed']}")
        print(f"Successful: {self.stats['successful']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"Passed filters: {self.stats['passed_filters']}")
        print(f"\nResults saved to: {self.swarm_results_csv}")
        print("=" * 70)


def test_swarm():
    """Test the swarm runner"""
    print("=" * 70)
    print("SWARM RUNNER - Test Mode")
    print("=" * 70)

    # Sample ideas
    ideas = [
        "Create an RSI mean reversion strategy that buys when RSI < 30 and sells when RSI > 70",
        "Momentum strategy using MACD crossover with volume confirmation"
    ]

    swarm = SwarmRunner(max_threads=2, cost_optimized=True)
    swarm.run_swarm(ideas)


if __name__ == '__main__':
    test_swarm()
