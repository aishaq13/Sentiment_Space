# Sentiment Space - Setup & Installation Guide

Complete step-by-step guide for setting up Sentiment Space locally.

## Prerequisites

### Backend
- Python 3.11 or higher
- pip (Python package manager)
- 6GB+ RAM available
- 4GB+ disk space for models

### iOS
- Xcode 15.0+
- macOS 13.0+
- iPhone 12+ (for Core ML) or any iPhone (with backend fallback)
- iOS 15.0+

### Optional
- Docker & Docker Compose (for containerized backend)
- AWS account (only if enabling S3 export)

## Backend Setup

### 1. Clone Repository

```bash
cd sentiment-space
```

### 2. Create Virtual Environment

```bash
cd backend

# macOS/Linux
python3.11 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: First install may take 5-10 minutes as Torch is large.

### 4. Configure Environment

```bash
# Copy environment template
cp ../.env.example .env

# Edit .env with your settings (optional for basic usage)
# nano .env  # or use your favorite editor
```

Default configuration works fine for local development:
- Database: `./data/sentiment.db`
- LLM: Llama 3 (will download on first use)
- S3: Disabled
- Port: 8000

### 5. Run Backend

```bash
python -m uvicorn app.main:app --reload
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### 6. Verify Installation

Open another terminal:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy","version":"0.1.0"}
```

### 7. Test Analysis Endpoint

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"raw_text":"Today was wonderful!"}'
```

First request will download the Llama 3 model (~13GB unquantized, ~3.5GB quantized).

## iOS Setup

### 1. Open Project in Xcode

```bash
open ios/SentimentSpaceApp
```

Or open via Xcode:
1. Launch Xcode
2. File → Open → Select `ios` folder

### 2. Configure Backend URL

Edit `ios/SentimentSpaceApp/Services/APIService.swift`:

```swift
init(backendURL: String = "http://localhost:8000") {
    // For simulator:
    // "http://localhost:8000" works (simulator → host)
    
    // For physical device:
    // "http://192.168.1.100:8000" (replace with your IP)
}
```

### 3. Build & Run

**For Simulator**:
1. Select simulator from Xcode toolbar
2. Press Cmd+R to run

**For Physical Device**:
1. Connect iPhone
2. Select device from toolbar
3. Press Cmd+R

### 4. Test App

1. Tap "Analyze Thought"
2. Enter text (e.g., "Today was amazing!")
3. Tap "Analyze"
4. View summary and sentiment on next screen

If backend not accessible:
- Check `APIService.swift` URL configuration
- Verify backend is running
- Check firewall settings

## Docker Setup

### 1. Build and Start

```bash
docker-compose up --build
```

First build takes 3-5 minutes due to dependencies.

### 2. Verify

```bash
curl http://localhost:8000/health
```

### 3. Access Logs

```bash
docker-compose logs -f backend
```

### 4. Stop

```bash
docker-compose down
```

## Model Download & Configuration

### First Run Behavior

On first API call to `/analyze`:
1. Backend checks if Llama 3 model exists
2. If not found, downloads from Hugging Face
3. Download: ~3.5GB (quantized) to ~13GB (full)
4. Uncompressed to disk
5. Loaded into memory

**Time**: 5-10 minutes on typical internet

### Manual Download

```bash
python
>>> from transformers import AutoModelForCausalLM
>>> model = AutoModelForCausalLM.from_pretrained(
...     "meta-llama/Llama-2-7b-hf"
... )
```

### Custom Model

To use a different model, edit `backend/.env`:

```
LLM_MODEL_NAME=meta-llama/Llama-2-13b-hf
LLM_QUANTIZATION=int8
```

## Optional: AWS S3 Export

### Enable S3

1. Edit `backend/.env`:

```env
S3_ENABLED=true
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
S3_BUCKET_NAME=sentiment-space-exports
AWS_REGION=us-east-1
```

2. Create S3 bucket on AWS
3. Create IAM user with S3 access
4. Verify endpoint works:

```bash
curl -X POST http://localhost:8000/export
```

## Optional: Core ML Integration

For iOS on-device inference (experimental):

1. Install MLX tools:
```bash
pip install mlx-lm mlx
```

2. Convert model:
```bash
mlx_lm.convert \
  --hf-path meta-llama/Llama-2-7b-hf \
  --mlx-path ./models/llama-3-mlx \
  --q --q-bits 4
```

3. See [COREML_INTEGRATION.md](COREML_INTEGRATION.md) for full instructions

## Troubleshooting

### Backend Won't Start

```
ModuleNotFoundError: No module named 'torch'
```

**Fix**: Reinstall requirements
```bash
pip install -r requirements.txt --force-reinstall
```

### GPU Not Detected

```
CUDA_VISIBLE_DEVICES=0 python -m uvicorn app.main:app
```

Most setups use CPU—it's fine. See [LLM_DEVICE config](backend/app/utils/config.py).

### Model Download Fails

```
ConnectionError: Failed to establish a new connection
```

**Fix**: 
- Check internet connection
- Set Hugging Face token if needed:
```bash
export HF_TOKEN="your_hf_token"
```

### iOS App Can't Reach Backend

**Simulator**:
- Ensure backend is running
- Check `APIService.swift` URL

**Physical Device**:
- Find your computer's IP:
```bash
ifconfig | grep "inet "
```
- Update APIService URL to `http://192.168.x.x:8000`
- Ensure same WiFi network

### Insufficient Disk Space

Free up 5GB minimum:
```bash
# macOS
df -h

# Linux
df -h
```

## Development Workflow

### Starting Fresh

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload

# Terminal 2: iOS
cd ios
open SentimentSpaceApp/
# Then run from Xcode
```

### Running Tests

```bash
cd backend
pytest -v
```

### Linting

```bash
cd backend
flake8 app/
black app/ --check
```

### Benchmarking

```bash
cd backend
python benchmark.py
```

## Production Deployment

### Backend in Production

See [docker-compose.yml](docker-compose.yml) for reference:

```bash
docker-compose -f docker-compose.yml up -d
```

Configuration changes:
```env
FASTAPI_ENV=production
FASTAPI_DEBUG=false
LOG_LEVEL=INFO
S3_ENABLED=true  # If using backup
```

### iOS App Distribution

1. Build for App Store:
```
Product → Scheme → Edit Scheme → Run → Release
Product → Build
```

2. Archive:
```
Product → Archive
```

3. Upload to App Store

## Next Steps

1. ✅ Backend running locally
2. ✅ iOS app connecting
3. ✅ Analyze first thought
4. 📚 Read [Architecture Overview](README.md#architecture)
5. 📊 Review [Benchmarks](backend/benchmark.py)
6. 🔒 Enable S3 if backup needed
7. 📱 Build Core ML version for iOS

## Support

### Check Logs

```bash
# Backend
tail -f logs/*.log

# Docker
docker-compose logs -f backend

# Xcode
View → Debug Area → Console
```

### Common Errors

See [Troubleshooting](#troubleshooting) section above.

### Getting Help

1. Check README.md
2. Review error messages
3. Enable DEBUG logging
4. Check GitHub issues

---

**You're all set!** Start with the iOS app or test the backend directly.

Happy analyzing! 🚀
