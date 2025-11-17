#!/bin/bash

echo "=================================================="
echo "Enterprise SRE System - Setup Script"
echo "=================================================="
echo ""

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "✅ Docker found: $(docker --version)"

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker Compose found: $(docker-compose --version)"
echo ""

# Stop any existing containers
echo "🧹 Cleaning up existing containers..."
docker-compose down -v 2>/dev/null
echo ""

# Build and start services
echo "🚀 Building and starting services..."
echo "   This may take a few minutes..."
echo ""
docker-compose build
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo ""
echo "🏥 Checking service health..."
echo ""

# Check MQTT
if docker ps | grep -q mqtt-broker; then
    echo "✅ MQTT Broker is running (port 1883)"
else
    echo "❌ MQTT Broker failed to start"
fi

# Check RabbitMQ
if docker ps | grep -q rabbitmq; then
    echo "✅ RabbitMQ is running (port 5672, management: 15672)"
else
    echo "❌ RabbitMQ failed to start"
fi

# Check Redis Region 1
if docker ps | grep -q redis-region1; then
    echo "✅ Redis Region 1 is running (port 6379)"
else
    echo "❌ Redis Region 1 failed to start"
fi

# Check Redis Region 2
if docker ps | grep -q redis-region2; then
    echo "✅ Redis Region 2 is running (port 6380)"
else
    echo "❌ Redis Region 2 failed to start"
fi

# Check Backend Region 1
if docker ps | grep -q backend-region1; then
    echo "✅ Backend Region 1 is running (port 8000)"
else
    echo "❌ Backend Region 1 failed to start"
fi

# Check Backend Region 2
if docker ps | grep -q backend-region2; then
    echo "✅ Backend Region 2 is running (port 8100)"
else
    echo "❌ Backend Region 2 failed to start"
fi

# Check Frontend
if docker ps | grep -q frontend; then
    echo "✅ Frontend is running (port 3000)"
else
    echo "❌ Frontend failed to start"
fi

# Check Simulators
if docker ps | grep -q iot-simulator; then
    echo "✅ IoT Simulator is running"
else
    echo "❌ IoT Simulator failed to start"
fi

if docker ps | grep -q user-simulator; then
    echo "✅ User Simulator is running"
else
    echo "❌ User Simulator failed to start"
fi

echo ""
echo "=================================================="
echo "🎉 Setup Complete!"
echo "=================================================="
echo ""
echo "Access the system:"
echo ""
echo "  Frontend Dashboard:    http://localhost:3000"
echo "  Backend API Region 1:  http://localhost:8000/docs"
echo "  Backend API Region 2:  http://localhost:8100/docs"
echo "  RabbitMQ Management:   http://localhost:15672 (admin/admin123)"
echo "  Redis Insight R1:      http://localhost:8001"
echo "  Redis Insight R2:      http://localhost:8002"
echo ""
echo "Useful commands:"
echo ""
echo "  View logs:             docker-compose logs -f"
echo "  Stop all services:     docker-compose down"
echo "  Restart services:      docker-compose restart"
echo "  Test system:           python scripts/test_system.py"
echo "  Test failover:         python scripts/test_failover.py"
echo ""
echo "=================================================="
