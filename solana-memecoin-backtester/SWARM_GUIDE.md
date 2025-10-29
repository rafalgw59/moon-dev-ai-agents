# 🚀 AI Swarm - Strategy Discovery Guide

## Overview

The **AI Swarm** is a parallel agent system that automatically discovers, tests, and validates trading strategies while preventing overfitting. It uses multiple AI agents working simultaneously to explore the strategy space efficiently and cost-effectively.

## Key Features

### 1. 🎯 **Parallel Processing**
- Run up to 5 strategies simultaneously (configurable)
- Thread-safe operations with proper locking
- Real-time progress monitoring

### 2. 🛡️ **Anti-Overfitting Measures**

#### Walk-Forward Analysis
- **Train/Test Split**: 70% training data, 30% testing data (default)
- Strategy trained on earlier data, validated on later data
- **Walk-Forward Ratio**: test_return / train_return
  - `> 0.8` = **GOOD** (low overfitting risk) ✅
  - `0.5-0.8` = **MODERATE** (some overfitting) ⚠️
  - `< 0.5` = **BAD** (likely overfitted) ❌

#### Out-of-Sample Testing
- Strategies never see the test data during development
- True performance measured on unseen data
- Only strategies that pass out-of-sample tests are saved

#### Multi-Token Validation (Optional)
- Test same strategy across multiple tokens
- Validates robustness and generalization
- Identifies strategies that work on specific assets vs. general patterns

### 3. 💰 **Cost Optimization**
- **Research Phase**: Uses DeepSeek (cheap, fast)
- **Code Generation**: Uses Claude (quality code generation)
- **Debugging**: Uses DeepSeek (cost-effective iterations)
- Estimated cost: ~$0.05-0.15 per strategy
- 10-20x cheaper than using GPT-4 for everything

### 4. 📊 **Comprehensive Results Tracking**
All results saved to CSV with:
- Initial backtest return
- Training period return
- **Out-of-sample** return (most important!)
- Walk-forward ratio
- Overfitting risk assessment
- Multi-token test results
- Full performance metrics

## Configuration

Edit `src/config.py` to customize swarm behavior:

```python
# Maximum parallel threads
SWARM_MAX_THREADS = 5  # Adjust based on API rate limits

# Walk-forward split (70% train, 30% test)
SWARM_WALKFORWARD_TRAIN_PCT = 0.7

# Multi-token testing
SWARM_MULTI_TOKEN_TEST = True
SWARM_TEST_TOKENS = [
    'So11111111111111111111111111111111111111112',  # Wrapped SOL
    # Add more tokens...
]

# Cost optimization (use cheaper models)
SWARM_COST_OPTIMIZED = True

# Quality filters (stricter than regular backtests)
SWARM_MIN_RETURN_PCT = 15.0           # Minimum 15% return
SWARM_MIN_WALKFORWARD_RATIO = 0.8     # Minimum 0.8 to avoid overfitting
SWARM_MIN_SHARPE_RATIO = 1.0          # Higher quality strategies
```

## Usage

### Option 1: Interactive CLI

```bash
python main.py
# Select option 8: "🚀 RUN AI SWARM"
```

The CLI will:
1. Show current swarm configuration
2. Ask for number of strategy ideas
3. Collect strategy ideas from you
4. Run the swarm
5. Display results

### Option 2: Programmatic

```python
from src.swarm_runner import SwarmRunner

# Strategy ideas
ideas = [
    "RSI mean reversion: buy RSI < 30, sell RSI > 70",
    "MACD momentum with volume confirmation",
    "Bollinger Band breakout with ATR stops",
    "Triple moving average crossover",
    "Stochastic RSI divergence strategy"
]

# Initialize swarm
swarm = SwarmRunner(
    max_threads=5,
    cost_optimized=True
)

# Run swarm
swarm.run_swarm(ideas)

# Results saved to: data/swarm/swarm_results.csv
```

## How It Works

### Pipeline for Each Strategy

```
┌─────────────────────────────────────────────────────────┐
│ Phase 1: AI Strategy Generation                         │
│   - Use AI to convert idea → Python backtest code      │
│   - Cost optimized: DeepSeek for research              │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 2: Initial Backtest                              │
│   - Quick test on available data                       │
│   - Early elimination of broken strategies             │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 3: Walk-Forward Analysis ⚠️ CRITICAL             │
│   - Split data: 70% train / 30% test                  │
│   - Train on early data, test on later data           │
│   - Calculate walk-forward ratio                       │
│   - Reject if ratio < 0.8 (overfitting detected!)     │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 4: Multi-Token Testing (Optional)                │
│   - Test on multiple tokens (if configured)            │
│   - Validates cross-asset performance                   │
│   - Identifies robust vs. token-specific strategies    │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 5: Final Evaluation & Saving                     │
│   - Check against all quality filters                  │
│   - Save only strategies that pass ALL checks          │
│   - Store comprehensive results in CSV                 │
└─────────────────────────────────────────────────────────┘
```

## Understanding Walk-Forward Ratio

The **walk-forward ratio** is the key anti-overfitting metric:

```
Walk-Forward Ratio = Test Return / Train Return
```

### Examples:

**Example 1: Good Strategy (Low Overfitting)**
- Training Return: 20%
- Testing Return: 18%
- Walk-Forward Ratio: 18/20 = **0.90** ✅
- **Assessment**: Strategy generalizes well to new data

**Example 2: Overfitted Strategy**
- Training Return: 50%
- Testing Return: 10%
- Walk-Forward Ratio: 10/50 = **0.20** ❌
- **Assessment**: Strategy "memorized" training data, fails on new data

**Example 3: Robust Strategy**
- Training Return: 15%
- Testing Return: 16%
- Walk-Forward Ratio: 16/15 = **1.07** ✅✅
- **Assessment**: Actually performs BETTER on test data (rare but excellent!)

## Interpreting Results

### Results CSV Columns

```csv
timestamp,thread_id,strategy_name,
initial_return_%,train_return_%,test_return_%,
walkforward_ratio,overfitting_risk,
sharpe_ratio,sortino_ratio,max_drawdown_%,
num_trades,win_rate_%,
multi_token_avg_%,multi_token_passed_count
```

### What to Look For:

✅ **GOOD Strategies:**
- Walk-forward ratio > 0.8
- Test return meets minimum (15%)
- Sharpe ratio > 1.0
- Reasonable drawdown (< 30%)
- If multi-token tested: avg > 10%, passed_count > 0

⚠️ **QUESTIONABLE Strategies:**
- Walk-forward ratio 0.5-0.8
- High train return, low test return
- Review manually before using

❌ **REJECT:**
- Walk-forward ratio < 0.5
- Zero trades on test data
- Test return negative
- Not saved automatically

## Cost Breakdown

Estimated costs per strategy (using cost optimization):

| Phase | Model | Tokens | Cost |
|-------|-------|--------|------|
| Research | DeepSeek | ~2K | $0.002 |
| Code Gen | Claude | ~4K | $0.048 |
| Debug (avg 2 iterations) | DeepSeek | ~4K | $0.004 |
| **Total per strategy** | | | **~$0.054** |

**For 100 strategies**: ~$5.40 with cost optimization
**Without optimization**: ~$54 (using GPT-4 for everything)

**Savings**: ~90% cost reduction

## Advanced Tips

### 1. Start Small
```bash
# First run: test 2-3 ideas to validate setup
python main.py → Option 8 → Enter 2 ideas
```

### 2. Use Good Data
- Fetch data for at least 6 months
- Use appropriate timeframe (15min-1hour recommended)
- More data = better train/test split

### 3. Diversify Ideas
Mix different strategy types:
- Mean reversion (RSI, Bollinger)
- Trend following (MA crossovers)
- Momentum (MACD, Stochastic)
- Breakouts (Support/resistance)

### 4. Interpret Walk-Forward Conservatively
- Ratio 0.8-0.9: Good, conservative estimate
- Ratio 0.9-1.0: Excellent generalization
- Ratio > 1.0: Be cautious, may be lucky
- Ratio < 0.8: Likely overfitted

### 5. Multi-Token Validation is Powerful
If a strategy works on:
- SOL, BTC, ETH → Robust, general strategy
- Only SOL → Token-specific, less reliable
- No other tokens → Likely overfitted

### 6. Check Results CSV Regularly
```python
import pandas as pd

df = pd.read_csv('data/swarm/swarm_results.csv')

# Filter for good strategies
good = df[
    (df['walkforward_ratio'] > 0.8) &
    (df['test_return_%'] > 15) &
    (df['sharpe_ratio'] > 1.0)
]

print(f"Found {len(good)} robust strategies")
```

## Troubleshooting

### "No data files found"
➡️ Run option 1 first to fetch token data

### "All threads failing"
➡️ Check API keys in `.env` file
➡️ Reduce `SWARM_MAX_THREADS` if hitting rate limits

### "All strategies rejected (high overfitting)"
➡️ Normal! Overfitting is common
➡️ Try simpler strategy ideas
➡️ Reduce filters temporarily to see what's happening

### "Swarm running very slow"
➡️ Reduce `SWARM_MAX_THREADS`
➡️ Use shorter data periods for testing
➡️ Enable `SWARM_COST_OPTIMIZED = True`

## Best Practices

### DO:
✅ Start with 2-5 strategies to test the system
✅ Use walk-forward ratio as primary filter
✅ Validate on multiple tokens when possible
✅ Review saved strategies manually
✅ Use cost optimization for exploration
✅ Document your best strategy ideas

### DON'T:
❌ Trust strategies with WF ratio < 0.8
❌ Skip the validation steps
❌ Use only training period returns
❌ Over-optimize on one token
❌ Ignore risk metrics (drawdown, Sharpe)
❌ Deploy without paper trading first

## Example Session

```bash
$ python main.py

🚀 SOLANA MEMECOIN BACKTESTER
==================================================
✅ Configuration valid
📅 Date range: 2024-01-01 to 2024-12-31
⏱  Timeframe: 15min
🤖 AI Model: anthropic

What would you like to do?

8. 🚀 RUN AI SWARM (parallel strategy discovery with anti-overfitting)

Enter choice (1-9): 8

🚀 AI SWARM - PARALLEL STRATEGY DISCOVERY
==================================================

Swarm Configuration:
  Max Threads: 5
  Walk-Forward Analysis: 70% train / 30% test
  Multi-Token Testing: ENABLED
  Cost Optimized: True

⚠️  ANTI-OVERFITTING MEASURES:
  ✓ Walk-forward analysis (train/test split)
  ✓ Out-of-sample validation
  ✓ Multi-token testing (if enabled)
  ✓ Minimum walkforward ratio: 0.8

----------------------------------------------------------------------

How many strategy ideas to generate? (default 5): 3

📝 Please provide 3 strategy ideas:
   (Enter each idea on a new line, press Enter twice when done)

Idea 1:
RSI mean reversion with 14-period RSI
Buy when RSI crosses below 30
Sell when RSI crosses above 70
Use 2% stop loss

✓ Idea 1 captured

[... processing ...]

🎉 SWARM COMPLETED
==================================================
Total processed: 3
Successful: 3
Failed: 0
Passed filters: 1

Results saved to: data/swarm/swarm_results.csv
==================================================
```

## Next Steps After Swarm

1. **Review Results CSV**: Look for high walk-forward ratios
2. **Check Strategies**: Review generated code in `strategies/` folder
3. **Paper Trade**: Test best strategies in paper trading
4. **Monitor Performance**: Track live vs. backtest performance
5. **Iterate**: Run swarm again with refined ideas

---

**Remember**: The swarm is a discovery tool. Always validate results, use proper risk management, and never trade with money you can't afford to lose.

**Anti-overfitting is critical**: A strategy with 50% backtest return but 0.3 walk-forward ratio is worse than one with 15% return and 0.9 walk-forward ratio.

🚀 **Happy Strategy Hunting!**
