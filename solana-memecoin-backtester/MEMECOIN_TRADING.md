# 💰 MEMECOIN TRADING OPTIMIZATION GUIDE

## Overview

This backtester has been **optimized for Solana memecoin trading** (10k-100k MC, short-lived tokens). Memecoins require completely different parameters and strategies than traditional assets.

## Key Differences: Memecoins vs Traditional Assets

| Aspect | Traditional (BTC/ETH) | Memecoins (10k-100k MC) |
|--------|----------------------|-------------------------|
| **Lifespan** | Years | Days to weeks |
| **Timeframe** | 15min - 4hour | **1min** - 5min |
| **Data Range** | 6-12 months | **7 days** typical |
| **Volatility** | Moderate (5-15%) | Extreme (50-500%+ in hours) |
| **Liquidity** | High | Very low (wide spreads) |
| **Slippage** | 0.1% | **2-10%** |
| **Trading Style** | Swing/Position | **Scalping/Momentum** |
| **Hold Time** | Days/Weeks | **Minutes/Hours** |
| **Return Expectations** | 10-30% | **50-500%+** or -100% |

## Configuration Changes

### 1. Timeframes (Most Important!)

```python
# OLD (traditional):
TIMEFRAME = '15min'
DATE_START = '2024-01-01'
DATE_END = '2024-12-31'

# NEW (memecoin):
TIMEFRAME = '1min'          # Catch quick pumps
DATE_START = 'auto'         # Last 7 days
DATE_END = 'today'
AUTO_DAYS_BACK = 7          # Most memecoins don't last longer
```

**Why 1min?**
- Memecoins pump in **minutes**, not hours
- Example: Token goes 5x in 30 minutes, then crashes
- 15min candles miss the entire move!

### 2. Capital & Risk

```python
# OLD:
INITIAL_CAPITAL = 10000     # $10k
COMMISSION = 0.003          # 0.3%
SLIPPAGE = 0.001            # 0.1%

# NEW (memecoin):
INITIAL_CAPITAL = 1000      # $1k (smaller, high-risk plays)
COMMISSION = 0.005          # 0.5% (DEX fees + gas)
SLIPPAGE = 0.02             # 2% (low liquidity)
MAX_POSITION_SIZE_PCT = 100  # All-in OK (calculated risk)
```

**Why Higher Slippage?**
- Memecoin liquidity is **terrible**
- Buy order can move price 5-10%
- Must account for this in backtests

### 3. Performance Filters

```python
# OLD (traditional):
MIN_RETURN_PCT = 10.0       # 10% is good for BTC
MIN_SHARPE_RATIO = 1.0      # Quality over quantity
MAX_DRAWDOWN_PCT = 30.0     # Conservative

# NEW (memecoin):
MIN_RETURN_PCT = 20.0       # Memecoins must return 20%+
MIN_SHARPE_RATIO = 0.3      # Sharpe is meaningless for memecoins
MAX_DRAWDOWN_PCT = 50.0     # Volatility is extreme
MIN_WIN_RATE = 40.0         # Few big wins > many small wins
```

**Why Lower Quality Bars?**
- Sharpe Ratio assumes normal distribution (memecoins are NOT normal)
- One 10x trade covers 10 small losses
- Memecoin trading is about **asymmetric bets**

### 4. Swarm Settings

```python
# OLD:
SWARM_WALKFORWARD_TRAIN_PCT = 0.70  # 70/30 split
SWARM_MULTI_TOKEN_TEST = True       # Cross-validate
SWARM_MIN_RETURN_PCT = 15.0

# NEW (memecoin):
SWARM_WALKFORWARD_TRAIN_PCT = 0.80  # 80/20 (less data)
SWARM_MULTI_TOKEN_TEST = False      # Each memecoin is unique
SWARM_MIN_RETURN_PCT = 30.0         # Higher bar
SWARM_MIN_WALKFORWARD_RATIO = 0.7   # Lower OK (unpredictable)
```

**Why No Multi-Token Testing?**
- Each memecoin has **unique community dynamics**
- $BONK behaves differently than $WIF
- Better to validate across time on same token

## Strategy Patterns for Memecoins

### ✅ GOOD Strategies for Memecoins

#### 1. Volume Spike + Momentum
```
Entry:
- Volume > 5x average
- Price breaks 5min high
- RSI > 50 (momentum confirmed)

Exit:
- Volume drops below 2x average
- Price breaks 5min low
- OR +50% profit target
```

#### 2. Quick Scalp (1-5 minutes)
```
Entry:
- Price > VWAP
- 1min candle closes above prev high
- Fast MA crosses above slow MA

Exit:
- Take profit at +10%
- Stop loss at -5%
- Max hold time: 5 minutes
```

#### 3. Breakout + Retest
```
Entry:
- New 1hour high
- Pullback to breakout level
- Volume confirms (still elevated)

Exit:
- Break below breakout level
- OR +30% profit target
```

### ❌ BAD Strategies for Memecoins

#### Don't Use These:

1. **Long-term moving averages (50/200 MA)**
   - Memecoin probably doesn't have 200 candles of data!
   - By the time MA crosses, pump is over

2. **Complex indicators (Ichimoku, Fibonacci)**
   - Need months of data to be valid
   - Memecoins don't respect technical levels

3. **Mean reversion (buy dips)**
   - "Dip" could be -90% permanent loss
   - No bottom in memecoins, only rug pulls

4. **Long hold times (days/weeks)**
   - Most memecoins are dead in 7 days
   - Community moves to next token

## Data Fetching for Memecoins

### Auto Mode (Recommended)

```python
from src.data_fetcher import MoralisDataFetcher

fetcher = MoralisDataFetcher()

# Auto uses config defaults (last 7 days, 1min)
df = fetcher.get_ohlcv_data(
    token_address='YOUR_MEMECOIN_ADDRESS'
)
# No date_start/date_end needed!
```

### Manual Mode

```python
# For specific date range
df = fetcher.get_ohlcv_data(
    token_address='YOUR_MEMECOIN_ADDRESS',
    date_start='2025-01-20',  # Day token launched
    date_end='2025-01-27',     # 7 days later
    timeframe='1min'
)
```

### Expected Data Volume

**1min timeframe, 7 days:**
- Expected: 7 days × 24 hours × 60 min = **10,080 candles**
- Reality: ~5,000-8,000 (trading isn't 24/7, gaps exist)
- Minimum: 100 candles (config.MIN_CANDLES_REQUIRED)

## Swarm for Memecoin Discovery

### Running Swarm

```bash
python main.py
# Option 8: Run AI Swarm

# Enter memecoin-specific ideas:
```

### Good Swarm Ideas for Memecoins

```
1. "Volume explosion strategy: enter when volume is 10x average,
   exit when volume drops to 3x average, max hold 10 minutes"

2. "First pump catcher: buy on first 1min candle that closes
   20% above previous high, sell after 3 candles or -10% stop"

3. "VWAP momentum: buy when price crosses above VWAP with
   volume > 5x avg, sell on VWAP cross below or +30% profit"

4. "Breakout scalper: enter on new 15min high, exit on 5min
   low break or +15% target, 2% stop loss"

5. "Volume fade: short when volume peaks and starts declining
   while price still elevated, cover on volume surge or -20% loss"
```

### Bad Ideas for Memecoins

```
❌ "Buy when RSI < 30, sell when RSI > 70, hold for weeks"
   - Too slow, memecoin will be dead

❌ "200-day MA golden cross strategy"
   - Memecoin doesn't have 200 days of data!

❌ "Accumulate on every 10% dip, sell after 6 months"
   - This is NOT DCA into BTC, you'll lose everything

❌ "Fibonacci retracement levels with Elliott Wave confirmation"
   - Memecoins don't care about your fancy TA
```

## Walk-Forward Analysis for Memecoins

### Adjusted Split

```
Traditional: 70% train / 30% test
Memecoin:    80% train / 20% test
```

**Why?**
- Less data available (only 7 days)
- Need more data to train on quick patterns
- 20% test is still ~1.5 days (2,000 candles at 1min)

### Example:

**7 days of 1min data:**
- Total: 10,000 candles
- Train: 8,000 candles (first 5.6 days)
- Test: 2,000 candles (last 1.4 days)

**Validation:**
- Did strategy work on days 6-7 after training on days 1-5?
- Walk-forward ratio = day 6-7 return / day 1-5 return
- Ratio > 0.7 = acceptable for memecoins (they're chaotic)

## Real-World Example

### Token: $BONK-like Memecoin

**Launch Date**: January 20, 2025
**Initial MC**: 50k
**Peak MC**: 2M (40x in 3 days)
**Current MC**: 100k (crashed 95% from peak)

### Strategy That Would Work:

```python
class MemecoinMomentum(Strategy):
    def init(self):
        # 5-period MA (5 minutes at 1min candles)
        self.fast_ma = self.I(talib.SMA, self.data.Close, timeperiod=5)
        # Volume MA
        self.vol_ma = self.I(talib.SMA, self.data.Volume, timeperiod=20)

    def next(self):
        # Entry: Volume spike + momentum
        if (self.data.Volume[-1] > self.vol_ma[-1] * 5 and
            self.data.Close[-1] > self.fast_ma[-1] and
            not self.position):
            self.buy(size=1.0)  # All in

        # Exit: Volume fades or profit target
        elif self.position:
            entry_price = self.trades[-1].entry_price
            profit_pct = (self.data.Close[-1] - entry_price) / entry_price

            # Take profit at 50%
            if profit_pct > 0.50:
                self.position.close()

            # Stop loss at -10%
            elif profit_pct < -0.10:
                self.position.close()

            # Exit on volume fade
            elif self.data.Volume[-1] < self.vol_ma[-1] * 2:
                self.position.close()
```

**Results on $BONK:**
- Caught initial pump: +80% (day 1)
- Exited on volume fade: +120% total
- Avoided crash: NOT holding at -95%

### Strategy That Would Fail:

```python
# BAD: Traditional mean reversion
class BadMemecoinStrategy(Strategy):
    def init(self):
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=14)

    def next(self):
        # Buy "dip"
        if self.rsi[-1] < 30:
            self.buy()
        # Sell "overbought"
        elif self.rsi[-1] > 70 and self.position:
            self.position.close()
```

**Results on $BONK:**
- Bought "dip" at -50%: Token keeps crashing
- Never sold (RSI never reached 70 again)
- Final loss: -95%

## Tips for Success

### 1. Speed is Everything
- Use 1min data
- Quick entries (within seconds of signal)
- Even quicker exits (don't get greedy)

### 2. Volume is King
- Price without volume = fake pump
- Always confirm with volume spike
- Exit when volume fades

### 3. Profit Taking
- Set realistic targets (20-50% is great)
- Don't wait for 10x (you'll miss it)
- Partial exits: take 50% at +30%, let rest ride

### 4. Risk Management
- Stop losses are MANDATORY
- Max hold time limits (5-30 min)
- Never hold through "dips" (there's no bottom)

### 5. Avoid Emotional Traps
- Don't "believe" in the token
- No community attachment
- It's a trade, not an investment

## Common Mistakes

### ❌ Waiting for "The Perfect Entry"
- By the time you're certain, pump is over
- In memecoins, good enough > perfect

### ❌ Holding Through Corrections
- "It'll come back" - No, it won't
- 20% correction in memecoin = RUG PULL

### ❌ Using Complex Indicators
- By the time Ichimoku Cloud aligns, it's over
- Simple = fast = profitable

### ❌ Backtesting on Old Data
- Memecoin from 3 months ago is ancient history
- Only backtest on recent similar tokens

## Conclusion

**Memecoin trading is completely different from traditional trading:**

- **Speed**: 1min timeframes, quick decisions
- **Volatility**: 50% moves are normal
- **Risk**: High risk, high reward
- **Strategy**: Momentum & volume, not mean reversion
- **Timeframe**: Minutes to hours, not days to weeks

**This backtester is now optimized for these differences.**

Use `DATE_START = 'auto'` and `TIMEFRAME = '1min'` and you're ready to find strategies that actually work for memecoins!

🚀 **Good luck, and remember: Take profits, use stops, don't get rugged!**
