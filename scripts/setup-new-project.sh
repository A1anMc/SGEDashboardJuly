#!/bin/bash

# New Full-Stack Project Setup Script
# Usage: ./scripts/setup-new-project.sh <project-name>

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if project name is provided
if [ $# -eq 0 ]; then
    error "Please provide a project name"
    echo "Usage: $0 <project-name>"
    exit 1
fi

PROJECT_NAME=$1
PROJECT_DIR="$PROJECT_NAME"

log "Setting up new full-stack project: $PROJECT_NAME"

# Create project directory
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Initialize git repository
git init

# Create project structure
log "Creating project structure..."

# Backend structure
mkdir -p app/{api/v1/endpoints,core,db,models,schemas,services,templates}
mkdir -p tests
mkdir -p alembic/versions

# Frontend structure
mkdir -p frontend/{src/{app,components,hooks,lib,services,types,utils},public}
mkdir -p frontend/src/app/{api,error,not-found}
mkdir -p frontend/src/components/{ui,layout}

# Scripts directory
mkdir -p scripts

# Create backend files
log "Creating backend files..."

# requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
httpx==0.25.2
pytest==7.4.3
pytest-asyncio==0.21.1
ruff==0.1.6
black==23.11.0
EOF

# app/main.py
cat > app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title="Your App API",
    description="API for your full-stack application",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to Your App API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "backend"}
EOF

# app/core/config.py
cat > app/core/config.py << 'EOF'
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Core settings
    PROJECT_NAME: str = "Your App"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this"
    JWT_SECRET_KEY: str = "your-jwt-secret-key-change-this"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    # Frontend URL
    FRONTEND_URL: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"

settings = Settings()
EOF

# app/api/v1/api.py
cat > app/api/v1/api.py << 'EOF'
from fastapi import APIRouter
from app.api.v1.endpoints import health

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
EOF

# app/api/v1/endpoints/health.py
cat > app/api/v1/endpoints/health.py << 'EOF'
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "backend"}
EOF

# Create frontend files
log "Creating frontend files..."

# frontend/package.json
cat > frontend/package.json << 'EOF'
{
  "name": "your-app-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "PORT=$PORT node .next/standalone/server.js",
    "lint": "next lint",
    "type-check": "tsc --noEmit",
    "test": "jest",
    "format": "prettier --write \"src/**/*.{ts,tsx,js,jsx,json,md}\""
  },
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "axios": "^1.6.0",
    "@tanstack/react-query": "^5.0.0",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "typescript": "^5.0.0",
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0"
  },
  "devDependencies": {
    "eslint": "^8.0.0",
    "eslint-config-next": "14.0.0",
    "prettier": "^3.0.0",
    "jest": "^29.0.0",
    "@testing-library/react": "^13.0.0",
    "@testing-library/jest-dom": "^6.0.0"
  }
}
EOF

# frontend/next.config.js
cat > frontend/next.config.js << 'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  poweredByHeader: false,
  compress: true,
  env: {
    BACKEND_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  headers: async () => [
    {
      source: '/:path*',
      headers: [
        { key: 'X-Frame-Options', value: 'DENY' },
        { key: 'X-Content-Type-Options', value: 'nosniff' },
        { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
      ],
    },
  ],
}

module.exports = nextConfig
EOF

# frontend/tailwind.config.js
cat > frontend/tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
EOF

# frontend/postcss.config.js
cat > frontend/postcss.config.js << 'EOF'
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF

# frontend/tsconfig.json
cat > frontend/tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "es6"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
EOF

# frontend/src/app/layout.tsx
cat > frontend/src/app/layout.tsx << 'EOF'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Your App',
  description: 'Your full-stack application',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
EOF

# frontend/src/app/page.tsx
cat > frontend/src/app/page.tsx << 'EOF'
export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm lg:flex">
        <h1 className="text-4xl font-bold">Welcome to Your App</h1>
        <p className="text-lg">Your full-stack application is ready!</p>
      </div>
    </main>
  )
}
EOF

# frontend/src/app/globals.css
cat > frontend/src/app/globals.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;
EOF

# Create deployment files
log "Creating deployment files..."

# render.yaml
cat > render.yaml << 'EOF'
services:
  # Backend API Service
  - type: web
    name: your-app-backend
    env: python
    buildCommand: |
      pip install -r requirements.txt
    startCommand: |
      gunicorn app.main:app --bind 0.0.0.0:$PORT --workers 2 --timeout 300
    envVars:
      - key: RENDER
        value: "true"
      - key: ENVIRONMENT
        value: production
      - key: DEBUG
        value: "false"
      - key: DATABASE_URL
        sync: false
      - key: SECRET_KEY
        generateValue: true
      - key: JWT_SECRET_KEY
        generateValue: true
      - key: FRONTEND_URL
        value: "https://your-app-frontend.onrender.com"
      - key: CORS_ORIGINS
        value: '["https://your-app-frontend.onrender.com", "https://*.onrender.com"]'
    healthCheckPath: /health
    autoDeploy: true
    scaling:
      minInstances: 1
      maxInstances: 2
      targetMemoryPercent: 70
      targetCPUPercent: 70
    
  # Frontend Service
  - type: web
    name: your-app-frontend
    env: node
    buildCommand: |
      cd frontend
      npm ci --only=production
      npm run build
    startCommand: |
      cd frontend
      PORT=$PORT node .next/standalone/server.js
    envVars:
      - key: NEXT_PUBLIC_API_URL
        value: "https://your-app-backend.onrender.com"
      - key: NODE_ENV
        value: production
      - key: PORT
        value: "3000"
    healthCheckPath: /
    autoDeploy: true
    scaling:
      minInstances: 1
      maxInstances: 2
      targetMemoryPercent: 70
      targetCPUPercent: 70
EOF

# .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/

# Environment variables
.env
.env.local
.env.production

# Database
*.db
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Next.js
.next/
out/
.vercel

# Testing
.coverage
.pytest_cache/
htmlcov/

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp
EOF

# README.md
cat > README.md << 'EOF'
# Your App

A full-stack application built with FastAPI and Next.js.

## Features

- FastAPI backend with automatic API documentation
- Next.js frontend with TypeScript
- PostgreSQL database with SQLAlchemy ORM
- Automated deployment with Render
- Health checks and monitoring

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- PostgreSQL (for production)

### Development Setup

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd your-app
   ```

2. Set up the backend:
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Set up environment variables
   cp .env.example .env
   # Edit .env with your configuration
   
   # Run the backend
   uvicorn app.main:app --reload
   ```

3. Set up the frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. Access the application:
   - Backend API: http://localhost:8000
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8000/docs

## Deployment

This project is configured for deployment on Render. The `render.yaml` file contains the configuration for both backend and frontend services.

### Manual Deployment

1. Push your code to GitHub
2. Connect your repository to Render
3. Set up environment variables in the Render dashboard
4. Deploy both services

### Automated Deployment

Use the deployment script:
```bash
./scripts/deploy.sh
```

## Project Structure

```
├── app/                    # Backend application
│   ├── api/               # API endpoints
│   ├── core/              # Core configuration
│   ├── db/                # Database models and session
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   └── services/          # Business logic
├── frontend/              # Next.js frontend
│   ├── src/
│   │   ├── app/          # Next.js app router
│   │   ├── components/   # React components
│   │   └── services/     # API client services
├── scripts/               # Deployment and utility scripts
├── tests/                 # Backend tests
└── render.yaml           # Render deployment configuration
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
EOF

# Make scripts executable
chmod +x scripts/deploy.sh

success "Project setup completed!"

echo
log "Next steps:"
echo "1. cd $PROJECT_DIR"
echo "2. Update the URLs in render.yaml with your actual service names"
echo "3. Set up your database (PostgreSQL recommended for production)"
echo "4. Configure environment variables"
echo "5. Push to GitHub and connect to Render"
echo
log "Happy coding! 🚀" 