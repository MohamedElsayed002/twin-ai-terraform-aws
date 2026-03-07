from pathlib import Path
import json
from pypdf import PdfReader

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def _read_text_with_fallback(*filenames: str, default: str = "") -> str:
    for filename in filenames:
        path = DATA_DIR / filename
        if path.exists():
            return path.read_text(encoding="utf-8")
    return default


# Read LinkedIn PDF
try:
    reader = PdfReader(str(DATA_DIR / "linkedin.pdf"))
    linkedin = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            linkedin += text
except FileNotFoundError:
    linkedin = "LinkedIn profile not available"

# Read other data files
summary = _read_text_with_fallback(
    "summary.txt",
    "me.txt",
    default="Summary not available",
)
style = _read_text_with_fallback("style.txt", default="Style notes not available")

with open(DATA_DIR / "facts.json", "r", encoding="utf-8") as f:
    facts = json.load(f)
