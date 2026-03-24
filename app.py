import streamlit as st
import requests
import pandas as pd
from groq import Groq
import base64
import io

# --- 1. CORE FUNCTIONS ---
def verify_license(key):
    """
    Checks the key with Lemon Squeezy API.
    For local testing, you can change this to:
    if key == "TEST123": return True
    """
    url = "https://api.lemonsqueezy.com/v1/licenses/validate"
    try:
        # Lemon Squeezy requires the license_key in the POST body
        response = requests.post(url, data={"license_key": key})
        if response.status_code == 200:
            return response.json().get("valid", False)
    except Exception as e:
        st.sidebar.error(f"Connection Error: {e}")
        return False
    return False

def encode_image(image_file):
    """Encodes the uploaded image to base64 for the AI"""
    return base64.b64encode(image_file.read()).decode('utf-8')

def process_receipt(image_file, api_key):
    """The AI Vision Engine using Llama 3.2 Vision via Groq"""
    client = Groq(api_key=api_key)
    
    # Reset file pointer to start before reading
    image_file.seek(0)
    base64_image = encode_image(image_file)
    
    prompt = (
        "Analyze this receipt image. "
        "Return ONLY the data in CSV format with these headers: Date, Item, Category, Amount. "
        "Do not include any introductory text, markdown code blocks, or explanations. "
        "Just the raw CSV rows."
    )
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.2-11b-vision-pixtral",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            temperature=0,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error processing {image_file.name}: {str(e)}"

# --- 2. SIDEBAR (THE LICENSE GATE) ---
st.sidebar.title("🚀 The 500 Machine")
st.sidebar.markdown("---")
user_key = st.sidebar.text_input("Enter Pro License Key", type="password", help="Get your key from your Lemon Squeezy email.")

is_pro = False
if user_key:
    # Check if the key is valid
    if verify_license(user_key):
        st.sidebar.success("✅ PRO ACCESS ACTIVE")
        is_pro = True
    else:
        st.sidebar.error("❌ Invalid License Key")

# --- 3. MAIN APP INTERFACE ---
st.title("📊 AI Data Pro: Bulk Receipt Scanner")
st.markdown("Convert your paper receipts into a professional dashboard in seconds.")

if is_pro:
    st.write("### 🔓 Pro Mode: Bulk Upload")
    uploaded_files = st.file_uploader(
        "Upload multiple receipts at once", 
        type=['png', 'jpg', 'jpeg'], 
        accept_multiple_files=True
    )
else:
    st.warning("🔒 **Free Mode:** 1 Image Limit. Enter a License Key to unlock Bulk Mode.")
    uploaded_file = st.file_uploader(
        "Upload a single receipt", 
        type=['png', 'jpg', 'jpeg'], 
        accept_multiple_files=False
    )
    uploaded_files = [uploaded_file] if uploaded_file else []

# --- 4. PROCESSING LOGIC ---
if st.button("Generate CSV Data") and uploaded_files:
    if "GROQ_API_KEY" not in st.secrets:
        st.error("Missing API Key! Please add 'GROQ_API_KEY' to your Streamlit Secrets.")
    else:
        all_results = []
        progress_text = "Operation in progress. Please wait."
        my_bar = st.progress(0, text=progress_text)
        
        # We use a set to keep headers unique or just clean them later
        for i, file in enumerate(uploaded_files):
            with st.spinner(f"AI is reading: {file.name}..."):
                raw_output = process_receipt(file, st.secrets["GROQ_API_KEY"])
                
                # Basic cleaning to remove AI headers if they repeat
                lines = raw_output.split('\n')
                for line in lines:
                    if "Date, Item, Category, Amount" not in line and len(line) > 5:
                        all_results.append(line)
            
            # Update progress
            progress = (i + 1) / len(uploaded_files)
            my_bar.progress(progress, text=f"Processed {i+1} of {len(uploaded_files)} files")

        if all_results:
            # Combine everything into one clean block
            final_csv_body = "\n".join(all_results)
            header = "Date, Item, Category, Amount\n"
            full_csv = header + final_csv_body
            
            st.success("✨ Processing Complete!")
            
            # Show the data to the user
            st.markdown("### 📋 Your Data")
            st.text_area("Copy and paste this into your Google Sheet 'RAW INPUT' tab:", value=full_csv, height=300)
            
            # Create a download button
            st.download_button(
                label="📥 Download CSV File",
                data=full_csv,
                file_name="receipt_data.csv",
                mime="text/csv",
            )
else:
    if not uploaded_files:
        st.info("Please upload your receipt images to begin.")

# --- 5. FOOTER ---
st.markdown("---")
st.caption("Built for the 500 Machine Project. Secure, Fast, and AI-Powered.")
            
