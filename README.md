# MTG Analysis Project

This project analyzes Magic: The Gathering card data from Scryfall to explore how card prices vary by color identity, release year, set, and color combination. It downloads the current Scryfall default-card dataset, filters it to expansion sets, calculates summary statistics, and displays interactive Plotly charts plus Seaborn visualizations in a Jupyter notebook.

## Requirements

- Python 3.12 or newer
- Internet access to download the Scryfall dataset
- A graphical environment for the charts to open correctly
- Either [uv](https://docs.astral.sh/uv/) or standard Python packaging tools
- A browser for JupyterLab

The analysis downloads data at runtime, so the project does not require a checked-in copy of the large card dataset.

## Setup

From the repository root, create the environment and install the project:

```bash
uv sync
```

To use standard Python tooling instead:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install .
```

## Run the notebook

From the repository root, start JupyterLab with:

```bash
uv run mtg-analysis-project
```

This opens JupyterLab with `notebooks/MTG_Analysis_Visualization.ipynb`. Run the cells from top to bottom. The first cell downloads the Scryfall data, and later cells display the charts inline in the notebook.

You can also start JupyterLab directly:

```bash
uv run jupyter lab notebooks/MTG_Analysis_Visualization.ipynb
```

With an activated virtual environment, the equivalent command is:

```bash
mtg-analysis-project
```

The notebook downloads the Scryfall data to `cards.json` in the current directory and creates image files for the Seaborn charts. Run it from the repository root or another writable directory.

## What the analysis produces

- A filtered dataset containing expansion-set cards and selected card metadata
- Average non-foil prices by mono-color identity
- Average prices by release year
- Card counts by color identity
- Average prices for color combinations containing up to three colors
- A set-level comparison of average prices by color

Prices are the USD values supplied by Scryfall. Missing prices are converted to `NaN` and are excluded from the relevant averages.

## Data source and limitations

The script uses Scryfall's public default-card data endpoint. Results reflect the data available when the command is run and can change as card prices and metadata are updated. The analysis is exploratory: price averages do not account for condition, printing-specific market differences beyond the source fields, supply, demand, legality, or deck performance.

The visualization module is intentionally a script-style analysis and does not expose command-line options. Its charts require a display-capable environment; headless environments may need a configured Matplotlib/Plotly renderer.

## Project layout

```text
notebooks/
└── MTG_Analysis_Visualization.ipynb
src/mtg_analysis_project/
├── __init__.py
└── MTG_Analysis_Visualization.py
pyproject.toml
uv.lock
README.md
```

## Development

The project uses a `src` layout and `uv.lock` to keep dependency resolution reproducible. Before submitting changes, verify that the package compiles and that the notebook launcher imports successfully:

```bash
python -m compileall src
python -c "import mtg_analysis_project"
```

There are currently no automated tests in the repository. The `.py` file is retained as the original script-based analysis; the notebook is the recommended user-facing workflow.
