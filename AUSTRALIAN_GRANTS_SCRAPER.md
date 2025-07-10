# Australian Grants Scraper Solution

## Overview

This document outlines the issues with the current GrantConnect scraper and provides a comprehensive solution using a new Australian grants scraper that targets multiple reliable sources.

## Issues with Current GrantConnect Scraper

### 1. API Access Problems

The current GrantConnect scraper in `app/services/scrapers/grantconnect.py` tries to access:
- `https://www.grants.gov.au/api/v1/grants/search`
- `https://www.grants.gov.au/api/v1/grants/{id}`

**Issues identified:**
- These API endpoints may no longer be publicly accessible
- API structure may have changed
- Authentication may now be required
- Rate limiting may be blocking requests

### 2. Reliability Issues

Based on testing and research:
- The grants.gov.au API appears to have access restrictions
- Limited documentation available for public API access
- Inconsistent response formats
- Potential for frequent changes without notice

### 3. Scope Limitations

The current scraper only targets one source, which limits the diversity of grants available for Australian companies like Shadow Goose Entertainment.

## Solution: New Australian Grants Scraper

### Key Features

1. **Multiple Source Coverage**: Targets 4+ reliable Australian grant sources
2. **Robust Error Handling**: Graceful failure and retry mechanisms
3. **Intelligent Parsing**: Source-specific parsing logic for better data extraction
4. **Comprehensive Data Extraction**: Extracts amounts, dates, eligibility, and more
5. **Respectful Scraping**: Implements delays and rate limiting

### Target Sources

#### 1. Screen Australia (`screen_australia`)
- **URL**: https://www.screenaustralia.gov.au
- **Focus**: Government funding for screen/media content
- **Relevance**: Highly relevant for Shadow Goose Entertainment
- **Endpoints**:
  - Narrative content development
  - Narrative content production
  - Documentary funding
  - Games funding
  - Industry development

#### 2. Creative Australia (`creative_australia`)
- **URL**: https://creative.gov.au
- **Focus**: Federal arts funding (formerly Australia Council for the Arts)
- **Relevance**: Supports creative industries and artists
- **Endpoints**:
  - Arts projects for individuals and groups
  - Arts projects for organisations
  - Multi-year investment programs

#### 3. Business.gov.au (`business_gov`)
- **URL**: https://business.gov.au
- **Focus**: Business grants including creative industries
- **Relevance**: Business development and industry support
- **Endpoints**:
  - Screen Australia funding information
  - Arts and culture grants
  - Creative industry support

#### 4. Create NSW (`create_nsw`)
- **URL**: https://www.create.nsw.gov.au
- **Focus**: NSW state government arts funding
- **Relevance**: State-level creative industry support
- **Endpoints**:
  - Organisation funding
  - Individual artist support
  - Quick response grants

## Implementation Details

### Architecture

```python
class AustralianGrantsScraper(BaseScraper):
    """
    Comprehensive Australian grants scraper targeting multiple sources
    """
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, "australian_grants")
        # Configure sources and endpoints
        
    async def scrape(self) -> List[Dict[str, Any]]:
        # Coordinate scraping across all sources
        
    async def _scrape_source(self, source_name: str, source_config: Dict):
        # Scrape individual source
        
    async def _parse_[source_name](self, soup: BeautifulSoup, url: str):
        # Source-specific parsing logic
```

### Data Extraction Features

#### 1. Intelligent Amount Extraction
- Supports multiple currency formats
- Handles ranges (e.g., "$10,000 - $50,000")
- Identifies minimum and maximum amounts
- Recognizes context (e.g., "up to $50,000")

#### 2. Date Parsing
- Multiple date formats supported
- Contextual date identification (opening vs. deadline)
- Handles various date representations

#### 3. Industry Focus Detection
- Keyword-based industry classification
- Specific categories for media, creative arts, digital, etc.
- Tailored for Shadow Goose Entertainment's needs

#### 4. Eligibility Extraction
- Parses eligibility criteria from text
- Identifies organization types
- Extracts requirements and restrictions

### Error Handling

1. **Request-Level**: Timeout handling, HTTP error responses
2. **Source-Level**: Continue processing other sources if one fails
3. **Parsing-Level**: Graceful handling of missing or malformed data
4. **Data-Level**: Validation and sanitization of extracted information

### Rate Limiting

- Random delays between requests (1-2 seconds)
- Longer delays between different sources (2-4 seconds)
- Respectful scraping practices
- User-Agent rotation

## Usage

### 1. Add to Scraper Service

The new scraper is automatically added to the scraper service:

```python
from app.services.scrapers.australian_grants_scraper import AustralianGrantsScraper

# Available in ScraperService
self.scrapers = {
    "business.gov.au": BusinessGovScraper,
    "grantconnect": GrantConnectScraper,
    "dummy": DummyScraper,
    "australian_grants": AustralianGrantsScraper  # New scraper
}
```

### 2. Running the Scraper

```python
# Via API endpoint
POST /api/v1/grants/scrape
{
    "sources": ["australian_grants"],
    "force_refresh": false
}

# Via ScraperService
scraper_service = ScraperService(db)
results = scraper_service.scrape_source("australian_grants")
```

### 3. Expected Output

```json
{
    "status": "success",
    "grants_found": 15,
    "grants_added": 12,
    "grants_updated": 3,
    "duration_seconds": 45.2
}
```

### 4. Grant Data Structure

```json
{
    "title": "Screen Australia Documentary Production",
    "description": "Funding for documentary production by Australian practitioners...",
    "source": "Screen Australia",
    "source_url": "https://www.screenaustralia.gov.au/funding-and-support/documentary",
    "amount_min": 10000,
    "amount_max": 500000,
    "open_date": "2024-01-01",
    "deadline": "2024-12-31",
    "contact_email": "info@screenaustralia.gov.au",
    "industry_focus": "media",
    "location": "Australia",
    "eligibility_criteria": ["Australian citizens or permanent residents", "Professional practitioners"],
    "org_type": ["individual", "small_business", "not_for_profit"],
    "status": "open",
    "scraped_at": "2024-01-15T10:30:00",
    "grant_id": "Screen Australia_1234567890"
}
```

## Benefits for Shadow Goose Entertainment

### 1. Expanded Grant Coverage
- Access to 4+ reliable Australian grant sources
- Comprehensive coverage of media, creative, and business grants
- Both federal and state-level funding opportunities

### 2. Better Data Quality
- Structured data extraction
- Consistent formatting across sources
- Rich metadata (amounts, dates, eligibility)

### 3. Improved Reliability
- Multiple fallback sources
- Robust error handling
- Automatic retry mechanisms

### 4. Industry-Specific Focus
- Tailored for media and entertainment industry
- Relevant funding categories
- Appropriate organization types

## Monitoring and Maintenance

### 1. Logging
- Comprehensive logging at all levels
- Error tracking and reporting
- Performance monitoring

### 2. Data Validation
- Automatic validation of extracted data
- Duplicate detection and prevention
- Data quality checks

### 3. Source Health Monitoring
- Track success rates per source
- Monitor for changes in website structure
- Alert on consistent failures

### 4. Regular Updates
- Monthly review of target sources
- Quarterly review of parsing logic
- Annual review of grant categories

## Future Enhancements

### 1. Additional Sources
- State-level arts councils (VIC, QLD, SA, WA, etc.)
- Industry-specific grant providers
- Corporate foundation grants

### 2. Advanced Features
- Machine learning for better data extraction
- Natural language processing for eligibility matching
- Automated grant matching for specific criteria

### 3. Integration Features
- Email notifications for new grants
- Calendar integration for deadlines
- Application tracking and reminders

## Troubleshooting

### Common Issues

1. **Low Grant Count**: Check if source websites have changed structure
2. **Missing Data**: Review parsing logic for specific sources
3. **Timeout Errors**: Increase timeout settings or add retry logic
4. **Rate Limiting**: Increase delays between requests

### Debugging

```python
# Enable debug logging
import logging
logging.getLogger("app.services.scrapers.australian_grants_scraper").setLevel(logging.DEBUG)

# Test individual source
scraper = AustralianGrantsScraper(db)
grants = await scraper._scrape_source("screen_australia", scraper.sources["screen_australia"])
```

## Conclusion

The new Australian Grants Scraper provides a robust, reliable alternative to the problematic GrantConnect scraper. By targeting multiple high-quality sources and implementing intelligent parsing logic, it ensures Shadow Goose Entertainment has access to comprehensive, up-to-date grant information relevant to their industry.

The scraper is designed to be maintainable, extensible, and respectful of the target websites while providing maximum value for grant discovery and application processes.