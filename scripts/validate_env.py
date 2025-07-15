#!/usr/bin/env python3
"""
Environment Configuration Validator

This script validates the environment configuration for the SGE Dashboard application.
It ensures all required variables are set and properly formatted.
"""

import os
import sys
from typing import List, Dict, Optional
from urllib.parse import urlparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnvValidator:
    """Validates environment configuration."""
    
    REQUIRED_VARS = {
        'core': [
            'PROJECT_NAME',
            'SECRET_KEY',
            'JWT_SECRET_KEY',
        ],
        'database': [
            'DATABASE_URL',
        ],
        # Removed Supabase configuration
    }
    
    def __init__(self, env_file: str = '.env'):
        self.env_file = env_file
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_database_url(self, url: Optional[str]) -> bool:
        """Validate database URL format and configuration."""
        if not url:
            self.errors.append("DATABASE_URL is not set")
            return False
            
        if url.startswith('sqlite:'):
            self.errors.append("SQLite is not supported. Please use PostgreSQL.")
            return False
            
        if not url.startswith('postgresql://'):
            self.errors.append("DATABASE_URL must start with postgresql://")
            return False
            
        try:
            parsed = urlparse(url)
            if not parsed.username or not parsed.password:
                self.warnings.append("DATABASE_URL should include username and password")
            if not parsed.hostname:
                self.errors.append("DATABASE_URL must include hostname")
                return False
        except Exception as e:
            self.errors.append(f"Invalid DATABASE_URL format: {str(e)}")
            return False
            
        return True
    
    # Removed Supabase validation
    
    def validate_security_config(self, config: Dict[str, str]) -> bool:
        """Validate security-related configuration."""
        is_valid = True
        
        # Check secret keys
        for key in ['SECRET_KEY', 'JWT_SECRET_KEY']:
            value = config.get(key)
            if not value:
                self.errors.append(f"{key} is not set")
                is_valid = False
            elif len(value) < 32:
                self.warnings.append(f"{key} should be at least 32 characters long")
        
        return is_valid
    
    def validate(self) -> bool:
        """Validate all environment configuration."""
        if not os.path.exists(self.env_file):
            self.errors.append(f"Environment file {self.env_file} not found")
            return False
        
        # Read environment file
        env_vars = {}
        with open(self.env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip().strip('"').strip("'")
                    except ValueError:
                        self.warnings.append(f"Invalid line in {self.env_file}: {line}")
        
        # Check required variables
        for category, vars in self.REQUIRED_VARS.items():
            for var in vars:
                if var not in env_vars:
                    self.errors.append(f"Required variable {var} not found in {category} configuration")
        
        # Validate specific configurations
        if 'DATABASE_URL' in env_vars:
            self.validate_database_url(env_vars['DATABASE_URL'])
        
        # Removed Supabase validation
        
        self.validate_security_config(env_vars)
        
        # Log results
        if self.warnings:
            logger.warning("Configuration warnings:")
            for warning in self.warnings:
                logger.warning(f"  - {warning}")
        
        if self.errors:
            logger.error("Configuration errors:")
            for error in self.errors:
                logger.error(f"  - {error}")
            return False
        
        logger.info("Environment configuration validation passed!")
        return True

def main():
    """Main entry point."""
    validator = EnvValidator()
    if not validator.validate():
        sys.exit(1)

if __name__ == '__main__':
    main() 