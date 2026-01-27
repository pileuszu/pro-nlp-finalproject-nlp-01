from .base import BaseExtractor

class NotionExtractor(BaseExtractor):
    """Extractor for Notion pages via API."""

    def extract(self, source: str) -> str:
        # TODO: Implement Notion API integration
        # source might be a Page ID or URL
        return f"Notion extraction not implemented yet. Source provided: {source}"
