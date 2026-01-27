# Portfolio Processing Pipeline (Experimental)

This module implements an experimental pipeline for processing user portfolios from various sources (Files, GitHub, Notion), refining the content using an LLM, and storing it as vector embeddings in Chroma DB.

## Features

-   **Multi-Source Extraction**:
    -   **File**: Text files (`.txt`, `.md`, `.json`), Images (`.png`, `.jpg` via Surya OCR).
    -   **GitHub**: Extracts raw content from GitHub READMEs or files.
    -   **Notion**: (Planned) Extracts content via Notion API.
-   **LLM Refinement**: Uses Google Gemini to clean, structure, and correct extracted text.
-   **Vector Storage**: stores embeddings using HuggingFace models in a local Chroma DB instance.

## Setup

1.  **Environment Variables**:
    Create a `.env` file in `llm-pipeline/portfolios/` (or use the one in `llm-pipeline/`):
    ```ini
    GOOGLE_API_KEY=your_google_api_key
    ```

2.  **Installation**:
    It is recommended to use the dedicated virtual environment.
    ```bash
    # Create venv (if not exists)
    python -m venv llm-pipeline/portfolios/venv

    # Install dependencies
    llm-pipeline/portfolios/venv/Scripts/pip install -r llm-pipeline/portfolios/requirements.txt
    ```

    > **Note**: For image extraction, `surya-ocr` requires PyTorch and may download models on the first run.

## Usage

Run the `main.py` script from the project root.

### 1. Process a Local File
```bash
llm-pipeline/portfolios/venv/Scripts/python llm-pipeline/portfolios/main.py --source_type file --source_path llm-pipeline/portfolios/data/sample_portfolio.txt
```

### 2. Process a GitHub URL
```bash
llm-pipeline/portfolios/venv/Scripts/python llm-pipeline/portfolios/main.py --source_type github --source_path https://github.com/user/repo/blob/main/README.md
```

### 3. Process Notion (Planned)
```bash
llm-pipeline/portfolios/venv/Scripts/python llm-pipeline/portfolios/main.py --source_type notion --source_path <page_id>
```

## Directory Structure

```
llm-pipeline/portfolios/
├── src/
│   ├── extractors/       # Source-specific extractors (File, GitHub, Notion)
│   ├── processors/       # Text processing (LLM Refinement)
│   └── storage/          # Vector database interactions (Chroma)
├── data/                 # Sample data
├── venv/                 # Virtual environment
├── main.py               # Entry point script
├── requirements.txt      # Dependencies
└── README.md             # This file
```
