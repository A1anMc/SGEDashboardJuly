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
git clone <repository-url>
cd sge-dashboard

# Backend Setup
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend Setup  
cd ../frontend
npm install
npm run dev
```

### Production Deployment

The application is deployed on Render with the following services:

- **Backend API**: `https://sge-dashboard-api.onrender.com`
- **Frontend**: `https://sge-dashboard-web-new.onrender.com`

## 📁 Project Structure

```
sge-dashboard/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── main.py         # FastAPI app
│   └── requirements.txt
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # App router pages
│   │   ├── components/    # React components
│   │   ├── services/      # API services
│   │   ├── hooks/         # Custom hooks
│   │   ├── types/         # TypeScript types
│   │   └── utils/         # Utility functions
│   └── package.json
└── docs/                  # Documentation
```

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT
- **Deployment**: Render

### Frontend
- **Framework**: Next.js 15
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: TanStack Query
- **UI Components**: Radix UI, Headless UI
- **Deployment**: Render

## 📚 Documentation

- [Architecture Overview](./docs/architecture/README.md)
- [API Documentation](./docs/api/README.md)
- [Development Guide](./docs/development/README.md)
- [Deployment Guide](./docs/deployment/README.md)

## 🔧 Environment Variables

### Backend
```env
DATABASE_URL=postgresql://user:password@localhost:5432/sge_dashboard
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
FRONTEND_URL=https://sge-dashboard-web-new.onrender.com
```

### Frontend
```env
NEXT_PUBLIC_API_URL=https://sge-dashboard-api.onrender.com
NODE_ENV=production
```

## 🚀 Features

- **Grant Management**: Track and manage grant opportunities
- **Task Management**: Organize tasks and workflows
- **Impact Metrics**: Monitor success rates and outcomes
- **Media Investments**: Track media campaigns
- **Real-time Updates**: Live data synchronization
- **Responsive Design**: Works on all devices

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
