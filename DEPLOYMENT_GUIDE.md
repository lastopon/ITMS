# 🐳 ITMS Docker Deployment Guide

## ภาพรวมระบบ

**ITMS (IT Management System)** เป็นระบบจัดการ IT ที่พัฒนาด้วย FastAPI และ PostgreSQL พร้อม Docker containerization สำหรับการ deploy ที่ง่ายและมีประสิทธิภาพ

## 🏗️ **สถาปัตยกรรมระบบ**

```
┌─────────────────────────────────────────────────────────────────┐
│                        ITMS System                             │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (Static Files)                                       │
│  ├── Login Page (login.html)                                   │
│  ├── Dashboard (homepage.html)                                 │
│  ├── Booking System (booking.html)                             │
│  └── Settings (settings.html)                                  │
├─────────────────────────────────────────────────────────────────┤
│  Backend (FastAPI)                                             │
│  ├── 35+ REST API Endpoints                                    │
│  ├── Real-time Notifications                                   │
│  ├── Email System (SMTP)                                       │
│  ├── Booking Management                                        │
│  └── User Authentication                                       │
├─────────────────────────────────────────────────────────────────┤
│  Database (PostgreSQL 15)                                      │
│  ├── Users & Roles                                             │
│  ├── Bookings & Resources                                      │
│  ├── Notifications                                             │
│  └── Audit Logs                                                │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 **Quick Start**

### 1. ข้อกำหนดเบื้องต้น

```bash
# ตรวจสอบ Docker
docker --version          # Docker 20.10+
docker-compose --version  # Docker Compose 2.0+

# ตรวจสอบ Memory และ Storage
free -h                   # RAM: 2GB+ แนะนำ
df -h                     # Disk: 5GB+ แนะนำ
```

### 2. การติดตั้งแบบง่าย

```bash
# Clone หรือ copy โปรเจค
cd /path/to/ITMS

# เริ่มต้นระบบ (ครั้งแรก)
docker-compose up --build -d

# ตรวจสอบสถานะ
docker-compose ps

# ดู logs
docker-compose logs -f
```

### 3. ตรวจสอบการทำงาน

```bash
# ทดสอบ API
curl http://localhost:8000/health

# ทดสอบ Database
curl http://localhost:8000/database/test

# เข้าใช้งานระบบ
open http://localhost:8000/static/login.html
```

## ⚙️ **การกำหนดค่า**

### Environment Variables

สร้างไฟล์ `.env`:

```env
# Database Configuration
DATABASE_URL=postgresql://itms_user:itms_password@db:5432/itms_db

# Email Configuration (SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
SMTP_USE_TLS=true

# Security
SECRET_KEY=your-super-secret-key-change-this
JWT_EXPIRE_MINUTES=60

# Application Settings
APP_DEBUG=false
APP_ENVIRONMENT=production
```

### Docker Compose Configuration

```yaml
# docker-compose.yml
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://itms_user:itms_password@db:5432/itms_db
    volumes:
      - .:/app
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=itms_db
      - POSTGRES_USER=itms_user
      - POSTGRES_PASSWORD=itms_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

## 📊 **การจัดการระบบ**

### การเริ่มต้น/หยุด Services

```bash
# เริ่มระบบ
docker-compose up -d

# หยุดระบบ
docker-compose down

# Restart ระบบ
docker-compose restart

# Rebuild และเริ่มใหม่
docker-compose up --build -d
```

### การตรวจสอบสถานะ

```bash
# ดู Container status
docker-compose ps

# ดู Resource usage
docker stats itms-web-1 itms-db-1

# ดู Logs
docker-compose logs web    # API logs
docker-compose logs db     # Database logs

# เข้าไปใน Container
docker-compose exec web bash
docker-compose exec db psql -U itms_user -d itms_db
```

### การ Backup ข้อมูล

```bash
# Backup Database
docker-compose exec db pg_dump -U itms_user itms_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore Database
docker-compose exec -T db psql -U itms_user -d itms_db < backup_file.sql

# Backup Application Files
tar -czf itms_backup_$(date +%Y%m%d).tar.gz static/ main.py requirements.txt
```

## 🔧 **การปรับแต่งประสิทธิภาพ**

### 1. Database Optimization

```yaml
# docker-compose.yml - PostgreSQL tuning
db:
  image: postgres:15
  command: >
    postgres
    -c shared_buffers=256MB
    -c effective_cache_size=1GB
    -c max_connections=100
    -c work_mem=4MB
```

### 2. Application Scaling

```yaml
# docker-compose.yml - Multiple web instances
web:
  build: .
  ports:
    - "8000-8003:8000"
  deploy:
    replicas: 4
```

### 3. Nginx Reverse Proxy

```nginx
# nginx.conf
upstream itms_backend {
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
    server localhost:8003;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://itms_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static/ {
        expires 1d;
        add_header Cache-Control "public, immutable";
    }
}
```

## 🔒 **การรักษาความปลอดภัย**

### 1. HTTPS Configuration

```yaml
# docker-compose.yml with SSL
web:
  ports:
    - "443:8000"
  environment:
    - SSL_CERT_PATH=/certs/cert.pem
    - SSL_KEY_PATH=/certs/key.pem
  volumes:
    - ./certs:/certs:ro
```

### 2. Database Security

```yaml
db:
  environment:
    - POSTGRES_DB=itms_db
    - POSTGRES_USER=itms_user
    - POSTGRES_PASSWORD=${DB_PASSWORD}  # Use env file
  # Remove port exposure for production
  # ports:
  #   - "5432:5432"
```

### 3. Network Isolation

```yaml
networks:
  itms_network:
    driver: bridge
    internal: true  # Isolate from external networks
  
  web_network:
    driver: bridge
```

## 📈 **Monitoring และ Logging**

### 1. Health Checks

```bash
# API Health Check
curl -f http://localhost:8000/health || exit 1

# Database Check
curl -f http://localhost:8000/database/test || exit 1

# Complete System Check
docker-compose exec web python3 -c "
import requests
import sys
try:
    r = requests.get('http://localhost:8000/health')
    if r.status_code == 200:
        print('✅ System healthy')
        sys.exit(0)
    else:
        print('❌ System unhealthy')
        sys.exit(1)
except:
    print('❌ System down')
    sys.exit(1)
"
```

### 2. Log Management

```yaml
# docker-compose.yml - Logging configuration
web:
  logging:
    driver: "json-file"
    options:
      max-size: "10m"
      max-file: "3"
      labels: "service=web"

db:
  logging:
    driver: "json-file"
    options:
      max-size: "10m"
      max-file: "3"
      labels: "service=database"
```

### 3. Metrics Collection

```bash
# System metrics script
#!/bin/bash
echo "$(date): ITMS System Metrics"
echo "================================"

# Container stats
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

# Database size
docker-compose exec db psql -U itms_user -d itms_db -c "
SELECT 
    pg_size_pretty(pg_database_size('itms_db')) as database_size,
    COUNT(*) as total_connections
FROM pg_stat_activity 
WHERE datname = 'itms_db';
"

# API response time
curl -w "@curl-format.txt" -s -o /dev/null http://localhost:8000/health
```

## 🚨 **Troubleshooting**

### ปัญหาที่พบบ่อย

#### 1. Container ไม่เริ่มต้น

```bash
# ตรวจสอบ logs
docker-compose logs web

# ตรวจสอบ port conflicts
netstat -tulpn | grep :8000

# ลบ containers เก่า
docker-compose down --volumes
docker system prune -a
```

#### 2. Database Connection Error

```bash
# ตรวจสอบ PostgreSQL
docker-compose exec db pg_isready -U itms_user

# ตรวจสอบ password
docker-compose exec db psql -U itms_user -d itms_db -c "SELECT version();"

# Reset database
docker-compose down -v
docker-compose up -d db
```

#### 3. Permission Errors

```bash
# แก้ไข file permissions
sudo chown -R $USER:$USER .
chmod -R 755 static/

# Docker permissions
sudo usermod -aG docker $USER
newgrp docker
```

#### 4. Memory/Performance Issues

```bash
# ตรวจสอบ resource usage
docker stats

# Increase Docker memory limit
# Docker Desktop: Settings -> Resources -> Memory (4GB+)

# Clean up unused resources
docker system prune -a --volumes
```

## 🌐 **Production Deployment**

### 1. Infrastructure Requirements

**Minimum Specifications:**
- CPU: 2 cores
- RAM: 4GB
- Storage: 20GB SSD
- Network: 1Gbps

**Recommended Specifications:**
- CPU: 4 cores
- RAM: 8GB
- Storage: 50GB SSD
- Network: 10Gbps

### 2. Production Checklist

```bash
# ✅ Security
- [ ] Change default passwords
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall
- [ ] Set up VPN access
- [ ] Enable audit logging

# ✅ Performance
- [ ] Configure database tuning
- [ ] Set up caching (Redis)
- [ ] Configure CDN for static files
- [ ] Enable gzip compression
- [ ] Set up load balancing

# ✅ Monitoring
- [ ] Set up health checks
- [ ] Configure alerts
- [ ] Enable log aggregation
- [ ] Set up metrics collection
- [ ] Configure backup automation

# ✅ Compliance
- [ ] Data privacy compliance
- [ ] Security scanning
- [ ] Vulnerability assessment
- [ ] Documentation updates
- [ ] Staff training
```

### 3. Auto-Deployment Script

```bash
#!/bin/bash
# deploy.sh - Production deployment script

set -e

echo "🚀 Starting ITMS production deployment..."

# Backup current system
echo "📦 Creating backup..."
./backup.sh

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Build and deploy
echo "🔨 Building containers..."
docker-compose -f docker-compose.prod.yml build --no-cache

echo "🏁 Deploying..."
docker-compose -f docker-compose.prod.yml up -d

# Health check
echo "🔍 Running health checks..."
sleep 30
curl -f http://localhost/health || {
    echo "❌ Health check failed, rolling back..."
    docker-compose -f docker-compose.prod.yml down
    docker-compose -f docker-compose.prod.yml up -d
    exit 1
}

echo "✅ Deployment completed successfully!"
echo "📊 System status:"
docker-compose -f docker-compose.prod.yml ps
```

## 📞 **การสนับสนุน**

### การรายงานปัญหา

1. **เก็บ logs:** `docker-compose logs > system.log`
2. **ระบุเวอร์ชัน:** `curl http://localhost:8000/health`
3. **ข้อมูลระบบ:** `docker version && docker-compose version`
4. **สเต็ปการทำซ้ำ:** รายละเอียดการเกิดปัญหา

### เอกสารเพิ่มเติม

- 📖 **API Documentation:** http://localhost:8000/docs
- 🧪 **Testing Guide:** [TESTING_GUIDE.md](./TESTING_GUIDE.md)
- 📚 **Learning Guide:** [PROJECT_LEARNING_GUIDE.md](./PROJECT_LEARNING_GUIDE.md)
- 🐳 **Docker Best Practices:** [Official Docker Documentation](https://docs.docker.com/)

---

## 📝 **สรุป**

ITMS เป็นระบบที่พร้อมใช้งานใน production พร้อมฟีเจอร์ครบครัน:

- ✅ **35+ API Endpoints** - RESTful APIs ครบถ้วน
- ✅ **Real-time Notifications** - การแจ้งเตือนแบบเรียลไทม์
- ✅ **Email System** - ระบบอีเมลพร้อมเทมเพลต
- ✅ **Booking Management** - จัดการการจองครบครัน
- ✅ **Mobile Responsive** - รองรับทุกอุปกรณ์
- ✅ **Docker Ready** - พร้อม deploy ด้วย containers
- ✅ **PostgreSQL Database** - ฐานข้อมูลที่มั่นคงและเชื่อถือได้
- ✅ **Production Security** - ความปลอดภัยระดับ enterprise

🎉 **Happy Deploying!**