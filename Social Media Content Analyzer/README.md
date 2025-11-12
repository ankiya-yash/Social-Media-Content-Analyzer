# Social Media Content Analyzer

A lightweight FastAPI web application that extracts text from uploaded PDFs and images (with OCR for scans) and provides quick engagement suggestions for social media content.

## Features

- **Drag-and-drop upload** for PDFs and images
- **PDF text extraction** via PyMuPDF
- **OCR for images** and scanned PDFs via Tesseract
- **Real-time loading indicators** and error handling
- **Clean, responsive UI** with no database required
- **One-click Render deployment** support

## Tech Stack

- **Backend:** FastAPI, Uvicorn
- **Text Extraction:** PyMuPDF (PDF), Pillow + Tesseract (OCR)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Deployment:** Docker, Render

## Quick Start (Local Development)

### Prerequisites

- Python 3.10+
- Tesseract OCR installed:
  - **macOS:** `brew install tesseract`
  - **Ubuntu/Debian:** `sudo apt-get install tesseract-ocr`
  - **Windows:** Download from [UB Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) and ensure `tesseract.exe` is in PATH

### Setup & Run

1. **Clone or download the project**

2. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv
   
   # Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   
   # macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

5. **Open in browser:**
   ```
   http://localhost:8000
   ```

## Usage

1. Open the web interface
2. Upload a PDF or image (drag & drop or use file picker)
3. The app extracts text using:
   - PyMuPDF for PDFs
   - Tesseract OCR for images and scanned documents
4. View extracted content and engagement suggestions
5. Download results (optional)

## Project Structure

```
.
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── render.yaml           # Render deployment config
├── Dockerfile            # Docker image config
├── .gitignore           # Git ignore rules
└── app/
    ├── main.py          # FastAPI application
    ├── extractors.py    # PDF & image text extraction logic
    ├── templates/
    │   └── index.html   # Main UI template
    └── static/
        ├── app.js       # Drag-drop & frontend logic
        └── styles.css   # Styling
```

## Deployment

### Deploy to Render (One-Click)

1. Push this repository to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml` and deploy

The `render.yaml` includes:
- Automatic Docker image building
- Free tier deployment
- Automatic redeploys on push

### Deploy Locally with Docker

```bash
docker build -t social-media-analyzer .
docker run -p 8000:8000 social-media-analyzer
```

## Configuration

### Environment Variables

Create a `.env` file (optional):

```env
UVICORN_HOST=0.0.0.0
UVICORN_PORT=8000
UPLOAD_MAX_MB=50
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Tesseract not found | Install Tesseract and add to PATH |
| PDF extraction fails | Ensure PyMuPDF is installed: `pip install pymupdf` |
| OCR not working | Verify Tesseract binary is accessible |
| Port 8000 in use | Change port: `uvicorn app.main:app --port 8001` |

## API Endpoints

- `GET /` - Main page (UI)
- `POST /extract` - Upload file and extract text
- `GET /health` - Health check

## License

MIT License - feel free to use and modify

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review logs for error messages
3. Ensure all dependencies are installed correctly
"# Social-Media-Content-Analyzer" 
