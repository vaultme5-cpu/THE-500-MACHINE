import streamlit as st
import requests
import pandas as pd
from groq import Groq
import base64

# --- 1. CORE FUNCTIONS ---
def verify_license(key):
    """Checks the key with Lemon Squeezy API"""
    # For testing, you can uncomment the next line:
    # if key == "HUSTLE": return True
    url = "https://api.lemonsqueezy.com/v1/licenses/validate"
    try:
        response = requests.post(url, data={"license_key": key})
        return response.json().get("valid", False)
    except:
        return False

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

def process_receipt(image_file, api_key):
    """The AI Vision Engine - Updated for 2026 Stability"""
    client = Groq(api_key=api_key)
    image_file.seek(0)
    base64_image = encode_image(image_file)
    
    # USING THE MOST STABLE VISION MODEL AVAILABLE ON GROQ
    model_id = "llama-3.2-90b-vision-preview"
    
    prompt = "Extract Date, Item, Category, and Amount from this receipt. Return ONLY raw CSV rows."
    
    try:
        completion = client.chat.completions.create(
            model=model_id,
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
        return f"Error: {str(e)}"

# --- 2. SIDEBAR ---
st.sidebar.title("🚀 The 500 Machine")
user_key = st.sidebar.text_input("Enter Pro License Key", type="password")
is_pro = False

if user_key:
    if verify_license(user_key):
        st.sidebar.success("✅ PRO ACTIVE")
        is_pro = True
    else:
        st.sidebar.error("❌ Invalid Key")

# --- 3. MAIN INTERFACE ---
st.title("📊 AI Bulk Receipt Scanner")

if is_pro:
    uploaded_files = st.file_uploader("Upload Receipts (Bulk)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
else:
    st.info("💡 Free Mode: 1 image limit. Upgrade for Bulk.")
    uploaded_file = st.file_uploader("Upload Receipt", type=['png', 'jpg', 'jpeg'], accept_multiple_files=False)
    uploaded_files = [uploaded_file] if uploaded_file else []

# --- 4. PROCESSING ---
if st.button("Start Processing") and uploaded_files:
    if "GROQ_API_KEY" not in st.secrets:
        st.error("Add GROQ_API_KEY to Secrets!")
    else:
        all_data = []
        progress_bar = st.progress(0)
        
        for i, file in enumerate(uploaded_files):
            with st.spinner(f"Reading {file.name}..."):
                result = process_receipt(file, st.secrets["GROQ_API_KEY"])
                # Only keep lines that look like data
                lines = result.split('\n')
                for line in lines:
                    if "," in line and "Date" not in line:
                        all_data.append(line)
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        if all_data:
            final_csv = "Date, Item, Category, Amount\n" + "\n".join(all_data)
            st.success("✨ Done!")
            st.text_area("Copy this to your Dashboard:", value=final_csv, height=300)
            st.download_button("Download CSV", data=final_csv, file_name="data.csv")
            
