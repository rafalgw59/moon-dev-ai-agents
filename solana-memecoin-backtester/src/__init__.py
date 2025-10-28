"""
Solana Memecoin Backtester
AI-powered backtesting tool for Solana memecoins
"""

__version__ = '1.0.0'
__author__ = 'Based on moon-dev-ai-agents'

from . import config
from .data_fetcher import MoralisDataFetcher
from .strategy_builder import AIStrategyBuilder
from .backtest_runner import BacktestRunner

__all__ = [
    'config',
    'MoralisDataFetcher',
    'AIStrategyBuilder',
    'BacktestRunner'
]
