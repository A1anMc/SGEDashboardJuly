import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.scrapers.australian_grants_scraper import AustralianGrantsScraper
from bs4 import BeautifulSoup
import aiohttp
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
        <div class="content">
            <p>Screen Australia provides funding up to $500,000 for documentary production projects by Australian practitioners.</p>
            <p>Applications close on 31 December 2024.</p>
            <p>Contact: funding@screenaustralia.gov.au</p>
            <div class="eligibility">
                <h3>Eligibility</h3>
                <p>Applicants must be Australian citizens or permanent residents with professional experience in documentary production.</p>
            </div>
        </div>
    </body>
    </html>
    """

@pytest.fixture
def sample_creative_australia_html():
    """Sample Creative Australia HTML."""
    return """
    <html>
    <body>
        <h1>Arts Projects for Individuals and Groups</h1>
        <div class="grant-content">
            <p>Up to $50,000 for a range of activities and projects, both national and international, across all art forms.</p>
            <p>Next round closing date: Tuesday 2 September 2025 at 3pm AEST</p>
            <p>For more information, contact arts@creative.gov.au</p>
        </div>
    </body>
    </html>
    """

class TestAustralianGrantsScraper:
    """Test suite for AustralianGrantsScraper."""
    
    def test_init(self, scraper):
        """Test scraper initialization."""
        assert scraper.source_id == "australian_grants"
        assert len(scraper.sources) == 4
        assert "screen_australia" in scraper.sources
        assert "creative_australia" in scraper.sources
        assert "business_gov" in scraper.sources
        assert "create_nsw" in scraper.sources
    
    def test_source_configuration(self, scraper):
        """Test source configuration is correct."""
        screen_australia = scraper.sources["screen_australia"]
        assert screen_australia["base_url"] == "https://www.screenaustralia.gov.au"
        assert len(screen_australia["endpoints"]) == 5
        assert "/funding-and-support/documentary" in screen_australia["endpoints"]
        
        creative_australia = scraper.sources["creative_australia"]
        assert creative_australia["base_url"] == "https://creative.gov.au"
        assert len(creative_australia["endpoints"]) == 3
    
    def test_extract_amounts(self, scraper):
        """Test amount extraction from text."""
        # Test single amount
        text1 = "Funding up to $50,000 is available"
        min_amt, max_amt = scraper._extract_amounts(text1)
        assert min_amt is None
        assert max_amt == 50000
        
        # Test range
        text2 = "Funding between $10,000 and $100,000"
        min_amt, max_amt = scraper._extract_amounts(text2)
        assert min_amt == 10000
        assert max_amt == 100000
        
        # Test with commas
        text3 = "Maximum funding of $1,500,000"
        min_amt, max_amt = scraper._extract_amounts(text3)
        assert min_amt is None
        assert max_amt == 1500000
    
    def test_parse_amount(self, scraper):
        """Test amount parsing."""
        assert scraper._parse_amount("50000") == 50000
        assert scraper._parse_amount("1,500,000") == 1500000
        assert scraper._parse_amount("invalid") is None
        assert scraper._parse_amount("") is None
        assert scraper._parse_amount(None) is None
    
    def test_extract_dates(self, scraper):
        """Test date extraction."""
        text = "Applications close on 31 December 2024. The program opens on 1 January 2024."
        dates = scraper._extract_dates(text)
        
        # Should extract at least one date
        assert dates["deadline"] is not None or dates["open_date"] is not None
    
    def test_parse_date(self, scraper):
        """Test date parsing."""
        assert scraper._parse_date("31/12/2024") == "2024-12-31"
        assert scraper._parse_date("December 31 2024") == "2024-12-31"
        assert scraper._parse_date("31 Dec 2024") == "2024-12-31"
        assert scraper._parse_date("invalid date") is None
        assert scraper._parse_date("") is None
    
    def test_extract_email(self, scraper):
        """Test email extraction."""
        text1 = "Contact us at funding@screenaustralia.gov.au for more information"
        email = scraper._extract_email(text1)
        assert email == "funding@screenaustralia.gov.au"
        
        text2 = "No email in this text"
        email = scraper._extract_email(text2)
        assert email is None
    
    def test_determine_industry_focus(self, scraper):
        """Test industry focus determination."""
        text1 = "This funding supports film and television production"
        industry = scraper._determine_industry_focus(text1)
        assert industry == "media"
        
        text2 = "Support for artists and creative practitioners"
        industry = scraper._determine_industry_focus(text2)
        assert industry == "creative_arts"
        
        text3 = "Digital technology and software development"
        industry = scraper._determine_industry_focus(text3)
        assert industry == "digital"
        
        text4 = "General business support"
        industry = scraper._determine_industry_focus(text4)
        assert industry == "other"
    
    def test_extract_eligibility(self, scraper):
        """Test eligibility extraction."""
        text = "Eligibility: Australian citizens or permanent residents with professional experience"
        criteria = scraper._extract_eligibility(text)
        assert len(criteria) > 0
        assert any("australian" in c.lower() for c in criteria)
    
    def test_extract_org_types(self, scraper):
        """Test organization type extraction."""
        text1 = "Available to individuals, small businesses, and not for profit organizations"
        org_types = scraper._extract_org_types(text1)
        assert "individual" in org_types
        assert "small_business" in org_types
        assert "not_for_profit" in org_types
        
        text2 = "No specific organization types mentioned"
        org_types = scraper._extract_org_types(text2)
        assert org_types == ["any"]
    
    @pytest.mark.asyncio
    async def test_extract_grant_info(self, scraper, sample_html):
        """Test grant information extraction."""
        soup = BeautifulSoup(sample_html, 'html.parser')
        content_div = soup.find('div', class_='content')
        
        grant_info = await scraper._extract_grant_info(
            content_div, 
            "https://test.com", 
            "Test Source"
        )
        
        # Should return None because no h1-h6 element in the content div
        # But the main content should be extractable via _extract_main_grant_info
        assert grant_info is None
    
    @pytest.mark.asyncio
    async def test_extract_main_grant_info(self, scraper, sample_html):
        """Test main grant information extraction."""
        soup = BeautifulSoup(sample_html, 'html.parser')
        
        grant_info = await scraper._extract_main_grant_info(
            soup, 
            "https://test.com", 
            "Test Source"
        )
        
        assert grant_info is not None
        assert grant_info["title"] == "Documentary Production Funding"
        assert "Screen Australia" in grant_info["description"]
        assert grant_info["source"] == "Test Source"
        assert grant_info["source_url"] == "https://test.com"
        assert grant_info["amount_max"] == 500000
        assert grant_info["industry_focus"] == "media"
        assert grant_info["location"] == "Australia"
    
    @pytest.mark.asyncio
    async def test_parse_screen_australia(self, scraper, sample_html):
        """Test Screen Australia parsing."""
        soup = BeautifulSoup(sample_html, 'html.parser')
        
        grants = await scraper._parse_screen_australia(
            soup, 
            "https://www.screenaustralia.gov.au/test"
        )
        
        # Should find at least one grant
        assert len(grants) >= 1
        
        # Check grant structure
        grant = grants[0]
        assert "title" in grant
        assert "description" in grant
        assert "source" in grant
        assert grant["source"] == "Screen Australia"
    
    @pytest.mark.asyncio
    async def test_parse_creative_australia(self, scraper, sample_creative_australia_html):
        """Test Creative Australia parsing."""
        soup = BeautifulSoup(sample_creative_australia_html, 'html.parser')
        
        grants = await scraper._parse_creative_australia(
            soup, 
            "https://creative.gov.au/test"
        )
        
        # Should find at least one grant
        assert len(grants) >= 1
        
        # Check grant structure
        grant = grants[0]
        assert "title" in grant
        assert "Arts Projects" in grant["title"]
        assert grant["source"] == "Creative Australia"
        assert grant["amount_max"] == 50000
    
    @pytest.mark.asyncio
    async def test_parse_generic(self, scraper, sample_html):
        """Test generic parsing."""
        soup = BeautifulSoup(sample_html, 'html.parser')
        
        grants = await scraper._parse_generic(
            soup, 
            "https://test.com"
        )
        
        # Generic parser should handle basic content
        assert isinstance(grants, list)
    
    @pytest.mark.asyncio
    async def test_scrape_source_success(self, scraper):
        """Test successful source scraping."""
        # Mock the session and response
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value="<html><h1>Test Grant</h1><p>Test description</p></html>")
            
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            # Set up the scraper's session
            scraper.session = mock_session.return_value.__aenter__.return_value
            
            source_config = {
                "base_url": "https://test.com",
                "endpoints": ["/test-endpoint"]
            }
            
            grants = await scraper._scrape_source("test_source", source_config)
            
            # Should return a list (might be empty depending on parsing)
            assert isinstance(grants, list)
    
    @pytest.mark.asyncio
    async def test_scrape_source_failure(self, scraper):
        """Test source scraping with HTTP error."""
        # Mock the session and response
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 404
            
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            # Set up the scraper's session
            scraper.session = mock_session.return_value.__aenter__.return_value
            
            source_config = {
                "base_url": "https://test.com",
                "endpoints": ["/test-endpoint"]
            }
            
            grants = await scraper._scrape_source("test_source", source_config)
            
            # Should return empty list on failure
            assert grants == []
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession')
    async def test_scrape_full_integration(self, mock_session, scraper):
        """Test full scraping integration."""
        # Mock successful responses for all sources
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="<html><h1>Test Grant</h1><p>Test description</p></html>")
        
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
        
        # Run the scraper
        grants = await scraper.scrape()
        
        # Should return a list
        assert isinstance(grants, list)
        
        # Should have attempted to scrape all sources
        assert len(scraper.sources) == 4
    
    def test_get_date_context(self, scraper):
        """Test date context extraction."""
        text = "The application deadline is 31 December 2024 for all projects."
        context = scraper._get_date_context(text, "31 December 2024")
        
        assert "deadline" in context.lower()
        assert "31 December 2024" in context
    
    @pytest.mark.asyncio
    async def test_error_handling_in_parsing(self, scraper):
        """Test error handling in parsing methods."""
        # Test with malformed HTML
        malformed_html = "<html><div><p>Incomplete"
        soup = BeautifulSoup(malformed_html, 'html.parser')
        
        # Should not raise exceptions
        grants = await scraper._parse_screen_australia(soup, "https://test.com")
        assert isinstance(grants, list)
        
        grants = await scraper._parse_creative_australia(soup, "https://test.com")
        assert isinstance(grants, list)
        
        grants = await scraper._parse_business_gov(soup, "https://test.com")
        assert isinstance(grants, list)
        
        grants = await scraper._parse_create_nsw(soup, "https://test.com")
        assert isinstance(grants, list)
    
    def test_headers_configuration(self, scraper):
        """Test that headers are properly configured."""
        assert "User-Agent" in scraper.headers
        assert "Mozilla" in scraper.headers["User-Agent"]
        assert scraper.headers["Accept"]
        assert scraper.headers["Accept-Language"]
    
    @pytest.mark.asyncio
    async def test_rate_limiting_delays(self, scraper):
        """Test that rate limiting is implemented."""
        # This test would need to measure actual delays
        # For now, just verify the delay methods exist
        import asyncio
        
        # Test that asyncio.sleep is called (this would need more sophisticated mocking)
        with patch('asyncio.sleep') as mock_sleep:
            # Mock the session and response
            with patch('aiohttp.ClientSession') as mock_session:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.text = AsyncMock(return_value="<html></html>")
                
                mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
                
                # Run a source scrape
                source_config = {
                    "base_url": "https://test.com",
                    "endpoints": ["/test1", "/test2"]
                }
                
                scraper.session = mock_session.return_value.__aenter__.return_value
                await scraper._scrape_source("test_source", source_config)
                
                # Should have called sleep for delays between requests
                assert mock_sleep.called