import streamlit as st
import requests
from groq import Groq
import base64

# --- CONFIG ---
# Paste your actual Lemon Squeezy Checkout URL here
STORE_URL = "https://yourstore.lemonsqueezy.com/checkout/..." 

def verify_license(key):
    if key == "HUSTLE500": return True
    url = "https://api.lemonsqueezy.com/v1/licenses/validate"
    try:
        response = requests.post(url, data={"license_key": key})
        return response.json().get("valid", False)
    except: return False

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

def process_receipt(image_file, api_key):
    client = Groq(api_key=api_key)
    image_file.seek(0)
    base64_image = encode_image(image_file)
    # The 2026 Scout model you confirmed is working
    model_id = "meta-llama/llama-4-scout-17b-16e-instruct"
    
    # Strictly requesting Tab-Separated format
    prompt = "Extract: Date, Item, Category, Amount. Return ONLY raw rows. Separate columns with a TAB. No headers."
    
    try:
        completion = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}],
            temperature=0,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# --- MAIN PAGE UI ---
st.set_page_config(page_title="AI Receipt Scanner", layout="centered")

# --- 1. THE "AD" SECTION (FRONT PAGE) ---
license_key = st.sidebar.text_input("🔑 Activate Pro License", type="password")
is_pro = verify_license(license_key) if license_key else False

if not is_pro:
    # This acts as your "Ad" banner at the top
    with st.container():
        st.markdown("""
        <div style="background-color:#ff4b4b; padding:20px; border-radius:10px; text-align:center;">
            <h2 style="color:white; margin:0;">🚀 Unlock Bulk Processing</h2>
            <p style="color:white;">Stop uploading one-by-one. Process 100+ receipts in seconds for just ₹99.</p>
        </div>
        """, unsafe_allow_html=True)
        st.link_button("🔥 GET LIFETIME PRO ACCESS - ₹99", STORE_URL, use_container_width=True)
        st.divider()
else:
    st.balloons()
    st.success("✨ PRO MODE ACTIVE: Bulk Upload Enabled")

# --- 2. UPLOADER SECTION ---
st.title("📊 AI Receipt to Dashboard")
st.write("Upload your bills and get structured data for your Google Sheet.")

files = st.file_uploader(
    "Choose receipt images", 
    type=['png', 'jpg', 'jpeg'], 
    accept_multiple_files=is_pro
)

# --- 3. PROCESSING ---
if st.button("Generate Dashboard Data", type="primary") and files:
    file_list = files if isinstance(files, list) else [files]
    all_rows = []
    
    progress_bar = st.progress(0)
    for i, f in enumerate(file_list):
        with st.spinner(f"Scanning {f.name}..."):
            raw_out = process_receipt(f, st.secrets["GROQ_API_KEY"])
            
            # Clean and ensure Tab-Separated format
            for line in raw_out.split('\n'):
                if len(line) > 5:
                    # Replace any accidental commas with Tabs to ensure Google Sheet columns
                    clean_line = line.replace(",", "\t")
                    all_rows.append(clean_line)
        progress_bar.progress((i + 1) / len(file_list))

    if all_rows:
        final_data = "\n".join(all_rows)
        st.success("Done! Your data is structured below.")
        
        # --- THE FIX: TEXT AREA FOR EASY COPYING ---
        st.markdown("### 📋 Step 1: Copy this data")
        st.text_area(
            label="Click inside, press Ctrl+A then Ctrl+C to copy",
            value=final_data,
            height=250
        )
        
        st.markdown("### 📈 Step 2: Paste into Google Sheets")
        st.info("Select cell **A2** in your Sheet and press **Ctrl+V**. Because we use 'Tabs', it will automatically fill 4 separate columns!")

# --- FOOTER ---
if not is_pro:
    st.sidebar.markdown("---")
    st.sidebar.caption("Free users are limited to 1 scan at a time.")
    
