import os
from pathlib import Path
from PIL import Image
from .base import BaseExtractor

try:
    from surya.ocr import run_ocr
    from surya.model.detection import segformer
    from surya.model.recognition.model import load_model as load_rec_model
    from surya.model.recognition.processor import load_processor as load_rec_processor
    SURYA_AVAILABLE = True
except ImportError:
    SURYA_AVAILABLE = False
    print("Warning: Surya OCR not found. Image extraction will fail.")

class FileExtractor(BaseExtractor):
    """Extractor for local files (Text, Markdown, Images)."""

    def extract(self, source: str) -> str:
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {source}")

        suffix = path.suffix.lower()
        
        if suffix in ['.txt', '.md', '.json', '.yaml', '.yml']:
            return self._extract_text(path)
        elif suffix in ['.jpg', '.jpeg', '.png', '.bmp']:
            return self._extract_image(path)
        # TODO: Add PDF support
        else:
            print(f"Unsupported file type: {suffix}. Treating as text.")
            return self._extract_text(path)

    def _extract_text(self, path: Path) -> str:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    def _extract_image(self, path: Path) -> str:
        if not SURYA_AVAILABLE:
            raise ImportError("Surya OCR is not installed.")
        
        try:
            image = Image.open(path)
            langs = ["ko", "en"] 
            
            # Load models (this might be slow on first run)
            # Optimization: Load once in __init__ if reused often, but here we invoke on demand
            det_processor, det_model = segformer.load_processor(), segformer.load_model()
            rec_model, rec_processor = load_rec_model(), load_rec_processor()

            predictions = run_ocr([image], [langs], det_model, det_processor, rec_model, rec_processor)
            
            full_text = ""
            for result in predictions:
                for line in result.text_lines:
                    full_text += line.text + "\n"
            
            return full_text
        except Exception as e:
            print(f"Error during Surya OCR extraction: {e}")
            return ""
