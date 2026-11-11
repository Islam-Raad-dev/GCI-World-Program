"""Central configuration for GCI World 2026 Final Assignment (Company A Telecom Churn PoC)."""
import os
from pathlib import Path

# Reproducibility seed
SEED = 42

# Omnicampus account name placeholder (update once confirmed by Islam)
ACCOUNT_NAME = os.environ.get("OMNICAMPUS_ACCOUNT_NAME", "ACCOUNT_NAME")
AUTHOR_NAME = "Islam Raad"
AUTHOR_AFFILIATION = "AI Engineering, University of Mosul"
MAX_SLIDES = 15
MAX_PDF_MB = 10.0

# Base directories
PROJECT_ROOT = Path(__file__).resolve().parent
REFERENCES_TXT = PROJECT_ROOT / "references.txt"
LOCAL_DATA_DIR = PROJECT_ROOT / "telecom"
COLAB_DATA_DIR = Path("/content/drive/MyDrive/Final Assignment/telecom")

if LOCAL_DATA_DIR.exists():
    DATA_DIR = LOCAL_DATA_DIR
elif COLAB_DATA_DIR.exists():
    DATA_DIR = COLAB_DATA_DIR
else:
    DATA_DIR = LOCAL_DATA_DIR

CLIENT_CSV = DATA_DIR / "Client.csv"
RECORD_CSV = DATA_DIR / "Record.csv"

# Output paths
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUTS_DIR / "figures"
TABLES_DIR = OUTPUTS_DIR / "tables"
MODELS_DIR = OUTPUTS_DIR / "models"
RESULTS_JSON = OUTPUTS_DIR / "results.json"

DOCS_DIR = PROJECT_ROOT / "docs"
RESEARCH_DIR = PROJECT_ROOT / "research"
SLIDES_DIR = PROJECT_ROOT / "slides"
SLIDES_SRC_DIR = SLIDES_DIR / "src"
SLIDES_BUILD_DIR = SLIDES_DIR / "build"
SUBMISSION_DIR = PROJECT_ROOT / "submission"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# Design system palette (PRD §10.2 — colorblind-safe pairing: Coral vs Blue)
PALETTE = {
    "navy": "#0B1F3A",       # Titles & primary headers
    "teal": "#0F8B8D",       # Accent / primary action
    "coral": "#E4572E",      # Churn / high risk
    "blue": "#3B7DD8",       # Stayed / baseline
    "slate": "#5B6B7B",      # Secondary text / axes
    "light": "#F5F7FA",      # Slide & chart background
    "amber": "#F2A541",      # Highlight / callout / threshold
    "white": "#FFFFFF",
    "grid": "#E2E8F0",
}

for _d in [FIGURES_DIR, TABLES_DIR, MODELS_DIR, DOCS_DIR, RESEARCH_DIR / "notes", SLIDES_SRC_DIR, SLIDES_BUILD_DIR, SUBMISSION_DIR, NOTEBOOKS_DIR / "checkpoints"]:
    _d.mkdir(parents=True, exist_ok=True)
