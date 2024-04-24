## Features

- **Automated Content Creation**: Leverages OpenAI's API for generating engaging images, titles, content, and tags, streamlining content creation for Xiaohongshu.
- **LangGPT Prompt Generation & Langchian Framework**: Utilizes the LangGPT project methodology and Langchian framework for creating structured, high-quality prompts and developing language model-powered applications.
- **Customizable & User-Friendly**: Offers prompt customization and model selection options within a Streamlit-based interface, ensuring a user-friendly experience.
- **Efficient Post Generation**:  Supports both topic and image-based post generation. Users can input a topic or upload photos, and MVP automatically crafts a complete, engaging post, simplifying the content creation process.


## Getting Started
1. To install MVP, follow these steps:
```bash
# Create a new conda environment with Python 3.9
conda create -n MVP python=3.9

# Activate the conda environment
conda activate MVP

# Clone the MVP repository to your local machine


# Navigate to the MVP project directory
cd MVP

# Install dependencies from requirements.txt
pip install -r requirements.txt

# If you are using a Linux system, you'll need to install the corresponding dependencies
# xargs -a packages.txt sudo apt-get install -y
```

2. After installing, you can launch the application simply by running:

```bash
streamlit run MVP2024.py
```
> Note: A high-speed internet connection is required, and users in China should use a proxy.

## Configuration
- Prompt Customization: Modify generation prompts in the `data\prompt` folder using the LangGPT methodology.
- Model Selection: Default models are `gpt-4-0125-preview` for text and `dall-e-3` for images. These can be selected in the app.
