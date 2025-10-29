"""
Configuration file for Solana Memecoin Backtester
Edit these parameters to customize your backtesting setup
"""

import os
from datetime import datetime, timedelta

# ============================================================================
# API KEYS (loaded from .env file)
# ============================================================================
MORALIS_API_KEY = os.getenv('MORALIS_API_KEY', '')
ANTHROPIC_KEY = os.getenv('ANTHROPIC_KEY', '')
OPENAI_KEY = os.getenv('OPENAI_KEY', '')
DEEPSEEK_KEY = os.getenv('DEEPSEEK_KEY', '')

# ============================================================================
# DATA FETCHING PARAMETERS (EASY TO CHANGE)
# ============================================================================

# Date range for backtesting
DATE_START = '2024-01-01'  # Format: YYYY-MM-DD
DATE_END = '2024-12-31'    # Format: YYYY-MM-DD or 'today' for current date

# Timeframe options: '1min', '5min', '15min', '30min', '1hour', '4hour', '1day'
TIMEFRAME = '15min'

# Default token addresses to backtest (Solana memecoin addresses)
DEFAULT_TOKENS = [
    # Add your token addresses here
    # Example: 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'
]

# Maximum number of candles to fetch per request (Moralis limit)
MAX_CANDLES_PER_REQUEST = 1000

# ============================================================================
# BACKTESTING PARAMETERS
# ============================================================================

# Initial capital for backtests
INITIAL_CAPITAL = 10000  # USD

# Commission/fees per trade (as decimal, e.g., 0.001 = 0.1%)
COMMISSION = 0.003  # 0.3% (typical for DEX)

# Slippage simulation (as decimal)
SLIPPAGE = 0.001  # 0.1%

# ============================================================================
# AI STRATEGY BUILDER SETTINGS
# ============================================================================

# Which AI model to use for strategy generation
# Options: 'anthropic', 'openai', 'deepseek'
STRATEGY_AI_MODEL = 'anthropic'

# Model-specific settings
AI_MODELS = {
    'anthropic': {
        'model': 'claude-3-5-sonnet-20241022',
        'max_tokens': 4000,
        'temperature': 0.7
    },
    'openai': {
        'model': 'gpt-4o',
        'max_tokens': 4000,
        'temperature': 0.7
    },
    'deepseek': {
        'model': 'deepseek-reasoner',
        'max_tokens': 8000,
        'temperature': 0.7
    }
}

# ============================================================================
# BACKTEST FILTERING & SAVING
# ============================================================================

# Minimum metrics to save a backtest result
MIN_RETURN_PCT = 10.0          # Minimum return % to save
MIN_SHARPE_RATIO = 0.5         # Minimum Sharpe ratio
MIN_WIN_RATE = 45.0            # Minimum win rate %
MAX_DRAWDOWN_PCT = 30.0        # Maximum acceptable drawdown %

# Auto-save all backtests regardless of performance?
SAVE_ALL_BACKTESTS = False

# ============================================================================
# DASHBOARD SETTINGS
# ============================================================================

# Dashboard host and port
DASHBOARD_HOST = '0.0.0.0'
DASHBOARD_PORT = 8002

# Number of top strategies to highlight
TOP_STRATEGIES_COUNT = 10

# ============================================================================
# FILE PATHS (relative to project root)
# ============================================================================

# Data directories
DATA_DIR = 'data'
DOWNLOADED_DATA_DIR = os.path.join(DATA_DIR, 'downloaded')
RESULTS_DIR = os.path.join(DATA_DIR, 'results')

# Strategy directories
STRATEGIES_DIR = 'strategies'

# Results CSV file
RESULTS_CSV = os.path.join(RESULTS_DIR, 'backtest_stats.csv')

# ============================================================================
# MORALIS API ENDPOINTS
# ============================================================================

MORALIS_BASE_URL = 'https://solana-gateway.moralis.io'
MORALIS_ENDPOINTS = {
    'token_price': '/token/{address}/price',
    'token_metadata': '/token/{address}/metadata',
    'ohlcv': '/token/{address}/ohlcv',
}

# ============================================================================
# LOGGING SETTINGS
# ============================================================================

LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = True
LOG_FILE = 'backtester.log'

# ============================================================================
# SWARM SETTINGS (AI Agent Swarm for Strategy Discovery)
# ============================================================================

# Maximum parallel threads for swarm
SWARM_MAX_THREADS = 5  # Adjust based on your API rate limits

# Walk-forward analysis settings (anti-overfitting)
SWARM_WALKFORWARD_TRAIN_PCT = 0.7  # 70% training, 30% testing

# Multi-token testing (test strategies on multiple tokens)
SWARM_MULTI_TOKEN_TEST = True
SWARM_TEST_TOKENS = [
    'So11111111111111111111111111111111111111112',  # Wrapped SOL
    # Add more token addresses to test strategies across multiple assets
]

# Cost optimization
SWARM_COST_OPTIMIZED = True  # Use cheaper AI models (DeepSeek) for initial passes

# Swarm result filtering (stricter than regular backtests)
SWARM_MIN_RETURN_PCT = 15.0          # Higher bar for swarm results
SWARM_MIN_WALKFORWARD_RATIO = 0.8    # Minimum 0.8 to avoid overfitting
SWARM_MIN_SHARPE_RATIO = 1.0         # Higher quality strategies

# Rate limiting for swarm
SWARM_RATE_LIMIT_DELAY = 1.0  # Seconds between API calls per thread

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_date_range():
    """Get start and end dates as datetime objects"""
    start = datetime.strptime(DATE_START, '%Y-%m-%d')

    if DATE_END.lower() == 'today':
        end = datetime.now()
    else:
        end = datetime.strptime(DATE_END, '%Y-%m-%d')

    return start, end


def get_ai_config():
    """Get current AI model configuration"""
    return AI_MODELS.get(STRATEGY_AI_MODEL, AI_MODELS['anthropic'])


def validate_config():
    """Validate configuration settings"""
    errors = []

    if not MORALIS_API_KEY:
        errors.append("MORALIS_API_KEY not set in environment")

    if STRATEGY_AI_MODEL not in AI_MODELS:
        errors.append(f"Invalid STRATEGY_AI_MODEL: {STRATEGY_AI_MODEL}")

    if STRATEGY_AI_MODEL == 'anthropic' and not ANTHROPIC_KEY:
        errors.append("ANTHROPIC_KEY not set but model is 'anthropic'")

    if STRATEGY_AI_MODEL == 'openai' and not OPENAI_KEY:
        errors.append("OPENAI_KEY not set but model is 'openai'")

    if STRATEGY_AI_MODEL == 'deepseek' and not DEEPSEEK_KEY:
        errors.append("DEEPSEEK_KEY not set but model is 'deepseek'")

    try:
        start, end = get_date_range()
        if start >= end:
            errors.append("DATE_START must be before DATE_END")
    except ValueError as e:
        errors.append(f"Invalid date format: {e}")

    if COMMISSION < 0 or COMMISSION > 1:
        errors.append("COMMISSION must be between 0 and 1")

    if INITIAL_CAPITAL <= 0:
        errors.append("INITIAL_CAPITAL must be positive")

    # Swarm validation
    if SWARM_MAX_THREADS < 1:
        errors.append("SWARM_MAX_THREADS must be at least 1")

    if not (0 < SWARM_WALKFORWARD_TRAIN_PCT < 1):
        errors.append("SWARM_WALKFORWARD_TRAIN_PCT must be between 0 and 1")

    return errors


if __name__ == '__main__':
    """Test configuration"""
    print("=" * 60)
    print("SOLANA MEMECOIN BACKTESTER - Configuration Test")
    print("=" * 60)

    errors = validate_config()

    if errors:
        print("\nCONFIGURATION ERRORS:")
        for error in errors:
            print(f"  ❌ {error}")
    else:
        print("\n✓ Configuration is valid!")

    print("\nCurrent Settings:")
    print(f"  Date Range: {DATE_START} to {DATE_END}")
    print(f"  Timeframe: {TIMEFRAME}")
    print(f"  Initial Capital: ${INITIAL_CAPITAL:,}")
    print(f"  Commission: {COMMISSION*100}%")
    print(f"  AI Model: {STRATEGY_AI_MODEL} ({get_ai_config()['model']})")
    print(f"  Min Return to Save: {MIN_RETURN_PCT}%")
    print(f"  Dashboard Port: {DASHBOARD_PORT}")

    start, end = get_date_range()
    days = (end - start).days
    print(f"\n  Backtest Duration: {days} days")
