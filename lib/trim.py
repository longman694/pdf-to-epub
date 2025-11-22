import fitz  # PyMuPDF
from pathlib import Path
from .config import Settings

# --- CONFIGURATION ---
# Define directories using Path objects
RAW_DIR = Settings.RAW_DIR
TRIM_DIR = Settings.TRIM_DIR

# Pixels from the top to mask with white
HEADER_HEIGHT = Settings.HEADER_HEIGHT
# ---------------------

def remove_header_batch():
    # 1. Create output directory if it doesn't exist
    # parents=True creates missing parent dirs; exist_ok=True doesn't crash if it exists
    TRIM_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check if input directory exists
    if not RAW_DIR.exists():
        print(f"Error: The directory '{RAW_DIR}' does not exist.")
        return

    # 2. Use glob to find all .pdf files (case insensitive for extensions is harder in glob, 
    # usually *.pdf covers it, but we can filter manually for robustness if needed)
    pdf_files = list(RAW_DIR.glob('*.pdf'))

    if not pdf_files:
        print(f"No PDF files found in '{RAW_DIR}'.")
        return

    print(f"Found {len(pdf_files)} PDF files. Processing...")

    # 3. Process each PDF
    for pdf_file in pdf_files:
        # Construct output path using the / operator
        output_path = TRIM_DIR / pdf_file.name

        try:
            # Open the document (PyMuPDF accepts Path objects)
            doc = fitz.open(pdf_file)

            for page in doc:
                # Get page dimensions
                page_rect = page.rect
                
                # Define the area to mask (x0, y0, x1, y1)
                header_rect = fitz.Rect(0, 0, page_rect.width, HEADER_HEIGHT)

                # Draw white box (removing header visually)
                # color and fill are set to White (1, 1, 1)
                page.draw_rect(header_rect, color=(1, 1, 1), fill=(1, 1, 1), overlay=True)

            # Save to the new path
            doc.save(output_path)
            doc.close()
            print(f"[Success] Saved: {output_path}")

        except Exception as e:
            print(f"[Error] Failed processing {pdf_file.name}: {e}")

    print("--- Batch processing complete ---")

if __name__ == "__main__":
    remove_header_batch()
