# VidhiChakshu (विधि-चक्षु) 3.0 - CI/CD & Production Deployment Guide

## 📋 Overview

This guide covers the containerization, orchestration, and continuous integration/deployment setup for VidhiChakshu 3.0:
- **Frontend**: React (Vite) + TypeScript + TailwindCSS + Radix UI (Port: 8080)
- **API Gateway**: Node.js (Express) with ArrayBuffer streaming (Port: 3000)
- **ML Intelligence Engine**: Python (FastAPI + PyMuPDF + ReportLab + faster-whisper + NetworkX RAG) (Port: 8000)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   GitHub Actions                     │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │  Frontend   │  │  Node Gateway│  │  Python ML │ │
│  │  Lint/Build │  │  Lint/Test   │  │  Lint/Test │ │
│  └──────┬──────┘  └──────┬───────┘  └─────┬──────┘ │
│         │                 │                 │        │
│         └─────────────────┴─────────────────┘        │
│                     │                                │
│         ┌───────────▼──────────────┐                │
│         │  Docker Build & Push     │                │
│         │  (Docker Hub: beast2711) │                │
│         └───────────┬──────────────┘                │
│                     │                                │
│         ┌───────────▼──────────────┐                │
│         │  Security Scan (Trivy)   │                │
│         │  Gitleaks Secret Audit   │                │
│         └──────────────────────────┘                │
│                                                       │
└─────────────────────────────────────────────────────┘
         │
         │ (on main branch push)
         ▼
    docker compose up -d
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git configured
- Docker Hub account (for image pushing)

### 1. Clone & Setup
```bash
git clone https://github.com/BEAST-AMMAR/vidhichakshu.git
cd "vidhichakshu"
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration
nano .env
```

Required variables:
```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
OPENROUTER_API_KEY=your-api-key
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

### 3. Build & Run Locally
```bash
# Build all images
make build

# Launch the core stack
make up

# View aggregated logs
make logs

# Check service health
./scripts/health-check.sh
```

## 📦 Container Registry

### Frontend (Nginx SPA)
```
Image: beast2711/vidhichakshu-frontend:latest
Port: 8080 (Mapped to 80 internal)
Size: ~50MB
Features:
  - Multi-stage Node 20 build
  - Gzip compression
  - SPA fallback routing
  - Static asset caching
```

### Node Gateway (Express)
```
Image: beast2711/vidhichakshu-node:latest
Port: 3000
Features:
  - Fail-fast authentication validation
  - Streaming arraybuffer for certified PDF reports
  - Rate limiting & Helmet security headers
```

### Python ML Engine (FastAPI)
```
Image: beast2711/vidhichakshu-python:latest
Port: 8000
Features:
  - PyMuPDF text & scanned image processing
  - Paleography VLM dispatcher for ancient scripts
  - ReportLab 5.0 certified legal PDF compiler
  - NetworkX statutory property & constitutional RAG
```

## 🌐 Cloud Deployment Options
- **Docker Compose**: Core stack (`docker-compose.yml`) or extended stack (`docker-compose.extended.yml`).
- **AWS CloudFormation**: Automated single-command deployment using `aws/deploy-to-aws.sh` and `aws/cloudformation.yaml`.
