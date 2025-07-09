#!/usr/bin/env python3
"""
Script to seed the database with test data.
"""
import os
import sys

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from app.db.seed import seed_database

if __name__ == "__main__":
    seed_database() 