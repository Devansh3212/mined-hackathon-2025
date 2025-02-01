import streamlit as st
import requests
import time

# Streamlit Workbench UI
def main():
    st.set_page_config(page_title="AI Research Paper Workbench", layout="wide")
    st.title("🚀 AI-Powered Research Paper Workbench 📄")
    st.markdown("""
    **Upload a research paper (PDF), and this AI will generate:**
    - 📝 **Summarized content**
    - 🎨 **Graphical Abstracts**
    - 🎙 **AI-generated Podcast**
    - 📽 **AI-generated Explainer Video**
    - 📊 **Presentation Slides**
    """)

    uploaded_file = st.file_uploader("📂 Upload Research Paper (PDF)", type=["pdf"], help="Drop your research paper here.")
    
    if uploaded_file is not None:
        with st.spinner("🔄 Processing Paper..."):
            # Save the uploaded file
            with open("temp_paper.pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Send the file to the FastAPI backend
            files = {"file": open("temp_paper.pdf", "rb")}
            response = requests.post("http://127.0.0.1:8080/process-paper/", files=files)
            
            if response.status_code == 200:
                outputs = response.json()
                summary = outputs["summary"]
                st.success("✅ Processing Complete!")
            else:
                st.error(f"❌ Error processing paper: {response.text}")
                return

        st.subheader("📌 Generated Summary")
        st.info(summary)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🎨 Generate Graphical Abstract"):
                st.image("graphical_abstract.png", caption="Graphical Abstract", use_column_width=True)
                st.success("✅ Graphical Abstract Generated!")

        with col2:
            if st.button("🎙 Generate AI Podcast"):
                st.audio("voiceover.mp3", format="audio/mp3")
                st.success("✅ Podcast Ready!")

        if st.button("📽 Generate AI Video"):
            st.video(outputs["video"])
            st.success("✅ Video Generation Complete!")

        if st.button("📊 Generate Presentation"):
            with open("presentation.pptx", "rb") as f:
                st.download_button("📥 Download Presentation", f, file_name="presentation.pptx")
            st.success("✅ Presentation Generated!")

    st.markdown("---")
    st.caption("🔗 Powered by GPT-4, Stable Diffusion, and Runway ML. 🚀")

if __name__ == "__main__":
    main()