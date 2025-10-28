# Strategy: RSI Mean Reversion
# Description: Buy oversold, sell overbought using RSI indicator
# Timeframe: 15min - 1hour

from backtesting import Backtest, Strategy
import pandas as pd
import talib


class RSIMeanReversion(Strategy):
    """
    Simple RSI mean reversion strategy

    Entry: RSI < 30 (oversold)
    Exit: RSI > 70 (overbought) OR price drops 2% below entry
    """

    # Strategy parameters (can be optimized)
    rsi_period = 14
    oversold_level = 30
    overbought_level = 70
    stop_loss_pct = 0.02

    def init(self):
        """Initialize indicators"""
        # Calculate RSI using talib (wrapped in self.I())
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)

    def next(self):
        """Execute on each candle"""
        # Entry: RSI crosses below oversold level
        if self.rsi[-1] < self.oversold_level and not self.position:
            # Buy with full capital (size=1 means 100% of available capital)
            self.buy(size=0.95)  # 95% to leave buffer

        # Exit: RSI crosses above overbought level
        elif self.position and self.rsi[-1] > self.overbought_level:
            self.position.close()

        # Stop loss: 2% below entry price
        elif self.position:
            entry_price = self.position.entry_price
            current_price = self.data.Close[-1]

            if current_price < entry_price * (1 - self.stop_loss_pct):
                self.position.close()


if __name__ == '__main__':
    # Example usage - load data and run backtest
    print("RSI Mean Reversion Strategy - Example")
    print("=" * 70)

    # Load your OHLCV data
    # Replace 'data.csv' with your actual data file
    try:
        df = pd.read_csv('data/downloaded/example_data.csv')

        # Convert datetime column
        df['datetime'] = pd.to_datetime(df['datetime'])

        # Capitalize column names (backtesting.py requirement)
        df.columns = [c.capitalize() for c in df.columns]

        # Set datetime as index
        df = df.set_index('Datetime')

        print(f"Loaded {len(df)} candles")
        print(f"Date range: {df.index[0]} to {df.index[-1]}")

        # Run backtest
        bt = Backtest(
            df,
            RSIMeanReversion,
            cash=10000,
            commission=.003  # 0.3%
        )

        print("\nRunning backtest...")
        stats = bt.run()

        print("\n" + "=" * 70)
        print("BACKTEST RESULTS")
        print("=" * 70)
        print(stats)

        # Optional: plot results (requires matplotlib)
        # bt.plot()

    except FileNotFoundError:
        print("Data file not found. Please download data first using data_fetcher.py")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
