# Strategy: Memecoin Quick Scalp
# Description: Ultra-fast scalping strategy for catching quick moves
# Timeframe: 1min
# Hold Time: 1-10 minutes max
# Best for: Active memecoin trading, high liquidity periods

from backtesting import Backtest, Strategy
import pandas as pd
import talib


class MemecoinQuickScalp(Strategy):
    """
    Quick Scalp Strategy for Memecoins

    Entry:
    - Price > VWAP (above average price)
    - 1min candle closes above previous high
    - RSI > 50 (momentum confirmed)
    - Volume > average

    Exit:
    - Take profit at +15% (quick scalp)
    - Stop loss at -5%
    - OR max hold of 10 candles (10 minutes)
    """

    # Parameters
    rsi_period = 14
    vol_ma_period = 20
    vwap_period = 20
    take_profit_pct = 0.15    # 15% profit target
    stop_loss_pct = 0.05      # 5% stop loss
    max_hold_candles = 10     # Max 10 minutes
    rsi_min = 50              # Minimum RSI for momentum

    def init(self):
        """Initialize indicators"""
        # RSI for momentum
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)

        # VWAP approximation (SMA of typical price)
        typical_price = (self.data.High + self.data.Low + self.data.Close) / 3
        self.vwap = self.I(talib.SMA, typical_price, timeperiod=self.vwap_period)

        # Volume average
        self.vol_ma = self.I(talib.SMA, self.data.Volume, timeperiod=self.vol_ma_period)

        # Track entry
        self.entry_candle = 0

    def next(self):
        """Execute on each candle"""

        # Need enough data
        if len(self.data) < self.vwap_period:
            return

        # Entry logic
        if not self.position:
            # Calculate conditions
            price = self.data.Close[-1]
            prev_high = self.data.High[-2]
            volume_ratio = self.data.Volume[-1] / self.vol_ma[-1] if self.vol_ma[-1] > 0 else 0

            # Entry conditions (all must be true)
            conditions = [
                price > self.vwap[-1],                    # Above VWAP
                self.data.Close[-1] > prev_high,          # Closes above prev high
                self.rsi[-1] > self.rsi_min,              # RSI shows momentum
                volume_ratio > 1.0,                       # Volume above average
                self.rsi[-1] < 80                         # Not overbought
            ]

            if all(conditions):
                # Enter (all-in for scalping)
                self.buy(size=1.0)
                self.entry_candle = len(self.data)

                print(f"⚡ SCALP ENTRY at {price:.6f} | "
                      f"RSI: {self.rsi[-1]:.1f} | "
                      f"Vol: {volume_ratio:.2f}x")

        # Exit logic
        elif self.position:
            entry_price = self.trades[-1].entry_price
            current_price = self.data.Close[-1]
            profit_pct = (current_price - entry_price) / entry_price

            candles_in_trade = len(self.data) - self.entry_candle

            # Exit conditions
            exit_reason = None

            # Take profit (quick scalp target)
            if profit_pct >= self.take_profit_pct:
                exit_reason = f"TARGET {profit_pct*100:.1f}%"

            # Stop loss (tight for scalping)
            elif profit_pct <= -self.stop_loss_pct:
                exit_reason = f"STOP {profit_pct*100:.1f}%"

            # Max hold time (exit regardless)
            elif candles_in_trade >= self.max_hold_candles:
                exit_reason = f"TIME LIMIT ({profit_pct*100:.1f}%)"

            # Price crosses below VWAP (momentum lost)
            elif current_price < self.vwap[-1]:
                exit_reason = f"VWAP CROSS ({profit_pct*100:.1f}%)"

            # RSI reverses below 50 (momentum lost)
            elif self.rsi[-1] < 45:
                exit_reason = f"RSI REVERSE ({profit_pct*100:.1f}%)"

            # Execute exit
            if exit_reason:
                self.position.close()
                print(f"💸 EXIT at {current_price:.6f} | {exit_reason}")


if __name__ == '__main__':
    """
    Example usage
    This strategy works best on 1min data with active trading
    """
    print("=" * 70)
    print("MEMECOIN QUICK SCALP STRATEGY")
    print("=" * 70)

    try:
        # Load 1min memecoin data
        df = pd.read_csv('data/downloaded/memecoin_1min.csv')

        # Process data
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.columns = [c.capitalize() for c in df.columns]
        df = df.set_index('Datetime')

        print(f"\n📊 Data loaded: {len(df)} candles")
        print(f"📅 Period: {df.index[0]} to {df.index[-1]}")

        # Run backtest (memecoin settings)
        bt = Backtest(
            df,
            MemecoinQuickScalp,
            cash=1000,         # $1k for quick scalps
            commission=0.005   # 0.5% (DEX fees)
        )

        print("\n⚡ Running backtest...")
        stats = bt.run()

        print("\n" + "=" * 70)
        print("BACKTEST RESULTS")
        print("=" * 70)
        print(stats)

        # Scalping metrics
        if stats['# Trades'] > 0:
            avg_trade_duration = stats['Avg. Trade Duration']
            print(f"\n📊 Scalping Metrics:")
            print(f"   Average trade duration: {avg_trade_duration}")
            print(f"   Win rate: {stats['Win Rate [%]']:.1f}%")
            print(f"   Total trades: {stats['# Trades']}")

    except FileNotFoundError:
        print("\n❌ Data file not found")
        print("   Please run: python main.py → Option 1")
        print("   Fetch data for a memecoin with 1min timeframe")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
