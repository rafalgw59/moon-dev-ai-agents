# Strategy: MACD + SMA Trend Following
# Description: Combine MACD momentum with SMA trend filter
# Timeframe: 1hour - 4hour

from backtesting import Backtest, Strategy
import pandas as pd
import talib


class MACDSMATrend(Strategy):
    """
    MACD momentum strategy with SMA trend filter

    Entry Conditions:
    - MACD line crosses above signal line (bullish momentum)
    - Price is above 50-period SMA (uptrend confirmation)

    Exit Conditions:
    - MACD line crosses below signal line (bearish momentum)
    - Price crosses below 50-period SMA (trend reversal)
    """

    # Strategy parameters
    macd_fast = 12
    macd_slow = 26
    macd_signal = 9
    sma_period = 50

    def init(self):
        """Initialize indicators"""
        # MACD indicator
        self.macd_line, self.signal_line, self.macd_hist = self.I(
            talib.MACD,
            self.data.Close,
            fastperiod=self.macd_fast,
            slowperiod=self.macd_slow,
            signalperiod=self.macd_signal
        )

        # Simple Moving Average (trend filter)
        self.sma = self.I(talib.SMA, self.data.Close, timeperiod=self.sma_period)

    def next(self):
        """Execute on each candle"""
        price = self.data.Close[-1]

        # Check MACD crossover (manual logic, no backtesting.lib.crossover)
        # Bullish crossover: MACD crosses above signal
        macd_cross_up = (
            self.macd_line[-2] < self.signal_line[-2] and
            self.macd_line[-1] > self.signal_line[-1]
        )

        # Bearish crossover: MACD crosses below signal
        macd_cross_down = (
            self.macd_line[-2] > self.signal_line[-2] and
            self.macd_line[-1] < self.signal_line[-1]
        )

        # Entry: MACD bullish cross + price above SMA
        if macd_cross_up and price > self.sma[-1] and not self.position:
            self.buy(size=0.95)

        # Exit: MACD bearish cross OR price below SMA
        elif self.position:
            if macd_cross_down or price < self.sma[-1]:
                self.position.close()


if __name__ == '__main__':
    # Example usage
    print("MACD + SMA Trend Following Strategy - Example")
    print("=" * 70)

    try:
        df = pd.read_csv('data/downloaded/example_data.csv')

        # Convert datetime
        df['datetime'] = pd.to_datetime(df['datetime'])

        # Capitalize columns
        df.columns = [c.capitalize() for c in df.columns]

        # Set index
        df = df.set_index('Datetime')

        print(f"Loaded {len(df)} candles")
        print(f"Date range: {df.index[0]} to {df.index[-1]}")

        # Run backtest
        bt = Backtest(
            df,
            MACDSMATrend,
            cash=10000,
            commission=.003
        )

        print("\nRunning backtest...")
        stats = bt.run()

        print("\n" + "=" * 70)
        print("BACKTEST RESULTS")
        print("=" * 70)
        print(stats)

        # Calculate some custom metrics
        total_return = stats['Return [%]']
        buy_hold = stats['Buy & Hold Return [%]']
        outperformance = total_return - buy_hold

        print(f"\nOutperformance vs Buy & Hold: {outperformance:.2f}%")

    except FileNotFoundError:
        print("Data file not found. Please download data first using data_fetcher.py")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
