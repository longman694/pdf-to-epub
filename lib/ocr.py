import base64
from mistralai import Mistral
from .config import Settings

# --- CONFIGURATION ---
MISTRAL_API_KEY = Settings.MISTRAL_API_KEY
TRIM_DIR = Settings.TRIM_DIR
OCR_DIR = Settings.OCR_DIR
# ---------------------

def save_base64_image(base64_string, save_path):
    """Decodes a base64 string and saves it as an image file."""
    try:
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]
        
        image_data = base64.b64decode(base64_string)
        with open(save_path, "wb") as f:
            f.write(image_data)
    except Exception as e:
        print(f"  [Warning] Failed to save image {save_path.name}: {e}")

def run_ocr_pipeline():
    # 1. Setup Directories
    OCR_DIR.mkdir(parents=True, exist_ok=True)

    if not TRIM_DIR.exists():
        print(f"Error: The directory '{TRIM_DIR}' does not exist.")
        return

    pdf_files = list(TRIM_DIR.glob('*.pdf'))
    if not pdf_files:
        print(f"No PDF files found in '{TRIM_DIR}'.")
        return

    # 2. Initialize Mistral Client
    if "YOUR_MISTRAL_API_KEY_HERE" in MISTRAL_API_KEY:
        print("Error: Please set your MISTRAL_API_KEY at the top of the script.")
        return
    
    client = Mistral(api_key=MISTRAL_API_KEY)
    print(f"Found {len(pdf_files)} files. Starting OCR with Mistral...")

    # 3. Process Files
    for pdf_file in pdf_files:
        print(f"\n--- Processing: {pdf_file.name} ---")
        
        file_stem = pdf_file.stem
        image_output_dir = OCR_DIR / file_stem
        image_output_dir.mkdir(exist_ok=True)

        uploaded_file = None
        try:
            # A. Upload the file to Mistral
            with open(pdf_file, "rb") as f:
                uploaded_file = client.files.upload(
                    file={
                        "file_name": pdf_file.name,
                        "content": f,
                    },
                    purpose="ocr"
                )
            print(f"  Uploaded (ID: {uploaded_file.id})")

            # B. Process with OCR model
            # FIX: Changed 'document_id' to 'file_id' to match SDK requirements
            ocr_response = client.ocr.process(
                model="mistral-ocr-latest",
                document={
                    "type": "file", 
                    "file_id": uploaded_file.id
                },
                include_image_base64=True 
            )

            # C. Extract Images and Fix Markdown
            # Combine markdown from all pages
            full_markdown = ""

            for page in ocr_response.pages:
                page_md = page.markdown
                
                # Handle Images
                if hasattr(page, 'images') and page.images:
                    for img in page.images:
                        img_filename = f"{img.id}"
                        img_save_path = image_output_dir / img_filename
                        
                        save_base64_image(img.image_base64, img_save_path)
                        
                        # Update Markdown reference to local path
                        relative_path = f"{file_stem}/{img_filename}"
                        page_md = page_md.replace(f"({img.id})", f"({relative_path})")

                full_markdown += page_md + "\n\n"

            # D. Save the Markdown File
            md_output_path = OCR_DIR / f"{file_stem}.md"
            with open(md_output_path, "w", encoding="utf-8") as f:
                f.write(full_markdown)
            
            print(f"  [Success] Markdown saved: {md_output_path}")

        except Exception as e:
            print(f"  [Error] Failed processing {pdf_file.name}: {e}")
            # Print detailed error info if available
            if hasattr(e, 'body'):
                print(f"  [Debug info]: {e.body}")
        
        finally:
            # OPTIONAL: Clean up file from Mistral server to save space
            if uploaded_file:
                try:
                    client.files.delete(file_id=uploaded_file.id)
                    print("  [Info] Cleanup: Remote file deleted.")
                except:
                    pass

    print("\n--- OCR Batch Complete ---")

if __name__ == "__main__":
    run_ocr_pipeline()
