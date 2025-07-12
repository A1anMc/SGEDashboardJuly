# SGE Dashboard Testing & Monitoring Scripts

This directory contains various scripts for testing, monitoring, and maintaining the SGE Dashboard application.

## 🧪 Testing Scripts

### `quick_test.py`
**Purpose**: Fast essential functionality tests  
**Usage**: `python scripts/quick_test.py`  
**Runtime**: ~10 seconds  

Tests:
- Critical imports
- Backend startup
- Database connection
- API health endpoint
- CORS configuration

### `continuous_testing.py`
**Purpose**: Comprehensive continuous testing with monitoring  
**Usage**: 
- Single run: `python scripts/continuous_testing.py --once`
- Continuous: `python scripts/continuous_testing.py --interval 300`

Features:
- Backend startup validation
- Database connectivity
- API endpoint testing
- CORS configuration validation
- PyTest suite execution
- Automatic alerting on failures
- JSON logging to `logs/test_results.json`

### `full_system_check.py`
**Purpose**: Complete system health validation  
**Usage**: `python scripts/full_system_check.py`  

Validates:
- Backend health
- Frontend availability
- All API endpoints
- CORS configuration
- Database connectivity

## 📊 Monitoring Scripts

### `monitor.py`
**Purpose**: Simple health monitoring for cron jobs  
**Usage**: `python scripts/monitor.py`  
**Runtime**: ~5 seconds  

Features:
- Health endpoint check
- CORS configuration validation
- Critical API endpoint testing
- JSON logging to `logs/monitor.log`
- Exit codes for automation

### `check-backend-health.sh`
**Purpose**: Backend health check script  
**Usage**: `./scripts/check-backend-health.sh [URL]`  

Features:
- Configurable backend URL
- Health endpoint validation
- Shell-friendly output

## 🔄 Automation Examples

### Cron Job Setup
```bash
# Run monitor every 5 minutes
*/5 * * * * cd /path/to/project && python scripts/monitor.py

# Run comprehensive tests every hour
0 * * * * cd /path/to/project && python scripts/continuous_testing.py --once
```

### Background Continuous Testing
```bash
# Start continuous testing with 3-minute intervals
python scripts/continuous_testing.py --interval 180 &

# Or use nohup for persistent background execution
nohup python scripts/continuous_testing.py --interval 300 > logs/continuous_testing.out 2>&1 &
```

## 📁 Log Files

All scripts create logs in the `logs/` directory:

- `logs/continuous_testing.log` - Continuous testing output
- `logs/test_results.json` - Latest test results (JSON)
- `logs/monitor.log` - Monitor script output
- `logs/continuous_testing.out` - Background process output

## 🚨 Alerting

The continuous testing script includes built-in alerting:
- Tracks consecutive failures
- Sends critical alerts after 3 consecutive failures
- Extensible for email/Slack/PagerDuty integration

## 🔧 Configuration

### Environment Variables
- `BACKEND_URL` - Override backend URL (default: http://localhost:8000)
- `FRONTEND_URL` - Override frontend URL (default: http://localhost:3000)

### Timeouts
- API calls: 10 seconds
- Test execution: 60-120 seconds
- Health checks: 5 seconds

## 📋 Best Practices

1. **Development**: Use `quick_test.py` for fast feedback
2. **CI/CD**: Use `continuous_testing.py --once` in pipelines
3. **Production**: Use `monitor.py` for health monitoring
4. **Debugging**: Check logs in `logs/` directory
5. **Background**: Use continuous testing during development

## 🔍 Troubleshooting

### Common Issues

**Tests failing with "Connection refused"**
- Ensure backend is running: `make backend` or `python -m uvicorn app.main:app --reload`
- Check port 8000 is available

**CORS tests failing**
- Verify CORS configuration includes production domains
- Check `/api/debug/cors` endpoint

**Import errors**
- Verify virtual environment is activated
- Check all dependencies are installed: `pip install -r requirements.txt`

### Debug Commands
```bash
# Check backend status
curl http://localhost:8000/api/v1/health

# Check CORS configuration
curl http://localhost:8000/api/debug/cors

# Run single test
python -c "from app.main import create_app; print('Backend OK')"
```

## 🚀 Quick Start

1. **Start backend**: `make backend`
2. **Run quick test**: `python scripts/quick_test.py`
3. **Start monitoring**: `python scripts/continuous_testing.py --interval 300 &`
4. **Check logs**: `tail -f logs/continuous_testing.log`

This testing infrastructure helps catch issues early and ensures system reliability! 🎯 