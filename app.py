import streamlit as st
from google import genai
from PIL import Image
import time
import pandas as pd
import io

st.set_page_config(page_title="AI Receipt Pro", layout="centered")
STORE_URL = "https://resumeweapon.lemonsqueezy.com/checkout/buy/bfb2b82e-22ed-4fe2-b2ba-998bafd9de65"

if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Missing API Key!")

def process_receipt(image_file):
    img = Image.open(image_file)
    model_id = "gemini-3-flash-preview" 
    prompt = "Extract Date, Item, Category, Amount. Use TAB between columns. No headers."
    try:
        response = client.models.generate_content(model=model_id, contents=[prompt, img])
        return response.text.strip()
    except:
        return "Error: System Busy"

st.sidebar.title("🔐 License")
key = st.sidebar.text_input("Enter Key", type="password")
is_pro = (key == "HUSTLE500" or len(str(key)) > 10)

if not is_pro:
    st.sidebar.markdown(f'[🔥 UNLOCK BULK MODE]({STORE_URL})')

st.title("📑 AI Receipt Pro")
files = st.file_uploader("Upload Receipts", type=['png', 'jpg', 'jpeg'], accept_multiple_files=is_pro)

if st.button("Generate Data", type="primary") and files:
    file_list = files if isinstance(files, list) else [files]
    all_rows = []
    bar = st.progress(0)
    
    for i, f in enumerate(file_list):
        with st.spinner(f"Reading {f.name}..."):
            data = process_receipt(f)
            if "Busy" in data:
                time.sleep(2)
                data = process_receipt(f)
            all_rows.append(data.replace("```", "").strip())
            time.sleep(1) # Faster 1-second delay
        bar.progress((i + 1) / len(file_list))

    final_text = "\n".join(all_rows)
    st.success("✅ Processing Complete!")
    st.code(final_text, language="text")
    
    try:
        df = pd.read_csv(io.StringIO(final_text), sep='\t', names=["Date", "Item", "Category", "Amount"])
        st.download_button("Download CSV", df.to_csv(index=False), "receipts.csv", "text/csv")
    except:
        st.warning("Download unavailable. Use 'Copy' above.")
        
