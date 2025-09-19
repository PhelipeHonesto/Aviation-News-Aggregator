#!/usr/bin/env python3
"""
Test script for the new harvest system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingest import load_sources, harvest_all_sources, run_harvest
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_load_sources():
    """Test loading sources from YAML"""
    print("Testing source loading...")
    sources = load_sources()
    print(f"Loaded {len(sources)} sources")
    
    for i, source in enumerate(sources[:5]):  # Show first 5
        print(f"{i+1}. {source.name} ({source.category}) - {source.kind}")
    
    return sources

def test_harvest():
    """Test the harvest process"""
    print("\nTesting harvest process...")
    try:
        saved_count = run_harvest()
        print(f"Harvest completed: {saved_count} articles saved")
    except Exception as e:
        print(f"Harvest failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    sources = test_load_sources()
    test_harvest()
