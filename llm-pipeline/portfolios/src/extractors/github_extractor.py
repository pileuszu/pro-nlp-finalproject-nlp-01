import requests
from .base import BaseExtractor

class GitHubExtractor(BaseExtractor):
    """Extractor for GitHub READMEs or raw files."""

    def extract(self, source: str) -> str:
        """
        Extracts content from a GitHub URL.
        If a normal GitHub URL is provided, tries to convert it to a raw content URL.
        """
        raw_url = self._convert_to_raw_url(source)
        try:
            response = requests.get(raw_url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            return f"Error fetching from GitHub: {e}"

    def _convert_to_raw_url(self, url: str) -> str:
        # Simple heuristic to convert github.com blobs to raw
        # Example: https://github.com/user/repo/blob/main/README.md -> https://raw.githubusercontent.com/user/repo/main/README.md
        if "github.com" in url and "blob" in url:
            return url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        return url
