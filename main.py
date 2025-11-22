from lib.trim import remove_header_batch
from lib.ocr import run_ocr_pipeline
from lib.epub import convert_md_to_epub


def main():
    print("Run trimming...")
    remove_header_batch()
    print("====================")
    
    print("Run OCR...")
    run_ocr_pipeline()
    print("====================")

    print("Run create EPUB")
    convert_md_to_epub()
    print("====================")


if __name__ == "__main__":
    main()
