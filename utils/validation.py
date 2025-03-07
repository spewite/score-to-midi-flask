import os
import magic
from PIL import Image
from werkzeug.utils import secure_filename

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".svg", ".png", ".jpg", ".jpeg", ".bmp", ".pdf"}
ALLOWED_PIXELS = 7000
ALLOWED_MIME_TYPES = {
    'image/png', 
    'image/jpeg', 
    'image/svg+xml',
    "image/bmp",
    "application/pdf"
}

def validate_file(file):
    """
    Validates a file for size, extension, and MIME type.
    
    Args:
        file: The file from request.files
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check if file exists
    if not file:
        return False, "No file provided"
    
    # Secure the filename to prevent path traversal attacks
    filename = secure_filename(file.filename)
    if not filename:
        return False, "Invalid filename"
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset file pointer
    
    if file_size > MAX_FILE_SIZE:
        return False, f"File size exceeds maximum allowed size ({MAX_FILE_SIZE//1024//1024}MB)"
    
    # Check file extension
    _, extension = os.path.splitext(filename)
    extension = extension.lower()
    
    if extension not in ALLOWED_EXTENSIONS:
        return False, f"File type not allowed. Accepted formats: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Check MIME type (more reliable than extension)
    file_content = file.read(2048)  # Read first 2048 bytes for MIME detection
    file.seek(0)  # Reset file pointer
    
    mime_type = magic.from_buffer(file_content, mime=True)
    if mime_type not in ALLOWED_MIME_TYPES:
        return False, f"File content does not match allowed types. Detected: {mime_type}"
       
    # Check image pixels ONLY for image files (not PDFs)
    if mime_type.startswith('image/') and mime_type != 'image/svg+xml' and mime_type != 'application/pdf':
        try:
            file.seek(0)  # Reset file pointer again before opening with PIL
            img = Image.open(file)
            width, height = img.size
            if width > ALLOWED_PIXELS or height > ALLOWED_PIXELS: 
                return False, f"The uploaded image exceeds the maximum resolution of {ALLOWED_PIXELS}x{ALLOWED_PIXELS} pixels. Please upload a smaller image."
            file.seek(0)  # Reset file pointer after checking
        except Exception as e:
            return False, f"Error validating image dimensions: {str(e)}"
   
    return True, None