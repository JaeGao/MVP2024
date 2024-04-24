import streamlit as st
from utils import playwright_install

playwright_install()

st.set_page_config(
    page_title="MVP2024",
    page_icon="😎",
    layout="wide"
)

st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)
st.sidebar.success("Select A Function Above.")

st.write("# Welcome to MVP 2024")

#st.image("assets/Autoxhs.png")

st.markdown(
"""

MVP 2024 Project Update:

Work in Progress: Our project, based on open-source tools, is currently being developed for the MVP 2024 initiative. It is specifically crafted to streamline content creation on Xiaohongshu (Little Red Book). Leveraging OpenAI's API, this tool aims to automate the generation and publication of multimedia content, encompassing images, titles, body text, and tags.

Key Features:
Theme-based post generation: As part of our ongoing development, users will be able to input a theme, empowering the tool to effortlessly generate complete post content alongside relevant images.
Image-based post generation: Additionally, users can upload their own images, enabling the tool to produce engaging post content, eliminating concerns over textual elements.

Please note that the project is currently in progress, and further updates will be provided as development continues.
"""
,unsafe_allow_html=True)