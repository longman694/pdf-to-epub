from pathlib import Path

from attr import dataclass


@dataclass
class Settings:
    RAW_DIR = Path('raw')    # input pdf
    TRIM_DIR = Path('trim')  # intermediate before OCR
    OCR_DIR = Path('ocr')    # 
    OUT_DIR = Path('out')    # final output

    # Pixels from the top to mask with white
    HEADER_HEIGHT = 55
