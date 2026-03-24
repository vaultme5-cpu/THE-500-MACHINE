import streamlit as st
import requests
import pandas as pd
from groq import Groq
import base64

# --- 1. CORE FUNCTIONS ---
def verify_license(key):
    """Checks the key with Lemon Squeezy. Includes a secret TEST bypass."""
    if key == "HUSTLE500":  
        return True
    
    url = "https://api.lemonsqueezy.com/v1/licenses/validate"
    try:
        response = requests.post(url, data={"license_key": key})
        return response.json().get("valid", False)
    except:
        return False

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

def process_receipt(image_file, api_key):
    client = Groq(api_key=api_key)
    image_file.seek(0)
    base64_image = encode_image(image_file)
    
    # THE VERIFIED, ACTIVE 2026 MODEL ID
    model_id = "meta-llama/llama-4-scout-17b-16e-instruct"
    
    prompt = "Extract: Date, Item, Category, Amount. Return ONLY raw CSV rows. No intro text."
    
    try:
        completion = client.chat.completions.create(
            model=model_id,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }],
            temperature=0,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# --- 2. SIDEBAR ---
st.sidebar.title("🚀 The 500 Machine")
st.sidebar.info("Goal: 500 Sales 🔥")
user_key = st.sidebar.text_input("License Key", type="password")

is_pro = False
if user_key:
    if verify_license(user_key):
        st.sidebar.success("✅ PRO ACTIVE")
        is_pro = True
    else:
        st.sidebar.error("❌ Invalid Key")

# --- 3. MAIN UI ---
st.title("📊 AI Bulk Receipt Scanner")

if is_pro:
    files = st.file_uploader("Upload Bulk Receipts", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
else:
    st.warning("🔒 Free Mode: 1 file limit.")
    files = st.file_uploader("Upload 1 Receipt", type=['png', 'jpg', 'jpeg'], accept_multiple_files=False)
    if files: files = [files] 

# --- 4. THE ACTION ---
if st.button("Generate Dashboard Data") and files:
    if "GROQ_API_KEY" not in st.secrets:
        st.error("Missing API Key in Streamlit Secrets!")
    else:
        all_rows = []
        bar = st.progress(0)
        
        for i, f in enumerate(files):
            with st.spinner(f"Reading {f.name}..."):
                raw_out = process_receipt(f, st.secrets["GROQ_API_KEY"])
                
                # Show exact error on screen if the API fails
                if "Error:" in raw_out:
                    st.error(f"Failed on {f.name}: {raw_out}")
                else:
                    for line in raw_out.split('\n'):
                        if "," in line and "Date" not in line:
                            all_rows.append(line)
            bar.progress((i + 1) / len(files))
        
        if all_rows:
            final_csv = "Date, Item, Category, Amount\n" + "\n".join(all_rows)
            st.success("Extraction Complete!")
            st.text_area("Copy this to your Google Sheet:", value=final_csv, height=300)
            st.download_button("Download CSV", data=final_csv, file_name="receipt_data.csv")
                
