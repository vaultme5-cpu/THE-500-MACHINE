    if st.button("🚀 EXECUTE EXTRACTION"):
        with st.spinner("The Machine is seeing the data..."):
            import base64
            
            # 1. Encode image to Base64
            base64_image = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
            
            # 2. Call the Vision Brain
            try:
                completion = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Extract all tabular data from this image. Format it as a clean CSV table only. No extra text."},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}",
                                    },
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
                
