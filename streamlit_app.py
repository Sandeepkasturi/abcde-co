import os
import streamlit as st
import subprocess
from streamlit_ace import st_ace
import requests
import base64
from google.generativeai import configure, GenerativeModel
import re
import time
from PIL import Image

# Configure the Generative AI
configure(api_key=st.secrets["api_key"])
model = GenerativeModel('gemini-pro')


# Function to download generated code
def download_generated_code(content, filename, format='txt'):
    extension = format
    temp_filename = f"{filename}.{extension}"
    with open(temp_filename, 'w') as file:
        file.write(content)
    with open(temp_filename, 'rb') as file:
        data = file.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:file/{format};base64,{b64}" download="{filename}.{format}">Download Code ({format.upper()})</a>'
    st.markdown(href, unsafe_allow_html=True)
    os.remove(temp_filename)


# Function to get AI-generated explanations for errors
def get_ai_explanation(error_message):
    try:
        prompt = f"The following error was encountered in the code:\n\n{error_message}\n\nPlease provide an explanation and suggest a solution."
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An unexpected error occurred while generating an explanation: {e}"


# Function to simulate AI pretend code compiler for Python and Java
def ai_pretend_compiler(language, code):
    try:
        if language == "Python":
            prompt = f"""Pretend you are a real Python interpreter and execute the following Python code. Provide the exact output as it would appear if run on an actual Python interpreter.

If there are any errors, please:
- Identify the type of error (e.g., syntax error, runtime exception).
- Describe where the error occurs in the code.
- Suggest a fix for the error.

Here is the Python code to evaluate:
\n\n{code}

What is the expected output of the code?
"""
        elif language == "Java":
            prompt = f"""Pretend you are a real JVM and execute the following Java code. Provide the exact output as it would appear if run on an actual JVM.

If there are any errors, please:
- Identify the type of error (e.g., syntax error, runtime exception).
- Describe where the error occurs in the code.
- Suggest a fix for the error.

Here is the Java code to evaluate:
\n\n{code}

What is the expected output of the code?
"""

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An unexpected error occurred while generating the pretend output: {e}"


# Function to detect I/O operations in the code
def contains_io_operations(language, code):
    if language == "Python":
        io_patterns = [
            r'\binput\s*\(',
            r'\bopen\s*\(',
            r'\bread\s*\(',
            r'\bwrite\s*\(',
        ]
    elif language == "Java":
        io_patterns = [
            r'\bScanner\s*\(',
            r'\bSystem\.in\b',
            r'\bBufferedReader\s*\(',
            r'\bFileReader\s*\(',
            r'\bFileWriter\s*\(',
        ]
    for pattern in io_patterns:
        if re.search(pattern, code):
            return True
    return False


# Function to compile and run the code
def run_code(language, code, filename):
    if contains_io_operations(language, code):
        io_message = "I/O Detected"
        ai_compiler_message = "Using AI to Simulate Output"
        ai_output = ai_pretend_compiler(language, code)
        return ai_output, f"{io_message}\n{ai_compiler_message}"

    try:
        start_time = time.time()
        if language == "Python":
            with open(filename, "w", encoding='utf-8') as f:
                f.write(code)
            result = subprocess.run(
                ["python3", filename],
                capture_output=True,
                text=True,
                timeout=20  # 20 seconds timeout
            )
            elapsed_time = time.time() - start_time
            if elapsed_time > 10:
                return ai_pretend_compiler(language, code), "Execution took too long. Using AI Compiler for results."
            return result.stdout, result.stderr

        elif language == "Java":
            # Simulate Java code execution using AI
            return ai_pretend_compiler(language, code), ""
    except subprocess.TimeoutExpired:
        return ai_pretend_compiler(language, code), "Execution timed out! Using AI Compiler for results."
    except FileNotFoundError as e:
        return "", f"File not found: {e.filename}"
    except Exception as e:
        return "", f"An unexpected error occurred: {e}"


# Function to install Python packages
def install_package(package):
    try:
        result = subprocess.run(
            ["pip", "install", package],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return f"Package '{package}' installed successfully!"
        else:
            return result.stderr
    except Exception as e:
        return f"An error occurred: {e}"


# Set up the Streamlit page
st.set_page_config(page_title="Autobot Code Compiler", page_icon="💻")

# Custom CSS for console-like styling
st.markdown(
    """
    <style>
    .generated-content {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
        color: #61dafb;
        font-family: "Courier New", Courier, monospace;
    }
    .error-content {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
        color: #ff0000;
        font-family: "Courier New", Courier, monospace;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Title of the application
st.title("ABCDE & CO")
image_path = "abcde2.png"
image = Image.open(image_path)
resized_image = image.resize((400, 250))
st.image(resized_image)
st.markdown("AutoBot Code Development Environment & Computational Optimization.(ABCDE & CO)")

st.subheader("Autobot Code Compiler")
# Sidebar for navigation
st.sidebar.title("Navigation")
st.markdown("**Developed by SANDEEP KASTURI**")
st.sidebar.image("abcde2.png")
page = st.sidebar.selectbox("Go to", ["Home", "About", "Our Company", "Support", "Become Insider"])

if page == "Home":
    # Create a dropdown menu for language selection
    language = st.selectbox("Choose Language", ["Python", "Java"])

    # Define default code for each language
    default_code = {
        "Python": "print('Hello, World!')",
        "Java": """
    public class Main {
        public static void main(String[] args) {
            System.out.println("Hello, World!");
        }
    }
    """
    }

    # Initialize session state if not already done
    if 'language' not in st.session_state:
        st.session_state.language = language
        st.session_state.code = default_code[language]
        st.session_state.saved_code = default_code[language]
        st.session_state.filename = "main.py" if language == "Python" else "Main.java"

    # Update the code editor content if the language changes
    if st.session_state.language != language:
        st.session_state.language = language
        st.session_state.code = default_code[language]
        st.session_state.saved_code = default_code[language]  # Reset saved code on language change
        st.session_state.filename = "main.py" if language == "Python" else "Main.java"

    # Display the code editor with the appropriate code
    st.info("Write code here according to the Selected Language.")
    code = st_ace(
        language=language.lower(),
        theme="monokai",
        key="ace_editor",
        value=st.session_state.code
    )

    # Update session state with the current code
    st.session_state.code = code

    # Update the Java filename based on the class name in the code
    if language == "Java":
        class_name_match = re.search(r"\bclass\s+(\w+)", code)
        if class_name_match:
            class_name = class_name_match.group(1)
            st.session_state.filename = f"{class_name}.java"


    # Function to save the current code
    def save_code():
        st.session_state.saved_code = code
        st.success("Code saved successfully!")


    # Add a button to save the code
    if st.button("Save Code"):
        save_code()

    # Handle key events for saving code
    if code and (
            st.session_state.get("key_event") == "F3"
            or (st.session_state.get("key_event") == "S" and st.session_state.get("shift"))
    ):
        save_code()

    # Input field for the filename
    filename = st.text_input(
        "Enter the filename (with appropriate extension)",
        value=st.session_state.filename
    )

    # Ensure the filename has the correct extension
    if language == "Python" and not filename.endswith(".py"):
        filename += ".py"

    # Input fields for command-line arguments (only for Java)
    if language == "Java":
        arg1 = st.text_input("Enter the first argument (integer):", value="1")
        arg2 = st.text_input("Enter the second argument (integer):", value="2")

    # Create a button to run the code
    if st.button("Run Code"):
        with st.spinner("Running..."):
            stdout, stderr = run_code(language, code, filename)

        # Display output and errors
        if stderr and "I/O Detected" in stderr:
            st.markdown(
                """
                <div style="background-color: #282c34; color: #61dafb; padding: 10px; border-radius: 5px;">
                    <h3 style="color: red;">I/O Detected</h3>
                   <b>* Using AI to Simulate Output...<b>

                </div>
                """,
                unsafe_allow_html=True
            )
            # Display the AI-simulated output
            st.subheader("Output:")
            st.markdown(f"<div class='generated-content'>{stdout}</div>", unsafe_allow_html=True)

        else:
            st.subheader("Output:")
            st.markdown(f"<div class='generated-content'>{stdout}</div>", unsafe_allow_html=True)

            if stderr:
                st.subheader("Errors:")
                st.markdown(f"<div class='error-content'>{stderr}</div>", unsafe_allow_html=True)

