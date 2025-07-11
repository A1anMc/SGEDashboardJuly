import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.scrapers.australian_grants_scraper import AustralianGrantsScraper
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

@pytest.fixture
def db_session():
    """Mock database session."""
    return Mock(spec=Session)

@pytest.fixture
def scraper(db_session):
    """Create an instance of AustralianGrantsScraper."""
    return AustralianGrantsScraper(db_session)

@pytest.fixture
def sample_html():
    """Sample HTML for testing parsing."""
    return """
    <html>
    <head>
        <title>Screen Australia Funding</title>
        <meta name="description" content="Funding for Australian screen content creators">
    </head>
    <body>
        <h1>Documentary Production Funding</h1>
        <div class="funding-details">
            <p>This program provides funding up to $500,000 for documentary production projects.</p>
            <p>Applications close on 31 December 2024.</p>
            <p>Available to Australian producers and production companies.</p>
            <p>Contact: funding@screenaustralia.gov.au</p>
        </div>
    </body>
    </html>
    """

@pytest.fixture
def sample_creative_australia_html():
    """Sample Creative Australia HTML."""
    return """
    <html>
    <head>
        <title>Arts Projects for Individuals</title>
        <meta name="description" content="Support for individual artists and creative practitioners">
    </head>
    <body>
        <h1>Arts Projects for Individuals and Groups</h1>
        <div class="grant-info">
            <p>Funding from $5,000 to $50,000 for creative projects.</p>
            <p>Applications open 1 February 2024 and close 15 June 2024.</p>
            <p>Available to individual artists, groups, and small organisations.</p>
            <p>For more information, contact arts@creative.gov.au</p>
        </div>
    </body>
    </html>
    """

class TestAustralianGrantsScraper:
    """Test cases for the Australian Grants Scraper."""
    
    def test_scraper_initialization(self, scraper):
        """Test that the scraper initializes correctly."""
        assert scraper.source_id == "australian_grants"
        assert len(scraper.sources) == 4
        assert "screen_australia" in scraper.sources
        assert "creative_australia" in scraper.sources
        assert "business_gov" in scraper.sources
        assert "create_nsw" in scraper.sources
    
    def test_extract_amounts_single_max(self, scraper):
        """Test extracting a single maximum amount."""
        text = "Funding up to $500,000 for documentary production"
        min_amount, max_amount = scraper._extract_amounts(text)
        assert min_amount is None
        assert max_amount == 500000.0
    
    def test_extract_amounts_range(self, scraper):
        """Test extracting amount ranges."""
        text = "Funding from $5,000 to $50,000 for creative projects"
        min_amount, max_amount = scraper._extract_amounts(text)
        assert min_amount == 5000.0
        assert max_amount == 50000.0
    
    def test_extract_amounts_between(self, scraper):
        """Test extracting amounts with 'between' keyword."""
        text = "Grants between $10,000 and $100,000 available"
        min_amount, max_amount = scraper._extract_amounts(text)
        assert min_amount == 10000.0
        assert max_amount == 100000.0
    
    def test_extract_amounts_no_match(self, scraper):
        """Test when no amounts are found."""
        text = "This is a program description with no monetary amounts"
        min_amount, max_amount = scraper._extract_amounts(text)
        assert min_amount is None
        assert max_amount is None
    
    def test_extract_email(self, scraper):
        """Test email extraction."""
        text = "For more information, contact funding@screenaustralia.gov.au"
        email = scraper._extract_email(text)
        assert email == "funding@screenaustralia.gov.au"
    
    def test_extract_email_no_match(self, scraper):
        """Test email extraction when no email is present."""
        text = "This text has no email address"
        email = scraper._extract_email(text)
        assert email is None
    
    def test_determine_industry_focus_media(self, scraper):
        """Test industry focus determination for media content."""
        text = "Screen Australia funding for documentary production"
        industry = scraper._determine_industry_focus(text)
        assert industry == "media"
    
    def test_determine_industry_focus_creative_arts(self, scraper):
        """Test industry focus determination for creative arts."""
        text = "Arts projects for creative practitioners and cultural organizations"
        industry = scraper._determine_industry_focus(text)
        assert industry == "creative_arts"
    
    def test_determine_industry_focus_digital(self, scraper):
        """Test industry focus determination for digital/tech."""
        text = "Digital technology and gaming development grants"
        industry = scraper._determine_industry_focus(text)
        assert industry == "digital"
    
    def test_determine_industry_focus_other(self, scraper):
        """Test industry focus determination for unmatched content."""
        text = "General support and funding opportunities"
        industry = scraper._determine_industry_focus(text)
        assert industry == "other"
    
    def test_extract_org_types(self, scraper):
        """Test organization type extraction."""
        text = "Available to individuals, small businesses, and not for profit organizations"
        org_types = scraper._extract_org_types(text)
        assert "individual" in org_types
        assert "small_business" in org_types
        assert "not_for_profit" in org_types
    
    def test_extract_org_types_default(self, scraper):
        """Test organization type extraction with no matches."""
        text = "This text has no organization type keywords"
        org_types = scraper._extract_org_types(text)
        assert org_types == ["any"]
    
    def test_extract_funding_purpose(self, scraper):
        """Test funding purpose extraction."""
        text = "Support for research and development of new creative content"
        purposes = scraper._extract_funding_purpose(text)
        assert "research" in purposes
        assert "development" in purposes
    
    def test_extract_audience_tags(self, scraper):
        """Test audience tag extraction."""
        text = "Support for Australian emerging artists in regional areas"
        tags = scraper._extract_audience_tags(text)
        assert "australian" in tags
        assert "creative" in tags
        assert "emerging" in tags
        assert "regional" in tags
    
    @pytest.mark.asyncio
    @patch('app.services.scrapers.australian_grants_scraper.AustralianGrantsScraper._make_request')
    async def test_parse_screen_australia(self, mock_make_request, scraper, sample_html):
        """Test parsing Screen Australia content."""
        soup = BeautifulSoup(sample_html, 'html.parser')
        grants = await scraper._parse_screen_australia(soup, "https://test.com")
        
        # Should find at least one grant from the main content
        assert len(grants) >= 1
        
        # Check the grant data structure
        grant = grants[0]
        assert grant["title"] == "Documentary Production Funding"
        assert "funding" in grant["description"].lower()
        assert grant["max_amount"] == 500000.0
        assert grant["industry_focus"] == "media"
        assert grant["contact_email"] == "funding@screenaustralia.gov.au"
    
    @pytest.mark.asyncio
    @patch('app.services.scrapers.australian_grants_scraper.AustralianGrantsScraper._make_request')
    async def test_parse_creative_australia(self, mock_make_request, scraper, sample_creative_australia_html):
        """Test parsing Creative Australia content."""
        soup = BeautifulSoup(sample_creative_australia_html, 'html.parser')
        grants = await scraper._parse_creative_australia(soup, "https://test.com")
        
        # Should find at least one grant
        assert len(grants) >= 1
        
        # Check the grant data structure
        grant = grants[0]
        assert grant["title"] == "Arts Projects for Individuals and Groups"
        assert grant["min_amount"] == 5000.0
        assert grant["max_amount"] == 50000.0
        assert grant["industry_focus"] == "creative_arts"
        assert grant["contact_email"] == "arts@creative.gov.au"
    
    def test_extract_description_from_element(self, scraper):
        """Test description extraction from HTML element."""
        html = """
        <div>
            <h2>Grant Title</h2>
            <p class="description">This is a detailed description of the grant program.</p>
            <p>Additional information about eligibility.</p>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.find('div')
        description = scraper._extract_description(element)
        assert description == "This is a detailed description of the grant program."
    
    def test_extract_page_description_from_meta(self, scraper):
        """Test page description extraction from meta tag."""
        html = """
        <html>
        <head>
            <meta name="description" content="This is the meta description for the page">
        </head>
        <body>
            <p>Body content</p>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        description = scraper._extract_page_description(soup)
        assert description == "This is the meta description for the page"
    
    def test_get_date_context(self, scraper):
        """Test getting context around a date."""
        text = "Applications for this program open on 1 January 2024 and close on 31 December 2024"
        context = scraper._get_date_context(text, "1 January 2024")
        assert "applications" in context.lower()
        assert "open" in context.lower()
    
    def test_normalize_grant_data_integration(self, scraper):
        """Test that the scraper properly integrates with BaseScraper's normalize_grant_data."""
        # Test data that should be normalized
        test_data = {
            "title": "  Test Grant Title  ",
            "description": "  This is a test description  ",
            "source_url": "https://example.com/grant",
            "min_amount": 5000.0,
            "max_amount": 50000.0,
            "contact_email": "  test@example.com  ",
            "industry_focus": "creative_arts",
            "location": "national",
            "org_types": ["individual", "small_business"],
            "funding_purpose": ["development"],
            "audience_tags": ["australian", "creative"]
        }
        
        normalized = scraper.normalize_grant_data(test_data)
        
        # Check that text fields are cleaned
        assert normalized["title"] == "Test Grant Title"
        assert normalized["description"] == "This is a test description"
        assert normalized["contact_email"] == "test@example.com"
        
        # Check that numeric fields are preserved
        assert normalized["min_amount"] == 5000.0
        assert normalized["max_amount"] == 50000.0
        
        # Check that other fields are preserved
        assert normalized["industry_focus"] == "creative_arts"
        assert normalized["org_types"] == ["individual", "small_business"]
    
    @pytest.mark.asyncio
    @patch('app.services.scrapers.australian_grants_scraper.AustralianGrantsScraper._make_request')
    @patch('asyncio.sleep')
    async def test_scrape_integration(self, mock_sleep, mock_make_request, scraper, sample_html):
        """Test the main scrape method integration."""
        # Mock the _make_request to return sample HTML
        mock_make_request.return_value = sample_html
        
        # Run the scraper
        grants = await scraper.scrape()
        
        # Should have made requests to multiple sources
        assert mock_make_request.call_count > 0
        
        # Should have found some grants
        assert len(grants) > 0
        
        # Check that delays were added (respectful scraping)
        assert mock_sleep.call_count > 0
    
    def test_parse_amount_float_conversion(self, scraper):
        """Test that amounts are properly converted to float."""
        assert scraper._parse_amount("5000") == 5000.0
        assert scraper._parse_amount("5,000") == 5000.0
        assert scraper._parse_amount("$5,000") == 5000.0
        assert scraper._parse_amount("5000.50") == 5000.5
        assert scraper._parse_amount("") is None
        assert scraper._parse_amount("invalid") is None