from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
from gtts import gTTS
from django.http import HttpResponse
import pdfplumber
import os
from pdf2image import convert_from_path

def home(request):
    return render(request, 'cso211/home.html')

# Function to extract text from PDF 
def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf = PdfReader(file)
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:  
                    text += page_text + "\n"
    except Exception as e:
        error_msg = f"[ERROR] Failed to extract text: {str(e)}"
        return error_msg
    return text.strip()



def extract_text_from_scanned_pdf(pdf_path, lang='eng', dpi=300):

    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path, dpi=dpi)
        extracted_text = []
        
        for image in images:
            # Preprocessing can be done here
            
            text = pytesseract.image_to_string(image, lang=lang).strip()
            if text:
                extracted_text.append(text)
        
        return "\n\n".join(extracted_text) if extracted_text else "[INFO] No text detected."
    
    except FileNotFoundError:
        error_msg = f"[ERROR] Image file not found: {pdf_path}"
        return error_msg
    except Exception as e:
        error_msg = f"[ERROR] Failed to extract text: {str(e)}"
        return error_msg


# Function to extract text from an image using pytesseract
def extract_text_from_image(image_path, lang='eng'):

    try:
        image = Image.open(image_path)
        
        # we can Preprocess the image for better OCR results
        text = pytesseract.image_to_string(image, lang=lang)
        
        return text.strip()  
    
    except FileNotFoundError:
        error_msg = f"[ERROR] Image file not found: {image_path}"
        return error_msg
    except Exception as e:
        error_msg = f"[ERROR] Failed to extract text: {str(e)}"
        return error_msg

# Function to read text out loud using gTTS and save it as an audio file in the 'uploads' directory
def read_text_out_loud(text):
    if not text:
        return None
    tts = gTTS(text=text, lang='en')
    
    # Save the audio file directly to the 'uploads' directory
    audio_file_path = os.path.join(settings.BASE_DIR, 'uploads', 'output.mp3')
    tts.save(audio_file_path)
    return audio_file_path



def upload_file(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        upload_dir = os.path.join(settings.BASE_DIR, 'uploads')
        
        # Use FileSystemStorage to save the uploaded file
        fs = FileSystemStorage(location=upload_dir)
        file_path = fs.save(uploaded_file.name, uploaded_file)
        file_path = os.path.join(upload_dir, file_path)

        # Extract text based on file type
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        extracted_text = ""

        if file_extension == '.txt':
            with open(file_path, 'r') as file:
                extracted_text = file.read()
        elif file_extension == '.pdf':
            
            extracted_text = extract_text_from_pdf(file_path)
            if not extracted_text.strip():
                extracted_text = extract_text_from_scanned_pdf(file_path)

        elif file_extension in ['.png', '.jpg', '.jpeg']:
            extracted_text = extract_text_from_image(file_path)
        else:
            extracted_text = "Unsupported file format! Please upload a .txt, .pdf, or an image file."
        
        if extracted_text:
            pass        
        else:
            extracted_text="Failed to find any text from the file"

        # Generate audio file from extracted text and save it in 'uploads'
        audio_path = read_text_out_loud(extracted_text)
        audio_url = None
        if audio_path:
            audio_url = '/uploads/output.mp3'

        return render(request, 'cso211/output.html', {
            'file_url': fs.url(file_path),
            'audio_url': audio_url,
            'extracted_text': extracted_text
        })

    return render(request, 'cso211/upload.html')

# how to implement multiprocessing here like breaking the file if it's size is more than 5 mb into chunks of 5mb
