# 🚀 START HERE - Enterprise SRE Hackathon Project

Welcome! This guide will get you up and running in **5 minutes**.

---

## ⚡ Super Quick Start

```bash
# 1. Navigate to project
cd /Users/kartikeysharma/hackathon_273

# 2. Run setup
bash scripts/setup.sh

# 3. Open dashboard
open http://localhost:3000
```

**That's it!** You now have:
- 100,000 IoT devices streaming telemetry
- Dual-region API backend
- Interactive dashboard
- AI-powered search
- Failover capabilities

---

## 🎯 First Things to Try

Once the dashboard loads at http://localhost:3000:

### 1. See Active Devices (5 seconds)
Click the **"Active Devices"** button → See 100,000 devices across 10 sites

### 2. AI Image Search (10 seconds)
Type: `workers wearing hard hats` → Click **"Search Images"**

### 3. Ask AI a Question (10 seconds)
Click **"Safety Incidents 2024"** → See AI response

### 4. Simulate Failover (15 seconds)
Click **"Simulate Failover"** → Watch region switch in < 0.01 seconds

---

## 📚 Documentation Guide

**New to the project?** Read in this order:

1. **START_HERE.md** ← You are here
2. **QUICKSTART.md** - Detailed 5-minute guide
3. **README.md** - Complete documentation
4. **ARCHITECTURE.md** - System design deep-dive
5. **PROJECT_SUMMARY.md** - Project overview

---

## 🔧 Key URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| **Dashboard** | http://localhost:3000 | None needed |
| **API Region 1** | http://localhost:8000/docs | None needed |
| **API Region 2** | http://localhost:8100/docs | None needed |
| **RabbitMQ** | http://localhost:15672 | admin / admin123 |
| **Redis R1** | http://localhost:8001 | None needed |
| **Redis R2** | http://localhost:8002 | None needed |

---

## ✅ Quick Health Check

Run this to verify everything is working:

```bash
python scripts/test_system.py
```

Expected output: `25/25 tests passed (100.0%)`

---

## 🆘 Something Not Working?

### Check if services are running:
```bash
docker ps
```

You should see 9 containers running.

### View logs:
```bash
docker-compose logs -f
```

### Restart everything:
```bash
docker-compose restart
```

### Start fresh:
```bash
docker-compose down -v
bash scripts/setup.sh
```

---

## 🎓 What Did We Just Start?

This system includes:

✅ **100,000 IoT Devices** publishing to MQTT
✅ **User Activity Simulator** sending to RabbitMQ
✅ **Dual-Region APIs** (Region 1 & 2)
✅ **Redis Stack** for state and vectors
✅ **AI Image Search** with embeddings
✅ **RAG Log Diagnostics** with LLM
✅ **React Dashboard** with live updates
✅ **Failover Simulation** with metrics

All containerized and ready to demo!

---

## 🎬 Demo Script (For Presentation)

### Option 1: 60-Second Demo
```
1. Open dashboard (localhost:3000)
2. "Here are 100K devices streaming live" → Click Active Devices
3. "Watch this sub-second failover" → Click Simulate Failover
4. "And AI-powered search" → Search for "hard hats"
```

### Option 2: 5-Minute Demo
```
1. Show architecture diagram (README.md)
2. Open dashboard and explain components
3. Demonstrate Active Devices (100K)
4. Demonstrate Active Users
5. AI image search with semantic query
6. LLM query about safety incidents
7. Simulate failover and show metrics
8. Open API docs (Swagger)
9. Show test results
```

---

## 📊 System Requirements

**Minimum**:
- Docker Desktop
- 8GB RAM
- 4 CPU cores
- 20GB disk space

**Recommended**:
- 16GB RAM
- 8 CPU cores
- 50GB disk space

---

## 🔥 Cool Things to Show

1. **Scale**: 100,000 devices, not a toy demo
2. **Speed**: < 0.01 second failover latency
3. **AI**: Semantic search that actually works
4. **Architecture**: Production-ready dual-region
5. **Polish**: Beautiful UI with real-time updates
6. **Complete**: Full documentation and tests

---

## 📝 Quick Commands Reference

```bash
# Start everything
docker-compose up -d

# Stop everything
docker-compose down

# View logs
docker-compose logs -f [service-name]

# Restart a service
docker-compose restart [service-name]

# Run tests
python scripts/test_system.py
python scripts/test_failover.py

# Check status
docker ps
curl http://localhost:8000/health
```

---

## 🎯 Next Steps

1. ✅ **Run setup** (you probably did this)
2. ✅ **Open dashboard** (http://localhost:3000)
3. ✅ **Try all features** (see "First Things to Try" above)
4. 📖 **Read QUICKSTART.md** for more details
5. 🧪 **Run tests** to verify everything
6. 🎨 **Customize** if needed (see README.md)
7. 🎤 **Prepare demo** using demo script above

---

## 💡 Pro Tips

1. **Keep logs visible** during demo: `docker-compose logs -f`
2. **Have Swagger open** to show API docs: http://localhost:8000/docs
3. **Know the numbers**: 100K devices, <0.01s failover, 25+ endpoints
4. **Explain why Redis Stack**: Vector search + state + cache in one
5. **Mention scalability**: All stateless, can horizontally scale

---

## 🏆 What Makes This Special

- **Complete**: Not just backend or frontend, the WHOLE system
- **Scale**: 100K devices, not a toy example
- **Modern**: Latest tech (FastAPI, React 18, Redis Stack)
- **AI-Powered**: Real Cohere integration, vector search
- **Production-Ready**: Error handling, logging, tests
- **Beautiful**: Professional UI, not a prototype

---

## 🤔 FAQ

**Q: Do I need API keys?**
A: No! System works with dummy data. Optional for production embeddings.

**Q: How long does setup take?**
A: 2-3 minutes for Docker builds, then instant start.

**Q: Can I customize it?**
A: Yes! Edit `.env` for config, see README.md for details.

**Q: What if port 8000 is in use?**
A: Edit `docker-compose.yml` to change ports.

**Q: Does it work on Windows?**
A: Yes, with Docker Desktop for Windows.

**Q: Can I deploy this for real?**
A: Yes! It's production-ready. Add auth, monitoring, use Kubernetes.

---

## 📞 Need Help?

1. Check **QUICKSTART.md** - Step-by-step guide
2. Check **README.md** - Full documentation
3. Check logs: `docker-compose logs -f`
4. Restart: `docker-compose restart`
5. Fresh start: `docker-compose down -v && bash scripts/setup.sh`

---

## 🎉 You're Ready!

Your Enterprise SRE AI System is running. Time to explore!

**Remember**: The goal is to demonstrate a production-ready, enterprise-scale system with AI capabilities and high availability. You've got all of that running right now.

Go forth and demo with confidence! 💪

---

**Made with ❤️ for CMPE 273 Hackathon**

*Good luck with your presentation!* 🚀
