import streamlit as st
import pandas as pd
from groq import Groq
from PIL import Image
import io
import base64

# 1. Page Configuration
st.set_page_config(page_title="The 500 Machine", page_icon="💰")

# 2. Sidebar - The Gatekeeper
st.sidebar.title("🔐 Pro Access")
license_key = st.sidebar.text_input("Enter License Key", type="password")
is_pro = (license_key == "HUSTLE500") # This is your secret "Key" for now

if is_pro:
    st.sidebar.success("✅ PRO UNLOCKED")
    st.sidebar.markdown("- Bulk Upload (100+ files) active.")
    st.sidebar.markdown("- [**Download Pro Dashboard**](YOUR_GOOGLE_SHEET_COPY_LINK)")
else:
    st.sidebar.warning("Free Version (1 File Limit)")
    st.sidebar.markdown("### 🚀 Unlock Pro for ₹99")
    st.sidebar.markdown("- Bulk extract images to one CSV")
    st.sidebar.markdown("- Pro Google Sheets Dashboard")
    st.sidebar.markdown("[**Get Lifetime Access Now**](YOUR_LEMON_SQUEEZY_LINK)")

st.title("⚡ Data Bridge: Image to CSV")

# 3. Connection to the Brain
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 4. User Input (Bulk is enabled ONLY if is_pro is True)
uploaded_files = st.file_uploader(
    "Upload data images", 
    type=["jpg", "png", "jpeg"], 
    accept_multiple_files=is_pro # This is the "Magic" switch
)

# Handle single vs multiple files
files_to_process = uploaded_files if isinstance(uploaded_files, list) else ([uploaded_files] if uploaded_files else [])

if files_to_process:
    if st.button("🚀 EXECUTE EXTRACTION"):
        all_results = []
        with st.spinner(f"Processing {len(files_to_process)} file(s)..."):
            for uploaded_file in files_to_process:
                try:
                    base64_image = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                    completion = client.chat.completions.create(
                        model="meta-llama/llama-4-scout-17b-16e-instruct",
                        messages=[{"role": "user", "content": [
                            {"type": "text", "text": "Extract all tabular data from this image. CSV only."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]}]
                    )
                    all_results.append(completion.choices[0].message.content)
                except Exception as e:
                    st.error(f"Error: {e}")
            
            if all_results:
                final_csv = "\n".join(all_results)
                st.success("✅ Complete!")
                st.code(final_csv, language="csv")
                st.download_button("📥 Download Final CSV", final_csv, file_name="output.csv")
                
