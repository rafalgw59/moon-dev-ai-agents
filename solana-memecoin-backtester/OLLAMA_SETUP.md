# 🚀 Ollama Setup Guide

## What is Ollama?

Ollama is a tool for running **local LLMs (Large Language Models)** on your computer - completely FREE and private. Perfect for running the AI Swarm without needing API keys or paying for cloud services.

## Why Use Ollama?

✅ **FREE** - No API costs, run unlimited strategies  
✅ **PRIVATE** - All processing happens locally  
✅ **NO API KEYS** - No need for Anthropic, OpenAI, etc.  
✅ **FAST** - Direct access, no network latency  
✅ **OFFLINE** - Works without internet (after initial download)  

## Installation

### macOS / Linux
```bash
curl https://ollama.ai/install.sh | sh
```

### Windows
Download installer from: https://ollama.ai/download

### Docker
```bash
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

## Quick Start

### 1. Start Ollama Server
```bash
ollama serve
```

Leave this terminal running. It will listen on port 11434.

### 2. Pull Models (in a new terminal)

**Recommended for Swarm:**
```bash
# Llama 3.2 (3B) - Balanced performance
ollama pull llama3.2
```

**Alternative models:**
```bash
# DeepSeek R1 (7B) - Better reasoning, shows thinking process
ollama pull deepseek-r1

# Gemma 2B - Faster, lighter (good for high volume)
ollama pull gemma:2b
```

### 3. Verify Installation
```bash
ollama list
```

You should see the models you pulled:
```
NAME            ID              SIZE    MODIFIED
llama3.2        abc123          2.0GB   2 minutes ago
deepseek-r1     def456          4.7GB   3 minutes ago
```

### 4. Test the Model
```bash
ollama run llama3.2
```

Try: "Write a simple trading strategy"  
Type `/bye` to exit.

## Configure Swarm to Use Ollama

Edit `src/config.py`:

```python
# Enable Ollama mode
SWARM_USE_OLLAMA = True

# Choose your model
SWARM_OLLAMA_MODEL = 'llama3.2'  # or 'deepseek-r1', 'gemma:2b'
```

That's it! Now run the swarm:
```bash
python main.py
# Select option 8: RUN AI SWARM
```

## Model Comparison

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| **llama3.2** | 3B | Fast | Good | Balanced - **Recommended** |
| **deepseek-r1** | 7B | Medium | Better | Complex strategies, reasoning |
| **gemma:2b** | 2B | Very Fast | OK | High volume, quick tests |

## Troubleshooting

### "Connection refused" error
**Solution**: Make sure `ollama serve` is running in another terminal.

### Model not found
**Solution**: Pull the model first: `ollama pull llama3.2`

### Slow responses
**Solution**: Try a smaller model like `gemma:2b` or upgrade your hardware. Ollama works best with:
- 8GB+ RAM
- Modern CPU (or GPU for faster inference)

### Out of memory
**Solution**: Use a smaller model:
```bash
ollama pull gemma:2b
```

Then update config:
```python
SWARM_OLLAMA_MODEL = 'gemma:2b'
```

## Performance Tips

1. **GPU Acceleration**: Ollama automatically uses GPU if available (NVIDIA/AMD/Apple Silicon)
2. **Keep Models Loaded**: First query is slow (loads model), subsequent queries are fast
3. **Increase Context**: Edit model config for longer contexts (advanced)

## Cost Comparison

Running 100 strategies through the swarm:

| Mode | Cost | Time | Quality |
|------|------|------|---------|
| **Ollama (Local)** | $0.00 | ~2-4 hours | Good |
| **Cost Optimized (Cloud)** | ~$5.40 | ~30-60 min | Better |
| **GPT-4 Only (Cloud)** | ~$50 | ~30-60 min | Best |

## Additional Resources

- Official Ollama Docs: https://ollama.ai/docs
- Model Library: https://ollama.ai/library
- GitHub: https://github.com/ollama/ollama
- Discord: https://discord.gg/ollama

## Next Steps

Once Ollama is running:
1. Configure swarm: `SWARM_USE_OLLAMA = True`
2. Run main.py and select option 8
3. Generate unlimited strategies for FREE!

Happy experimenting! 🚀
