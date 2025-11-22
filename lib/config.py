import os
from pathlib import Path

from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    RAW_DIR = Path('raw')    # input pdf
    TRIM_DIR = Path('trim')  # intermediate before OCR
    OCR_DIR = Path('ocr')    # 
    OUT_DIR = Path('out')    # final output

    # Pixels from the top to mask with white
    HEADER_HEIGHT = 55

    # API key from Mistral AI
    MISTRAL_API_KEY = os.environ.get('MISTRAL_API_KEY')
