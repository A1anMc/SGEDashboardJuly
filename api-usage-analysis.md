# API Usage Analysis - Potential Charge Sources

## Executive Summary

Based on your Shadow Goose Entertainment Dashboard codebase, I've identified several potential sources of API usage charges. The main culprits are likely **hosting services**, **automated scrapers**, and **external service integrations**.

## 🔍 Identified Charge Sources

### 1. **Hosting Services (Primary Suspect)**

#### Render.com Services
From your `render.yaml`, you're running:
- **Backend API**: `sge-dashboard-api` (Python/FastAPI with 4 workers)
- **Frontend**: `sge-dashboard` (Node.js/Next.js)
- **PostgreSQL Database**: `sge-dashboard-db` (Starter plan)

**Cost Factors:**
- CPU/Memory usage from web services
- Database operations and storage
- Network bandwidth from API calls
- Auto-deployment triggers

#### Recommended Actions:
```bash
# Check your Render dashboard for usage metrics
# Look for: Compute hours, bandwidth usage, database queries
```

### 2. **Automated Grant Scrapers (High Activity)**

Your application runs **daily automated scrapers** that make HTTP requests to external websites:

#### Active Scrapers:
- **business.gov.au** - Scrapes grant listings and detail pages
- **grantconnect.gov.au** - Uses JSON API endpoints
- **community_grants** - Additional grant source
- **grants_gov** - Government grant API

#### Daily Schedule:
```python
# From SGE_Dashboard_Scaffold/backend/main.py:52
@repeat_every(seconds=60 * 60 * 24)  # Runs DAILY
async def scrape_grants():
    # Makes multiple HTTP requests per day
```

#### Manual Trigger Usage:
Your app also allows manual scraper runs through the UI, which could be triggered frequently.

**Cost Impact:**
- Each scraper run makes dozens of HTTP requests
- Daily automated runs = 365 runs/year minimum
- Manual runs add additional API calls
- Each grant detail page requires a separate HTTP request

### 3. **External Service Integrations**

#### Configured Services (Potential Charges):
1. **SendGrid** (Email Service)
   - Email sending for notifications
   - Task assignments and updates
   
2. **Sentry** (Error Monitoring)
   - Error tracking and performance monitoring
   - Transaction sampling at 100% rate

3. **Render PostgreSQL**
   - Database operations
   - Connection pooling (5 connections configured)

#### From Configuration Files:
```python
# Potential API keys that could be active:
SENDGRID_API_KEY
SENTRY_DSN
BUSINESS_GOV_API_KEY
GRANTS_GOV_API_KEY
AIRTABLE_API_KEY  # Not currently used but configured
```

### 4. **Database Usage Patterns**

#### High-Frequency Operations:
- Grant scraping saves/updates multiple records daily
- React Query polling (frontend refetches every 10 seconds)
- Database connection pooling with automatic retries

```python
# High-frequency settings that increase DB usage:
DATABASE_POOL_SIZE: 5
DATABASE_MAX_OVERFLOW: 10
DATABASE_RETRY_LIMIT: 5
```

## 🎯 Immediate Cost Reduction Steps

### 1. **Verify Active Services**
Check which services are actually being used:

```bash
# Check environment variables in your deployment
echo $SENDGRID_API_KEY
echo $SENTRY_DSN
```

### 2. **Optimize Scraper Frequency**
Consider reducing scraper frequency:
- Change from daily to weekly
- Implement smart scheduling (only scrape when new grants are likely)
- Add rate limiting between requests

### 3. **Review Render Usage**
In your Render dashboard:
- Check **Billing** section for service breakdown
- Look at **Metrics** for resource usage
- Consider downgrading to free tier if possible

### 4. **Database Optimization**
- Reduce polling frequency in frontend
- Optimize query patterns
- Consider caching frequently accessed data

## 📊 Cost Breakdown Estimates

### Render.com Likely Costs:
- **Backend Web Service**: $7-25/month (depending on usage)
- **Frontend Web Service**: $7-25/month 
- **PostgreSQL Starter**: $7/month
- **Bandwidth**: Variable based on API calls

### External Services:
- **SendGrid**: $14.95/month for basic plan (if sending emails)
- **Sentry**: $26/month for error monitoring (if configured)

## 🔧 Quick Actions to Take Now

1. **Check Render Dashboard**: Look at your billing breakdown
2. **Disable Unused Services**: Remove any API keys you're not using
3. **Reduce Scraper Frequency**: Consider weekly instead of daily
4. **Monitor Frontend Polling**: Reduce React Query refetch intervals

## 📝 Next Steps

Would you like me to:
1. Help you optimize the scraper scheduling?
2. Review your Render service configuration?
3. Implement cost-saving measures in the code?
4. Set up usage monitoring and alerts?

The most likely culprit is your **Render hosting costs** combined with the **daily automated scrapers** generating high API/bandwidth usage.