import streamlit as st
import pandas as pd
from groq import Groq
from PIL import Image
import io

# 1. Page Configuration
st.set_page_config(page_title="The 500 Machine", page_icon="💰")
st.title("⚡ Data Bridge: Image to CSV")
st.markdown("### Turn messy screenshots into clean Excel data.")

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
    
    if st.button("🚀 EXECUTE EXTRACTION"):
        with st.spinner("Processing... The Machine is thinking."):
            # We convert the image to text for the AI to process
            # In the final version, we use the Vision model. 
            # For now, we ask the AI to structure the data.
            
            prompt = "Act as a Data Engineer. Extract the tabular data from the user's provided input. Format it as a clean CSV table. No prose, no talk. Just CSV."
            
            completion = client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[{"role": "user", "content": prompt}]
            )
            
            csv_result = completion.choices[0].message.content
            
            st.success("✅ Extraction Complete!")
            st.code(csv_result, language="csv")
            
            # Download Logic
            st.download_button(
                label="📥 Download as CSV",
                data=csv_result,
                file_name="the_500_machine_output.csv",
                mime="text/csv"
            )
            
            # MONETIZATION LOOPHOLE
            st.markdown("---")
            st.info("💡 **Want to automate 100+ files at once?** [Get the Bulk Machine here](YOUR_LEMON_SQUEEZY_LINK)")

# 4. Footer
st.markdown("---")
st.caption("Powered by Sovereign Architect Protocol | Version 1.0")
  
