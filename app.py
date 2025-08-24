import os
import streamlit as st
import pdfplumber
import cohere
from dotenv import load_dotenv

# Load API key
load_dotenv()
cohere_api_key = os.getenv("COHERE_API_KEY")

co = cohere.Client(cohere_api_key)

def enhance_bullet_point(bullet_point, max_input_length=200):
    try:
        truncated_input = bullet_point[:max_input_length].rstrip()
        prompt = f"Rewrite this resume bullet point to sound more professional and concise:\n{truncated_input}"

        response = co.generate(
            model='command',
            prompt=prompt,
            max_tokens=80,
            temperature=0.6,
        )
        return response.generations[0].text.strip()
    except Exception as e:
        st.error(f"Cohere API error: {e}")
        return bullet_point

# ... keep the rest of your Streamlit code unchanged ...


def extract_bullet_points(text):
    lines = text.splitlines()
    bullet_points = []
    
    for line in lines:
        stripped_line = line.strip()
        # Debugging output to see each line processed
        st.write(f"Processing line: {stripped_line}")
        # Check if the line is likely a bullet point
        if (stripped_line.startswith('- ') or
            stripped_line.startswith('* ') or
            stripped_line.startswith('• ') or
            (len(stripped_line) > 2 and stripped_line[:2].isdigit() and
             (stripped_line[2] == '.' or stripped_line[2] == ')'))):
            bullet_points.append(stripped_line)
    return bullet_points

def main():
    st.set_page_config(page_title="Gen-AI-Powered Resume Enhancer", layout="wide")
    
    # Inject custom CSS for clean styling
    st.markdown(
    """
    <style>
    body {
        background-color: #e6f2ff;  /* Light blue background */
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #0b3d91;
        margin-bottom: 0.3rem;
    }
    .subtitle {
        font-size: 1.2rem;
        margin-bottom: 2rem;
        color: #333;
        font-weight: 500;
    }
    .bullet-point-col {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        min-height: 100px;
        word-wrap: break-word;
        overflow-wrap: break-word;
        color: black;  /* Ensure text is black */
    }
    .stButton button {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.6em 1.6em;
        border: none;
        transition: background 0.3s ease;
    }
    .stButton button:hover {
        background: linear-gradient(90deg, #182848 0%, #4b6cb7 100%);
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

    
    st.markdown('<h1 class="title">Gen-AI-Powered Resume Enhancer</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">Upload your resume as a text or PDF file and see bullet points enhanced professionally!</p>',
        unsafe_allow_html=True,
    )
    
    uploaded_file = st.file_uploader("Upload your resume (text or PDF)", type=["txt", "pdf"])
    
    if uploaded_file:
        # Extract text from PDF or TXT
        if uploaded_file.type == "application/pdf":
            try:
                with pdfplumber.open(uploaded_file) as pdf:
                    text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except Exception as e:
                st.error(f"Failed to process PDF: {e}")
                return
        else:
            text = uploaded_file.read().decode("utf-8")
        
        # Extract bullet points with improved logic
        bullet_points = extract_bullet_points(text)
        
        # Limit number of bullet points processed to 10 to reduce usage
        bullet_points = bullet_points[:10]  
        
        if bullet_points:
            st.subheader("Original vs Enhanced Bullet Points")
            enhanced_points = []
            
            for bullet in bullet_points:
                enhanced = enhance_bullet_point(bullet)
                enhanced_points.append(enhanced)
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f'<div class="bullet-point-col"><strong>Original:</strong><br>{bullet}</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<div class="bullet-point-col"><strong>Enhanced:</strong><br>{enhanced}</div>', unsafe_allow_html=True)
            
            # Download button for enhanced bullet points text file
            enhanced_text = "\n".join(enhanced_points)
            st.download_button(
                label="Download Enhanced Bullet Points",
                data=enhanced_text,
                file_name="enhanced_bullet_points.txt",
                mime="text/plain"
            )
        else:
            st.warning("No bullet points found in the resume. Please check the formatting of bullet points.")
    
if __name__ == "__main__":
    main()
