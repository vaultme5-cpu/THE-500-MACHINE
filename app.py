import streamlit as st
import requests
from groq import Groq
import base64

# --- CONFIG ---
STORE_URL = "https://yourstore.lemonsqueezy.com/checkout/..." # REPLACE WITH YOUR LINK

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
    model_id = "meta-llama/llama-4-scout-17b-16e-instruct"
    # Note: Using TAB-SEPARATED format in the prompt
    prompt = "Extract: Date, Item, Category, Amount. Return ONLY raw rows. Separate columns with a TAB. No text."
    
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

# --- SIDEBAR ---
st.sidebar.title("🚀 The 500 Machine")
user_key = st.sidebar.text_input("Enter License Key", type="password")

is_pro = verify_license(user_key) if user_key else False

if not is_pro:
    st.sidebar.warning("🔒 Bulk Mode Locked")
    st.sidebar.link_button("🔥 Unlock Bulk Upload (₹99)", STORE_URL)
else:
    st.sidebar.success("✅ PRO ACTIVE")

# --- MAIN UI ---
st.title("📊 AI Bulk Receipt Scanner")
files = st.file_uploader("Upload Receipts", type=['png', 'jpg', 'jpeg'], accept_multiple_files=is_pro)

if st.button("Generate Dashboard Data") and files:
    file_list = files if isinstance(files, list) else [files]
    all_rows = []
    bar = st.progress(0)
    
    for i, f in enumerate(file_list):
        with st.spinner(f"Reading {f.name}..."):
            raw_out = process_receipt(f, st.secrets["GROQ_API_KEY"])
            # The AI might give commas, we force Tabs for Google Sheets
            for line in raw_out.split('\n'):
                if len(line) > 5 and "Date" not in line:
                    clean_line = line.replace(",", "\t") 
                    all_rows.append(clean_line)
        bar.progress((i + 1) / len(file_list))
    
    if all_rows:
        final_data = "\n".join(all_rows)
        st.success("Ready! Click the copy icon below.")
        # st.code provides the "Copy" button automatically
        st.code(final_data, language="text")
        st.info("Paste into Google Sheet cell A2. It will auto-split into columns.")
        
