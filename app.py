import streamlit as st
import pandas as pd
from groq import Groq
import base64
import io

# --- 1. SETTINGS & STYLING ---
st.set_page_config(page_title="AI Receipt Scanner", layout="wide")

# REPLACE THIS with your actual Lemon Squeezy link
STORE_URL = "https://yourstore.lemonsqueezy.com/checkout/buy/pro" 

# --- 2. CORE ENGINE ---
def verify_license(key):
    """The key check. 'HUSTLE500' is your internal dev backdoor."""
    if key == "HUSTLE500": return True
    url = "https://api.lemonsqueezy.com/v1/licenses/validate"
    try:
        # Note: In production, you would use requests.post(url, data={"license_key": key})
        # For now, we return True for testing purposes if you have no API set up
        return False 
    except: return False

def process_receipt(image_file, api_key):
    client = Groq(api_key=api_key)
    image_file.seek(0)
    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    # THE 2026 PRODUCTION VISION ID
    # This model replaces the decommissioned llama-3.2 series
    model_id = "meta-llama/llama-4-scout-17b-16e-instruct"
    
    prompt = "Extract: Date, Item, Category, Amount. Format as CSV: Date,Item,Category,Amount. No headers. No talk."
    
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

# --- 3. SIDEBAR (KEY ENTRY) ---
st.sidebar.title("🔐 Account")
user_key = st.sidebar.text_input("License Key", type="password", help="Enter HUSTLE500 to test")
is_pro = verify_license(user_key)

# --- 4. MAIN FRONT PAGE AD ---
if not is_pro:
    st.markdown(f"""
    <div style="background-color:#0e1117; padding:30px; border: 2px solid #ff4b4b; border-radius:15px; text-align:center; margin-bottom:25px;">
        <h1 style="color:white; margin:0;">🚀 The 500 Machine: Bulk Receipt Power</h1>
        <p style="color:#fafafa; font-size:18px;">Tired of scanning one by one? Unlock <b>Bulk Mode</b> and scan 50+ bills at once.</p>
        <a href="{STORE_URL}" target="_blank">
            <button style="background-color:#ff4b4b; color:white; border:none; padding:15px 30px; border-radius:8px; font-weight:bold; cursor:pointer; width:100%;">
                GET LIFETIME BULK ACCESS - ₹99
            </button>
        </a>
    </div>
    """, unsafe_allow_html=True)
else:
    st.success("✅ PRO ACTIVE: Bulk Mode Enabled")

# --- 5. UPLOADER ---
st.title("📊 AI Receipt to Spreadsheet")
files = st.file_uploader("Drop receipts here", type=['jpg', 'jpeg', 'png'], accept_multiple_files=is_pro)

# --- 6. PROCESSING LOGIC ---
if st.button("🔥 Generate My Data", type="primary") and files:
    if "GROQ_API_KEY" not in st.secrets:
        st.error("Missing API Key! Add it to .streamlit/secrets.toml")
    else:
        file_list = files if isinstance(files, list) else [files]
        all_data = []
        progress = st.progress(0)
        
        for i, f in enumerate(file_list):
            with st.spinner(f"Scanning {f.name}..."):
                res = process_receipt(f, st.secrets["GROQ_API_KEY"])
                if "Error" not in res:
                    for line in res.split('\n'):
                        parts = line.split(',')
                        if len(parts) >= 4:
                            all_data.append(parts[:4])
            progress.progress((i + 1) / len(file_list))
        
        if all_data:
            df = pd.DataFrame(all_data, columns=["Date", "Item", "Category", "Amount"])
            
            st.divider()
            st.subheader("✅ Extraction Complete")
            
            # THE FIX: Display as a proper interactive table
            # Users can select all cells and copy-paste directly to Sheets!
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.info("💡 **Pro Tip:** Click one cell, press **Ctrl+A** then **Ctrl+C**. Paste into Google Sheets cell **A2**.")
            
            # Fallback text area with TABS (the secret for perfect pasting)
            tsv_data = df.to_csv(index=False, sep='\t', header=False)
            st.text_area("Alternative Copy (Raw Tabs):", value=tsv_data, height=150)
    
