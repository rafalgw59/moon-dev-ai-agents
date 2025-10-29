"""
AI-Powered Strategy Builder
Generates backtesting strategies from text descriptions using LLM
Based on RBI (Research-Based Inference) agent pattern
"""

import os
import re
from datetime import datetime
from typing import Dict, Optional

try:
    from . import config
except ImportError:
    import config


class AIStrategyBuilder:
    """Build trading strategies using AI from text descriptions"""

    def __init__(self, model_type: Optional[str] = None):
        """
        Initialize AI strategy builder

        Args:
            model_type: 'anthropic', 'openai', or 'deepseek' (default from config)
        """
        self.model_type = model_type or config.STRATEGY_AI_MODEL
        self.model_config = config.AI_MODELS.get(self.model_type)

        if not self.model_config:
            raise ValueError(f"Invalid model type: {self.model_type}")

        # Import the appropriate model client
        self.client = self._init_model()

        # Create strategies directory
        os.makedirs(config.STRATEGIES_DIR, exist_ok=True)

    def _init_model(self):
        """Initialize the AI model client"""
        if self.model_type == 'anthropic':
            import anthropic
            return anthropic.Anthropic(api_key=config.ANTHROPIC_KEY)

        elif self.model_type == 'openai':
            import openai
            return openai.OpenAI(api_key=config.OPENAI_KEY)

        elif self.model_type == 'deepseek':
            import openai
            client = openai.OpenAI(
                api_key=config.DEEPSEEK_KEY,
                base_url="https://api.deepseek.com"
            )
            return client

        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")

    def generate_strategy(self, idea_text: str, strategy_name: Optional[str] = None) -> Dict[str, str]:
        """
        Generate a backtesting strategy from text description

        Args:
            idea_text: Trading strategy description (can be from video transcript, PDF, or raw text)
            strategy_name: Optional custom name for strategy (auto-generated if None)

        Returns:
            Dictionary with:
                - 'name': Strategy name
                - 'research': Strategy analysis/explanation
                - 'code': Python backtesting code
                - 'filepath': Path to saved strategy file
        """
        print("=" * 70)
        print("AI STRATEGY BUILDER")
        print("=" * 70)

        # Phase 1: Research - Extract strategy logic
        print("\nPhase 1: Analyzing strategy idea...")
        research = self._research_phase(idea_text)

        # Extract strategy name from research
        if not strategy_name:
            strategy_name = self._extract_strategy_name(research)

        print(f"  Strategy Name: {strategy_name}")

        # Phase 2: Generate backtest code
        print("\nPhase 2: Generating backtest code...")
        code = self._backtest_phase(research, strategy_name)

        # Phase 3: Clean up code (remove backtesting.lib dependencies)
        print("\nPhase 3: Optimizing code for pandas-ta/talib...")
        code = self._cleanup_code(code)

        # Save files
        research_file = self._save_research(strategy_name, research)
        code_file = self._save_code(strategy_name, code)

        print(f"\n✓ Strategy generated successfully!")
        print(f"  Research: {research_file}")
        print(f"  Code: {code_file}")

        return {
            'name': strategy_name,
            'research': research,
            'code': code,
            'research_file': research_file,
            'code_file': code_file
        }

    def _research_phase(self, idea_text: str) -> str:
        """Phase 1: Analyze trading idea and extract strategy logic"""

        system_prompt = """You are a professional quantitative trading analyst specializing in HIGH-VOLATILITY MEMECOIN TRADING on Solana.

CRITICAL CONTEXT - MEMECOIN CHARACTERISTICS:
- Timeframe: 1min to 5min (memecoins pump in MINUTES, not hours)
- Lifespan: Days to weeks (most don't last beyond 7 days)
- Volatility: Extreme (50-500% moves in hours)
- Liquidity: Low (2-10% slippage is normal)
- Hold time: Minutes to hours (NOT days/weeks)
- Risk/Reward: Asymmetric (one 10x covers many losses)

AVOID THESE FOR MEMECOINS:
❌ Long-term MAs (50/200 period) - token won't have that much data
❌ Complex indicators (Ichimoku, Fibonacci) - too slow
❌ Mean reversion (buying dips) - dips can be -90% permanent
❌ Long hold times - community moves to next token

PREFER THESE FOR MEMECOINS:
✅ Volume-based signals (volume > 5x average)
✅ Short-period indicators (5-20 periods max)
✅ Momentum strategies (catch the pump)
✅ Quick exits (profit targets + stops)
✅ Time-based exits (max hold 5-30 minutes)

Extract and organize:
1. STRATEGY_NAME: A concise, descriptive name
2. INDICATORS: List indicators (use SHORT periods: 5-20 max)
3. ENTRY_CONDITIONS: Precise conditions (must include volume check)
4. EXIT_CONDITIONS: Precise conditions (profit target + stop loss + time limit)
5. RISK_MANAGEMENT: Aggressive stops (5-10%), big targets (30-100%+)
6. TIMEFRAME: 1min or 5min ONLY (memecoins are fast)
7. MAX_HOLD_TIME: Minutes, not hours (e.g., "5 minutes", "30 minutes")

Be specific and quantitative. Focus on SPEED and VOLUME."""

        user_prompt = f"""Analyze this trading strategy idea and extract the components:

{idea_text}

Provide a structured analysis with all key details."""

        response = self._call_llm(system_prompt, user_prompt)
        return response

    def _backtest_phase(self, research: str, strategy_name: str) -> str:
        """Phase 2: Generate backtesting.py compatible code"""

        system_prompt = """You are an expert Python developer specializing in backtesting.py library for MEMECOIN TRADING.

MEMECOIN-SPECIFIC REQUIREMENTS:
⚡ SHORT PERIODS: Use 5-20 period indicators MAX (not 50/200)
⚡ VOLUME CHECKS: Always include volume validation
⚡ QUICK EXITS: Implement profit targets (30-100%+) AND stop losses (5-10%)
⚡ TIME LIMITS: Add max hold time (use candle counting)
⚡ AGGRESSIVE SIZING: size=1.0 (all-in) is OK for memecoins
⚡ NO LONG HOLDS: Exit within minutes/hours, not days

Generate a complete, executable backtesting strategy using:
- backtesting.py library (from backtesting import Backtest, Strategy)
- talib for indicators (import talib)
- pandas-ta as backup (import pandas_ta as ta)

CRITICAL REQUIREMENTS:
1. All indicators MUST use self.I() wrapper: self.I(talib.RSI, self.data.Close, timeperiod=14)
2. NO backtesting.lib functions (no crossover, no cross, etc.) - write logic manually
3. Position sizing must be integer (units) or fraction 0-1, never float
4. Include proper if __name__ == '__main__' block with data loading
5. Use self.buy() and self.position.close() for trades
6. Data must have columns: datetime, open, high, low, close, volume (lowercase)
7. After loading, capitalize columns and set datetime as index
8. MEMECOIN: Use cash=1000, commission=0.005 (0.5%)

Example structure:
```python
from backtesting import Backtest, Strategy
import pandas as pd
import talib

class MyStrategy(Strategy):
    def init(self):
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=14)
        self.sma = self.I(talib.SMA, self.data.Close, timeperiod=20)

    def next(self):
        if self.rsi[-1] < 30 and not self.position:
            self.buy()
        elif self.position and self.rsi[-1] > 70:
            self.position.close()

if __name__ == '__main__':
    # Load data
    df = pd.read_csv('data.csv')
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.columns = [c.capitalize() for c in df.columns]
    df = df.set_index('Datetime')

    bt = Backtest(df, MyStrategy, cash=10000, commission=.003)
    stats = bt.run()
    print(stats)
```"""

        user_prompt = f"""Generate a complete backtesting.py strategy for:

STRATEGY_NAME: {strategy_name}

STRATEGY_DETAILS:
{research}

Requirements:
- Complete, executable Python code
- Use talib for all standard indicators
- Manual crossover logic (NO backtesting.lib.crossover)
- Proper position sizing
- Include if __name__ == '__main__' block
- CSV data loading example"""

        code = self._call_llm(system_prompt, user_prompt)
        return code

    def _cleanup_code(self, code: str) -> str:
        """Phase 3: Remove backtesting.lib dependencies and clean up code"""

        # Remove markdown code blocks if present
        code = re.sub(r'^```python\s*\n', '', code, flags=re.MULTILINE)
        code = re.sub(r'^```\s*$', '', code, flags=re.MULTILINE)

        # Remove import backtesting.lib
        code = re.sub(r'from backtesting\.lib import.*\n', '', code)
        code = re.sub(r'import backtesting\.lib.*\n', '', code)

        # Replace common backtesting.lib.crossover patterns
        # This is a simple replacement - in production, might need AI to rewrite
        code = code.replace('crossover(', '# crossover(')

        return code.strip()

    def _extract_strategy_name(self, research: str) -> str:
        """Extract strategy name from research text"""

        # Look for STRATEGY_NAME: or similar patterns
        patterns = [
            r'STRATEGY[_\s]*NAME:\s*([A-Za-z0-9_]+)',
            r'Strategy Name:\s*([A-Za-z0-9_]+)',
            r'Name:\s*([A-Za-z0-9_]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, research, re.IGNORECASE)
            if match:
                return match.group(1)

        # Fallback: generate from timestamp
        return f"Strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Call the configured LLM and return response"""

        if self.model_type == 'anthropic':
            response = self.client.messages.create(
                model=self.model_config['model'],
                max_tokens=self.model_config['max_tokens'],
                temperature=self.model_config['temperature'],
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.content[0].text

        elif self.model_type in ['openai', 'deepseek']:
            response = self.client.chat.completions.create(
                model=self.model_config['model'],
                max_tokens=self.model_config['max_tokens'],
                temperature=self.model_config['temperature'],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.choices[0].message.content

        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")

    def _save_research(self, strategy_name: str, research: str) -> str:
        """Save research text to file"""
        filename = f"{strategy_name}_research.txt"
        filepath = os.path.join(config.STRATEGIES_DIR, filename)

        with open(filepath, 'w') as f:
            f.write(f"Strategy: {strategy_name}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")
            f.write(research)

        return filepath

    def _save_code(self, strategy_name: str, code: str) -> str:
        """Save strategy code to file"""
        filename = f"{strategy_name}.py"
        filepath = os.path.join(config.STRATEGIES_DIR, filename)

        with open(filepath, 'w') as f:
            f.write(f"# Strategy: {strategy_name}\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Auto-generated by AI Strategy Builder\n\n")
            f.write(code)

        return filepath


def test_builder():
    """Test the strategy builder with a sample idea"""
    print("=" * 70)
    print("AI STRATEGY BUILDER - Test Mode")
    print("=" * 70)

    # Check config
    errors = config.validate_config()
    if errors:
        print("\n❌ Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        return

    # Sample trading idea
    sample_idea = """
    I want to create a momentum strategy using RSI and moving averages.

    Entry conditions:
    - RSI (14 period) crosses above 30 from below (oversold recovery)
    - Price is above the 50-period simple moving average (uptrend confirmation)
    - Volume is above average (strong conviction)

    Exit conditions:
    - RSI crosses above 70 (overbought)
    - Price crosses below the 50-period SMA (trend reversal)

    Risk management:
    - Stop loss at 2% below entry
    - Take profit at 5% above entry
    - Position size: 10% of capital per trade

    Best timeframe: 15 minutes for quick trades
    """

    try:
        builder = AIStrategyBuilder()
        print(f"\n✓ Using AI model: {builder.model_type} ({builder.model_config['model']})")

        result = builder.generate_strategy(sample_idea)

        print("\n" + "=" * 70)
        print("GENERATED STRATEGY")
        print("=" * 70)
        print(f"\nName: {result['name']}")
        print(f"\nResearch saved to: {result['research_file']}")
        print(f"Code saved to: {result['code_file']}")

        print("\n" + "=" * 70)
        print("RESEARCH SUMMARY")
        print("=" * 70)
        print(result['research'][:500] + "..." if len(result['research']) > 500 else result['research'])

        print("\n" + "=" * 70)
        print("✓ Strategy builder test completed!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_builder()
