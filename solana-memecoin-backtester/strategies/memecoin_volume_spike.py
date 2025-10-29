# Strategy: Memecoin Volume Spike Momentum
# Description: Catch pumps when volume explodes with momentum confirmation
# Timeframe: 1min
# Best for: New memecoin launches, initial pump phases

from backtesting import Backtest, Strategy
import pandas as pd
import talib


class MemecoinVolumeSpike(Strategy):
    """
    Volume Spike Momentum Strategy for Memecoins

    Entry:
    - Volume > 5x the 20-period average
    - Price breaks above 5-period high
    - Fast MA (5) > Slow MA (15)

    Exit:
    - Volume drops below 2x average (pump fading)
    - Take profit at +50%
    - Stop loss at -10%
    - Max hold: 30 candles (30 minutes at 1min)
    """

    # Parameters
    vol_spike_multiplier = 5  # Volume must be 5x average
    vol_exit_multiplier = 2   # Exit when volume drops to 2x
    fast_ma_period = 5        # 5 minutes
    slow_ma_period = 15       # 15 minutes
    vol_ma_period = 20        # 20 minute volume average
    take_profit_pct = 0.50    # 50% profit target
    stop_loss_pct = 0.10      # 10% stop loss
    max_hold_candles = 30     # Max 30 minutes

    def init(self):
        """Initialize indicators"""
        # Moving averages for trend
        self.fast_ma = self.I(talib.SMA, self.data.Close, timeperiod=self.fast_ma_period)
        self.slow_ma = self.I(talib.SMA, self.data.Close, timeperiod=self.slow_ma_period)

        # Volume average
        self.vol_ma = self.I(talib.SMA, self.data.Volume, timeperiod=self.vol_ma_period)

        # Rolling high for breakout detection
        self.period_high = self.I(talib.MAX, self.data.High, timeperiod=self.fast_ma_period)

        # Track entry candle for max hold time
        self.entry_candle = 0

    def next(self):
        """Execute on each candle"""

        # Entry logic
        if not self.position:
            # Check volume spike
            volume_ratio = self.data.Volume[-1] / self.vol_ma[-1] if self.vol_ma[-1] > 0 else 0

            # Entry conditions
            if (volume_ratio > self.vol_spike_multiplier and                    # Volume spike
                self.data.Close[-1] > self.period_high[-2] and                  # Breakout
                self.fast_ma[-1] > self.slow_ma[-1] and                         # Momentum
                len(self.data) > self.slow_ma_period):                          # Have enough data

                # Enter position (all-in for memecoins)
                self.buy(size=1.0)
                self.entry_candle = len(self.data)

                print(f"🚀 ENTRY at {self.data.Close[-1]:.6f} | "
                      f"Volume: {volume_ratio:.1f}x | "
                      f"Candle: {len(self.data)}")

        # Exit logic
        elif self.position:
            entry_price = self.trades[-1].entry_price
            current_price = self.data.Close[-1]
            profit_pct = (current_price - entry_price) / entry_price

            candles_in_trade = len(self.data) - self.entry_candle
            volume_ratio = self.data.Volume[-1] / self.vol_ma[-1] if self.vol_ma[-1] > 0 else 0

            # Exit conditions
            exit_reason = None

            # Take profit
            if profit_pct >= self.take_profit_pct:
                exit_reason = f"PROFIT TARGET {profit_pct*100:.1f}%"

            # Stop loss
            elif profit_pct <= -self.stop_loss_pct:
                exit_reason = f"STOP LOSS {profit_pct*100:.1f}%"

            # Volume fade
            elif volume_ratio < self.vol_exit_multiplier:
                exit_reason = f"VOLUME FADE ({volume_ratio:.1f}x)"

            # Max hold time
            elif candles_in_trade >= self.max_hold_candles:
                exit_reason = f"MAX HOLD TIME ({candles_in_trade} candles, {profit_pct*100:.1f}%)"

            # Execute exit
            if exit_reason:
                self.position.close()
                print(f"💰 EXIT at {current_price:.6f} | {exit_reason}")


if __name__ == '__main__':
    """
    Example usage
    Replace 'memecoin_data.csv' with your actual memecoin 1min data
    """
    print("=" * 70)
    print("MEMECOIN VOLUME SPIKE MOMENTUM STRATEGY")
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
            MemecoinVolumeSpike,
            cash=1000,         # $1k (smaller size for high risk)
            commission=0.005   # 0.5% (DEX fees + slippage)
        )

        print("\n🚀 Running backtest...")
        stats = bt.run()

        print("\n" + "=" * 70)
        print("BACKTEST RESULTS")
        print("=" * 70)
        print(stats)

    except FileNotFoundError:
        print("\n❌ Data file not found")
        print("   Please run: python main.py → Option 1")
        print("   Fetch data for a memecoin with 1min timeframe")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
