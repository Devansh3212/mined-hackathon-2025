# Mined-Hackathon-2025
# Paper to X

## Project Overview
This project provides an AI-powered workbench for generating alternative content from research papers. It allows users to upload a research paper (PDF) and automatically generates:

- 📝 **Summarized Content**
- 🎙 **AI-generated Podcast**
- 📊 **Presentation Slides**

This tool enables researchers, students, and professionals to quickly understand and present research findings in various formats using AI models.

## Features
- **PDF Extraction:** Extracts text from research papers.
- **AI-powered Summarization:** Uses Ollama's Llama2 model to summarize research papers.
- **AI Voiceover:** Converts summaries into AI-generated audio using ElevenLabs.
- **Presentation Slides:** Creates PowerPoint presentations from summarized content.
- **User Interface:** Provides an interactive UI via Streamlit.

## Tech Stack
- **Backend:** FastAPI
- **Frontend:** Streamlit
- **AI Models:** Llama2 (Ollama), ElevenLabs TTS
- **PDF Processing:** PyMuPDF, FPDF
- **Presentation Generation:** python-pptx
- **Logging:** Python logging module
- **Deployment:** Uvicorn

---

## Setup Instructions

### Prerequisites
Ensure you have the following installed on your system:
- Python 3.8+
- pip
- virtualenv (recommended)
- CUDA-enabled GPU (optional but recommended)

### 1. Clone the Repository
```sh
git clone https://github.com/Devansh3212/mined-hackathon-2025.git
cd mined-hackathon-2025
```

### 2. Install Dependencies
```sh
pip install -r requirements.txt
```

### 3. Set Up API Keys
Create a `.env` file in the root directory and add your API keys:
```ini
ELEVENLABS_API_KEY=your-elevenlabs-api-key
HUGGINGFACE_API_TOKEN=your-huggingface-api-token
```
Ensure you replace `your-elevenlabs-api-key` and `your-huggingface-api-token` with actual API keys.

### 4. Run the Backend Server
```sh
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```
This will start the FastAPI backend.

### 5. Run the Streamlit Frontend
```sh
streamlit run app.py
```
The application will be available at `http://localhost:8501/`.

---

## Troubleshooting

### 1. API Key Errors
- Ensure `.env` file is correctly set up.
- Reload the environment: `source venv/bin/activate` or `venv\Scripts\activate` (Windows).

### 2. CUDA Errors
- Ensure you have installed PyTorch with CUDA support if using a GPU.
- Use CPU mode if necessary by modifying `pipe.to("cuda")` to `pipe.to("cpu")` in `main.py`.

### 3. Missing Dependencies
- Run `pip install -r requirements.txt` to install all dependencies.
- Ensure you are inside the virtual environment when running the application.

---

## Future Enhancements
- **AI Video Generation** using RunwayML.
- **Multi-Language Summarization & Translation.**
- **Integration with Reference Management Tools.**

---

## License
This project is licensed under the MIT License.

---

## Contributors
- **Devansh Shah** - Developer
- **Roshni Rana** - Developer


