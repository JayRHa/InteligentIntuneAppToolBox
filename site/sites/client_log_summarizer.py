"""Streamlit app to summarize the log file content"""

import streamlit as st

from modules.openai import OpenAi


def summarize_logfile(openai: OpenAi):
    """Summarize the log file content"""
    st.subheader("IME Log File Summarizer")
    uploaded_file = st.file_uploader("Choose a file")

    if uploaded_file is not None:
        # Running indication
        st.write("Running...")
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()
        log_content = bytes_data[-128000:].decode("utf-8")  # Decode bytes to string

        prompt = f"""
        You are a senior Intune engineer. Your task is to find errors in the [Intune Management Extension log]. Give the user a summary of the log and point them to potential errors in a structured way. Explain to the user what it means and how they can check and troubleshoot this.

        [Intune Management Extension log]
        {log_content}
        [END Intune Management Extension log]
        """

        openai_response = openai.open_ai_run(prompt=prompt)

        st.write(openai_response)
