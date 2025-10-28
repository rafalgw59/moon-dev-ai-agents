# 🚀 Quick Start Guide

Get started with Solana Memecoin Backtester in 5 minutes!

## Step 1: Setup Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit and add your API keys
nano .env
```

Required keys:
- `MORALIS_API_KEY` - Get from https://moralis.io/
- `ANTHROPIC_KEY` - Get from https://console.anthropic.com/ (or use OpenAI/DeepSeek)

## Step 2: Install Dependencies

```bash
# Make sure you're in the tflow conda environment
conda activate tflow

# Install Python packages
pip install -r requirements.txt
```

## Step 3: Configure Settings (Optional)

Edit `src/config.py` to customize:

```python
DATE_START = '2024-01-01'
DATE_END = '2024-12-31'
TIMEFRAME = '15min'
INITIAL_CAPITAL = 10000
```

## Step 4: Run the Tool

### Option A: Interactive CLI (Recommended)

```bash
python main.py
```

This gives you a menu with all features:
1. Fetch token data
2. Generate AI strategy
3. Run backtest
4. Complete workflow
5. View dashboard
6. Batch test
7. View top strategies

### Option B: Individual Components

**Test Moralis API:**
```bash
cd src
python data_fetcher.py
```

**Test AI Strategy Builder:**
```bash
cd src
python strategy_builder.py
```

**Test Backtest Runner:**
```bash
cd src
python backtest_runner.py
```

**Start Dashboard:**
```bash
cd src
python dashboard.py
# Open http://localhost:8002
```

## Step 5: Your First Backtest

### Quick Example Workflow:

```python
from src.data_fetcher import MoralisDataFetcher
from src.backtest_runner import BacktestRunner

# 1. Fetch data for Wrapped SOL
fetcher = MoralisDataFetcher()
df = fetcher.get_ohlcv_data(
    token_address='So11111111111111111111111111111111111111112',
    date_start='2024-01-01',
    date_end='2024-01-31',
    timeframe='1hour',
    save_to_csv=True
)

# 2. Run example strategy
runner = BacktestRunner()
results = runner.run_backtest_from_file(
    strategy_file='strategies/example_rsi_strategy.py',
    data_file='data/downloaded/So111111_2024-01-01_to_2024-01-31_1hour.csv'
)

# 3. View results in dashboard
# python src/dashboard.py
```

## Common Token Addresses (Solana)

- Wrapped SOL: `So11111111111111111111111111111111111111112`
- USDC: `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`
- USDT: `Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB`

Find more on Solscan.io or Birdeye.so

## Troubleshooting

### "Moralis API key not provided"
➡️ Check your `.env` file has `MORALIS_API_KEY=your_key_here`

### "TA-Lib import error"
➡️ Install TA-Lib C library first (see README.md Installation section)

### "No data returned"
➡️ Verify token address is correct and has trading history in your date range

### Dashboard shows no results
➡️ Run some backtests first, check that they pass the filters in config.py

## Next Steps

1. ✅ Review example strategies in `strategies/` folder
2. ✅ Generate your own strategy with AI (`python main.py` → option 2)
3. ✅ Customize config.py for your needs
4. ✅ Batch test multiple strategies
5. ✅ Analyze results in the dashboard

## Tips

- Start with small date ranges (1 week) to test setup
- Use 1hour or 4hour timeframes for faster fetching
- Adjust filter thresholds in config.py based on your goals
- Save profitable strategies and iterate!

## Getting Help

- Check the full README.md for detailed documentation
- Review source code comments in src/ folder
- Test each component individually if issues arise

---

**Happy backtesting! 🚀**
