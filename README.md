# SIH 2026 Document Analyser

Analyse PDFs, Word documents, Excel workbooks, CSV files, and images with a
local Ollama model. PDFs, DOCX, Excel, and CSV files are converted to text
first; images are processed directly by Qwen's vision capability.

## Setup

```powershell
pip install -e .
ollama pull qwen3-vl:4b
```

Ensure Ollama is running, then analyse a file:

```powershell
python OCR/document_pipeline.py OCR/input/ai-data-scientist.pdf
python OCR/document_pipeline.py path/to/report.docx
python OCR/document_pipeline.py path/to/workbook.xlsx
python OCR/document_pipeline.py path/to/data.csv
python OCR/document_pipeline.py OCR/input/handwritten.jpeg
```

Use `--model` to select another Ollama vision-capable model. Supported
extensions are PDF, DOCX, XLSX/XLSM/XLTX/XLTM, CSV, PNG, JPG/JPEG, WEBP, BMP,
GIF, TIF, and TIFF.

## 🤝 Meet the Team

| Name | GitHub Profile |
| :--- | :--- |
| **Het** | [@Hetk28](https://github.com/Hetk28) |
| **Arijeet** | [@ArijeetKurse](https://github.com/ArijeetKurse) |
| **Yug** | [@YugShah17](https://github.com/YugShah17) |
| **Mahek** | [@mahekpatel2112](https://github.com/mahekpatel2112) |
| **Murli** | [@MurliT](https://github.com/MurliT) |
| **Vikas** | [@Vicky404-git](https://github.com/Vicky404-git) |
