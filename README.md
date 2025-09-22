# 🚀 Microservices Architecture Experiment

This is an experimental microservices architecture using Docker Compose, featuring:
- **BFF** (Flask) with productor SQS messages
- **Orders Service** (FastAPI) with load balancing
- **Background Workers** (Celery + Redis)  
- **Load Balancer** (HAProxy)
- **SQS Consumer** for message processing
- **PostgreSQL** database

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│     BFF     │───▶│     SQS     │───▶│   Consumer   │───▶│  HAProxy    │
│   :8001     │    │   Queue     │    │              │    │   :8080     │
│ (Products)  │    │             │    │              │    │             │
└─────────────┘    └─────────────┘    └──────────────┘    └─────────────┘
                                                                  │
                                                                  ▼
                                           ┌─────────────┬─────────────────┐
                                           │ Orders-1    │   Orders-2      │
                                           │ :3000       │   :3001         │
                                           └─────────────┴─────────────────┘
                                                      │
                                                      ▼
                                           ┌─────────────────────────────────┐
                                           │         PostgreSQL              │
                                           │         + Redis                 │
                                           │    (Database + Cache/Queue)     │
                                           └─────────────────────────────────┘
                                                      ▲
                                                      │
                                           ┌─────────────────────────────────┐
                                           │       Celery Workers            │
                                           │    (Background Tasks)           │
                                           └─────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone <your-repo>
cd <project-folder>

# Copy environment template
cp .env.example .env

# Edit with your values
nano .env
```

### 2. Configure AWS (Required for SQS)
```bash
# Configure AWS credentials
aws configure

# OR export directly
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

### 3. Update Environment
```bash
# Edit .env file
nano .env

# Minimum required changes:
SQS_QUEUE_URL=https://sqs.us-east-2.amazonaws.com/YOUR_ACCOUNT/your-queue.fifo
```

### 4. Run Everything
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## 📋 Services & Ports

| Service | URL | Purpose |
|---------|-----|---------|
| **Orders API** | http://localhost:3000 | Main API |
| **Orders API 2** | http://localhost:3001 | Load balanced instance |
| **HAProxy** | http://localhost:8080 | Load balancer |
| **HAProxy Stats** | http://localhost:8404/stats | Monitoring |
| **BFF** | http://localhost:8001 | Backend for Frontend |
| **PostgreSQL** | localhost:5432 | Database |
| **Redis** | localhost:6379 | Cache & Message Broker |

## 🔧 Configuration

### Environment Variables
All configuration is done via `.env` file:

```bash
# Database
POSTGRES_USER=user
POSTGRES_PASSWORD=your_secure_password

# Redis  
REDIS_PASSWORD=your_redis_password

# AWS
AWS_REGION=us-east-2
SQS_QUEUE_URL=https://sqs.your-region.amazonaws.com/account/queue-name

# Ports (optional)
ORDERS_PORT=3000
HAPROXY_PORT=8080
```

### HAProxy Configuration
Edit `./consumer-lb/app/load-balancer/haproxy.cfg` to modify load balancing settings.

## 🧪 Testing the Setup

### 1. Health Checks
```bash
# Check all services
docker-compose ps

# Test HAProxy
curl http://localhost:8080/health

# Test direct services
curl http://localhost:3000/health
curl http://localhost:3001/health
```

### 2. Load Balancing Test
```bash
# Multiple requests to see load balancing
for i in {1..10}; do
  curl http://localhost:8080/orders
  sleep 1
done
```

### 3. Background Tasks
```bash
# Check Celery workers
docker-compose logs worker-orders

# Check Redis
docker-compose exec redis redis-cli ping
```

## 🔍 Monitoring

### HAProxy Stats
Visit http://localhost:8404/stats (username: `admin`, password: `password`)

### Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f orders-service
docker-compose logs -f worker-orders
docker-compose logs -f consumer
```

### Redis Monitoring
```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Monitor commands
> MONITOR
> INFO
> KEYS *
```

## 🛠️ Development

### Making Changes
```bash
# Rebuild after code changes
docker-compose up -d --build

# Restart specific service
docker-compose restart orders-service

# View logs in real-time
docker-compose logs -f orders-service
```

### Database Operations
```bash
# Connect to PostgreSQL
docker-compose exec db psql -U user -d postgres

# Check orders database
docker-compose exec db psql -U user -d orders
```

## 🔒 Security Notes

- **Development Only**: Current configuration is for development/experimentation
- **Default Passwords**: Change all default passwords in `.env`
- **AWS Credentials**: Never commit AWS credentials to git
- **Production**: Use Docker secrets or external secret management for production

## 🏗️ Project Structure

```
├── docker-compose.yml          # Main orchestration
├── .env.example               # Environment template
├── bff/                       # Backend for Frontend
├── orders-service/            # Main orders microservice
├── consumer-lb/               # SQS consumer + HAProxy
│   ├── app/consumer/          # SQS message processor
│   └── app/load-balancer/     # HAProxy configuration
└── README.md                  # This file
```

## 🚧 Troubleshooting

### Common Issues

**Services won't start:**
```bash
# Check logs
docker-compose logs

# Rebuild everything
docker-compose down -v
docker-compose up -d --build
```

**Database connection issues:**
```bash
# Check database health
docker-compose exec db pg_isready -U user

# Reset database
docker-compose down -v
docker-compose up -d
```

**SQS Consumer not working:**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Check SQS queue exists
aws sqs list-queues --region us-east-2

# Check consumer logs
docker-compose logs consumer
```

## 📚 Tech Stack

- **🐳 Docker Compose** - Container orchestration
- **⚡ FastAPI** - Modern Python web framework
- **🐘 PostgreSQL** - Primary database
- **🔴 Redis** - Caching & message broker
- **🌶️ Celery** - Distributed task queue
- **⚖️ HAProxy** - Load balancer
- **☁️ AWS SQS** - Message queue
- **🔧 Gunicorn** - WSGI server

## 🤝 Contributing

This is an experimental project. Feel free to:
- Fork and experiment
- Submit issues
- Suggest improvements
- Share your learnings

## 📄 License

This project is for educational/experimental purposes.