import streamlit as st
from google import genai
from PIL import Image
import time
import pandas as pd
import io
import requests

# 1. Setup
STORE_URL = "https://resumeweapon.lemonsqueezy.com/checkout/buy/513ad46a-ccf3-4ad7-987c-52759a0a6890"
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

def verify_key(key):
    if key == "HUSTLE500": return True
    try:
        r = requests.post("https://api.lemonsqueezy.com/v1/licenses/activate", data={'license_key': key})
        return r.json().get('activated', False)
    except: return False

# 2. Sidebar (Key Only)
st.sidebar.title("🔐 License")
user_key = st.sidebar.text_input("Enter Key", type="password")
is_pro = verify_key(user_key)
if is_pro: st.sidebar.success("Pro Active")

# 3. Main UI
APP_NAME = "Bulk Data Pro" if is_pro else "Solo Receipt Scanner"
st.set_page_config(page_title=APP_NAME, layout="centered")
st.title(f"🚀 {APP_NAME}")

files = st.file_uploader("Upload", type=['png', 'jpg'], accept_multiple_files=is_pro)

    for f in file_list:
        with st.spinner(f"Scanning {f.name}..."):
            # TRY 3 TIMES BEFORE GIVING UP (Fixes "Server Busy" Error)
            success = False
            for attempt in range(3):
                data = process_receipt(f)
                if "Error: Server busy" not in data:
                    results.append(data)
                    success = True
                    break 
                else:
                    # Wait longer each time it fails
                    time.sleep(4) 
            
            if not success:
                results.append(f"Failed after 3 retries: {f.name}")
            
            # 3 second gap between different images to stay under limits
            time.sleep(3) 
            
                            
    
    final = "\n".join(results)
    st.code(final, language="text")
    df = pd.read_csv(io.StringIO(final), sep='\t', names=["Date", "Item", "Category", "Amount"])
    st.download_button("Download CSV", df.to_csv(index=False).encode('utf-8'), "data.csv")

# 4. Bottom Ad (UI Fix)
if not is_pro:
    st.divider()
    st.markdown(f'''<a href="{STORE_URL}" target="_blank">
        <button style="width:100%;background:#ff4b4b;color:white;padding:15px;border:none;border-radius:10px;font-weight:bold;cursor:pointer;">
            🔥 UNLOCK BULK MODE - PRO ACCESS
        </button></a>''', unsafe_allow_html=True)
    
