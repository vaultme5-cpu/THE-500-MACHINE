import streamlit as st
import pandas as pd
from groq import Groq
from PIL import Image
import io
import base64

# 1. Page Configuration
st.set_page_config(page_title="The 500 Machine", page_icon="💰")
st.title("⚡ Data Bridge: Image to CSV")

# 2. Connection to the Brain
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Setup incomplete. Add your GROQ_API_KEY to Streamlit Secrets.")
    st.stop()

# 3. User Input
uploaded_file = st.file_uploader("Upload a photo of a table or list", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="File Uploaded Successfully", use_container_width=True)
    
    # THIS PART MUST BE INDENTED
    if st.button("🚀 EXECUTE EXTRACTION"):
        with st.spinner("The Machine is seeing the data..."):
            try:
                # Encode image to Base64
                base64_image = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                
                completion = client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Extract all tabular data from this image. Format it as a clean CSV table only. No extra text."},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                                },
                            ],
                        }
                    ],
                )
                
                csv_result = completion.choices[0].message.content
                st.success("✅ Extraction Complete!")
                st.code(csv_result, language="csv")
                
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv_result,
                    file_name="extracted_data.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Brain Error: {e}")

# 4. Footer
st.markdown("---")
st.info("💡 **Want to automate 100+ files?** [Get the Bulk Machine here](YOUR_LEMON_SQUEEZY_LINK)")
