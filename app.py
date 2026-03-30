import streamlit as st
from google import genai
from PIL import Image
import time
import pandas as pd
import io
import requests

# --- 1. SETUP & CONFIG ---
STORE_URL = "https://resumeweapon.lemonsqueezy.com/checkout/buy/513ad46a-ccf3-4ad7-987c-52759a0a6890"

if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing API Key in Secrets!")
    st.stop()

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

def verify_key(key):
    if key == "HUSTLE500": return True
    try:
        r = requests.post("https://api.lemonsqueezy.com/v1/licenses/activate", data={'license_key': key}, timeout=10)
        return r.json().get('activated', False)
    except:
        return False

# --- 2. SIDEBAR ---
st.sidebar.title("🔐 License")
user_key = st.sidebar.text_input("Enter Key", type="password")
is_pro = verify_key(user_key)
if is_pro:
    st.sidebar.success("Pro Active")

# --- 3. MAIN UI ---
APP_NAME = "Bulk Data Pro" if is_pro else "Solo Receipt Scanner"
st.set_page_config(page_title=APP_NAME, layout="centered")
st.title(f"🚀 {APP_NAME}")

files = st.file_uploader("Upload Receipts", type=['png', 'jpg', 'jpeg'], accept_multiple_files=is_pro)

if st.button("Extract Data") and files:
    file_list = files if isinstance(files, list) else [files]
    results = []
    status = st.empty()
    
    for i, f in enumerate(file_list):
        status.text(f"Scanning {i+1}/{len(file_list)}: {f.name}...")
        success = False
        wait = 5 # Initial retry delay
        
        for attempt in range(4):
            try:
                img = Image.open(f)
                res = client.models.generate_content(
                    model="gemini-3-flash-preview", 
                    contents=["Extract Date, Item, Category, Amount. Tab-separated.", img]
                )
                if res and res.text:
                    results.append(res.text.strip())
                    success = True
                    break
            except Exception:
                time.sleep(wait)
                wait *= 2 # Wait longer each time
        
        if not success:
            results.append(f"N/A\t{f.name} (Scan Failed)\tError\t0.00")
        
        time.sleep(4) # Stability gap

    status.success("✅ Done!")
    
    if results:
        final_text = "\n".join(results)
        st.code(final_text, language="text")
        try:
            df = pd.read_csv(io.StringIO(final_text), sep='\t', names=["Date", "Item", "Category", "Amount"])
            st.download_button("Download CSV", df.to_csv(index=False).encode('utf-8'), "data.csv")
        except:
            st.warning("Could not format CSV, please copy text above.")

# --- 4. FOOTER AD ---
if not is_pro:
    st.divider()
    st.markdown(f'<a href="{STORE_URL}" target="_blank"><button style="width:100%;background:#ff4b4b;color:white;padding:15px;border:none;border-radius:10px;font-weight:bold;cursor:pointer;">🔥 UNLOCK BULK MODE - PRO ACCESS</button></a>', unsafe_allow_html=True)
            
