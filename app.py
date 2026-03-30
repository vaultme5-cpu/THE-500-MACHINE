import streamlit as st
from google import genai
from PIL import Image
import time
import pandas as pd
import io

# 1. License Check First
st.sidebar.title("🔐 License")
key = st.sidebar.text_input("Enter Key", type="password")
is_pro = (key == "HUSTLE500" or len(str(key)) > 10)

# 2. Dynamic Names
APP_NAME = "Bulk Data Pro" if is_pro else "Solo Receipt Scanner"
st.set_page_config(page_title=APP_NAME, layout="centered")
st.title(f"🚀 {APP_NAME}")

STORE_URL = "https://resumeweapon.lemonsqueezy.com/checkout/buy/bfb2b82e-22ed-4fe2-b2ba-998bafd9de65"

# 3. API Client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

def process_receipt(image_file):
    img = Image.open(image_file)
    prompt = "Extract Date, Item, Category, Amount. Tab-separated. No headers."
    try:
        response = client.models.generate_content(model="gemini-3-flash-preview", contents=[prompt, img])
        return response.text.strip()
    except:
        return "Error: Busy"

# 4. Logic
if not is_pro:
    st.sidebar.markdown(f'[🔥 Upgrade to Bulk Pro]({STORE_URL})')

files = st.file_uploader("Upload", type=['png', 'jpg'], accept_multiple_files=is_pro)

if st.button("Extract Data") and files:
    file_list = files if isinstance(files, list) else [files]
    results = []
    
    for f in file_list:
        with st.spinner(f"Scanning {f.name}..."):
            data = process_receipt(f)
            results.append(data.replace("```", "").strip())
            time.sleep(1) # Speed boost: 1s instead of 2s

    final = "\n".join(results)
    st.code(final, language="text")
    
    df = pd.read_csv(io.StringIO(final), sep='\t', names=["Date", "Item", "Category", "Amount"])
    st.download_button("Download CSV", df.to_csv(index=False).encode('utf-8'), "data.csv")
    
