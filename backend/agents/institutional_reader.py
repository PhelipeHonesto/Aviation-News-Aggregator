"""Placeholder for reading institutional news sources."""

from .base import NewsAgent

class InstitutionalReaderAgent(NewsAgent):
    def fetch(self):
        raise NotImplementedError("InstitutionalReaderAgent fetch not implemented yet.")

    def parse(self, raw_data):
        raise NotImplementedError("InstitutionalReaderAgent parse not implemented yet.")
