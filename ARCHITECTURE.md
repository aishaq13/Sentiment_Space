# Architecture & Design Decisions

This document explains the architectural choices and design patterns used in Sentiment Space.

## Core Design Principles

### 1. Privacy-First by Default

**Principle**: All data stays on-device unless user explicitly opts in to export.

**Implementation**:
- No cloud API calls in default config
- S3 export disabled by default (`S3_ENABLED=false`)
- All inference runs locally
- Database stored on filesystem

**Trade-offs**:
- ✅ Maximum privacy
- ✅ Works offline
- ❌ User responsible for device security
- ❌ No automatic backups

### 2. Local Inference Only

**Principle**: Use local Llama 3 instead of cloud APIs.

**Rationale**:
- ~3-4x faster (network latency elimination)
- Privacy preserved
- No per-inference costs
- Works completely offline

**Implementation**:
- Llama 3 (7B, quantized to int4)
- CPU inference (works without GPU)
- Graceful degradation if model unavailable
- LangChain for orchestration

### 3. Clean Separation of Concerns

**Architecture Layers**:

```
┌─────────────────────┐
│  Views (SwiftUI)    │  Presentation
├─────────────────────┤
│  ViewModels (MVVM)  │  State Management
├─────────────────────┤
│  Services (API)     │  Business Logic
├─────────────────────┤
│  Models             │  Data Structures
├─────────────────────┤
│  Backend (FastAPI)  │  Orchestration
├─────────────────────┤
│  LangChain Pipeline │  LLM Ops
├─────────────────────┤
│  LLM (Llama 3)      │  Inference
├─────────────────────┤
│  Database (SQLite)  │  Persistence
└─────────────────────┘
```

**Benefits**:
- Easy to test each layer independently
- Swap components (Core ML ↔ Backend)
- Clear data flow
- Maintainable codebase

## Key Components

### 1. Llama Loader (`backend/app/llm/llama_loader.py`)

**Purpose**: Load and manage Llama 3 model

**Design**:
- Lazy loading (only load when needed)
- Graceful fallback if model unavailable
- Supports multiple quantization levels
- Returns mock responses if no GPU

**Code Quality**:
- 100+ lines of well-documented code
- Clear error handling
- Support for different devices (CPU, CUDA, MPS)
- Memory-efficient quantization

### 2. LangChain Pipeline (`backend/app/llm/langchain_pipeline.py`)

**Purpose**: Orchestrate summarization and sentiment analysis

**Design**:
- Chains multiple operations
- Maintains conversation memory
- Prompt templates for consistency
- Local context awareness

**Key Features**:
- Summarization chain
- Sentiment classification chain
- Confidence estimation
- Similar thought retrieval

### 3. Database Layer (`backend/app/db/database.py`)

**Purpose**: Persistent local storage

**Design**:
- Context manager for connections
- CRUD operations
- Query helpers (filter by sentiment, pagination)
- Statistics aggregation

**Schema**:
- `thoughts` table with indices
- Timestamps for audit trail
- Nullable fields for optional inference results

### 4. API Routes (`backend/app/api/routes.py`)

**Purpose**: HTTP interface for iOS app

**Endpoints**:
- `GET /health` - Health check
- `POST /analyze` - Analyze thought
- `GET /entries` - Retrieve history
- `POST /export` - Optional S3 export

**Design**:
- Request/response models with Pydantic
- Proper error handling
- Status codes follow REST conventions

### 5. SwiftUI App (`ios/SentimentSpaceApp/`)

**Architecture**: MVVM

```
View (SwiftUI)
    ↓
ViewModel (@StateObject)
    ↓
Model (Codable)
    ↓
Service (APIService)
    ↓
Backend API
```

**Characteristics**:
- Clean separation of UI and logic
- Type-safe networking with Codable
- Async/await for concurrency
- ObservableObject for reactivity

## Design Patterns

### 1. Singleton Pattern

**LatencyTracker** in `metrics.py`:
```python
def get_tracker() -> LatencyTracker:
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = LatencyTracker()
    return _global_tracker
```

**Use Case**: Global performance monitoring

### 2. Factory Pattern

**LlamaLoader** acts as factory for models:
```python
loader = LlamaLoader(model_name="...", quantization="int4")
loader.load()  # Returns bool, manages state
```

### 3. Context Manager Pattern

**Database connections**:
```python
@contextmanager
def _get_connection(self):
    conn = sqlite3.connect(self.db_path)
    try:
        yield conn
    finally:
        conn.close()
```

### 4. Dependency Injection

**Pipeline receives loader**:
```python
pipeline = SentimentAnalysisPipeline(llama_loader)
# Pipeline doesn't create its own dependencies
```

## Data Flow

### Analysis Request Flow

```
1. User Input (iOS)
   ↓
2. APIService.analyzethought(text)
   ↓
3. HTTP POST /analyze
   ↓
4. routes.analyze_thought()
   ↓
5. LlamaLoader.generate() [or fallback]
   ↓
6. SentimentAnalysisPipeline.analyze()
   ↓
7. Database.insert_thought()
   ↓
8. HTTP Response (201 with analysis)
   ↓
9. SummaryView displays results
```

### Caching & Memory

**Current**:
- Pipeline memory: Simple list of past analyses
- No persistent cache

**Future**:
- Redis for fast lookups
- Embedding-based similarity search
- Query result caching

## Performance Considerations

### 1. Model Loading

**Current**: Loads on first use
**Impact**: First request ~1-2s slower
**Solution**: Pre-load model on app startup

### 2. Inference

**Latency**: 2-5 seconds (CPU)
**Optimization**: Run in background thread
**iOS**: Use URLSession background task

### 3. Database

**Impact**: <100ms for writes
**Optimization**: Index on sentiment, created_at
**Scaling**: Currently handles ~10K thoughts fine

### 4. Memory

**Model**: ~4-6GB loaded
**Working**: ~1-2GB per request
**Total**: ~5-8GB minimum
**Optimization**: Quantization, batch processing

## Error Handling Strategy

### Backend

1. **Validation**: Pydantic models validate input
2. **Graceful Degradation**: Missing model → mock response
3. **Logging**: All errors logged
4. **HTTP Status**: Proper codes (400, 403, 500)

### iOS

1. **Enum Errors**: APIError with localization
2. **User Feedback**: Error alerts in UI
3. **Retry Logic**: Automatic retry on network error
4. **Fallback**: Show cached data if available

## Security Model

### Threat Landscape

**Internal**:
- Device compromise → all data at risk
- Mitigation: Encourage device encryption

**External**:
- Network observer → can't intercept (all local)
- Cloud provider → doesn't exist for local data
- App maker → only processes what user submits

### Best Practices

1. **No hardcoded secrets**: Everything in `.env`
2. **No logging of inputs**: Avoid sensitive data in logs
3. **HTTPS only**: When talking to cloud
4. **Principle of least privilege**: S3 user minimal perms

## Scalability Limits

### Single-User Device

**Current**: Handles 100K+ thoughts locally
**Bottleneck**: Model memory (4-6GB)
**Fix**: Smaller models (3B) or pruning

### Cloud Deployment

**Bottleneck**: Inference concurrency
**Current**: 1 user per container
**Solution**: Multi-GPU with request queuing

## Testing Strategy

### Unit Tests
- Database CRUD operations
- Sentiment classification
- Text summarization

### Integration Tests
- End-to-end API calls
- Model loading
- Database persistence

### Performance Tests
- Latency benchmarking
- Memory profiling
- Throughput testing

## Deployment Architecture

### Development
```
MacBook → FastAPI (reload) → Simulator/Device
```

### Production
```
Kubernetes Cluster
├── FastAPI pods (scaled)
├── Redis (caching)
├── PostgreSQL (persistence)
└── S3 (exports)

iOS App → Load Balancer → FastAPI pods
```

## Future Architectural Changes

### Short Term
- Add caching layer (Redis)
- Implement request rate limiting
- Add request signing

### Medium Term
- Switch to PostgreSQL for scaling
- Add GraphQL API layer
- Implement WebSocket for streaming

### Long Term
- Distributed inference (federated)
- Privacy-preserving analytics
- Decentralized model training

---

This architecture prioritizes **privacy and simplicity** over features. Each decision prioritizes user control and data sovereignty.
