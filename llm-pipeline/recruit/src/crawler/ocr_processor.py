import pandas as pd
import requests
from PIL import Image
from io import BytesIO
from surya.ocr import run_ocr
from surya.model.detection import segformer
from surya.model.recognition.model import load_model as load_rec_model
from surya.model.recognition.processor import load_processor as load_rec_processor
import warnings
import time

warnings.filterwarnings("ignore")

class OCRProcessor:
    def __init__(self):
        print("Loading Surya OCR models...")
        self.det_processor, self.det_model = segformer.load_processor(), segformer.load_model()
        self.rec_model, self.rec_processor = load_rec_model(), load_rec_processor()
        print("Models loaded.")

    def process_csv(self, input_csv, output_csv):
        print(f"Reading {input_csv}...")
        try:
            df = pd.read_csv(input_csv)
        except FileNotFoundError:
            print(f"File {input_csv} not found.")
            return

        if 'Needs_OCR' not in df.columns or 'Image_URLs' not in df.columns:
            print("Required columns (Needs_OCR, Image_URLs) not found.")
            return

        # Filter rows needing OCR
        # Need to handle Needs_OCR being boolean or string "True"/"False" depending on how pandas loaded it
        # Let's force proper boolean interpretation
        df['Needs_OCR'] = df['Needs_OCR'].astype(str).str.lower() == 'true'
        
        ocr_indices = df[df['Needs_OCR']].index.tolist()
        print(f"Found {len(ocr_indices)} posts requiring OCR.")

        for idx in ocr_indices:
            row = df.loc[idx]
            image_urls = str(row['Image_URLs']).split(',')
            image_urls = [url.strip() for url in image_urls if url.strip()]

            if not image_urls:
                print(f"Row {idx}: Needs OCR but no images found.")
                continue

            print(f"Processing Row {idx} (Job ID: {row.get('Job ID', 'Unknown')})... {len(image_urls)} images.")
            
            extracted_texts = []
            
            for url in image_urls:
                try:
                    # Download image
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    image = Image.open(BytesIO(response.content)).convert("RGB")
                    
                    # Run OCR
                    print(f"  Running OCR on {url}...")
                    predictions = run_ocr([image], [self.language], self.det_model, self.det_processor, self.rec_model, self.rec_processor)
                    
                    # Surya returns a list of OCRResult objects. We want the text lines.
                    # predictions[0] is for the first (and only) image
                    text_lines = [line.text for line in predictions[0].text_lines]
                    full_text = "\n".join(text_lines)
                    
                    extracted_texts.append(full_text)
                    
                except Exception as e:
                    print(f"  Error processing image {url}: {e}")

            if extracted_texts:
                new_text = "\n\n[OCR Extracted Text]\n" + "\n\n".join(extracted_texts)
                # Append to Full_Context
                current_context = str(df.loc[idx, 'Full_Context'])
                if current_context == 'nan' or current_context == 'N/A':
                    df.loc[idx, 'Full_Context'] = new_text
                else:
                    df.loc[idx, 'Full_Context'] = current_context + "\n" + new_text
                
                # Mark as processed (optional, or separate status?)
                # User asked to just "read text and combine to Full_Context"
                # We can set Needs_OCR to False to indicate completion
                df.loc[idx, 'Needs_OCR'] = False
                print(f"  Updated Full_Context for Job {row.get('Job ID', 'Unknown')}.")

        # Save result
        df.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print(f"Processing complete. Saved to {output_csv}")
    
    # Surya's run_ocr doesn't take language arg in the simplified call, 
    # but the full pipeline does. The pip version might be different.
    # Let's check the imported run_ocr signature or just use the defaults.
    # Actually, run_ocr signature: (images, langs, det_model, det_processor, rec_model, rec_processor)
    # So we need to pass langs.
    language = ["ko", "en"] 

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="Input CSV file")
    parser.add_argument("--output", type=str, required=True, help="Output CSV file")
    args = parser.parse_args()

    processor = OCRProcessor()
    processor.process_csv(args.input, args.output)
