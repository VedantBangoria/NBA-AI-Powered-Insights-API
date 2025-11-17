# Ollama Setup Guide for NBA Analytics API

This guide will help you set up Ollama and download a local LLM model for the NBA Analytics API.

## Hardware Requirements

**Your Setup:**
- GPU: RTX 3050 Ti (4GB VRAM) ✅
- RAM: 16GB ✅
- Storage: At least 10GB free space

## Step 1: Install Ollama

### Windows (Your System)
1. Download Ollama from: https://ollama.ai/download
2. Run the installer and follow the setup wizard
3. Ollama will start automatically as a Windows service

### Alternative: Manual Installation
```bash
# Download and install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
```

## Step 2: Download the Recommended Model

For your RTX 3050 Ti with 4GB VRAM, I recommend **Llama 2 7B**:

```bash
# Open PowerShell or Command Prompt
ollama pull llama2:7b
```

**Model Details:**
- **Size:** ~4GB download, ~8GB RAM usage
- **Performance:** Excellent for your GPU
- **Speed:** ~10-20 tokens/second on your setup
- **Quality:** Very good for analytical tasks

## Step 3: Alternative Models (if needed)

If you want to try other models:

```bash
# Mistral 7B (excellent performance)
ollama pull mistral:7b

# Phi-2 (very efficient, smaller)
ollama pull phi:2.7b

# CodeLlama 7B (good for analytical tasks)
ollama pull codellama:7b
```

## Step 4: Verify Installation

```bash
# Check if Ollama is running
ollama list

# Test the model
ollama run llama2:7b "Hello, how are you?"
```

## Step 5: Configure the API

1. **Update your `.env` file:**
```env
LLM_MODEL_NAME=llama2:7b
```

2. **Start the API:**
```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the API
python main.py
```

## Performance Optimization

### For Better Performance:
1. **Close other GPU applications** while running the API
2. **Use GPU acceleration** (Ollama automatically detects your GPU)
3. **Monitor VRAM usage** with Task Manager

### Expected Performance:
- **First response:** 2-5 seconds (model loading)
- **Subsequent responses:** 1-3 seconds
- **Memory usage:** ~8-10GB RAM
- **GPU usage:** 70-90% during inference

## Troubleshooting

### Common Issues:

1. **"Model not found" error:**
```bash
# Re-download the model
ollama pull llama2:7b
```

2. **Out of memory errors:**
- Close other applications
- Try a smaller model: `ollama pull phi:2.7b`

3. **Slow performance:**
- Ensure GPU drivers are updated
- Check that Ollama is using GPU (should show in Task Manager)

4. **Ollama not starting:**
```bash
# Restart Ollama service
ollama serve
```

### Check GPU Usage:
- Open Task Manager → Performance → GPU
- Look for "Ollama" or "CUDA" processes

## Model Comparison for Your Hardware

| Model | Size | RAM Usage | Speed | Quality | Recommendation |
|-------|------|-----------|-------|---------|----------------|
| Llama 2 7B | 4GB | 8GB | Fast | Excellent | ✅ **Best Choice** |
| Mistral 7B | 4GB | 8GB | Fast | Excellent | ✅ Great Alternative |
| Phi-2 | 1.5GB | 4GB | Very Fast | Good | ✅ If RAM is limited |
| CodeLlama 7B | 4GB | 8GB | Fast | Good | ✅ For analytical tasks |

## Next Steps

1. **Test the API:**
```bash
# Health check
curl http://localhost:8000/health

# Generate hot takes
curl http://localhost:8000/hot-takes?num_takes=3
```

2. **Monitor Performance:**
- Watch Task Manager for GPU and RAM usage
- Check API response times

3. **Fine-tune if needed:**
- If too slow: try `phi:2.7b`
- If not enough RAM: close other applications
- If poor quality: try `mistral:7b`

## Support

If you encounter issues:
1. Check the Ollama logs: `ollama logs`
2. Restart Ollama: `ollama serve`
3. Reinstall the model: `ollama pull llama2:7b`

The API will automatically fall back to rule-based analysis if the LLM is unavailable, so it will always work even if Ollama has issues.
