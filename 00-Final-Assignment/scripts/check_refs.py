"""Task T11.2: Verify 100% consistency between references.txt, on-slide [n] tags, and Slide 15."""
import re
import sys
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config


def main() -> int:
    refs_path = config.REFERENCES_TXT
    html_path = config.SLIDES_SRC_DIR / "slides.html"
    pdf_path = config.SLIDES_BUILD_DIR / f"{config.ACCOUNT_NAME}.pdf"

    if not refs_path.exists():
        print(f"ERROR: {refs_path} does not exist.")
        return 1

    ref_lines = [line.strip() for line in refs_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    ref_ids = []
    for line in ref_lines:
        m = re.match(r"^\[(\d+)\]\s+(.+)$", line)
        if not m:
            print(f"FAIL: Malformed line in references.txt: {line}")
            return 1
        ref_ids.append(int(m.group(1)))

    expected_ids = list(range(1, len(ref_lines) + 1))
    if ref_ids != expected_ids:
        print(f"FAIL: Reference IDs {ref_ids} are not sequential 1..{len(ref_lines)}")
        return 1

    print(f"Loaded {len(ref_lines)} numbered references [1]..[{len(ref_lines)}] from references.txt.")

    if html_path.exists():
        html_text = html_path.read_text(encoding="utf-8")
        cited_in_html = sorted({int(x) for x in re.findall(r"\[(\d+)\]", html_text)})
        unknown_in_html = [x for x in cited_in_html if x not in ref_ids]
        if unknown_in_html:
            print(f"FAIL: HTML cites unknown reference IDs: {unknown_in_html}")
            return 1
        uncited = [x for x in ref_ids if x not in cited_in_html]
        if uncited:
            print(f"FAIL: References in references.txt never cited in HTML: {uncited}")
            return 1
        print(f"HTML citation check PASSED: All {len(ref_ids)} references cited.")

    if pdf_path.exists():
        doc = fitz.open(pdf_path)
        slide15_text = doc[-1].get_text("text")
        missing_on_slide15 = [i for i in ref_ids if f"[{i}]" not in slide15_text]
        if missing_on_slide15:
            print(f"FAIL: Slide 15 PDF is missing reference tags: {missing_on_slide15}")
            return 1
        print("Slide 15 PDF reference check PASSED: [1]..[{}] present on Slide 15.".format(len(ref_ids)))

    return 0


if __name__ == "__main__":
    sys.exit(main())
