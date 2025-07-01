from abc import ABC, abstractmethod

class NewsAgent(ABC):
    @abstractmethod
    def fetch(self):
        pass

    @abstractmethod
    def parse(self, raw_data):
        pass 