"""
FastAPI Dashboard for Backtest Results
Web interface to view and analyze backtest performance
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import os
from datetime import datetime

try:
    from . import config
except ImportError:
    import config

# Initialize FastAPI app
app = FastAPI(title="Solana Memecoin Backtester Dashboard")

# Get template and static directories
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates')
STATIC_DIR = os.path.join(os.path.dirname(__file__), '..', 'static')

# Create directories if they don't exist
os.makedirs(TEMPLATE_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, 'css'), exist_ok=True)

# Mount static files and templates
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATE_DIR)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main dashboard page"""

    # Load backtest results
    stats = load_backtest_stats()

    # Calculate summary metrics
    summary = calculate_summary(stats)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "stats": stats.to_dict('records') if not stats.empty else [],
            "summary": summary
        }
    )


@app.get("/api/stats")
async def get_stats():
    """API endpoint to get backtest statistics"""
    stats = load_backtest_stats()
    return JSONResponse(content=stats.to_dict('records'))


@app.get("/api/summary")
async def get_summary():
    """API endpoint to get summary statistics"""
    stats = load_backtest_stats()
    summary = calculate_summary(stats)
    return JSONResponse(content=summary)


@app.get("/api/top-strategies/{n}")
async def get_top_strategies(n: int = 10):
    """API endpoint to get top N strategies"""
    stats = load_backtest_stats()

    if stats.empty:
        return JSONResponse(content=[])

    # Filter passed strategies
    passed = stats[stats['passed_filters'] == True].copy()

    if passed.empty:
        return JSONResponse(content=[])

    # Sort by return and get top N
    top = passed.sort_values('return_pct', ascending=False).head(n)

    return JSONResponse(content=top.to_dict('records'))


def load_backtest_stats() -> pd.DataFrame:
    """Load backtest statistics from CSV"""

    if not os.path.exists(config.RESULTS_CSV):
        return pd.DataFrame()

    try:
        df = pd.read_csv(config.RESULTS_CSV)

        # Convert timestamp to datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])

        return df

    except Exception as e:
        print(f"Error loading stats: {e}")
        return pd.DataFrame()


def calculate_summary(stats: pd.DataFrame) -> dict:
    """Calculate summary statistics"""

    if stats.empty:
        return {
            'total_backtests': 0,
            'passed_backtests': 0,
            'unique_strategies': 0,
            'unique_tokens': 0,
            'avg_return': 0.0,
            'max_return': 0.0,
            'avg_sharpe': 0.0,
            'avg_sortino': 0.0,
            'total_trades': 0,
            'avg_win_rate': 0.0
        }

    # Filter passed backtests
    passed = stats[stats['passed_filters'] == True]

    return {
        'total_backtests': len(stats),
        'passed_backtests': len(passed),
        'unique_strategies': stats['strategy_name'].nunique(),
        'unique_tokens': stats['token_address'].nunique(),
        'avg_return': float(passed['return_pct'].mean()) if not passed.empty else 0.0,
        'max_return': float(passed['return_pct'].max()) if not passed.empty else 0.0,
        'avg_sharpe': float(passed['sharpe_ratio'].mean()) if not passed.empty else 0.0,
        'avg_sortino': float(passed['sortino_ratio'].mean()) if not passed.empty else 0.0,
        'total_trades': int(stats['num_trades'].sum()),
        'avg_win_rate': float(passed['win_rate_pct'].mean()) if not passed.empty else 0.0
    }


def run_dashboard(host: str = None, port: int = None):
    """Run the dashboard server"""
    import uvicorn

    host = host or config.DASHBOARD_HOST
    port = port or config.DASHBOARD_PORT

    print("=" * 70)
    print("SOLANA MEMECOIN BACKTESTER - Dashboard")
    print("=" * 70)
    print(f"\nStarting dashboard server...")
    print(f"  URL: http://{host}:{port}")
    print(f"  Results CSV: {config.RESULTS_CSV}")
    print(f"\nPress CTRL+C to stop the server")
    print("=" * 70)

    uvicorn.run(app, host=host, port=port)


if __name__ == '__main__':
    run_dashboard()
