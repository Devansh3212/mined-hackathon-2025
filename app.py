# app.py
import streamlit as st
import requests
from pathlib import Path
import tempfile
import base64

def get_download_link(file_path, link_text, mime_type):
    with open(file_path, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    return f'<a href="data:{mime_type};base64,{b64}" download="{file_path.name}" class="download-button">{link_text}</a>'

def main():
    st.set_page_config(
        page_title="AI Research Paper Workbench",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS
    st.markdown("""
        <style>
        .main { padding: 2rem; }
        .stButton>button { width: 100%; margin-top: 1rem; }
        .output-box { 
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #f8fafc;
            margin-bottom: 1rem;
        }
        .download-button {
            display: inline-block;
            padding: 0.5rem 1rem;
            background-color: #0ea5e9;
            color: white;
            text-decoration: none;
            border-radius: 0.375rem;
            margin: 0.5rem 0;
            text-align: center;
            transition: background-color 0.2s;
        }
        .download-button:hover {
            background-color: #0284c7;
        }
        .success-message {
            padding: 1rem;
            background-color: #d1fae5;
            color: #065f46;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        .presenter-notes {
            padding: 1rem;
            background-color: #f3f4f6;
            border-left: 4px solid #6366f1;
            margin: 1rem 0;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.title("🚀 AI Research Paper Workbench")
    
    with st.expander("ℹ️ About", expanded=True):
        st.markdown("""
        Transform research papers into multiple formats:
        - 📝 **Structured Summary**: Key findings, methodology, conclusions, and implications
        - 🎨 **Graphical Abstract**: AI-generated visual representation
        - 🎙️ **Audio Summary**: Professional voiceover explanation
        - 📊 **PowerPoint**: Ready-to-use presentation with speaker notes
        """)

    # Settings
    with st.sidebar:
        st.header("⚙️ Settings")
        summary_length = st.select_slider(
            "Summary Length",
            options=["short", "medium", "long"],
            value="medium",
            help="Choose the level of detail for the summary"
        )
        
        # Processing stats
        st.markdown("---")
        if 'processed_papers' not in st.session_state:
            st.session_state.processed_papers = 0
        st.metric("Papers Processed", st.session_state.processed_papers)
        
        # Advanced settings
        with st.expander("🛠️ Advanced Settings"):
            st.checkbox("Include speaker notes in presentation", value=True)
            st.checkbox("Generate citations", value=True)
            st.slider("Max slides", min_value=5, max_value=20, value=10)

    # Main content
    uploaded_file = st.file_uploader(
        "📂 Upload Research Paper (PDF)",
        type=["pdf"],
        help="Maximum file size: 10MB"
    )
    
    if uploaded_file:
        # Show file details
        file_details = {
            "Filename": uploaded_file.name,
            "Size": f"{uploaded_file.size/1024/1024:.2f} MB",
            "Type": uploaded_file.type
        }
        st.json(file_details)

        if st.button("🔄 Process Paper"):
            try:
                with st.spinner("Processing your paper... This may take a few minutes."):
                    # Create temporary directory for downloaded files
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_dir = Path(temp_dir)
                        
                        # Send to backend
                        files = {"file": uploaded_file}
                        response = requests.post(
                            "http://localhost:8080/process-paper/",
                            files=files,
                            params={"summary_length": summary_length}
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.processed_papers += 1
                            
                            # Success message
                            st.markdown("""
                                <div class="success-message">
                                    ✅ Paper processed successfully! Navigate through the tabs below to see the results.
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # Display results in tabs
                            tab1, tab2, tab3, tab4 = st.tabs([
                                "📝 Summary",
                                "🎨 Visual",
                                "🎙️ Audio",
                                "📊 Presentation"
                            ])
                            
                            with tab1:
                                st.markdown("### 📑 Structured Summary")
                                st.markdown(data["summary"])
                                
                                # Get and save PDF
                                pdf_response = requests.get(data["summary_pdf"])
                                if pdf_response.status_code == 200:
                                    pdf_path = temp_dir / "summary.pdf"
                                    pdf_path.write_bytes(pdf_response.content)
                                    with open(pdf_path, "rb") as f:
                                        st.download_button(
                                            "📥 Download Full Summary (PDF)",
                                            f,
                                            file_name="research_summary.pdf",
                                            mime="application/pdf",
                                            help="Download the complete summary with all details"
                                        )
                            
                            with tab2:
                                st.markdown("### 🎨 Graphical Abstract")
                                img_response = requests.get(data["graphical_abstract"])
                                if img_response.status_code == 200:
                                    img_path = temp_dir / "abstract.png"
                                    img_path.write_bytes(img_response.content)
                                    st.image(img_path, caption="AI-Generated Graphical Abstract")
                                    
                                    # Add description
                                    st.markdown("""
                                        <div class="info-box">
                                            This graphical abstract was generated using Stable Diffusion XL, 
                                            optimized for scientific visualization. It represents the key concepts 
                                            and findings from your paper.
                                        </div>
                                    """, unsafe_allow_html=True)
                                    
                                    with open(img_path, "rb") as f:
                                        st.download_button(
                                            "📥 Download Graphical Abstract",
                                            f,
                                            file_name="graphical_abstract.png",
                                            mime="image/png"
                                        )
                            
                            with tab3:
                                st.markdown("### 🎙️ Audio Summary")
                                audio_response = requests.get(data["voiceover"])
                                if audio_response.status_code == 200:
                                    audio_path = temp_dir / "summary.mp3"
                                    audio_path.write_bytes(audio_response.content)
                                    
                                    # Audio player with description
                                    st.markdown("""
                                        <div class="info-box">
                                            Listen to an AI-voiced summary of your paper's key points. 
                                            Perfect for quick review or sharing with colleagues.
                                        </div>
                                    """, unsafe_allow_html=True)
                                    
                                    st.audio(audio_path)
                                    
                                    with open(audio_path, "rb") as f:
                                        st.download_button(
                                            "📥 Download Audio Summary",
                                            f,
                                            file_name="audio_summary.mp3",
                                            mime="audio/mp3"
                                        )
                            
                            with tab4:
                                st.markdown("### 📊 PowerPoint Presentation")
                                pres_response = requests.get(data["presentation"])
                                if pres_response.status_code == 200:
                                    pres_path = temp_dir / "presentation.pptx"
                                    pres_path.write_bytes(pres_response.content)
                                    
                                    # Presentation description
                                    st.markdown("""
                                        <div class="info-box">
                                            A ready-to-use presentation has been generated with:
                                            - Title and overview slides
                                            - Key findings and methodology
                                            - Graphical abstract integration
                                            - Conclusions and implications
                                            - Speaker notes for each slide
                                        </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Presenter notes preview
                                    st.markdown("""
                                        <div class="presenter-notes">
                                            <strong>💡 Presenter Tips:</strong><br>
                                            - Review the speaker notes for each slide
                                            - Customize the content as needed
                                            - Practice the presentation flow
                                            - Consider your audience's background
                                        </div>
                                    """, unsafe_allow_html=True)
                                    
                                    with open(pres_path, "rb") as f:
                                        st.download_button(
                                            "📥 Download PowerPoint Presentation",
                                            f,
                                            file_name="research_presentation.pptx",
                                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                                            help="Download the complete presentation with speaker notes"
                                        )
                        
                        else:
                            st.error(f"Error: {response.text}")
                            st.info("Please check if the backend server is running.")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("""
                    Please ensure:
                    1. The backend server is running
                    2. Your PDF is not corrupted
                    3. The file size is under 10MB
                """)

    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #6b7280; font-size: 0.875rem;">
            🔬 Powered by GPT-4, Stable Diffusion XL, and ElevenLabs<br>
            Made for researchers, by researchers
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
