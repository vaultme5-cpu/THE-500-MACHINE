import streamlit as st
from google import genai
from PIL import Image

# 1. Page Setup
st.set_page_config(page_title="The 500 Machine", layout="centered")
STORE_URL = "https://resumeweapon.lemonsqueezy.com/checkout/buy/bfb2b82e-22ed-4fe2-b2ba-998bafd9de65"

# 2. Modern 2026 API Client
if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Go to Streamlit Settings > Secrets and add GEMINI_API_KEY")

def process_receipt(image_file):
    img = Image.open(image_file)
    # Using the 2026 stable workhorse model
    model_id = "gemini-3-flash-preview" 
    prompt = "Extract Date, Item, Category, Amount. Return ONLY raw rows. Use TAB between columns. No headers."
    
    try:
        response = client.models.generate_content(model=model_id, contents=[prompt, img])
        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# 3. Sidebar & License
st.sidebar.title("🔐 License")
license_key = st.sidebar.text_input("Enter Key", type="password")
is_pro = (license_key == "HUSTLE500" or len(str(license_key)) > 10)

if not is_pro:
    st.markdown(f'<a href="{STORE_URL}" target="_blank"><button style="width:100%;background:#ff4b4b;color:white;padding:12px;border:none;border-radius:8px;cursor:pointer;font-weight:bold;">🔥 UNLOCK BULK MODE - ₹99</button></a>', unsafe_allow_html=True)
    st.divider()

# 4. Main Interface
st.title("🚀 The 500 Machine")
files = st.file_uploader("Upload Receipts", type=['png', 'jpg', 'jpeg'], accept_multiple_files=is_pro)

if st.button("Generate Data", type="primary") and files:
    file_list = files if isinstance(files, list) else [files]
    final_output = []
    
    for f in file_list:
        with st.spinner(f"Reading {f.name}..."):
            data = process_receipt(f)
            # Remove any AI markdown formatting
            clean_data = data.replace("```", "").replace("csv", "").strip()
            final_output.append(clean_data)
    
    st.success("✅ Done!")
    st.text_area("Copy to Google Sheets (A2)", value="\n".join(final_output), height=300)
    
