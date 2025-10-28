# 🚀 Solana Memecoin Backtester

An AI-powered backtesting tool for researching, building, and testing trading strategies on Solana memecoins. Features Moralis API integration for data fetching, AI strategy generation, and a beautiful web dashboard for results visualization.

## ✨ Features

- 📊 **Moralis API Integration** - Fetch real-time and historical OHLCV data for any Solana token
- 🤖 **AI Strategy Builder** - Generate trading strategies from text descriptions using Claude, GPT-4, or DeepSeek
- 🔬 **Professional Backtesting** - Powered by `backtesting.py` with TA-Lib indicators
- 📈 **Web Dashboard** - Beautiful FastAPI dashboard to view and analyze backtest results
- ⚙️ **Easy Configuration** - Simple config file for all parameters (dates, timeframes, tokens)
- 💾 **Results Tracking** - Automatic CSV storage of profitable backtests

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Fetching Token Data](#1-fetching-token-data)
  - [AI Strategy Generation](#2-ai-strategy-generation)
  - [Running Backtests](#3-running-backtests)
  - [Viewing Results](#4-viewing-results)
- [Project Structure](#project-structure)
- [API Keys Setup](#api-keys-setup)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## 🔧 Installation

### Prerequisites

- Python 3.8+
- conda (recommended) or virtualenv
- TA-Lib library

### Step 1: Activate Environment

```bash
# Use existing conda environment (recommended)
conda activate tflow

# Or create a new one
# conda create -n backtester python=3.10
# conda activate backtester
```

### Step 2: Install Dependencies

```bash
cd solana-memecoin-backtester
pip install -r requirements.txt
```

### Step 3: Install TA-Lib

TA-Lib requires separate installation:

**macOS:**
```bash
brew install ta-lib
pip install TA-Lib
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install libta-lib0-dev
pip install TA-Lib
```

**Windows:**
Download pre-built wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib

### Step 4: Setup Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your favorite editor
```

## 🚀 Quick Start

### 1. Configure Your Settings

Edit `src/config.py`:

```python
# Date range for backtesting
DATE_START = '2024-01-01'
DATE_END = '2024-12-31'

# Timeframe: '1min', '5min', '15min', '30min', '1hour', '4hour', '1day'
TIMEFRAME = '15min'

# Initial capital
INITIAL_CAPITAL = 10000

# AI model for strategy generation
STRATEGY_AI_MODEL = 'anthropic'  # or 'openai', 'deepseek'
```

### 2. Test Your Setup

```bash
# Test Moralis API connection
cd src
python data_fetcher.py

# Test AI strategy builder
python strategy_builder.py

# Test backtest runner
python backtest_runner.py
```

### 3. Fetch Token Data

```python
from src.data_fetcher import MoralisDataFetcher

fetcher = MoralisDataFetcher()

# Fetch data for a Solana token
df = fetcher.get_ohlcv_data(
    token_address='So11111111111111111111111111111111111111112',  # Wrapped SOL
    date_start='2024-01-01',
    date_end='2024-01-31',
    timeframe='15min',
    save_to_csv=True
)
```

### 4. Generate AI Strategy

```python
from src.strategy_builder import AIStrategyBuilder

builder = AIStrategyBuilder()

idea = """
Create a momentum strategy using RSI and MACD.
Entry: RSI crosses above 30 AND MACD crosses above signal line
Exit: RSI crosses above 70 OR MACD crosses below signal line
Timeframe: 15 minutes
"""

result = builder.generate_strategy(idea)
print(f"Strategy saved to: {result['code_file']}")
```

### 5. Run Backtest

```python
from src.backtest_runner import BacktestRunner

runner = BacktestRunner()

# Run backtest with downloaded data
results = runner.run_backtest_from_file(
    strategy_file='strategies/RSI_MACD_Momentum.py',
    data_file='data/downloaded/So111111_2024-01-01_to_2024-01-31_15min.csv'
)
```

### 6. View Dashboard

```bash
# Start the web dashboard
cd src
python dashboard.py
```

Open browser to: `http://localhost:8002`

## ⚙️ Configuration

All settings are in `src/config.py`:

### Data Fetching Parameters

```python
DATE_START = '2024-01-01'  # Start date (YYYY-MM-DD)
DATE_END = 'today'          # End date or 'today'
TIMEFRAME = '15min'         # Candle size
```

### Backtesting Parameters

```python
INITIAL_CAPITAL = 10000     # Starting capital (USD)
COMMISSION = 0.003          # 0.3% per trade
SLIPPAGE = 0.001            # 0.1% slippage
```

### AI Strategy Builder

```python
STRATEGY_AI_MODEL = 'anthropic'  # AI provider

AI_MODELS = {
    'anthropic': {
        'model': 'claude-3-5-sonnet-20241022',
        'max_tokens': 4000,
        'temperature': 0.7
    }
}
```

### Result Filtering

```python
MIN_RETURN_PCT = 10.0       # Minimum return % to save
MIN_SHARPE_RATIO = 0.5      # Minimum Sharpe ratio
MIN_WIN_RATE = 45.0         # Minimum win rate %
MAX_DRAWDOWN_PCT = 30.0     # Maximum drawdown %
SAVE_ALL_BACKTESTS = False  # Save all regardless of filters
```

## 📖 Usage

### 1. Fetching Token Data

**Interactive Mode:**

```bash
cd src
python data_fetcher.py
```

**Programmatic:**

```python
from src.data_fetcher import MoralisDataFetcher
import src.config as config

fetcher = MoralisDataFetcher()

# Single token
df = fetcher.get_ohlcv_data(
    token_address='YOUR_TOKEN_ADDRESS',
    date_start=config.DATE_START,
    date_end=config.DATE_END,
    timeframe=config.TIMEFRAME
)

# Multiple tokens
tokens = ['TOKEN_1', 'TOKEN_2', 'TOKEN_3']
results = fetcher.get_multiple_tokens(
    token_addresses=tokens,
    date_start='2024-01-01',
    date_end='2024-12-31',
    timeframe='1hour'
)
```

### 2. AI Strategy Generation

**Interactive Mode:**

```bash
cd src
python strategy_builder.py
```

**Programmatic:**

```python
from src.strategy_builder import AIStrategyBuilder

builder = AIStrategyBuilder(model_type='anthropic')

# From text description
idea = """
I want a mean reversion strategy:
- Use Bollinger Bands (20 period, 2 std dev)
- Buy when price touches lower band + RSI < 30
- Sell when price touches upper band + RSI > 70
- Stop loss at 3% below entry
"""

result = builder.generate_strategy(idea, strategy_name='BollingerMeanReversion')

# Files saved to:
print(result['research_file'])  # Text analysis
print(result['code_file'])      # Python backtest code
```

### 3. Running Backtests

**Single Strategy:**

```python
from src.backtest_runner import BacktestRunner

runner = BacktestRunner()

# Option 1: Use existing data file
results = runner.run_backtest_from_file(
    strategy_file='strategies/MyStrategy.py',
    data_file='data/downloaded/token_data.csv'
)

# Option 2: Fetch data and run
results = runner.run_backtest_with_token(
    strategy_file='strategies/MyStrategy.py',
    token_address='TOKEN_ADDRESS',
    date_start='2024-01-01',
    date_end='2024-12-31',
    timeframe='15min'
)
```

**Batch Run Multiple Strategies:**

```python
import os
from src.backtest_runner import BacktestRunner

runner = BacktestRunner()

# Get all strategy files
strategy_files = [
    os.path.join('strategies', f)
    for f in os.listdir('strategies')
    if f.endswith('.py') and not f.startswith('_')
]

# Run all on same dataset
results = runner.batch_run_strategies(
    strategy_files=strategy_files,
    data_file='data/downloaded/BTC_data.csv'
)
```

### 4. Viewing Results

**Web Dashboard:**

```bash
cd src
python dashboard.py
```

Then open: `http://localhost:8002`

**Programmatic:**

```python
from src.backtest_runner import BacktestRunner
import pandas as pd

runner = BacktestRunner()

# Get top 10 strategies by return
top_strategies = runner.get_top_strategies(n=10, sort_by='return_pct')
print(top_strategies)

# Read results CSV directly
results_df = pd.read_csv('data/results/backtest_stats.csv')
print(results_df.head())
```

## 📁 Project Structure

```
solana-memecoin-backtester/
├── src/
│   ├── config.py              # All configuration settings
│   ├── data_fetcher.py        # Moralis API integration
│   ├── strategy_builder.py    # AI strategy generator
│   ├── backtest_runner.py     # Backtest execution engine
│   └── dashboard.py           # FastAPI web dashboard
├── strategies/
│   ├── example_rsi_strategy.py
│   └── example_macd_sma_strategy.py
├── data/
│   ├── downloaded/            # OHLCV data from Moralis
│   └── results/
│       └── backtest_stats.csv # All backtest results
├── static/
│   └── css/
│       └── dashboard.css      # Dashboard styling
├── templates/
│   └── dashboard.html         # Dashboard HTML template
├── requirements.txt
├── .env.example
└── README.md
```

## 🔑 API Keys Setup

### Moralis API (Required)

1. Go to https://moralis.io/
2. Sign up for free account
3. Create new project
4. Copy API key to `.env`:

```env
MORALIS_API_KEY=your_key_here
```

### Anthropic Claude (Recommended)

1. Go to https://console.anthropic.com/
2. Create account and add billing
3. Generate API key
4. Add to `.env`:

```env
ANTHROPIC_KEY=your_key_here
```

### OpenAI (Alternative)

1. Go to https://platform.openai.com/
2. Create account and add credits
3. Generate API key
4. Add to `.env`:

```env
OPENAI_KEY=your_key_here
```

### DeepSeek (Cost-Effective Alternative)

1. Go to https://platform.deepseek.com/
2. Sign up and add credits
3. Generate API key
4. Add to `.env`:

```env
DEEPSEEK_KEY=your_key_here
```

## 💡 Examples

### Example 1: Complete Workflow

```python
from src.data_fetcher import MoralisDataFetcher
from src.strategy_builder import AIStrategyBuilder
from src.backtest_runner import BacktestRunner

# 1. Fetch data
fetcher = MoralisDataFetcher()
df = fetcher.get_ohlcv_data(
    token_address='So11111111111111111111111111111111111111112',
    date_start='2024-01-01',
    date_end='2024-03-31',
    timeframe='1hour'
)

# 2. Generate strategy
builder = AIStrategyBuilder()
strategy = builder.generate_strategy(
    idea_text="Simple RSI mean reversion with 14 period RSI",
    strategy_name="RSI_Simple"
)

# 3. Run backtest
runner = BacktestRunner()
results = runner.run_backtest_from_file(
    strategy_file=strategy['code_file'],
    data_file='data/downloaded/So111111_2024-01-01_to_2024-03-31_1hour.csv'
)

# 4. Check results
if results and results['passed_filters']:
    print(f"✅ Strategy passed! Return: {results['return_pct']:.2f}%")
else:
    print("❌ Strategy didn't meet criteria")
```

### Example 2: Batch Test Multiple Tokens

```python
from src.data_fetcher import MoralisDataFetcher
from src.backtest_runner import BacktestRunner

# List of tokens to test
tokens = [
    'So11111111111111111111111111111111111111112',  # Wrapped SOL
    # Add more token addresses...
]

fetcher = MoralisDataFetcher()
runner = BacktestRunner()

# Fetch data for all tokens
token_data = fetcher.get_multiple_tokens(
    token_addresses=tokens,
    date_start='2024-01-01',
    date_end='2024-12-31',
    timeframe='15min'
)

# Run same strategy on all tokens
for token, df in token_data.items():
    print(f"\nTesting {token[:8]}...")
    # Save temporary CSV
    csv_path = f'data/downloaded/{token[:8]}_temp.csv'
    df.to_csv(csv_path, index=False)

    # Run backtest
    results = runner.run_backtest_from_file(
        strategy_file='strategies/example_rsi_strategy.py',
        data_file=csv_path
    )
```

## 🐛 Troubleshooting

### Issue: "Moralis API key not provided"

**Solution:** Make sure you've created `.env` file and added your `MORALIS_API_KEY`

### Issue: "TA-Lib import error"

**Solution:** TA-Lib requires C library installation. See [Installation](#installation) section.

### Issue: "No data returned for token"

**Solutions:**
- Check token address is correct (Solana mainnet address)
- Verify date range has trading activity
- Check Moralis API quota/limits

### Issue: "Strategy class not found in file"

**Solution:** Make sure your strategy:
- Inherits from `backtesting.Strategy`
- Is not named just "Strategy"
- Has both `init()` and `next()` methods

### Issue: Dashboard shows "No backtest results"

**Solution:**
- Run some backtests first
- Check `data/results/backtest_stats.csv` exists
- Verify backtests passed the filters in `config.py`

## 📊 Dashboard Features

The web dashboard (`http://localhost:8002`) provides:

- **Summary Cards** - Total backtests, pass rate, average metrics
- **Sortable Table** - All backtest results with key statistics
- **Filtering** - Search by strategy/token, filter by pass/fail
- **Auto-refresh** - Updates every 30 seconds
- **Visual Indicators** - Color-coded positive/negative returns

## 🎯 Tips for Best Results

1. **Start with small date ranges** - Test your setup with 1 week of data first
2. **Use appropriate timeframes** - Lower timeframes (1min, 5min) = more data, slower fetching
3. **Test strategies incrementally** - Generate one strategy, test it, refine before batch runs
4. **Monitor API quotas** - Moralis has rate limits, add delays between requests
5. **Adjust filter thresholds** - Tune `MIN_RETURN_PCT`, `MIN_SHARPE_RATIO` based on your goals
6. **Use version control** - Git track your custom strategies and configs

## 🤝 Contributing

This is a personal project forked from the moon-dev-ai-agents repository. Feel free to modify and adapt for your own use.

## ⚠️ Disclaimer

This tool is for educational and research purposes only. Backtested results do not guarantee future performance. Cryptocurrency trading carries substantial risk of loss. Only trade with capital you can afford to lose.

## 📝 License

Based on the moon-dev-ai-agents project. For educational use only.

---

**Happy Backtesting! 🚀**

For questions or issues, check the [Troubleshooting](#troubleshooting) section or review the source code comments.
