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
# DATA FETCHING PARAMETERS (MEMECOIN OPTIMIZED)
# ============================================================================

# Date range for backtesting - MEMECOIN DEFAULT: SHORT PERIODS
# Most memecoins are short-lived (days to weeks), so we use recent data
DATE_START = 'auto'  # 'auto' = last 7 days, or specify 'YYYY-MM-DD'
DATE_END = 'today'   # 'today' for current date

# AUTO DATE CALCULATION FOR MEMECOINS
AUTO_DAYS_BACK = 7  # For memecoins: 7 days is typical lifespan (10k-100k MC)

# Timeframe options: '1min', '5min', '15min', '30min', '1hour', '4hour', '1day'
# MEMECOIN DEFAULT: 1min for quick moves and pumps
TIMEFRAME = '1min'

# Memecoin-specific timeframes for different strategies
TIMEFRAME_SCALP = '1min'   # For catching quick pumps (minutes)
TIMEFRAME_MOMENTUM = '5min'    # For momentum trades (hours)
TIMEFRAME_SWING = '15min'      # For longer holds (days - rare for memecoins)

# Default token addresses to backtest (Solana memecoin addresses)
# Focus on: 10k-100k MC, recent launches, high volume
DEFAULT_TOKENS = [
    # Add your memecoin addresses here
    # Example: 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'
]

# Maximum number of candles to fetch per request (Moralis limit)
MAX_CANDLES_PER_REQUEST = 1000

# Memecoin data validation
MIN_CANDLES_REQUIRED = 100  # Need at least 100 candles (1.7 hours at 1min)
MAX_DAYS_FOR_MEMECOIN = 30  # Don't fetch more than 30 days for memecoins

# ============================================================================
# BACKTESTING PARAMETERS (MEMECOIN OPTIMIZED)
# ============================================================================

# Initial capital for backtests
INITIAL_CAPITAL = 1000  # USD - smaller size for memecoins (high risk)

# Commission/fees per trade (as decimal, e.g., 0.001 = 0.1%)
# MEMECOIN: Higher fees due to DEX + volatility
COMMISSION = 0.005  # 0.5% (Raydium/Jupiter typical with slippage)

# Slippage simulation (as decimal)
# MEMECOIN: Much higher slippage due to low liquidity
SLIPPAGE = 0.02  # 2% (can be 5-10% during pumps!)

# Memecoin-specific risk parameters
MAX_POSITION_SIZE_PCT = 100  # Can go all-in on memecoins (high risk/reward)
MIN_TRADE_SIZE_USD = 50      # Minimum $50 per trade

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
# BACKTEST FILTERING & SAVING (MEMECOIN ADJUSTED)
# ============================================================================

# Minimum metrics to save a backtest result
# MEMECOIN: Higher returns expected due to volatility
MIN_RETURN_PCT = 20.0          # Minimum 20% return (memecoins are high risk/reward)
MIN_SHARPE_RATIO = 0.3         # Lower Sharpe OK (memecoins are volatile)
MIN_WIN_RATE = 40.0            # Lower win rate OK (big wins, many small losses)
MAX_DRAWDOWN_PCT = 50.0        # Higher drawdown acceptable (volatile assets)

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
# SWARM SETTINGS (MEMECOIN OPTIMIZED - AI Agent Swarm for Strategy Discovery)
# ============================================================================

# Maximum parallel threads for swarm
SWARM_MAX_THREADS = 5  # Adjust based on your API rate limits

# Walk-forward analysis settings (anti-overfitting)
# MEMECOIN: More aggressive split since data is limited
SWARM_WALKFORWARD_TRAIN_PCT = 0.80  # 80% training, 20% testing (less data available)

# Multi-token testing (test strategies on multiple memecoins)
SWARM_MULTI_TOKEN_TEST = False  # Disable for memecoins (each is unique)
SWARM_TEST_TOKENS = [
    # Memecoins are too unique to cross-validate
    # Each has different community, holders, patterns
    # Better to test on same token across time
]

# Cost optimization
SWARM_COST_OPTIMIZED = True  # Use cheaper AI models (DeepSeek) for initial passes

# Swarm result filtering (MEMECOIN ADJUSTED)
SWARM_MIN_RETURN_PCT = 30.0          # Higher bar for memecoins (30%+ expected)
SWARM_MIN_WALKFORWARD_RATIO = 0.7    # Lower ratio OK (memecoins are unpredictable)
SWARM_MIN_SHARPE_RATIO = 0.5         # Lower Sharpe acceptable (high volatility)
SWARM_MIN_NUM_TRADES = 5             # At least 5 trades to validate strategy

# Rate limiting for swarm
SWARM_RATE_LIMIT_DELAY = 0.5  # Faster for memecoins (time-sensitive)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_date_range():
    """Get start and end dates as datetime objects (memecoin optimized)"""

    # Handle end date
    if DATE_END.lower() == 'today':
        end = datetime.now()
    else:
        end = datetime.strptime(DATE_END, '%Y-%m-%d')

    # Handle start date (with 'auto' for memecoins)
    if DATE_START.lower() == 'auto':
        # Auto-calculate based on AUTO_DAYS_BACK
        start = end - timedelta(days=AUTO_DAYS_BACK)
    else:
        start = datetime.strptime(DATE_START, '%Y-%m-%d')

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
