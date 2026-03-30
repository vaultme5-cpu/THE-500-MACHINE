import streamlit as st
from google import genai
from PIL import Image
import time
import pandas as pd
import io

# 1. Page Setup
st.set_page_config(page_title="The 500 Machine", layout="centered")
STORE_URL = "https://resumeweapon.lemonsqueezy.com/checkout/buy/bfb2b82e-22ed-4fe2-b2ba-998bafd9de65"

# 2. API Client
if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Missing API Key in Secrets!")

def process_receipt(image_file):
    img = Image.open(image_file)
    model_id = "gemini-3-flash-preview" 
    # STRICT PROMPT for consistent columns
    prompt = """
    Extract data into 4 columns: Date, Item, Category, Amount.
    Rules:
    1. Use 'N/A' if a value is missing.
    2. Separate columns with a TAB character.
    3. NO headers, NO bolding, NO extra text.
    4. One line per item.
    """
    
    try:
        response = client.models.generate_content(model=model_id, contents=[prompt, img])
        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# 3. Sidebar & License
st.sidebar.title("🔐 License")
key = st.sidebar.text_input("Enter Key", type="password")
is_pro = (key == "HUSTLE500" or len(str(key)) > 10)

if not is_pro:
    st.sidebar.markdown(f'[🔥 UNLOCK BULK MODE]({STORE_URL})')

# 4. Main Interface
st.title("🚀 The 500 Machine")
files = st.file_uploader("Upload Receipts", type=['png', 'jpg', 'jpeg'], accept_multiple_files=is_pro)

if st.button("Generate Data", type="primary") and files:
    file_list = files if isinstance(files, list) else [files]
    all_rows = []
    
    for f in file_list:
        with st.spinner(f"Reading {f.name}..."):
            data = process_receipt(f)
            # Handle the 503 Spike Error
            if "503" in data or "UNAVAILABLE" in data:
                time.sleep(3)
                data = process_receipt(f)
            
            all_rows.append(data.replace("```", "").replace("csv", "").strip())
            time.sleep(2) 

    # Combine everything
    final_text = "\n".join(all_rows)
    
    st.success("✅ Done!")

    # OPTION 1: THE PERFECT PASTE
    st.subheader("📋 Option 1: Quick Paste")
    st.info("Click the copy icon on the top right of the box below, then paste in Cell A2.")
    st.code(final_text, language="text")

    # OPTION 2: THE PROFESSIONAL DOWNLOAD
    st.subheader("📁 Option 2: Professional Download")
    try:
        # Convert the text into a clean CSV file
        df = pd.read_csv(io.StringIO(final_text), sep='\t', names=["Date", "Item", "Category", "Amount"])
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Data as CSV",
            data=csv_data,
            file_name="receipt_data.csv",
            mime="text/csv"
        )
    except:
        st.warning("Could not generate CSV, please use Option 1.")
        
