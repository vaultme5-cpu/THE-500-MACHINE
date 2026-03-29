import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. SETUP
st.set_page_config(page_title="The 500 Machine", layout="centered")
STORE_URL = "https://resumeweapon.lemonsqueezy.com/checkout/buy/bfb2b82e-22ed-4fe2-b2ba-998bafd9de65"

# 2. API KEY
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Missing GEMINI_API_KEY in Streamlit Secrets!")

def process_bill(image_file):
    model = genai.GenerativeModel('gemini-1.5-flash')
    img = Image.open(image_file)
    # The Prompt for perfect Google Sheets pasting
    prompt = "Extract: Date, Item, Category, Amount. Return ONLY raw rows. Separate columns with a TAB. No headers."
    response = model.generate_content([prompt, img])
    return response.text.strip()

# 3. UI & LICENSE
st.sidebar.title("🔐 License")
key = st.sidebar.text_input("Enter Key", type="password")
is_pro = (key == "HUSTLE500" or len(str(key)) > 10)

if not is_pro:
    st.markdown(f'''<a href="{STORE_URL}" target="_blank"><button style="width:100%;background:#ff4b4b;color:white;padding:12px;border:none;border-radius:8px;cursor:pointer;font-weight:bold;">🔥 UNLOCK BULK MODE - ₹99</button></a>''', unsafe_allow_html=True)
    st.divider()

st.title("🚀 The 500 Machine")
files = st.file_uploader("Upload Receipts", type=['png', 'jpg', 'jpeg'], accept_multiple_files=is_pro)

# 4. RUN
if st.button("Generate Data", type="primary") and files:
    file_list = files if isinstance(files, list) else [files]
    all_data = []
    
    for f in file_list:
        with st.spinner(f"Reading {f.name}..."):
            text = process_bill(f)
            # Force Tab separation fix
            clean_text = text.replace(",", "\t")
            all_data.append(clean_text)
    
    st.success("✅ Extraction Complete!")
    st.text_area("Copy (Ctrl+C) and Paste into Google Sheets (Cell A2)", value="\n".join(all_data), height=300)
    
