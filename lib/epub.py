import subprocess
import shutil

from .config import Settings

# --- CONFIGURATION ---
OCR_DIR = Settings.OCR_DIR
OUTPUT_DIR = Settings.OUT_DIR
STYLE_FILE = OUTPUT_DIR / 'epub_style.css'
# ---------------------

def create_css():
    """Creates a CSS file to center images and add margins."""
    css_content = """
    /* Standard EPUB Image Styling */
    img {
        display: block;           /* Makes the image a block element so margins work */
        margin-left: auto;        /* Centers horizontally */
        margin-right: auto;       /* Centers horizontally */
        margin-top: 1.5em;        /* Top margin (space) */
        margin-bottom: 1.5em;     /* Bottom margin (space) */
        max-width: 100%;          /* Ensures image fits on the screen */
        height: auto;             /* Maintains aspect ratio */
    }
    
    /* Optional: Style the caption if Pandoc generates one */
    figure {
        margin: 1.5em 0;
        text-align: center;
    }
    
    /* Make standard text look a bit nicer too */
    body {
        line-height: 1.6;
        font-family: sans-serif; 
    }
    """
    
    # Ensure output dir exists before writing
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(STYLE_FILE, 'w', encoding='utf-8') as f:
        f.write(css_content)
    print(f"[Info] Created stylesheet at: {STYLE_FILE}")

def convert_md_to_epub():
    # 1. Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    create_css()

    # Check if OCR directory exists
    if not OCR_DIR.exists():
        print(f"Error: Source directory '{OCR_DIR}' not found.")
        return

    # 2. Find Markdown files
    md_files = list(OCR_DIR.glob('*.md'))
    
    if not md_files:
        print(f"No .md files found in '{OCR_DIR}'.")
        return

    print(f"Found {len(md_files)} Markdown files. Converting to EPUB...")

    # 3. Check if Pandoc is installed
    if not shutil.which("pandoc"):
        print("Error: 'pandoc' is not installed or not in your PATH.")
        print("Please install it from https://pandoc.org/installing.html")
        return

    # 4. Loop and Convert
    for md_file in md_files:
        print(f"\nConverting: {md_file.name}...")
        
        # Define output file name (e.g., output/filename.epub)
        epub_filename = md_file.with_suffix('.epub').name
        output_path = OUTPUT_DIR / epub_filename
        
        # Get absolute paths to avoid confusion when changing working directories
        abs_output_path = output_path.resolve()
        abs_css_path = STYLE_FILE.resolve()
        
        # COMMAND EXPLANATION:
        # 1. We pass the input filename.
        # 2. -o defines the output path.
        # 3. --resource-path=. tells pandoc to look for images in the current folder.
        # 4. --metadata title="..." sets the internal book title (required for valid EPUBs).
        cmd = [
            "pandoc",
            md_file.name,                     # Input file (relative to OCR_DIR)
            "-o", str(abs_output_path),       # Output file (absolute path)
            "--resource-path=.",              # Look for images in current dir
            "--metadata", f"title={md_file.stem}", # Set title to filename
            "--standalone",                   # Create a complete file
            "--mathml",                       # Converts LaTeX to MathML standard for EPUB
            "--from=markdown+tex_math_dollars",
            "--webtex",
            "--css", str(abs_css_path),
        ]

        try:
            # CRITICAL STEP:
            # We run the command *inside* the 'ocr' directory (cwd=OCR_DIR).
            # Why? Because your markdown links look like "filename/image.jpg".
            # By being inside 'ocr', that relative path is valid and Pandoc finds the images.
            subprocess.run(cmd, check=True, cwd=OCR_DIR)
            
            print(f"  [Success] Created: {output_path}")
            
        except subprocess.CalledProcessError as e:
            print(f"  [Error] Pandoc failed for {md_file.name}.")
            print(f"  Command output: {e}")
        except Exception as e:
            print(f"  [Error] Unexpected error: {e}")

    print("\n--- Conversion Batch Complete ---")

if __name__ == "__main__":
    convert_md_to_epub()
