#!/usr/bin/env python3
"""
Solana Memecoin Backtester - Main CLI Interface
Easy-to-use command line interface for all features
"""

import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src import config
from src.data_fetcher import MoralisDataFetcher
from src.strategy_builder import AIStrategyBuilder
from src.backtest_runner import BacktestRunner
from src.dashboard import run_dashboard


def print_header():
    """Print welcome header"""
    print("=" * 70)
    print("🚀 SOLANA MEMECOIN BACKTESTER")
    print("=" * 70)
    print()


def print_menu():
    """Print main menu"""
    print("\nWhat would you like to do?\n")
    print("1. Fetch token data from Moralis")
    print("2. Generate AI trading strategy")
    print("3. Run backtest on existing strategy")
    print("4. Complete workflow (fetch + generate + backtest)")
    print("5. View dashboard")
    print("6. Batch test multiple strategies")
    print("7. View top strategies")
    print("8. 🚀 RUN AI SWARM (parallel strategy discovery with anti-overfitting)")
    print("9. Exit")
    print()


def fetch_data_menu():
    """Fetch token data from Moralis"""
    print("\n" + "=" * 70)
    print("FETCH TOKEN DATA")
    print("=" * 70)

    token_address = input("\nEnter Solana token address: ").strip()

    print(f"\nCurrent config: {config.DATE_START} to {config.DATE_END}, {config.TIMEFRAME}")
    use_config = input("Use config dates/timeframe? (y/n): ").strip().lower()

    if use_config == 'y':
        date_start = config.DATE_START
        date_end = config.DATE_END
        timeframe = config.TIMEFRAME
    else:
        date_start = input("Start date (YYYY-MM-DD): ").strip()
        date_end = input("End date (YYYY-MM-DD or 'today'): ").strip()
        timeframe = input("Timeframe (1min/5min/15min/1hour/4hour/1day): ").strip()

    try:
        fetcher = MoralisDataFetcher()
        df = fetcher.get_ohlcv_data(
            token_address=token_address,
            date_start=date_start,
            date_end=date_end,
            timeframe=timeframe,
            save_to_csv=True
        )

        if not df.empty:
            print(f"\n✅ Success! Fetched {len(df)} candles")
            return True
        else:
            print("\n❌ No data returned")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def generate_strategy_menu():
    """Generate AI trading strategy"""
    print("\n" + "=" * 70)
    print("AI STRATEGY GENERATOR")
    print("=" * 70)

    print(f"\nUsing AI model: {config.STRATEGY_AI_MODEL}")

    strategy_name = input("\nStrategy name (optional, press enter to auto-generate): ").strip()
    if not strategy_name:
        strategy_name = None

    print("\nEnter your trading strategy idea (press Enter twice when done):")
    print("-" * 70)

    lines = []
    empty_count = 0
    while empty_count < 2:
        line = input()
        if line:
            lines.append(line)
            empty_count = 0
        else:
            empty_count += 1

    idea_text = '\n'.join(lines)

    if not idea_text.strip():
        print("❌ No strategy idea provided")
        return False

    try:
        builder = AIStrategyBuilder()
        result = builder.generate_strategy(idea_text, strategy_name)

        print(f"\n✅ Strategy generated!")
        print(f"   Name: {result['name']}")
        print(f"   Code: {result['code_file']}")
        return result['code_file']

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_backtest_menu():
    """Run backtest on existing strategy"""
    print("\n" + "=" * 70)
    print("RUN BACKTEST")
    print("=" * 70)

    # List available strategies
    strategies_dir = config.STRATEGIES_DIR
    if os.path.exists(strategies_dir):
        strategies = [f for f in os.listdir(strategies_dir) if f.endswith('.py') and not f.startswith('_')]
        if strategies:
            print("\nAvailable strategies:")
            for i, s in enumerate(strategies, 1):
                print(f"  {i}. {s}")
        else:
            print("\n⚠ No strategies found in strategies/ folder")
            return False
    else:
        print("\n⚠ Strategies folder not found")
        return False

    strategy_choice = input("\nEnter strategy filename or number: ").strip()

    # Handle number selection
    if strategy_choice.isdigit():
        idx = int(strategy_choice) - 1
        if 0 <= idx < len(strategies):
            strategy_file = os.path.join(strategies_dir, strategies[idx])
        else:
            print("❌ Invalid strategy number")
            return False
    else:
        strategy_file = os.path.join(strategies_dir, strategy_choice)
        if not strategy_file.endswith('.py'):
            strategy_file += '.py'

    if not os.path.exists(strategy_file):
        print(f"❌ Strategy file not found: {strategy_file}")
        return False

    # List available data files
    data_dir = config.DOWNLOADED_DATA_DIR
    if os.path.exists(data_dir):
        data_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        if data_files:
            print("\nAvailable data files:")
            for i, d in enumerate(data_files, 1):
                print(f"  {i}. {d}")
        else:
            print("\n⚠ No data files found. Fetch data first (option 1)")
            return False
    else:
        print("\n⚠ Data folder not found")
        return False

    data_choice = input("\nEnter data filename or number: ").strip()

    # Handle number selection
    if data_choice.isdigit():
        idx = int(data_choice) - 1
        if 0 <= idx < len(data_files):
            data_file = os.path.join(data_dir, data_files[idx])
        else:
            print("❌ Invalid data file number")
            return False
    else:
        data_file = os.path.join(data_dir, data_choice)
        if not data_file.endswith('.csv'):
            data_file += '.csv'

    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        return False

    try:
        runner = BacktestRunner()
        results = runner.run_backtest_from_file(strategy_file, data_file)

        if results:
            print("\n✅ Backtest completed!")
            return True
        else:
            print("\n❌ Backtest failed")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def complete_workflow():
    """Complete workflow: fetch + generate + backtest"""
    print("\n" + "=" * 70)
    print("COMPLETE WORKFLOW")
    print("=" * 70)

    # Step 1: Fetch data
    print("\n📊 STEP 1: Fetch Token Data")
    print("-" * 70)
    success = fetch_data_menu()
    if not success:
        print("\n❌ Workflow aborted: data fetch failed")
        return

    # Step 2: Generate strategy
    print("\n🤖 STEP 2: Generate AI Strategy")
    print("-" * 70)
    strategy_file = generate_strategy_menu()
    if not strategy_file:
        print("\n❌ Workflow aborted: strategy generation failed")
        return

    # Step 3: Run backtest
    print("\n🔬 STEP 3: Run Backtest")
    print("-" * 70)

    # Use most recent data file
    data_dir = config.DOWNLOADED_DATA_DIR
    data_files = sorted(
        [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.csv')],
        key=os.path.getmtime,
        reverse=True
    )

    if not data_files:
        print("❌ No data files found")
        return

    data_file = data_files[0]
    print(f"Using most recent data file: {os.path.basename(data_file)}")

    try:
        runner = BacktestRunner()
        results = runner.run_backtest_from_file(strategy_file, data_file)

        if results:
            print("\n" + "=" * 70)
            print("✅ WORKFLOW COMPLETED SUCCESSFULLY!")
            print("=" * 70)
        else:
            print("\n❌ Backtest failed")

    except Exception as e:
        print(f"\n❌ Error in backtest: {e}")


def batch_test_menu():
    """Batch test multiple strategies"""
    print("\n" + "=" * 70)
    print("BATCH TEST STRATEGIES")
    print("=" * 70)

    # Get data file
    data_dir = config.DOWNLOADED_DATA_DIR
    if not os.path.exists(data_dir):
        print("❌ Data folder not found")
        return

    data_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    if not data_files:
        print("❌ No data files found. Fetch data first.")
        return

    print("\nAvailable data files:")
    for i, d in enumerate(data_files, 1):
        print(f"  {i}. {d}")

    data_choice = input("\nSelect data file (number): ").strip()
    if not data_choice.isdigit():
        print("❌ Invalid choice")
        return

    idx = int(data_choice) - 1
    if not (0 <= idx < len(data_files)):
        print("❌ Invalid choice")
        return

    data_file = os.path.join(data_dir, data_files[idx])

    # Get strategies
    strategies_dir = config.STRATEGIES_DIR
    if not os.path.exists(strategies_dir):
        print("❌ Strategies folder not found")
        return

    strategy_files = [
        os.path.join(strategies_dir, f)
        for f in os.listdir(strategies_dir)
        if f.endswith('.py') and not f.startswith('_')
    ]

    if not strategy_files:
        print("❌ No strategies found")
        return

    print(f"\nFound {len(strategy_files)} strategies to test")
    confirm = input("Proceed with batch test? (y/n): ").strip().lower()

    if confirm != 'y':
        print("❌ Cancelled")
        return

    try:
        runner = BacktestRunner()
        results = runner.batch_run_strategies(strategy_files, data_file)

        print(f"\n✅ Batch test completed! {len(results)} successful backtests")

    except Exception as e:
        print(f"\n❌ Error: {e}")


def view_top_strategies():
    """View top performing strategies"""
    print("\n" + "=" * 70)
    print("TOP STRATEGIES")
    print("=" * 70)

    n = input("\nHow many top strategies to show? (default 10): ").strip()
    n = int(n) if n.isdigit() else 10

    try:
        runner = BacktestRunner()
        top = runner.get_top_strategies(n=n, sort_by='return_pct')

        if top.empty:
            print("\n⚠ No strategies found. Run some backtests first!")
            return

        print(f"\nTop {len(top)} Strategies:")
        print("-" * 70)

        for i, row in top.iterrows():
            print(f"\n{i+1}. {row['strategy_name']}")
            print(f"   Return: {row['return_pct']:.2f}%")
            print(f"   Sharpe: {row['sharpe_ratio']:.3f}")
            print(f"   Win Rate: {row['win_rate_pct']:.2f}%")
            print(f"   Max DD: {row['max_drawdown_pct']:.2f}%")

    except Exception as e:
        print(f"\n❌ Error: {e}")


def run_swarm_menu():
    """Run AI swarm for parallel strategy discovery"""
    print("\n" + "=" * 70)
    print("🚀 AI SWARM - PARALLEL STRATEGY DISCOVERY")
    print("=" * 70)

    print(f"\nSwarm Configuration:")
    print(f"  Max Threads: {config.SWARM_MAX_THREADS}")
    print(f"  Walk-Forward Analysis: {config.SWARM_WALKFORWARD_TRAIN_PCT*100:.0f}% train / {(1-config.SWARM_WALKFORWARD_TRAIN_PCT)*100:.0f}% test")
    print(f"  Multi-Token Testing: {'ENABLED' if config.SWARM_MULTI_TOKEN_TEST else 'DISABLED'}")
    print(f"  Cost Optimized: {config.SWARM_COST_OPTIMIZED}")

    print("\n⚠️  ANTI-OVERFITTING MEASURES:")
    print("  ✓ Walk-forward analysis (train/test split)")
    print("  ✓ Out-of-sample validation")
    print("  ✓ Multi-token testing (if enabled)")
    print("  ✓ Minimum walkforward ratio: 0.8")

    print("\n" + "-" * 70)

    num_ideas = input("\nHow many strategy ideas to generate? (default 5): ").strip()
    num_ideas = int(num_ideas) if num_ideas.isdigit() else 5

    print(f"\n📝 Please provide {num_ideas} strategy ideas:")
    print("   (Enter each idea on a new line, press Enter twice when done)\n")

    ideas = []
    for i in range(num_ideas):
        print(f"Idea {i+1}:")
        idea_lines = []
        empty_count = 0

        while empty_count < 2:
            line = input()
            if line:
                idea_lines.append(line)
                empty_count = 0
            else:
                empty_count += 1

        idea = '\n'.join(idea_lines)
        if idea.strip():
            ideas.append(idea.strip())
            print(f"✓ Idea {i+1} captured\n")

    if not ideas:
        print("❌ No ideas provided")
        return

    print(f"\n📊 Ready to process {len(ideas)} ideas with swarm")
    confirm = input("Start swarm? (y/n): ").strip().lower()

    if confirm != 'y':
        print("❌ Cancelled")
        return

    try:
        from src.swarm_runner import SwarmRunner

        swarm = SwarmRunner(
            max_threads=config.SWARM_MAX_THREADS,
            cost_optimized=config.SWARM_COST_OPTIMIZED
        )

        swarm.run_swarm(ideas)

        print("\n✅ Swarm completed! Check results in dashboard or CSV.")
        print(f"   Results CSV: {swarm.swarm_results_csv}")

    except Exception as e:
        print(f"\n❌ Swarm error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main CLI loop"""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    print_header()

    # Validate config
    errors = config.validate_config()
    if errors:
        print("⚠️  Configuration Errors:")
        for error in errors:
            print(f"   - {error}")
        print("\nPlease fix errors in .env file or src/config.py\n")
        sys.exit(1)

    print("✅ Configuration valid")
    print(f"📅 Date range: {config.DATE_START} to {config.DATE_END}")
    print(f"⏱  Timeframe: {config.TIMEFRAME}")
    print(f"🤖 AI Model: {config.STRATEGY_AI_MODEL}")

    while True:
        print_menu()
        choice = input("Enter choice (1-8): ").strip()

        if choice == '1':
            fetch_data_menu()
        elif choice == '2':
            generate_strategy_menu()
        elif choice == '3':
            run_backtest_menu()
        elif choice == '4':
            complete_workflow()
        elif choice == '5':
            print("\n🌐 Starting dashboard server...")
            print("Press CTRL+C to return to menu")
            try:
                run_dashboard()
            except KeyboardInterrupt:
                print("\n\n✅ Dashboard stopped")
        elif choice == '6':
            batch_test_menu()
        elif choice == '7':
            view_top_strategies()
        elif choice == '8':
            run_swarm_menu()
        elif choice == '9':
            print("\n👋 Goodbye!")
            sys.exit(0)
        else:
            print("\n❌ Invalid choice. Please enter 1-9.")

        input("\nPress Enter to continue...")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
