"""
Text extraction utilities for PDFs and images
Supports OCR via EasyOCR (no installation required)
"""

import easyocr
from PIL import Image
import os
import platform
import tempfile

# Initialize OCR reader (will download model on first use)
try:
    reader = easyocr.Reader(['en'], gpu=False)
except Exception as e:
    print(f"[WARNING] EasyOCR initialization failed: {e}")
    reader = None


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from PDF file
    
    Converts PDF pages to images using pdf2image (requires Poppler). Each page is
    OCR'd with EasyOCR and combined. If `pdf2image` or Poppler isn't available
    the function raises an informative exception with install instructions.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as string
    """
    # Try to import pdf2image here so the main app can run without it for image-only use
    try:
        from pdf2image import convert_from_path
    except Exception as e:
        raise Exception(
            "PDF extraction requires the Python package 'pdf2image' and the Poppler binaries.\n"
            "Install pdf2image: pip install pdf2image\n"
            "Install Poppler (Windows): https://blog.alivate.com.au/poppler-windows/ (add to PATH)\n"
            "Or (Linux) apt-get install poppler-utils\n"
            f"Original error: {e}"
        )

    # Convert PDF pages to images
    try:
        # If Poppler is installed in a custom location on Windows, set POPPLER_PATH env var
        poppler_path = os.environ.get('POPPLER_PATH')
        if poppler_path:
            pages = convert_from_path(pdf_path, dpi=200, fmt='png', poppler_path=poppler_path)
        else:
            pages = convert_from_path(pdf_path, dpi=200, fmt='png')
    except Exception as e:
        raise Exception(
            "Failed to convert PDF to images. Ensure Poppler is installed and accessible.\n"
            "See: https://pdf2image.readthedocs.io/en/latest/installation.html\n"
            f"Original error: {e}"
        )

    # OCR each page and combine text
    texts = []
    for i, page in enumerate(pages):
        tmp = None
        try:
            tmp = tempfile.NamedTemporaryFile(suffix=f'_page{i}.png', delete=False)
            page.save(tmp.name, format='PNG')
            tmp.close()

            # Use the image extractor (EasyOCR)
            page_text = extract_text_from_image(tmp.name)
            if page_text and page_text.strip():
                texts.append(page_text)
        finally:
            if tmp is not None:
                try:
                    os.unlink(tmp.name)
                except Exception:
                    pass

    if not texts:
        raise Exception("No text extracted from PDF pages")

    return "\n\n--- Page Break ---\n\n".join(texts)


def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from image file using EasyOCR
    
    Supports: JPG, PNG, GIF, BMP, TIFF
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Extracted text as string
    """
    global reader
    
    if reader is None:
        raise Exception("EasyOCR not initialized. Please reinstall easyocr: pip install easyocr")
    
    try:
        print(f"[DEBUG] Opening image: {image_path}")
        img = Image.open(image_path)
        print(f"[DEBUG] Image mode: {img.mode}, Size: {img.size}")
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Apply contrast enhancement for better OCR
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
        
        # Perform OCR using EasyOCR
        print(f"[DEBUG] Starting EasyOCR...")
        results = reader.readtext(image_path)
        
        # Extract text from results
        extracted_text = '\n'.join([text[1] for text in results])
        print(f"[DEBUG] OCR completed. Text length: {len(extracted_text)}")
        print(f"[DEBUG] Extracted text (first 200 chars): {extracted_text[:200]}")
        
        return extracted_text.strip() if extracted_text else "No text found in image"
    
    except Exception as e:
        print(f"[ERROR] Exception in extract_text_from_image: {str(e)}")
        import traceback
        traceback.print_exc()
        raise Exception(f"Error extracting text from image: {str(e)}")


def extract_text(file_path: str) -> str:
    """
    Auto-detect file type and extract text accordingly
    
    Args:
        file_path: Path to the file (PDF or image)
        
    Returns:
        Extracted text as string
    """
    file_ext = file_path.lower().split('.')[-1]
    
    if file_ext == 'pdf':
        return extract_text_from_pdf(file_path)
    elif file_ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff']:
        return extract_text_from_image(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")
