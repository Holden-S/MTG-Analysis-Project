import subprocess
import sys
from pathlib import Path


def main() -> None:
    notebook = (
        Path(__file__).resolve().parents[2]
        / "notebooks"
        / "MTG_Analysis_Visualization.ipynb"
    )
    subprocess.run(
        [sys.executable, "-m", "jupyter", "lab", str(notebook)],
        check=True,
    )
