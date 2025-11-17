# Quick Start Guide

Get the Enterprise SRE System running in 5 minutes!

---

## Prerequisites Check

Before starting, ensure you have:

- [ ] Docker Desktop installed and running
- [ ] Docker Compose installed (v2.0+)
- [ ] At least 8GB free RAM
- [ ] Ports available: 3000, 5672, 6379, 6380, 8000, 8100, 15672, 1883

---

## Step 1: Setup (1 minute)

```bash
# Navigate to project directory
cd /Users/kartikeysharma/hackathon_273

# Run setup script
bash scripts/setup.sh
```

The setup script will:
1. Build all Docker images
2. Start all services
3. Verify health of components

---

## Step 2: Access the Dashboard (30 seconds)

Open your browser and navigate to:

**http://localhost:3000**

You should see the Enterprise SRE AI Dashboard with:
- Live system status
- Region selector (Region 1 / Region 2)
- Control buttons
- Search interface

---

## Step 3: Try Core Features (3 minutes)

### Test 1: View Active Devices
1. Click the **"Active Devices"** button
2. See the count of 100,000 simulated devices across 10 sites

### Test 2: View Active Users
1. Click the **"Active Users"** button
2. See real-time user activity metrics

### Test 3: AI Search
1. In the search box, type: `workers wearing hard hats`
2. Click **"Search Images"**
3. See semantic search results from site images

### Test 4: LLM Query
1. Click **"Safety Incidents 2024"** quick query button
2. See AI-generated response about BP operations safety

### Test 5: Simulate Failover
1. Click **"Simulate Failover"** button
2. Watch the region switch from Region 1 → Region 2
3. Note the failover latency (should be < 0.01 seconds)

---

## Step 4: Explore APIs (1 minute)

### Open API Documentation

**Region 1 API Docs**: http://localhost:8000/docs
**Region 2 API Docs**: http://localhost:8100/docs

Try these endpoints in the Swagger UI:

1. **GET** `/health` - Check system health
2. **GET** `/api/status` - Get current status
3. **GET** `/api/devices/active` - Get active device count
4. **POST** `/api/diagnostics/query` - Ask an LLM question
   ```json
   {
     "question": "How many safety incidences occurred in BP operations in 2024?"
   }
   ```

---

## Step 5: Run Tests (Optional)

```bash
# Install Python dependencies for testing
pip install requests

# Run full system test
python scripts/test_system.py

# Run failover test
python scripts/test_failover.py
```

---

## Common Tasks

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend-region1
docker-compose logs -f iot-simulator
docker-compose logs -f user-simulator
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend-region1
```

### Stop Everything

```bash
docker-compose down
```

### Start Again

```bash
docker-compose up -d
```

---

## Verification Checklist

After setup, verify these are working:

- [ ] Frontend loads at http://localhost:3000
- [ ] "Active Devices" button shows ~100,000 devices
- [ ] "Active Users" button shows user metrics
- [ ] Image search returns results
- [ ] LLM queries return answers
- [ ] Failover completes in < 1 second
- [ ] Both regions respond to API calls

---

## Troubleshooting

### "Cannot connect to Docker daemon"
```bash
# Start Docker Desktop
# Wait for it to fully start, then retry
```

### "Port already in use"
```bash
# Find what's using the port
lsof -i :8000

# Stop the conflicting service or change the port in docker-compose.yml
```

### "Services not starting"
```bash
# Check Docker resources
docker system df

# Clean up
docker system prune -a

# Restart from scratch
docker-compose down -v
bash scripts/setup.sh
```

### "Frontend shows connection errors"
```bash
# Wait 30 seconds for backend to fully start
# Check backend logs
docker-compose logs backend-region1

# Verify backend is accessible
curl http://localhost:8000/health
```

### "No devices showing"
```bash
# Check IoT simulator is running
docker-compose logs iot-simulator

# Restart simulator if needed
docker-compose restart iot-simulator
```

---

## Next Steps

Once everything is running:

1. **Read the full README.md** for detailed documentation
2. **Explore ARCHITECTURE.md** to understand the system design
3. **Try all API endpoints** using the Swagger docs
4. **Modify simulation parameters** in `.env` file
5. **Add your Cohere/OpenAI API keys** for real embeddings/LLM

---

## Support

For issues:
1. Check `docker-compose logs -f`
2. Verify all containers are running: `docker ps`
3. Review troubleshooting section above
4. Check README.md for detailed docs

---

## Demo Script for Presentation

### 1-Minute Demo
```
1. Open dashboard (localhost:3000)
2. Show real-time status updating
3. Click "Active Devices" - show 100K devices
4. Click "Simulate Failover" - show sub-second latency
```

### 5-Minute Demo
```
1. Overview dashboard and architecture
2. Show active devices and users
3. Demonstrate AI image search
4. Run LLM query about safety incidents
5. Simulate failover and show latency
6. Open API docs and show endpoints
7. Show logs and monitoring
```

### 10-Minute Demo
```
1-5: Same as 5-minute demo
6. Run test scripts (test_system.py)
7. Show RabbitMQ management UI
8. Show Redis Insight
9. Demonstrate log diagnostics
10. Explain architecture and scalability
```

---

Happy hacking! 🚀
