"""Placeholder for a future GroundNews scraping agent."""

from .base import NewsAgent

class GroundNewsAgent(NewsAgent):
    def fetch(self):
        raise NotImplementedError("GroundNewsAgent fetch not implemented yet.")

    def parse(self, raw_data):
        raise NotImplementedError("GroundNewsAgent parse not implemented yet.")
