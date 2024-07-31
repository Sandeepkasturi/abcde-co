import os
import streamlit as st
import subprocess
from streamlit_ace import st_ace
import requests
import base64
from google.generativeai import configure, GenerativeModel
from streamlit_lottie import st_lottie
import streamlit.components.v1 as components
import re
import time
from PIL import Image

# Configure the Generative AI
configure(api_key=st.secrets["api_key"])
model = GenerativeModel('gemini-pro')

# Lottie animation loader
def load_lottie_url(url: str):
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()

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

# Function to simulate AI pretend code compiler
def ai_pretend_compiler(language, code):
    try:
        prompt = f"Simulate the execution of the following {language} code and provide the expected output:\n\n{code}"
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
        return ai_pretend_compiler(language, code), "Detected I/O operations! Using AI Compiler for results."

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
                return ai_pretend_compiler(language, code), "Execution took too long. Here is the simulated output."
            return result.stdout, result.stderr

        elif language == "Java":
            # Write the code to a file
            with open(filename, "w", encoding='utf-8') as f:
                f.write(code)
            # Check if the file was created successfully
            if not os.path.exists(filename):
                return "", f"File not found: {filename}"
            # Compile the Java code
            compile_result = subprocess.run(
                ["javac", filename],
                capture_output=True,
                text=True,
                timeout=20
            )
            if compile_result.returncode != 0:
                return "", compile_result.stderr
            # Run the compiled Java class
            class_name = filename.split(".")[0]
            java_args = [arg1, arg2]
            result = subprocess.run(
                ["java", class_name] + java_args,
                capture_output=True,
                text=True,
                timeout=5
            )
            elapsed_time = time.time() - start_time
            if elapsed_time > 10:
                return ai_pretend_compiler(language, code), "Execution took too long. Here is the simulated output."
            return result.stdout, result.stderr
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
        st.session_state.filename = "hello.py" if language == "Python" else "Main.java"

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

        st.subheader("Output:")
        st.text(stdout)

        if stderr:
            st.subheader("Errors:")
            st.text(stderr)

            if "Using AI Compiler for results." not in stderr:
                # Optional: Show animation
                lottie_url = "https://lottie.host/fb24aa71-e6dd-497e-8a6c-3098cb64b1ed/V9N1Sd3klS.json"
                lottie_animation = load_lottie_url(lottie_url)
                if lottie_animation:
                    st_lottie(lottie_animation, speed=27, width=150, height=100, key="lottie_animation")
                else:
                    st.error("Failed to load Lottie animation.")

                # Generate AI explanation for the error with a spinner
                with st.spinner("Generating AI explanation..."):
                    ai_explanation = get_ai_explanation(stderr)
                st.subheader("AI Explanation:")
                st.text(ai_explanation)

            # Allow user to download generated code
            if st.button("Download Generated Code"):
                download_generated_code(ai_explanation, "generated_code")

    # Python Package Installation
    if language == "Python":
        st.subheader("Install Python Packages")
        package_name = st.text_input("Enter the package name:")
        if st.button("Install Package"):
            result = install_package(package_name)
            st.text(result)

    # Donation Section
    st.markdown("### Support Us")
    st.markdown("If you find this tool useful, please consider supporting us by making a donation.")
    components.html("""
        <form>
            <script src="https://checkout.razorpay.com/v1/payment-button.js" data-payment_button_id="pl_Oe7PyEQO3xI82m" async> </script>
        </form>
    """, height=600, width=300)  # Adjust the height if necessary

elif page == "About":
    st.header("About Autobot Code Compiler")
    st.info("""
        **Autobot Code Compiler** is an advanced tool designed to help developers write, debug, and compile code seamlessly. 
        With support for multiple programming languages like Python and Java, it leverages the power of AI to provide instant feedback and solutions for code errors.
    """)
    st.subheader("How to Use This App")
    st.write("""
        1. **Select Language**: Choose the programming language you want to work with from the dropdown menu.
        2. **Write Code**: Use the code editor to write your code. The editor supports syntax highlighting for the selected language.
        3. **Save Code**: Save your code using the 'Save Code' button to ensure your changes are not lost.
        4. **Run Code**: Click the 'Run Code' button to compile and execute your code. The output and any errors will be displayed below.
        5. **Install Packages (Python)**: For Python, you can install additional packages by entering the package name and clicking 'Install Package'.
    """)

elif page == "Our Company":
    st.header("About SKAV TECH")
    st.write("""
        **SKAV TECH** is a cutting-edge technology company specializing in NO CODE and Low Code application development using Prompt Engineering and leveraging AI.
        Our mission is to make software development accessible to everyone, regardless of their technical background.
    """)
    st.write("""
        **Founder**: Sandeep Kasturi
        - [Company](https://skavtech.wegic.app)
        - [Instagram](https://instagram.com/sandeep_kasturi_)
        - [GitHub](https://github.com/Sandeepkasturi)
    """)

elif page == "Support":
    st.header("Support Us")
    st.write("""
        At **SKAV TECH**, our vision is to empower developers and non-developers alike with the tools they need to create powerful applications effortlessly.
        We are always looking for investments to grow and improve our offerings. If you believe in our mission, please consider supporting us.
    """)
    if st.button("Support Us"):
        components.html("""
            <form>
                <script src="https://checkout.razorpay.com/v1/payment-button.js" data-payment_button_id="pl_Oe7PyEQO3xI82m" async> </script>
            </form>
        """, height=600, width=300)  # Adjust the height if necessary

        st.write("Thank you for your support!")

elif page == "Become Insider":
    st.header("Become an Insider at SKAV TECH")
    st.write("""
        We are hiring!

        **Positions Available**:
        - Prompt Engineers
        - ChatGPT Experts
        - Large Language Model Experts

        Join us and be part of a dynamic team at the forefront of AI and Prompt Engineering technology.
    """)
    st.write("""
        **Founder**: Sandeep Kasturi
        - [Company](https://skavtech.wegic.app)
        - [Instagram](https://instagram.com/sandeep_kasturi_)
        - [GitHub](https://github.com/Sandeepkasturi)
    """)
