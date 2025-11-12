"""
Social Media Content Analyzer - FastAPI Application
Extracts text from PDFs and images, provides engagement suggestions
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.requests import Request
import os
import tempfile
from pathlib import Path

from .extractors import extract_text_from_pdf, extract_text_from_image

# Initialize FastAPI app
app = FastAPI(
    title="Social Media Content Analyzer",
    description="Extract text from PDFs and images with OCR support",
    version="1.0.0"
)

# Setup directories
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATE_DIR = BASE_DIR / "templates"

# Mount static files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

# Allowed file extensions
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def get_engagement_suggestions(text: str) -> list:
    """
    Generate quick engagement suggestions based on extracted text
    """
    suggestions = []
    
    text_lower = text.lower()
    word_count = len(text.split())
    
    # Analyze content and provide suggestions
    if word_count < 50:
        suggestions.append("💡 Consider adding more detailed information to increase engagement")
    elif word_count > 500:
        suggestions.append("✂️ Try breaking long content into shorter, digestible sections")
    
    if "?" in text:
        suggestions.append("❓ Good! Questions encourage audience interaction")
    else:
        suggestions.append("❓ Consider adding a question to prompt comments")
    
    if any(word in text_lower for word in ["please", "share", "comment", "follow", "subscribe"]):
        suggestions.append("📢 Strong CTA detected - great for driving engagement!")
    else:
        suggestions.append("📢 Add a clear call-to-action (CTA) to guide your audience")
    
    if any(emoji in text for emoji in ["😀", "❤️", "👍", "🎉", "✨"]):
        suggestions.append("😊 Emojis detected - great for visual interest!")
    else:
        suggestions.append("😊 Consider adding emojis to make content more visually appealing")
    
    if "\n" in text or text.count(".") > 3:
        suggestions.append("📝 Good formatting detected - easy to read")
    else:
        suggestions.append("📝 Try using line breaks and shorter paragraphs for better readability")
    
    return suggestions


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main UI page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/extract")
async def extract_content(file: UploadFile = File(...)):
    """
    Extract text from uploaded PDF or image
    
    Args:
        file: Uploaded PDF or image file
        
    Returns:
        JSON with extracted text and engagement suggestions
    """
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Validate file size
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024:.0f}MB"
            )
        
        # Extract text based on file type
        if file_ext == ".pdf":
            # Create temporary file for PDF
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(contents)
                tmp_path = tmp.name
            
            try:
                extracted_text = extract_text_from_pdf(tmp_path)
            except Exception as e:
                raise HTTPException(
                    status_code=422,
                    detail=f"PDF extraction error: {str(e)}. Try using images instead."
                )
            finally:
                try:
                    os.unlink(tmp_path)
                except:
                    pass
        
        elif file_ext in {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}:
            # Create temporary file for image
            with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as tmp:
                tmp.write(contents)
                tmp_path = tmp.name
            
            try:
                extracted_text = extract_text_from_image(tmp_path)
            except Exception as e:
                # Check if it's a Tesseract error
                if "pytesseract" in str(e).lower() or "tesseract" in str(e).lower():
                    raise HTTPException(
                        status_code=500,
                        detail="Tesseract OCR not installed. Please install: https://github.com/UB-Mannheim/tesseract/wiki"
                    )
                raise HTTPException(
                    status_code=422,
                    detail=f"Image extraction error: {str(e)}"
                )
            finally:
                try:
                    os.unlink(tmp_path)
                except:
                    pass
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        if not extracted_text or extracted_text.strip() == "":
            raise HTTPException(
                status_code=422,
                detail="No text could be extracted from the file. Try a clearer image or different file."
            )
        
        # Generate engagement suggestions
        suggestions = get_engagement_suggestions(extracted_text)
        
        return JSONResponse({
            "success": True,
            "filename": file.filename,
            "extracted_text": extracted_text,
            "suggestions": suggestions,
            "text_length": len(extracted_text),
            "word_count": len(extracted_text.split())
        })
    
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"ERROR in /extract: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Social Media Content Analyzer"}


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail}
    )


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

