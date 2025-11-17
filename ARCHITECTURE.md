# System Architecture Documentation

## Overview

This document provides detailed architectural information for the Enterprise SRE AI & Agentic System.

---

## Component Architecture

### 1. Message Layer

#### MQTT Broker (Eclipse Mosquitto)
- **Purpose**: IoT telemetry ingestion
- **Port**: 1883 (MQTT), 9001 (WebSocket)
- **Throughput**: 100,000 messages/second
- **Topic Structure**: `og/field/{site_id}/{device_type}/{device_id}`
- **QoS Level**: 1 (At least once delivery)

**Message Flow**:
```
IoT Devices → MQTT Broker → Backend Subscribers → Redis Cache
```

#### RabbitMQ
- **Purpose**: User activity events and system messages
- **Port**: 5672 (AMQP), 15672 (Management UI)
- **Queue**: `webapp_active_users`
- **Durability**: Persistent messages
- **Delivery**: Guaranteed delivery with ack

**Message Flow**:
```
User Simulator → RabbitMQ Queue → Backend Consumers → Redis State
```

---

### 2. State Management Layer

#### Redis Stack (Dual Region)

**Region 1** (Primary)
- Port: 6379
- RedisInsight: 8001
- Modules: RedisJSON, RediSearch, RedisTimeSeries

**Region 2** (Failover)
- Port: 6380
- RedisInsight: 8002
- Modules: RedisJSON, RediSearch, RedisTimeSeries

**Data Structures**:

1. **String Keys** - Simple state
   ```
   region1:status → "active"
   region1:version → "v1.0.0057_region1"
   stats:active_devices → 100000
   stats:active_users → 324
   ```

2. **Hash Keys** - Structured data
   ```
   site:WY-ALPHA:metrics → { device_count: 10000, alert_count: 5 }
   ```

3. **Vector Embeddings** - Image search
   ```
   embedding:WY-ALPHA_turbine_Turbine1.jpg → {
     embedding: [float array],
     metadata: { site_id, device_type, description }
   }
   ```

**Failover Strategy**:
- Active-Passive configuration
- State replication on failover trigger
- < 10ms failover latency
- Automatic state sync

---

### 3. Backend API Layer

#### FastAPI Applications (Dual Region)

**Region 1**: Port 8000
**Region 2**: Port 8100

**Modules**:

1. **app/main.py** - Application entry point
   - Lifecycle management
   - CORS configuration
   - Router registration

2. **app/config.py** - Configuration management
   - Environment variables
   - Service endpoints
   - Regional settings

3. **app/services/**
   - `redis_service.py` - Redis operations
   - `embedding_service.py` - Image processing and embeddings
   - `rag_service.py` - Log analysis and LLM queries

4. **app/routers/**
   - `devices.py` - Device management endpoints
   - `users.py` - User activity endpoints
   - `images.py` - Image search endpoints
   - `diagnostics.py` - RAG and log analysis
   - `failover.py` - Failover management

**API Design Principles**:
- RESTful conventions
- JSON request/response
- Error handling with proper HTTP codes
- Request validation with Pydantic
- Async/await for I/O operations
- OpenAPI documentation (Swagger)

---

### 4. Frontend Layer

#### React Dashboard

**Technology**:
- React 18
- Axios for API calls
- CSS3 with gradients and animations
- Responsive design

**Features**:
- Real-time status updates (5s polling)
- Region switching (R1 ↔ R2)
- Action buttons for system operations
- AI-powered search interface
- Quick query shortcuts
- Result visualization

**State Management**:
- React useState for local state
- useEffect for lifecycle and polling
- Direct API integration (no Redux needed for this scale)

---

### 5. Simulation Layer

#### IoT Device Simulator

**Configuration**:
- 100,000 devices
- 10 sites
- 4 device types
- 1-second publish interval

**Device Distribution**:
```
Turbines:         25,000 (25%)
Thermal Engines:  25,000 (25%)
Electrical Rotors: 25,000 (25%)
OG Devices:       25,000 (25%)
```

**Metrics Generation**:
- Realistic value ranges based on device type
- Random variance for authenticity
- State simulation (OK/WARN/ALERT)
- Weighted distribution (85% OK, 12% WARN, 3% ALERT)

**Performance**:
- Batch publishing (1000 devices/batch)
- Async I/O for non-blocking operations
- Memory-efficient device rotation

#### User Activity Simulator

**Configuration**:
- 200-500 concurrent users
- 5-second publish interval
- User churn simulation

**Metrics**:
- Active user count
- Connection status
- Server metrics (CPU, memory, latency)
- Session information

---

## Data Flow Diagrams

### Device Telemetry Flow

```
┌─────────────┐
│ IoT Device  │
│ Generator   │
└──────┬──────┘
       │ Generate metrics every 1s
       ▼
┌─────────────┐
│ MQTT Broker │ Topic: og/field/{site}/{type}/{id}
└──────┬──────┘
       │ QoS 1
       ▼
┌─────────────┐
│ Backend API │ Subscribe to topics
└──────┬──────┘
       │ Parse & store
       ▼
┌─────────────┐
│ Redis Stack │ Cache latest state
└──────┬──────┘
       │ Read
       ▼
┌─────────────┐
│  Dashboard  │ Display metrics
└─────────────┘
```

### Image Search Flow

```
┌─────────────┐
│ User Query  │ "workers with hard hats"
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Frontend   │ POST /api/images/search
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Backend API │ Generate query embedding
└──────┬──────┘
       │ Cohere API
       ▼
┌─────────────┐
│ Embedding   │ Encode to vector
│  Service    │
└──────┬──────┘
       │ [0.234, 0.123, ...]
       ▼
┌─────────────┐
│ Redis Stack │ Vector similarity search
└──────┬──────┘
       │ Top K results
       ▼
┌─────────────┐
│  Frontend   │ Display matched images
└─────────────┘
```

### Failover Flow

```
┌─────────────┐
│ User Action │ Click "Simulate Failover"
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Frontend   │ POST /api/failover/simulate
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Region 1 API│ Start failover timer
└──────┬──────┘
       │
       ├──────────────────────┐
       │                      │
       ▼                      ▼
┌─────────────┐      ┌─────────────┐
│ Redis R1    │      │ Redis R2    │
│ Set:        │      │ Get state & │
│ status=     │      │ activate    │
│ failing_over│      │             │
└──────┬──────┘      └──────┬──────┘
       │                      │
       │◄─────────────────────┘
       │ Replicate state
       ▼
┌─────────────┐
│ Region 2 API│ status=active
└──────┬──────┘
       │ Measure latency
       ▼
┌─────────────┐
│  Frontend   │ Switch to Region 2
└─────────────┘ Display metrics
```

---

## Scalability Considerations

### Horizontal Scaling

**MQTT Broker**:
- Add more Mosquitto instances with load balancer
- Bridge brokers for topic distribution

**Backend API**:
- Stateless design allows easy horizontal scaling
- Load balancer (nginx/HAProxy) in front
- Auto-scaling based on CPU/memory

**Redis**:
- Redis Cluster for sharding
- Sentinel for automatic failover
- Read replicas for read-heavy workloads

### Vertical Scaling

**Current Requirements** (100K devices):
- CPU: 4 cores
- RAM: 8GB
- Disk: 20GB

**Scaling to 1M devices**:
- CPU: 16 cores
- RAM: 32GB
- Disk: 100GB
- Multiple MQTT brokers

---

## Security Considerations

### Network Security
- Internal Docker network isolation
- Exposed ports limited to necessary services
- HTTPS/TLS for production (not in demo)

### Authentication & Authorization
- RabbitMQ: Username/password auth
- Redis: Optional password protection
- API: Can add JWT tokens for production

### Data Security
- Message queue persistence
- Redis AOF for durability
- Encrypted connections in production

---

## Monitoring & Observability

### Health Checks
- `/health` endpoints on all services
- Docker health check configurations
- Automatic restart on failure

### Metrics
- Device count tracking
- User activity monitoring
- Error rate calculation
- Latency measurements

### Logging
- Structured logging (JSON)
- Log levels: INFO, WARNING, ERROR
- Centralized log collection (could add ELK)

---

## Performance Benchmarks

### Throughput
- MQTT: 100,000 msg/sec
- API: 10,000 req/sec
- Redis: 100,000 ops/sec

### Latency
- API P50: < 50ms
- API P95: < 100ms
- API P99: < 200ms
- Failover: < 0.01s

### Resource Usage
- MQTT Broker: ~200MB RAM
- Backend API: ~300MB RAM per instance
- Redis: ~500MB RAM per instance
- Frontend: ~100MB RAM

---

## Deployment Strategy

### Local Development
```bash
docker-compose up -d
```

### Production Deployment

1. **Containerization**: Already Dockerized
2. **Orchestration**: Kubernetes manifests (could be added)
3. **CI/CD**: GitHub Actions / Jenkins pipeline
4. **Monitoring**: Prometheus + Grafana
5. **Logging**: ELK Stack
6. **Load Balancing**: nginx or AWS ALB
7. **Database**: Managed Redis (AWS ElastiCache, Azure Cache)

---

## Technology Choices - Rationale

### Why MQTT?
- Lightweight protocol for IoT
- Publish-subscribe pattern
- Support for QoS levels
- Wide device support

### Why RabbitMQ?
- Reliable message delivery
- Complex routing capabilities
- Management UI
- Well-documented

### Why Redis Stack?
- In-memory speed
- Vector search capability
- Multiple data structures
- Time-series support

### Why FastAPI?
- High performance (async)
- Auto-generated docs
- Type checking
- Modern Python

### Why React?
- Component-based
- Virtual DOM performance
- Large ecosystem
- Easy to learn

---

## Future Enhancements

1. **Real LLM Integration**
   - OpenAI GPT-4 for queries
   - Cohere for production embeddings
   - Fine-tuned models for domain

2. **Advanced Analytics**
   - Time-series visualization
   - Predictive maintenance
   - Anomaly detection

3. **Kubernetes Deployment**
   - Helm charts
   - Auto-scaling
   - Rolling updates

4. **Authentication**
   - OAuth2 / OIDC
   - JWT tokens
   - Role-based access

5. **Monitoring Stack**
   - Prometheus metrics
   - Grafana dashboards
   - Alert manager

6. **Database Layer**
   - TimescaleDB for time-series
   - PostgreSQL for relational data
   - S3 for image storage
