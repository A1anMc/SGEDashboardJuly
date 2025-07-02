import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.orm import Session
from app.models.grant import Grant, IndustryFocus, LocationEligibility, OrgType
from app.services.scrapers.base_scraper import BaseScraper
from app.services.scrapers.business_gov import BusinessGovScraper
from app.services.scrapers.grantconnect import GrantConnectScraper

# Sample HTML responses for mocking
SAMPLE_GRANT_LIST_HTML = """
<div class="grant-card">
    <h3>Test Grant</h3>
    <div class="description">A test grant description</div>
    <a href="/grants/test-grant">More Info</a>
</div>
"""

SAMPLE_GRANT_DETAIL_HTML = """
<div class="grant-details">
    <div class="date-field">
        <label>Opening Date</label>
        <span>2024-03-01</span>
    </div>
    <div class="date-field">
        <label>Closing Date</label>
        <span>2024-06-30</span>
    </div>
    <div class="funding-amount">
        Up to $50,000
    </div>
    <div class="eligibility">
        <ul>
            <li>Small business</li>
            <li>Social enterprise</li>
        </ul>
    </div>
    <div class="industry-sectors">
        Media and Film
    </div>
    <div class="location">
        Victoria
    </div>
    <div class="contact-info">
        <a href="mailto:test@example.com">Contact</a>
    </div>
</div>
"""

# Sample JSON responses for GrantConnect
SAMPLE_GRANT_SEARCH_JSON = {
    "grants": [
        {
            "id": "123",
            "title": "Media Development Grant",
            "description": "Support for media projects"
        }
    ]
}

SAMPLE_GRANT_DETAIL_JSON = {
    "grant": {
        "openDate": "2024-03-01",
        "closeDate": "2024-06-30",
        "estimatedValueFrom": "10000",
        "estimatedValueTo": "50000",
        "contactEmail": "grants@example.com",
        "categories": ["Media and Film", "Digital Content"],
        "eligibility": {
            "location": "Victoria",
            "organizationTypes": ["Small Business", "Social Enterprise"]
        },
        "fundingPurpose": ["Production", "Development"],
        "targetGroups": ["Media Producers", "Content Creators"]
    }
}

@pytest.fixture
def db_session():
    """Mock database session."""
    return Mock(spec=Session)

@pytest.fixture
def mock_aiohttp_session():
    """Mock aiohttp client session."""
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    
    async def mock_text():
        if "grants-and-programs" in str(mock_response._url):
            return SAMPLE_GRANT_LIST_HTML
        return SAMPLE_GRANT_DETAIL_HTML
    
    mock_response.text = mock_text
    mock_session.get.return_value.__aenter__.return_value = mock_response
    return mock_session

class TestBaseScraper:
    """Test suite for BaseScraper."""
    
    def test_normalize_industry(self, db_session):
        scraper = BaseScraper(db_session, "test")
        assert scraper._normalize_industry("media") == IndustryFocus.MEDIA
        assert scraper._normalize_industry("film") == IndustryFocus.MEDIA
        assert scraper._normalize_industry("arts") == IndustryFocus.CREATIVE_ARTS
        assert scraper._normalize_industry("unknown") == IndustryFocus.OTHER
    
    def test_normalize_location(self, db_session):
        scraper = BaseScraper(db_session, "test")
        assert scraper._normalize_location("victoria") == LocationEligibility.VIC
        assert scraper._normalize_location("national") == LocationEligibility.NATIONAL
        assert scraper._normalize_location(None) == LocationEligibility.NATIONAL
    
    def test_normalize_org_types(self, db_session):
        scraper = BaseScraper(db_session, "test")
        org_types = ["social enterprise", "not for profit"]
        normalized = scraper._normalize_org_types(org_types)
        assert OrgType.SOCIAL_ENTERPRISE in normalized
        assert OrgType.NFP in normalized
    
    def test_parse_date(self, db_session):
        scraper = BaseScraper(db_session, "test")
        assert scraper._parse_date("2024-03-20") == datetime(2024, 3, 20)
        assert scraper._parse_date("20/03/2024") == datetime(2024, 3, 20)
        assert scraper._parse_date("invalid") is None
    
    def test_normalize_grant_data(self, db_session):
        scraper = BaseScraper(db_session, "test")
        raw_data = {
            "title": "Test Grant",
            "description": "Test Description",
            "industry_focus": "media",
            "location": "victoria",
            "org_types": ["social enterprise"],
            "open_date": "2024-03-20",
            "deadline": "2024-06-30"
        }
        
        normalized = scraper.normalize_grant_data(raw_data)
        assert normalized["title"] == "Test Grant"
        assert normalized["industry_focus"] == IndustryFocus.MEDIA
        assert normalized["location_eligibility"] == LocationEligibility.VIC
        assert OrgType.SOCIAL_ENTERPRISE in normalized["org_type_eligible"]
        assert normalized["open_date"] == datetime(2024, 3, 20)
        assert normalized["deadline"] == datetime(2024, 6, 30)

class TestBusinessGovScraper:
    """Test suite for BusinessGovScraper."""
    
    @pytest.mark.asyncio
    async def test_scrape_grants(self, db_session, mock_aiohttp_session):
        with patch("aiohttp.ClientSession", return_value=mock_aiohttp_session):
            scraper = BusinessGovScraper(db_session)
            grants = await scraper.scrape()
            
            assert len(grants) == 1
            grant = grants[0]
            assert grant["title"] == "Test Grant"
            assert grant["industry_focus"] == IndustryFocus.MEDIA
            assert grant["location_eligibility"] == LocationEligibility.VIC
            assert grant["max_amount"] == 50000
    
    @pytest.mark.asyncio
    async def test_fetch_grant_details(self, db_session, mock_aiohttp_session):
        scraper = BusinessGovScraper(db_session)
        details = await scraper._fetch_grant_details(mock_aiohttp_session, "test-url")
        
        assert details["open_date"] == "2024-03-01"
        assert details["deadline"] == "2024-06-30"
        assert details["max_amount"] == 50000
        assert "small business" in details["org_types"]
        assert details["industry_focus"] == "Media and Film"
        assert details["location"] == "Victoria"
        assert details["contact_email"] == "test@example.com"
    
    def test_extract_amount(self, db_session):
        scraper = BusinessGovScraper(db_session)
        assert scraper._extract_amount("Up to $50,000") == 50000
        assert scraper._extract_amount("$1,000,000") == 1000000
        assert scraper._extract_amount("Invalid") is None

class TestGrantConnectScraper:
    """Test suite for GrantConnectScraper."""
    
    @pytest.fixture
    def mock_grantconnect_session(self):
        """Mock aiohttp session for GrantConnect API."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        
        async def mock_json():
            if "search" in str(mock_response._url):
                return SAMPLE_GRANT_SEARCH_JSON
            return SAMPLE_GRANT_DETAIL_JSON
        
        mock_response.json = mock_json
        mock_session.get.return_value.__aenter__.return_value = mock_response
        return mock_session
    
    @pytest.mark.asyncio
    async def test_scrape_grants(self, db_session, mock_grantconnect_session):
        with patch("aiohttp.ClientSession", return_value=mock_grantconnect_session):
            scraper = GrantConnectScraper(db_session)
            grants = await scraper.scrape()
            
            assert len(grants) == 1
            grant = grants[0]
            assert grant["title"] == "Media Development Grant"
            assert grant["industry_focus"] == IndustryFocus.MEDIA
            assert grant["location_eligibility"] == LocationEligibility.VIC
            assert grant["max_amount"] == 50000
            assert grant["min_amount"] == 10000
            assert OrgType.SME in grant["org_type_eligible"]
            assert OrgType.SOCIAL_ENTERPRISE in grant["org_type_eligible"]
    
    @pytest.mark.asyncio
    async def test_fetch_grant_details(self, db_session, mock_grantconnect_session):
        scraper = GrantConnectScraper(db_session)
        details = await scraper._fetch_grant_details(mock_grantconnect_session, "123")
        
        assert details["open_date"] == "2024-03-01"
        assert details["deadline"] == "2024-06-30"
        assert details["min_amount"] == 10000
        assert details["max_amount"] == 50000
        assert details["contact_email"] == "grants@example.com"
        assert details["industry_focus"] == "Media and Film"
        assert details["location"] == "Victoria"
        assert "small_business" in details["org_types"]
        assert "social_enterprise" in details["org_types"]
        assert "Production" in details["funding_purpose"]
        assert "Media Producers" in details["audience_tags"]
    
    def test_parse_amount(self, db_session):
        scraper = GrantConnectScraper(db_session)
        assert scraper._parse_amount("50000") == 50000
        assert scraper._parse_amount("1000.50") == 1000
        assert scraper._parse_amount(None) is None
        assert scraper._parse_amount("invalid") is None
    
    def test_extract_industry(self, db_session):
        scraper = GrantConnectScraper(db_session)
        assert scraper._extract_industry(["Media and Film"]) == "Media and Film"
        assert scraper._extract_industry(["Digital Content"]) == "Digital Content"
        assert scraper._extract_industry(["Other"]) == "Other"
    
    def test_extract_location(self, db_session):
        scraper = GrantConnectScraper(db_session)
        assert scraper._extract_location({"location": "Victoria"}) == "Victoria"
        assert scraper._extract_location({"location": "all"}) == "National"
        assert scraper._extract_location({}) == ""
    
    def test_extract_org_types(self, db_session):
        scraper = GrantConnectScraper(db_session)
        org_types = scraper._extract_org_types({
            "organizationTypes": ["Small Business", "Not for Profit", "Social Enterprise"]
        })
        assert "small_business" in org_types
        assert "not_for_profit" in org_types
        assert "social_enterprise" in org_types
        
        # Test empty/invalid input
        assert scraper._extract_org_types({}) == ["any"]
        assert scraper._extract_org_types({"organizationTypes": []}) == ["any"] 