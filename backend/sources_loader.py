"""
Sources Loader for Loud Hawk v2
Loads sources from CSV and populates the database
"""

import csv
import logging
from pathlib import Path
from typing import List, Dict, Optional
from sqlmodel import Session, select
from database import get_session
import yaml

logger = logging.getLogger(__name__)

class SourcesLoader:
    """Loads and manages source configurations"""
    
    def __init__(self):
        self.csv_path = Path(__file__).parent / "osa_sources_seed.csv"
        self.yaml_path = Path(__file__).parent / "trusted_sources.yaml"
    
    def load_from_csv(self) -> List[Dict]:
        """Load sources from CSV file"""
        sources = []
        
        if not self.csv_path.exists():
            logger.error(f"CSV file not found: {self.csv_path}")
            return sources
        
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    source = self._parse_csv_row(row)
                    if source:
                        sources.append(source)
            
            logger.info(f"Loaded {len(sources)} sources from CSV")
            return sources
            
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            return []
    
    def _parse_csv_row(self, row: Dict) -> Optional[Dict]:
        """Parse a CSV row into source configuration"""
        try:
            name = row.get("name", "").strip()
            domain = row.get("domain", "").strip()
            homepage_url = row.get("homepage_url", "").strip()
            category = row.get("category", "").strip().upper()
            region = row.get("region", "").strip()
            adapter_strategy = row.get("adapter_strategy", "").strip()
            notes = row.get("notes", "").strip()
            
            if not name or not domain:
                return None
            
            # Map adapter strategy to our format
            adapter_mapping = {
                "RSS_NATIVE": "rss",
                "RSS_REDIRECTED": "rss",
                "RSS_NATIVE_OR_TIDY_XML": "rss",
                "RSS_REDIRECTED_OR_TIDY_XML": "rss",
                "SITEMAP_OR_RSS_REDIRECTED": "rss",
                "SITEMAP_NEWS": "sitemap",
                "HTML_SCRAPE_WHITELIST": "html",
                "HTML_TIDY_XML": "html",
                "HTML_SCRAPE_OR_JSON": "html",
                "RSS_OR_HTML_SCRAPE": "rss",
                "RSS_NATIVE_OR_JSON": "rss",
                "JSON_API": "json",
                "YOUTUBE_API": "youtube"
            }
            
            kind = adapter_mapping.get(adapter_strategy, "rss")
            
            # Determine weight based on category
            weight_mapping = {
                "REGULATOR": 10,
                "SAFETY": 9,
                "OEM": 8,
                "ATC": 7,
                "INDUSTRY": 6,
                "AIRLINE": 6,
                "MEDIA": 5,
                "DATA": 5,
                "EVTOL": 4,
                "AIRPORT": 4,
                "MRO": 4,
                "CREATOR": 3
            }
            
            weight = weight_mapping.get(category, 5)
            
            # Determine if enabled by default
            enabled = kind in ["rss", "json"] and "403" not in notes.lower()
            
            source = {
                "name": name,
                "category": category,
                "weight": weight,
                "kind": kind,
                "enabled": enabled,
                "home": homepage_url,
                "discover": kind == "rss",
                "adapter_strategy": adapter_strategy,
                "notes": notes,
                "region": region
            }
            
            # Add specific URL for known RSS feeds
            if kind == "rss" and "rss" in notes.lower():
                # Extract RSS URL from notes if mentioned
                if "rss.xml" in notes:
                    source["url"] = homepage_url.rstrip("/") + "/rss.xml"
                elif "feed" in notes:
                    source["url"] = homepage_url.rstrip("/") + "/feed/"
            
            return source
            
        except Exception as e:
            logger.error(f"Error parsing CSV row: {e}")
            return None
    
    def save_to_yaml(self, sources: List[Dict], output_path: Optional[Path] = None) -> bool:
        """Save sources to YAML file"""
        if output_path is None:
            output_path = self.yaml_path
        
        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                yaml.dump(sources, file, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"Saved {len(sources)} sources to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving to YAML: {e}")
            return False
    
    def load_from_yaml(self, yaml_path: Optional[Path] = None) -> List[Dict]:
        """Load sources from YAML file"""
        if yaml_path is None:
            yaml_path = self.yaml_path
        
        if not yaml_path.exists():
            logger.error(f"YAML file not found: {yaml_path}")
            return []
        
        try:
            with open(yaml_path, 'r', encoding='utf-8') as file:
                sources = yaml.safe_load(file)
                if not isinstance(sources, list):
                    sources = []
            
            logger.info(f"Loaded {len(sources)} sources from YAML")
            return sources
            
        except Exception as e:
            logger.error(f"Error loading YAML: {e}")
            return []
    
    def update_existing_sources(self, new_sources: List[Dict]) -> List[Dict]:
        """Update existing sources with new configurations"""
        existing_sources = self.load_from_yaml()
        existing_names = {source["name"] for source in existing_sources}
        
        # Add new sources
        updated_sources = existing_sources.copy()
        for source in new_sources:
            if source["name"] not in existing_names:
                updated_sources.append(source)
                logger.info(f"Added new source: {source['name']}")
        
        # Update existing sources with new configurations
        for i, existing_source in enumerate(updated_sources):
            for new_source in new_sources:
                if existing_source["name"] == new_source["name"]:
                    # Update with new configuration
                    updated_sources[i].update(new_source)
                    logger.info(f"Updated source: {existing_source['name']}")
                    break
        
        return updated_sources
    
    def generate_source_stats(self, sources: List[Dict]) -> Dict:
        """Generate statistics about sources"""
        stats = {
            "total_sources": len(sources),
            "by_category": {},
            "by_kind": {},
            "by_region": {},
            "enabled_count": 0,
            "disabled_count": 0
        }
        
        for source in sources:
            # Category stats
            category = source.get("category", "Unknown")
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
            
            # Kind stats
            kind = source.get("kind", "unknown")
            stats["by_kind"][kind] = stats["by_kind"].get(kind, 0) + 1
            
            # Region stats
            region = source.get("region", "Unknown")
            stats["by_region"][region] = stats["by_region"].get(region, 0) + 1
            
            # Enabled stats
            if source.get("enabled", False):
                stats["enabled_count"] += 1
            else:
                stats["disabled_count"] += 1
        
        return stats
    
    def print_stats(self, stats: Dict):
        """Print source statistics"""
        print("\n" + "="*50)
        print("LOUD HAWK V2 - SOURCE STATISTICS")
        print("="*50)
        print(f"Total Sources: {stats['total_sources']}")
        print(f"Enabled: {stats['enabled_count']}")
        print(f"Disabled: {stats['disabled_count']}")
        
        print("\nBy Category:")
        for category, count in sorted(stats['by_category'].items()):
            print(f"  {category}: {count}")
        
        print("\nBy Type:")
        for kind, count in sorted(stats['by_kind'].items()):
            print(f"  {kind}: {count}")
        
        print("\nBy Region:")
        for region, count in sorted(stats['by_region'].items()):
            print(f"  {region}: {count}")
        print("="*50)

def main():
    """Main function for CLI usage"""
    loader = SourcesLoader()
    
    # Load from CSV
    print("Loading sources from CSV...")
    csv_sources = loader.load_from_csv()
    
    if not csv_sources:
        print("No sources loaded from CSV!")
        return
    
    # Update existing sources
    print("Updating existing sources...")
    updated_sources = loader.update_existing_sources(csv_sources)
    
    # Save to YAML
    print("Saving to YAML...")
    if loader.save_to_yaml(updated_sources):
        print("Sources saved successfully!")
    else:
        print("Failed to save sources!")
        return
    
    # Generate and print stats
    stats = loader.generate_source_stats(updated_sources)
    loader.print_stats(stats)

if __name__ == "__main__":
    main()
