"""Task T10.7: Automated PDF compliance checker (page count, file size, live text, R3 Slide 9 check)."""
import os
import sys
from pathlib import Path

import fitz  # PyMuPDF

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config


def main() -> int:
    pdf_path = config.SLIDES_BUILD_DIR / f"{config.ACCOUNT_NAME}.pdf"
    if not pdf_path.exists():
        print(f"ERROR: PDF not found at {pdf_path}")
        return 1

    size_bytes = os.path.getsize(pdf_path)
    size_mb = size_bytes / (1024 * 1024)
    print(f"PDF Path: {pdf_path}")
    print(f"File Size: {size_mb:.2f} MB ({size_bytes:,} bytes) [Limit: <= {config.MAX_PDF_MB} MB]")
    if size_mb > config.MAX_PDF_MB:
        print(f"FAIL: PDF exceeds {config.MAX_PDF_MB} MB limit!")
        return 1

    doc = fitz.open(pdf_path)
    n_pages = len(doc)
    print(f"Page Count: {n_pages} [Required: == {config.MAX_SLIDES}]")
    if n_pages != config.MAX_SLIDES:
        print(f"FAIL: Expected {config.MAX_SLIDES} pages, got {n_pages}")
        return 1

    for idx, page in enumerate(doc):
        rect = page.rect
        txt = page.get_text("text").strip()
        if len(txt) < 80:
            print(f"FAIL: Slide {idx + 1} has insufficient selectable text ({len(txt)} chars).")
            return 1
        # Check aspect ratio is ~16:9 (1.777...)
        ratio = rect.width / rect.height
        if abs(ratio - (16.0 / 9.0)) > 0.05:
            print(f"FAIL: Slide {idx + 1} aspect ratio is {ratio:.3f}, expected 16:9 (1.778).")
            return 1

    # R3 Check on Slide 9 (index 8): Model name, evaluation metric, and score must be selectable text
    slide9_text = doc[8].get_text("text")
    required_slide9_tokens = [
        "XGBoost",
        "LightGBM",
        "Logistic Regression",
        "ROC-AUC",
        "Accuracy",
        "0.6938",
        "0.6357",
        "0.7013",
        "0.7011",
    ]
    missing_tokens = [t for t in required_slide9_tokens if t not in slide9_text]
    if missing_tokens:
        print(f"FAIL: Slide 9 (R3 check) missing selectable tokens: {missing_tokens}")
        return 1

    print("PASS: All 15 pages verified (16:9 aspect ratio, <= 10 MB, selectable text, R3 Slide 9 check passed).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
