# SGE Dashboard

Strategic Grant Evaluation Dashboard - A comprehensive platform for managing grants, tasks, and impact metrics.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- Python 3.8+
- PostgreSQL
- npm or yarn

### Development Setup

```bash
# Clone the repository
git clone https://github.com/A1anMc/SGEDashboardJuly.git
cd SGEDashboardJuly

# Backend Setup
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend Setup  
cd frontend
npm install
npm run dev
```

### Production Deployment

The application is deployed on Render with the following services:

- **Backend API**: `https://sge-dashboard-api.onrender.com`
- **Frontend**: `https://sge-dashboard-web-new.onrender.com` (to be deployed)

## 📁 Project Structure

```
SGEDashboardJuly/
├── app/                    # FastAPI backend
│   ├── api/               # API endpoints
│   ├── core/              # Core configuration
│   ├── models/            # Database models
│   ├── services/          # Business logic
│   └── main.py            # FastAPI app
├── frontend/              # Next.js frontend
│   ├── src/
│   │   ├── app/          # App router pages
│   │   ├── components/   # React components
│   │   ├── services/     # API services
│   │   ├── hooks/        # Custom hooks
│   │   ├── types/        # TypeScript types
│   │   ├── lib/          # Configuration & utilities
│   │   └── utils/        # Utility functions
│   └── package.json
├── alembic/               # Database migrations
├── tests/                 # Backend tests
├── scripts/               # Utility scripts
├── docs/                  # Documentation
└── ARCHIVE/               # Archived old versions
```

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT
- **Deployment**: Render
- **Migrations**: Alembic

### Frontend
- **Framework**: Next.js 15
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: TanStack Query
- **UI Components**: Radix UI, Headless UI
- **Deployment**: Render

## 📚 Documentation

- [Architecture Overview](./docs/architecture.md)
- [API Documentation](./docs/api/README.md)
- [Development Guide](./docs/development/README.md)
- [Deployment Guide](./docs/deployment/README.md)
- [Task Management](./docs/task_management.md)
- [Strategic Handoff](./docs/strategic_handoff.md)

## 🔧 Environment Variables

### Backend
```env
DATABASE_URL=postgresql://user:password@localhost:5432/sge_dashboard
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
FRONTEND_URL=https://sge-dashboard-web-new.onrender.com
ENV=production
DEBUG=false
```

### Frontend
```env
NEXT_PUBLIC_API_URL=https://sge-dashboard-api.onrender.com
NEXT_PUBLIC_APP_NAME=SGE Dashboard
NODE_ENV=production
```

## 🚀 Features

- **Grant Management**: Track and manage grant opportunities with full CRUD operations
- **Task Management**: Organize tasks and workflows with comments and tags
- **Impact Metrics**: Monitor success rates and outcomes
- **Media Investments**: Track media campaigns
- **Real-time Updates**: Live data synchronization
- **Responsive Design**: Works on all devices
- **Database Integration**: Full PostgreSQL integration with migrations
- **API-First Design**: RESTful API with comprehensive endpoints

## 🔄 Current Status

### ✅ Completed
- **Backend**: Fully functional FastAPI with all endpoints restored
- **Database**: PostgreSQL configured with Alembic migrations
- **Frontend**: Next.js 15 app with direct backend integration
- **API Communication**: Frontend connects directly to backend API
- **Project Structure**: Cleaned up and organized

### 🚧 In Progress
- **Frontend Deployment**: Ready for Render deployment
- **Production Testing**: End-to-end testing of complete system

### 📋 Next Steps
1. Deploy frontend to Render
2. Test complete system integration
3. Add authentication system
4. Implement advanced features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support, email support@sgedashboard.com or create an issue in this repository.

## 🔗 Quick Links

- **Live Backend**: https://sge-dashboard-api.onrender.com/health
- **API Documentation**: https://sge-dashboard-api.onrender.com/api/docs
- **GitHub Repository**: https://github.com/A1anMc/SGEDashboardJuly
