# --- 1. CONFIGURATION ---
# Replace this with your actual Lemon Squeezy checkout link
STORE_URL = "https://resumeweapon.lemonsqueezy.com/checkout/buy/bfb2b82e-22ed-4fe2-b2ba-998bafd9de65" 

def verify_license(key):
    """
    Validates the license key. 
    Use 'HUSTLE500' to test the app yourself without buying a key.
    """
    if key == "HUSTLE500":
        return True
    
    # Lemon Squeezy API Validation
    url = "https://api.lemonsqueezy.com/v1/licenses/validate"
    try:
        # Note: Replace with your actual Lemon Squeezy API logic if needed
        # For testing, we check if the key is provided
        return len(key) > 5 
    except:
        return False

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

def process_receipt(image_file, api_key):
    client = Groq(api_key=api_key)
    image_file.seek(0)
    base64_image = encode_image(image_file)
    
    # THE 2026 PRODUCTION MODEL (Fixed the Decommissioned error)
    model_id = "meta-llama/llama-4-scout-17b-16e-instruct"
    
    # Explicitly asking for TABS to fix the Google Sheets pasting issue
    prompt = """Extract these 4 fields: Date, Item, Category, Amount.
    Return ONLY the raw data rows. 
    Separate each column with a TAB character. 
    Do not include headers or any other text."""
    
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

# --- 2. USER INTERFACE ---
st.set_page_config(page_title="The 500 Machine", layout="centered")

# SIDEBAR: License Entry
st.sidebar.title("🔐 Account")
license_key = st.sidebar.text_input("Enter License Key", type="password")
is_pro = verify_license(license_key) if license_key else False

# MAIN PAGE: The "Ad" for Free Users
if not is_pro:
    st.markdown(f"""
    <div style="background-color:#ff4b4b; padding:25px; border-radius:15px; text-align:center; color:white;">
        <h1 style="margin:0;">🚀 Unlock Bulk Scanning</h1>
        <p style="font-size:18px;">Stop doing one-by-one. Process 100+ receipts at once for just ₹99.</p>
        <a href="{https://resumeweapon.lemonsqueezy.com/checkout/buy/bfb2b82e-22ed-4fe2-b2ba-998bafd9de65}" target="_blank" style="text-decoration:none;">
            <button style="background-color:white; color:#ff4b4b; border:none; padding:12px 24px; border-radius:8px; font-weight:bold; cursor:pointer; width:100%; margin-top:10px;">
                BUY LIFETIME PRO ACCESS
            </button>
        </a>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
else:
    st.balloons()
    st.success("✨ PRO MODE ACTIVE: Bulk Upload Enabled")

st.title("📊 AI Receipt Scanner")
st.write("Upload your bills and get structured data for your Google Sheet Dashboard.")

# File Uploader (Multiple files only for Pro)
files = st.file_uploader(
    "Choose receipt images", 
    type=['png', 'jpg', 'jpeg'], 
    accept_multiple_files=is_pro
)

# --- 3. EXECUTION ---
if st.button("Generate Dashboard Data", type="primary") and files:
    if "GROQ_API_KEY" not in st.secrets:
        st.error("API Key missing! Add 'GROQ_API_KEY' to your Streamlit Secrets.")
    else:
        file_list = files if isinstance(files, list) else [files]
        all_rows = []
        
        progress_bar = st.progress(0)
        for i, f in enumerate(file_list):
            with st.spinner(f"Processing {f.name}..."):
                raw_out = process_receipt(f, st.secrets["GROQ_API_KEY"])
                
                # Cleanup: Ensure Tab-separation for the clipboard
                for line in raw_out.split('\n'):
                    if len(line) > 5:
                        # Convert any accidental commas to Tabs
                        clean_line = line.replace(",", "\t")
                        all_rows.append(clean_line)
            progress_bar.progress((i + 1) / len(file_list))

        if all_rows:
            final_output = "\n".join(all_rows)
            st.success("✅ Extraction Complete!")
            
            st.markdown("### 📋 1. Copy the data below")
            # Text area is best for preserving TAB characters for Google Sheets
            st.text_area(
                label="Select all (Ctrl+A), Copy (Ctrl+C)", 
                value=final_output, 
                height=200
            )
            
            st.markdown("### 📈 2. Paste into Google Sheets")
            st.info("Click cell **A2** in your Expense Sheet and press **Ctrl+V**. The data will automatically split into 4 columns.")
            
