# The Secure Way: Fetching the key from the vault
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("Missing API Key. Please configure it in Streamlit Cloud Secrets.")
    st.stop()
  
