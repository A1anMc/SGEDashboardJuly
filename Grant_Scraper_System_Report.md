# Grant Scraper System & API Connections Report

## Executive Summary

Your SGE Dashboard includes a comprehensive grant scraper system designed to automatically collect grant information from multiple Australian government sources. The system features a modular architecture with automated data collection, intelligent processing, and comprehensive monitoring capabilities.

## 🔍 Current Scraper System Overview

### Active Scrapers

Your system currently implements **4 main scrapers**:

1. **Business.gov.au Scraper** (`BusinessGovScraper`)
   - **Target**: Australian Government Business Grants
   - **Method**: Web scraping using BeautifulSoup
   - **Base URL**: `https://business.gov.au/grants-and-programs`
   - **Status**: Fully implemented

2. **GrantConnect Scraper** (`GrantConnectScraper`)
   - **Target**: GrantConnect Portal (grants.gov.au)
   - **Method**: API-based scraping
   - **Base URL**: `https://www.grants.gov.au/api/v1/grants`
   - **Status**: Fully implemented with API integration

3. **Custom Multi-Source Scraper** (`CustomScraper`)
   - **Target**: Arts.gov.au & Screen Australia
   - **Method**: Advanced web scraping
   - **URLs**: 
     - `https://www.arts.gov.au/funding-and-support`
     - `https://www.screenaustralia.gov.au/funding-and-support`
   - **Status**: Implemented with intelligent parsing

4. **Dummy Scraper** (`DummyScraper`)
   - **Purpose**: Testing and development
   - **Function**: Generates test data for system validation
   - **Status**: Active for development/testing

### Scraper Architecture

```
ScraperService (Main Controller)
├── BaseScraper (Abstract Base Class)
├── BusinessGovScraper (Web Scraping)
├── GrantConnectScraper (API-based)
├── CustomScraper (Multi-source)
└── DummyScraper (Testing)
```

## 🔗 API Connections & External Services

### 1. Government Grant APIs

**GrantConnect API** (grants.gov.au)
- **Type**: RESTful API
- **Endpoints**:
  - Search: `/api/v1/grants/search`
  - Details: `/api/v1/grants/{grant_id}`
- **Authentication**: No API key required (public API)
- **Rate Limiting**: Built-in with respect delays
- **Data Format**: JSON responses with structured grant data

### 2. Database Connections

**Primary Database**:
- **Type**: PostgreSQL (via Supabase)
- **URL**: Configured via `DATABASE_URL` environment variable
- **Connection Pool**: 10 connections with 20 overflow
- **Features**: 
  - Automatic retry with exponential backoff
  - Health check monitoring
  - Connection timeout handling

**Test Database**:
- **Type**: SQLite
- **Purpose**: Development and testing
- **Auto-switching**: Based on `TESTING` environment variable

### 3. Supabase Integration

**Services Connected**:
- **Database**: PostgreSQL hosting
- **Authentication**: JWT-based auth system
- **Storage**: File storage capabilities (configured but not actively used)

**Configuration Keys**:
- `SUPABASE_URL`: Primary service URL
- `SUPABASE_SERVICE_ROLE_KEY`: Admin access
- `SUPABASE_ANON_KEY`: Anonymous access
- `SUPABASE_JWT_SECRET`: Token validation

### 4. External Domain Security

**Whitelisted Domains**:
- `business.gov.au`
- `grants.gov.au`
- `arts.gov.au`
- `screenaustralia.gov.au`
- `supabase.co`

**Security Features**:
- Domain verification before external requests
- HTTPS enforcement
- Request timeout handling
- Error logging and monitoring

## 📊 Data Processing & Storage

### Grant Data Structure

Each scraped grant includes:
- **Basic Info**: Title, description, source URL
- **Financial**: Min/max amounts, funding purpose
- **Temporal**: Open date, deadline, application periods
- **Eligibility**: Industry focus, location, organization types
- **Metadata**: Contact details, application URLs, tags

### Database Schema

**Primary Tables**:
- `grants`: Main grant storage
- `scraper_logs`: Execution tracking and analytics
- `grant_tags`: Categorization system
- `user_grants`: User-specific grant matching

## 🚀 Scraper Execution & Monitoring

### Execution Methods

1. **Manual Trigger**: Via API endpoint `/api/v1/grants/scrape`
2. **Selective Scraping**: Choose specific sources
3. **Background Processing**: Non-blocking execution
4. **Scheduled Runs**: Ready for cron/scheduler integration

### Monitoring & Logging

**ScraperLog System**:
- **Metrics Tracked**:
  - Execution time and duration
  - Grants found/added/updated
  - Success/error rates
  - URLs scraped and rate limits
  - Error messages and stack traces

**API Endpoints**:
- `GET /api/v1/scraper/sources`: Overall scraper status
- `GET /api/v1/scraper/sources/{source}/history`: Detailed logs
- Real-time status monitoring with performance metrics

### Performance Analytics

**Current Metrics Available**:
- Average execution time per source
- Success/failure rates
- Total grants processed
- Error rate percentages
- Historical performance trends

## 🔧 System Configuration

### Environment Variables

**Required**:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Application security key
- `JWT_SECRET_KEY`: Token signing key

**Optional**:
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY`: Admin access key
- `LOG_LEVEL`: Logging verbosity (default: INFO)

### Rate Limiting & Politeness

**Built-in Features**:
- Random delays between requests (1-3 seconds)
- Respectful scraping with proper headers
- Automatic retry with exponential backoff
- Request timeout handling

## 📈 Frontend Integration

### API Client Configuration

**Base URL**: Configurable via `NEXT_PUBLIC_API_URL`
**Authentication**: JWT token-based
**Error Handling**: Comprehensive retry logic with user feedback

### User Interface

**Scraper Manager Component**:
- Real-time status monitoring
- Selective source execution
- Historical performance data
- Error reporting and diagnostics

## 🛡️ Security & Compliance

### Data Protection

- **Domain Whitelisting**: Only approved external domains
- **Request Validation**: All external requests verified
- **Error Handling**: Secure error messages (no sensitive data exposed)
- **Rate Limiting**: Prevents abuse and respects external services

### Compliance Features

- **Robots.txt Respect**: Honors website scraping policies
- **User-Agent**: Proper identification in requests
- **Rate Limiting**: Prevents overwhelming external services
- **Error Logging**: Comprehensive audit trails

## 📋 Current Status & Health

### System Health

✅ **Fully Operational**:
- All scrapers implemented and tested
- Database connections stable
- API endpoints functional
- Frontend integration complete

### Data Sources Status

| Source | Status | Method | Last Update |
|--------|--------|---------|-------------|
| Business.gov.au | ✅ Active | Web Scraping | Real-time |
| GrantConnect | ✅ Active | API | Real-time |
| Arts.gov.au | ✅ Active | Web Scraping | Real-time |
| Screen Australia | ✅ Active | Web Scraping | Real-time |

## 🚨 Potential Issues & Recommendations

### Current Limitations

1. **No API Keys**: Most scrapers rely on public data (not API keys)
2. **Rate Limiting**: Conservative approach may slow large-scale scraping
3. **Data Freshness**: Manual trigger required (no automatic scheduling)

### Recommendations

1. **Implement Scheduler**: Add cron job for regular scraping
2. **API Key Integration**: Explore official API access for better reliability
3. **Caching Layer**: Add Redis for performance optimization
4. **Monitoring Alerts**: Set up notifications for scraper failures

## 🔍 API Integration Summary

### Active External APIs

1. **GrantConnect Government API** (grants.gov.au)
   - Full REST API integration
   - JSON responses
   - No authentication required
   - Rate limited and monitored

2. **Supabase Database API**
   - PostgreSQL hosting
   - Real-time subscriptions
   - Authentication services
   - File storage capabilities

### Web Scraping Targets

1. **Business.gov.au** - Government business grants
2. **Arts.gov.au** - Creative arts funding
3. **Screen Australia** - Film and media grants

All scraping operations include:
- Respectful rate limiting
- Error handling and recovery
- Data normalization and validation
- Comprehensive logging and monitoring

## 📊 System Metrics

Based on the scraper log system, you can track:
- **Performance**: Average execution time, success rates
- **Volume**: Total grants processed, new vs. updated
- **Reliability**: Error rates, failure patterns
- **Coverage**: Sources active, data freshness

The system is designed for scalability and can easily accommodate additional grant sources as needed.

---

*Report generated on: {{ current_date }}*
*System Version: 0.1.0*
*Status: Production Ready*