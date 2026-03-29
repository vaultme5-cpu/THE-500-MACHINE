import streamlit as st
import requests
from groq import Groq
import base64

# --- 1. PAGE SETUP (Must be the first Streamlit command) ---
st.set_page_config(page_title="The 500 Machine", layout="centered", page_icon="🚀")

# --- 2. CONFIGURATION ---
# Your official Lemon Squeezy link
STORE_URL = "https://resumeweapon.lemonsqueezy.com/checkout/buy/bfb2b82e-22ed-4fe2-b2ba-998bafd9de65" 

def verify_license(key):
    """
    Checks the license. Use 'HUSTLE500' for your own testing.
    """
    if key == "HUSTLE500":
        return True
    # Basic check for real keys (can be expanded with Lemon Squeezy API)
    return len(key) > 10 

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

def process_receipt(image_file, api_key):
    client = Groq(api_key=api_key)
    image_file.seek(0)
    base64_image = encode_image(image_file)
    
    # 2026 Stable Scout Model
    model_id = "meta-llama/llama-4-scout-17b-16e-instruct"
    
    # Prompt optimized for TAB separation (Google Sheets friendly)
    prompt = """Extract: Date, Item, Category, Amount. 
    Return ONLY raw rows. 
    Use a TAB character to separate columns. 
    No headers, no markdown, no conversational text."""
    
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

# --- 3. SIDEBAR ---
st.sidebar.title("🔐 License")
license_key = st.sidebar.text_input("Enter License Key", type="password", help="Get your key by clicking the Red button on the main page.")
is_pro = verify_license(license_key) if license_key else False

if is_pro:
    st.sidebar.success("Pro Mode Active")
else:
    st.sidebar.warning("Free Mode: 1 scan at a time")

# --- 4. MAIN INTERFACE ---
st.title("🚀 The 500 Machine")
st.write("Convert your physical receipts into clean Google Sheets data in seconds.")

# Bulk Ad for Free Users
if not is_pro:
    st.markdown(f"""
    <div style="background-color:#1e1e1e; padding:20px; border-radius:10px; border: 2px solid #ff4b4b; text-align:center;">
        <h3 style="color:white; margin-top:0;">Tired of scanning one-by-one?</h3>
        <p style="color:#cccccc;">Unlock <b>Bulk Mode</b> to process 50+ bills at once.</p>
        <a href="{STORE_URL}" target="_blank" style="text-decoration:none;">
            <button style="background-color:#ff4b4b; color:white; border:none; padding:10px 20px; border-radius:5px; font-weight:bold; cursor:pointer; width:100%;">
                GET LIFETIME BULK ACCESS - ₹99
            </button>
        </a>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
else:
    st.balloons()
    st.info("✨ Bulk Scanning Enabled. Upload as many receipts as you want!")

# File Uploader
files = st.file_uploader(
    "Drop your receipts here", 
    type=['png', 'jpg', 'jpeg'], 
    accept_multiple_files=is_pro
)

# --- 5. PROCESSING LOGIC ---
if st.button("Generate Dashboard Data", type="primary") and files:
    if "GROQ_API_KEY" not in st.secrets:
        st.error("API Key missing! Add 'GROQ_API_KEY' to your Streamlit Secrets.")
    else:
        # Normalize files into a list
        file_list = files if isinstance(files, list) else [files]
        all_rows = []
        
        progress_bar = st.progress(0)
        for i, f in enumerate(file_list):
            with st.spinner(f"Analyzing {f.name}..."):
                raw_out = process_receipt(f, st.secrets["GROQ_API_KEY"])
                
                # Double-check for Tab separation
                for line in raw_out.split('\n'):
                    if len(line) > 5:
                        clean_line = line.replace(",", "\t") # Safety fix for commas
                        all_rows.append(clean_line)
            progress_bar.progress((i + 1) / len(file_list))

        if all_rows:
            final_output = "\n".join(all_rows)
            st.success("✅ Done!")
            
            st.subheader("📋 Your Data (Ready to Paste)")
            st.text_area(
                label="Copy this and paste into Cell A2 of your Google Sheet", 
                value=final_output, 
                height=250
            )
            st.caption("Pro Tip: Data is separated by Tabs for perfect column alignment.")
            
