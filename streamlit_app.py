import os
import streamlit as st
import subprocess
from streamlit_ace import st_ace
import streamlit.components.v1 as components
import requests
import streamlit_lottie as st_lottie
import base64
from google.generativeai import configure, GenerativeModel
import re
import time

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

# Set up the Streamlit page
st.set_page_config(page_title="Autobot Code Compiler", page_icon="💻", layout="wide")

# Custom CSS for styling
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
        overflow-x: auto;
        max-height: 400px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease-in-out;
    }
    .generated-content:hover {
        transform: scale(1.02);
    }
    .error-content {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
        color: #ff0000;
        font-family: "Courier New", Courier, monospace;
        overflow-x: auto;
        max-height: 400px;
        box-shadow: 0 0 10px rgba(255, 0, 0, 0.2);
        transition: transform 0.2s ease-in-out;
    }
    .error-content:hover {
        transform: scale(1.02);
    }
    .title-container {
        display: flex;
        align-items: center;
    }
    .title-container img {
        margin-right: 10px;
    }
    .footer {
        text-align: center;
        margin-top: 30px;
        padding: 10px 0;
        background-color: #f1f1f1;
    }
    .footer a {
        margin: 0 15px;
        text-decoration: none;
        color: #4e73df;
    }
    .footer img {
        width: 24px;
        height: 24px;
        vertical-align: middle;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Title of the application with logo
st.markdown(
    """
    <div class="title-container">
        <img src="data:image/png;base64,{}" width="60" height="60">
        <h1>ABCDE & CO</h1>
    </div>
    """.format(base64.b64encode(open("abcde2.png", "rb").read()).decode()),
    unsafe_allow_html=True
)

st.markdown("AutoBot Code Development Environment & Computational Optimization (ABCDE & CO)")

st.subheader("Autobot Code Compiler")
# Sidebar for navigation
st.sidebar.title("Navigation")
st.markdown("*Developed by Sandeep Kasturi*")
st.sidebar.image("abcde2.png", use_column_width=True)
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

    # ACE editor configuration
    code = st_ace(
        language=language.lower(),
        theme="cobalt",
        value=st.session_state.code,
        height=300,
        auto_update=False,
        readonly=False,
        keybinding="vscode",
        font_size=14,
        tab_size=4,
        show_gutter=True,
        wrap=False,
        min_lines=20,
        key="ace_editor",
    )
    #INTEGRATING AUTOBOT AI
    st.header("AutoBot 💀")
    st.markdown(
        "AutoBot is effective for code generation. If your prompt contains code generation **-prompt-**, you can get downloadable files.")

    question = st.text_input("Ask the model a question:")

    if st.button("Ask AI"):

        # Animation for insider page
        lottie_animation_url = "https://lottie.host/9ea2d5e2-feac-4b64-b36b-8dfad9d46e6e/fUbiNI1HFw.json"
        lottie_animation = load_lottie_url(lottie_animation_url)
        if lottie_animation:
            st_lottie.st_lottie(lottie_animation, height=300)
        with st.spinner("Generating response 💀..."):
            try:
                response = model.generate_content(question)
                if response.text:
                    st.text("AutoBot Response:")
                    st.write(response.text)
                    st.markdown('---')
                    st.markdown(
                        "Security Note: We use **.txt** file format for code downloads, which is not easily susceptible to virus and malware attacks.")
                else:
                    st.error("No valid response received from the AI model.")
                    st.write(f"Safety ratings: {response.safety_ratings}")
            except ValueError as e:
                st.info(f"Unable to assist with that prompt due to: {e}")
            except IndexError as e:
                st.info(f"Unable to assist with that prompt due to: {e}")
            except Exception as e:
                st.info(f"An unexpected error occurred: {e}")

            code_keywords = ["code", "write code", "develop code", "generate code", "generate", "build"]
            if any(keyword in question.lower() for keyword in code_keywords):
                st.text("Download the generated code 💀:")
                download_generated_code(response.text, "code", format='txt')

    # Initialize the compilation count in session state if not already set
    if 'compile_count' not in st.session_state:
        st.session_state.compile_count = 0

    # Add the "Compile and Run" button
    if st.button("Compile and Run Code"):
        st.session_state.saved_code = code
        st.session_state.saved_code = code
        output, error = run_code(language, code, st.session_state.filename)
        st.session_state.compile_count += 1  # Increment compile count

        # Display the output in a styled container
        st.subheader("Output:")
        if output:
            st.markdown(
                f'<div class="generated-content">{output}</div>',
                unsafe_allow_html=True
            )
        else:
            st.write("No output.")

        # Display any errors in a styled container
        if error:
            st.subheader("Errors:")
            st.markdown(
                f'<div class="error-content">{error}</div>',
                unsafe_allow_html=True
            )

            # Display AI-generated explanation for errors
            ai_explanation = get_ai_explanation(error)
            st.subheader("AI Explanation:")
            st.markdown(
                f'<div class="generated-content">{ai_explanation}</div>',
                unsafe_allow_html=True
            )

    #Explanation of Output
    if st.session_state.compile_count > 0:
        if st.button("Explain"):
            with st.spinner("Preparing Explanation..."):
                compiled_code = f"Explain the Code and Output{code}"
                response = model.generate_content(compiled_code)
                if response.text:
                    st.text("AutoBot Response:")
                    st.write(response.text)

    # Add a button to download the code
    if st.button("Download Code"):
        filename_without_ext = os.path.splitext(st.session_state.filename)[0]
        download_generated_code(code, filename_without_ext, "py" if language == "Python" else "java")
    # Add Razorpay donation button to the sidebar
    st.sidebar.markdown("### Support Us")
    st.sidebar.markdown("If you find this tool useful, please consider supporting us by making a donation.")
    components.html(
        """
        <form>
            <script src="https://checkout.razorpay.com/v1/payment-button.js" data-payment_button_id="pl_Oe7PyEQO3xI82m" async> </script>
        </form>
        """,
        height=450,
        width=300
    )


elif page == "About":
    # Animation for about page
    lottie_animation_url = "https://assets5.lottiefiles.com/packages/lf20_YXD37qLQnb.json"
    lottie_animation = load_lottie_url(lottie_animation_url)
    if lottie_animation:
        st_lottie.st_lottie(lottie_animation, height=300)
    st.write(
        "Autobot Code Compiler is a powerful tool designed to make code compilation and execution seamless. Developed by SANDEEP KASTURI, it leverages advanced AI techniques to provide comprehensive code analysis and error handling.")
    st.markdown("""
    Here’s a step-by-step guide for using the application from within the Streamlit interface:

### **How to Use the AutoBot Code Compiler Application**

#### **1. Navigating the Application**

1. **Home Page**:
   - **Select Language**: 
     - From the dropdown menu, choose between **Python** or **Java**. This will determine the language for the code editor and default code provided.
   - **Code Editor**:
     - Edit the code in the ACE editor. The editor supports syntax highlighting and other features specific to the selected language.
   - **Compile and Run Code**:
     - Click the **"Compile and Run Code"** button to execute the code. The output and any errors will be displayed below the button.
   - **Download Code**:
     - Click the **"Download Code"** button to download your code in the `.py` (for Python) or `.java` (for Java) format.

2. **About Page**:
   - View information about the application and its features. The page includes a Lottie animation to provide a visual overview.

3. **Our Company Page**:
   - Learn about ABCDE & CO, the company behind the application. This page includes details about the company's mission and vision, along with a Lottie animation.

4. **Support Page**:
   - Access contact information for support inquiries. This page includes an animation and provides contact details for help.

5. **Become Insider Page**:
   - Sign up for the insider program to receive exclusive updates and early access to new features. The page invites users to join the program with a Lottie animation.

#### **2. Interacting with the Code Editor**

1. **Editing Code**:
   - Use the ACE editor to write or modify code. The editor provides features like syntax highlighting, line numbers, and auto-indentation.

2. **Running Code**:
   - Click the **"Compile and Run Code"** button to execute the code in the editor. The application will compile and run the code, displaying the results or errors below the button.

3. **Handling Errors**:
   - If there are errors in your code, the application will display them in a styled container. It will also provide an AI-generated explanation and suggested fixes for the errors.

4. **Viewing Output**:
   - The output of the code execution will be shown in a styled container. This includes standard output and error messages from the execution.

5. **Downloading Code**:
   - Click the **"Download Code"** button to download your code file. The file will be saved with the appropriate extension (`.py` or `.java`) based on the selected language.

#### **3. Using Additional Features**

1. **Lottie Animations**:
   - Enjoy animations on various pages that provide visual enhancements and contextual information.

2. **Support and Donations**:
   - If you find the application useful, consider making a donation via the Razorpay button available in the sidebar and footer.

3. **Navigation**:
   - Use the sidebar to navigate between different pages (Home, About, Our Company, Support, Become Insider) of the application.

By following these instructions, you will be able to effectively use the features of the AutoBot Code Compiler application for code editing, execution, and error handling.
""")
    # Add Razorpay donation button to the sidebar
    st.sidebar.markdown("### Support Us")
    st.sidebar.markdown("If you find this tool useful, please consider supporting us by making a donation.")
    components.html(
        """
        <form>
            <script src="https://checkout.razorpay.com/v1/payment-button.js" data-payment_button_id="pl_Oe7PyEQO3xI82m" async> </script>
        </form>
        """,
        height=450,
        width=300
    )

elif page == "Our Company":
    # Animation for our company page
    lottie_animation_url = "https://assets5.lottiefiles.com/packages/lf20_zZ2Y27.json"
    lottie_animation = load_lottie_url(lottie_animation_url)
    if lottie_animation:
        st_lottie.st_lottie(lottie_animation, height=300)
    st.write(
        "At ABCDE & CO, we are committed to building innovative software solutions that empower developers and businesses alike. Our team of experts is dedicated to delivering high-quality tools that streamline development processes.")
    st.markdown("[Website](https://skavtech.wegic.app)")
    # Add Razorpay donation button to the sidebar
    st.sidebar.markdown("### Support Us")
    st.sidebar.markdown("If you find this tool useful, please consider supporting us by making a donation.")
    components.html(
        """
        <form>
            <script src="https://checkout.razorpay.com/v1/payment-button.js" data-payment_button_id="pl_Oe7PyEQO3xI82m" async> </script>
        </form>
        """,
        height=450,
        width=300
    )

elif page == "Support":
    # Animation for support page
    lottie_animation_url = "https://assets5.lottiefiles.com/packages/lf20_QSo3N6.json"
    lottie_animation = load_lottie_url(lottie_animation_url)
    if lottie_animation:
        st_lottie.st_lottie(lottie_animation, height=300)
    st.write("For support inquiries, please contact us at skavtech.in@gmail.com or call us at +91 9919932723.")
    # Add Razorpay donation button to the sidebar
    st.sidebar.markdown("### Support Us")
    st.sidebar.markdown("If you find this tool useful, please consider supporting us by making a donation.")
    components.html(
        """
        <form>
            <script src="https://checkout.razorpay.com/v1/payment-button.js" data-payment_button_id="pl_Oe7PyEQO3xI82m" async> </script>
        </form>
        """,
        height=450,
        width=400
    )

elif page == "Become Insider":
    # Animation for insider page
    lottie_animation_url = "https://assets5.lottiefiles.com/packages/lf20_UJNc2t.json"
    lottie_animation = load_lottie_url(lottie_animation_url)
    if lottie_animation:
        st_lottie.st_lottie(lottie_animation, height=300)
    st.write(
        "Join our insider program to receive exclusive updates, early access to new features, and special offers. Sign up today and be a part of our growing community!")
    st.markdown("""
    
        <a href="https://pages.razorpay.com/becomeinsider" target="_blank">
            <img src="https://img.icons8.com/ios-glyphs/48/000000/money.png" alt="Donate">Become Insider
        </a> """, unsafe_allow_html=True)
# Add the footer with social links and donation button
st.markdown(
    """
    <div class="footer">
        <a href="https://instagram.com/sandeep_kasturi_" target="_blank">
            <img src="https://img.icons8.com/fluency/48/000000/instagram-new.png" alt="Instagram">
        </a>
        <a href="https://github.com/sandeepkasturi" target="_blank">
            <img src="https://img.icons8.com/ios-glyphs/48/000000/github.png" alt="GitHub">
        </a>
        <a href="https://skavtech.wegic.app" target="_blank">
            <img src="https://img.icons8.com/ios-glyphs/48/000000/domain.png" alt="Website">
        </a>
        <a href="https://pages.razorpay.com/becomeinsider" target="_blank">
            <img src="https://img.icons8.com/ios-glyphs/48/000000/money.png" alt="Donate">
        </a>
        <br>
        <form>
            <script src="https://checkout.razorpay.com/v1/payment-button.js" data-payment_button_id="pl_Oe7PyEQO3xI82m" async> </script>
        </form>
    </div>
    """,
    unsafe_allow_html=True
)
