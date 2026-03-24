import streamlit as st
import requests
import pandas as pd
from groq import Groq
import base64

# --- 1. CORE FUNCTIONS ---
def verify_license(key):
    """Checks the key with Lemon Squeezy API"""
    # For testing purposes, you can uncomment the line below:
    # if key == "TEST123": return True
    
    url = "https://api.lemonsqueezy.com/v1/licenses/validate"
    try:
        response = requests.post(url, data={"license_key": key})
        if response.status_code == 200:
            return response.json().get("valid", False)
    except:
        return False
    return False

def encode_image(image_file):
    """Encodes image to base64 for AI processing"""
    return base64.b64encode(image_file.read()).decode('utf-8')

def process_receipt(image_file, api_key):
    """The AI Vision Engine - Fixed for Pixtral Vision Model"""
    client = Groq(api_key=api_key)
    
    # Reset file pointer to start
    image_file.seek(0)
    base64_image = encode_image(image_file)
    
    # Using the stable Pixtral Vision model
    model_id = "llama-3.2-11b-vision-pixtral"
    
    prompt = "Extract Date, Item, Category, and Amount from this receipt. Return ONLY raw CSV rows. No intro or markdown."
    
    try:
        completion = client.chat.completions.create(
            model=model_id,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url", 
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            temperature=0,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error processing {image_file.name}: {str(e)}"

# --- 2. SIDEBAR (LICENSING) ---
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
    uploaded_files = st.file_uploader("Upload Receipts (Bulk Mode)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
else:
    st.info("💡 Free Version: 1 image limit. Enter license key for Bulk Mode.")
    uploaded_file = st.file_uploader("Upload Receipt", type=['png', 'jpg', 'jpeg'], accept_multiple_files=False)
    uploaded_files = [uploaded_file] if uploaded_file else []

# --- 4. PROCESSING ---
if st.button("Start Processing") and uploaded_files:
    if "GROQ_API_KEY" not in st.secrets:
        st.error("Please add GROQ_API_KEY to Streamlit Secrets.")
    else:
        all_data = []
        progress_bar = st.progress(0)
        
        for i, file in enumerate(uploaded_files):
            with st.spinner(f"Reading {file.name}..."):
                result = process_receipt(file, st.secrets["GROQ_API_KEY"])
                # Clean out any repeated headers the AI might generate
                lines = result.split('\n')
                for line in lines:
                    if "Date" not in line and len(line) > 5:
                        all_data.append(line)
            
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        if all_data:
            final_csv = "Date, Item, Category, Amount\n" + "\n".join(all_data)
            st.success("Processing Complete!")
            st.text_area("Copy and paste this into your Dashboard:", value=final_csv, height=300)
            st.download_button("Download CSV", data=final_csv, file_name="data.csv", mime="text/csv")
            
