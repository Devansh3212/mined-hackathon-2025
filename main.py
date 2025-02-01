import os
import fitz  # PyMuPDF for PDF processing
from fastapi import FastAPI, UploadFile, HTTPException
from dotenv import load_dotenv
from diffusers import StableDiffusionPipeline
from elevenlabs import generate
import requests
from pptx import Presentation
import uvicorn
from huggingface_hub import login
import ollama  # Use the ollama package directly
import logging
from fpdf import FPDF

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)

# Load environment variables
load_dotenv()

# Create a directory for temporary files
TEMP_DIR = "temp_files"
os.makedirs(TEMP_DIR, exist_ok=True)

# Get API keys securely
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

# Ensure API keys are set
if not ELEVENLABS_API_KEY or not HUGGINGFACE_API_TOKEN:
    logging.error("API keys are not set correctly.")
    raise ValueError("API keys are missing.")

# Authenticate with Hugging Face Hub
login(token=HUGGINGFACE_API_TOKEN)

# Load Stable Diffusion model
pipe = StableDiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-xl").to("cuda")
logging.info("Stable Diffusion model loaded successfully.")

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "FastAPI server is running!"}

# Extract text from PDF
def extract_text_from_pdf(pdf_path):
    try:
        with fitz.open(pdf_path) as doc:
            return "".join(page.get_text("text") for page in doc)
    except Exception as e:
        logging.error(f"PDF Extraction Error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"PDF Extraction Error: {str(e)}")

# Ollama Summary
def ollama_summary(text, summary_length="medium"):
    try:
        response = ollama.generate(
            model="llama2",  # Replace with your Ollama model
            prompt=f"Summarize the following research paper in {summary_length} key points: {text}",
            options={"max_tokens": 1000}
        )
        logging.info("Ollama summary generated successfully.")
        return response["response"] if "response" in response else ""
    except Exception as e:
        logging.error(f"Ollama Summary Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ollama Summary Error: {str(e)}")

# Save summary to PDF
def save_summary_to_pdf(summary, output_path):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, summary)
        pdf.output(output_path)
        logging.info(f"Summary saved to {output_path}")
    except Exception as e:
        logging.error(f"Error saving summary to PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving summary to PDF: {str(e)}")

# Generate Graphical Abstract
def generate_graphical_abstract(summary):
    try:
        prompt = f"Graphical abstract for a research paper: {summary[:300]}"
        output = pipe(prompt)

        if not output or not hasattr(output, "images") or not output.images:
            logging.warning("No images generated, using placeholder image.")
            placeholder_path = os.path.join(TEMP_DIR, "placeholder.png")
            with open(placeholder_path, "wb") as f:
                f.write(b"")  # Create an empty placeholder file
            return placeholder_path  # Provide a fallback image

        image = output.images[0]
        graphical_abstract_path = os.path.join(TEMP_DIR, "graphical_abstract.png")
        image.save(graphical_abstract_path)
        logging.info(f"Graphical abstract saved at {graphical_abstract_path}")
        return graphical_abstract_path
    except Exception as e:
        logging.error(f"Graphical Abstract Error: {str(e)}")
        return os.path.join(TEMP_DIR, "placeholder.png")  # Return placeholder image instead of crashing

# AI Voiceover
def generate_voice(summary):
    try:
        audio = generate(
            text=summary,
            voice="Lily",
            model="eleven_monolingual_v1",
            api_key=ELEVENLABS_API_KEY
        )
        voiceover_path = os.path.join(TEMP_DIR, "voiceover.mp3")
        with open(voiceover_path, "wb") as f:
            f.write(audio)
    except Exception as e:
        logging.error(f"Voiceover Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Voiceover Error: {str(e)}")

# Generate Presentation
def generate_presentation(summary):
    try:
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        slide.shapes.title.text = "Research Paper Summary"
        slide.shapes.placeholders[1].text_frame.text = summary
        presentation_path = os.path.join(TEMP_DIR, "presentation.pptx")
        prs.save(presentation_path)
    except Exception as e:
        logging.error(f"Presentation Generation Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Presentation Generation Error: {str(e)}")

# FastAPI Route
@app.post("/process-paper/")
async def process_paper(file: UploadFile, summary_length: str = "medium"):
    try:
        file_path = os.path.join(TEMP_DIR, "temp_paper.pdf")
        with open(file_path, "wb") as f:
            while chunk := file.file.read(1024 * 1024):
                f.write(chunk)

        text = extract_text_from_pdf(file_path)
        summary = ollama_summary(text, summary_length)
        
        # Save summary to a PDF file
        summary_pdf_path = os.path.join(TEMP_DIR, "summary.pdf")
        save_summary_to_pdf(summary, summary_pdf_path)
        
        graphical_abstract = generate_graphical_abstract(summary)
        generate_voice(summary)
        generate_presentation(summary)

        return {
            "summary": summary,
            "summary_pdf": summary_pdf_path,
            "graphical_abstract": graphical_abstract,
            "presentation": os.path.join(TEMP_DIR, "presentation.pptx"),
        }
    except Exception as e:
        logging.error(f"Error processing paper: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Run FastAPI Server
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
