# Sentiment Space

A privacy-centric, on-device AI assistant for thought summarization and sentiment analysis. Runs Llama 3 locally for instant, offline processing without requiring cloud infrastructure or user data ever leaving your device.

## Key Features

- **100% On-Device Inference**: Llama 3 runs locally on CPU, no cloud calls
- **Privacy-First**: User data never leaves the device unless explicitly exported
- **Instant Responses**: ~80% faster than cloud-based alternatives due to no network latency
- **Offline-Capable**: Works completely without internet connection
- **Local Persistence**: SQLite database on device
- **Optional Export**: User-controlled S3 uploads with explicit consent

## Tech Stack

- **iOS**: SwiftUI, MVVM, Core ML
- **Backend**: FastAPI, Python
- **LLM**: Llama 3 (local, quantized for CPU)
- **Orchestration**: LangChain
- **Storage**: SQLite
- **Optional Cloud**: AWS S3
- **Infrastructure**: Docker, docker-compose

## Quick Start

See [SETUP.md](./SETUP.md) for complete setup instructions.

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### iOS

Open `ios/SentimentSpace.xcodeproj` in Xcode and run on simulator or device.

## Project Structure

```
sentiment-space/
├── ios/                    # SwiftUI iOS application
├── backend/                # FastAPI Python backend
├── models/                 # ML model artifacts
├── docker-compose.yml      # Local development orchestration
└── README.md              # This file
```

## Privacy Guarantee

No data is sent to external servers by default. The optional S3 export feature:
- Requires explicit user action
- Requires AWS credentials in `.env`
- Must be manually configured
- Can be completely disabled

## Performance

On-device Llama 3 inference achieves 80% lower latency than cloud alternatives:

- **Local Inference**: ~2-5 seconds (CPU, quantized)
- **Cloud + Network**: ~8-15 seconds (API call overhead)

See benchmarks in the documentation.

## License

MIT
