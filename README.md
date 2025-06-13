MMCMate – School Policy Chatbot for Mapúa MCM
===================================================

Welcome to the repository for **MMCMate**, an AI-powered chatbot developed to assist students of **Mapúa Malayan Colleges Mindanao (Mapúa MCM)** with queries related to **school policies**, including rules and regulations. This project was developed as part of our **IT104L: Application Development and Emerging Technologies** course.

The chatbot provides an interactive and user-friendly experience for students seeking clarity on institutional guidelines and policies.

---------------------------------------------------



🧠 Technologies Used
--------------------

- **Python** – Core programming language for backend logic and chatbot handling  
- **Gemini** – Utilized for natural language understanding and enhancing conversational capabilities  
- **Streamlit** – Web framework for building the interactive frontend  
- **LangChain + Google GenAI** – For integrating advanced language processing features  
- **NLTK, langdetect, uuid** – Utility libraries for natural language processing, language detection, and ID generation

---------------------------------------------------



✨ Features
-----------

- **Interactive Chat Interface** – Ask about school rules, regulations, and other policy-related topics  
- **Smart Input Handling** – Detects and responds to irrelevant or nonsense inputs  
- **Natural Language Support** – Understands user queries with the help of AI models  
- **Chat Save Feature** – Users can save, rename, and delete their conversation history in `.txt` format  
- **API Integration** – Connects with Gemini via LangChain and handles `.env`-based secure API key usage  
- **User-Friendly GUI** – Seamless interaction via a browser-based interface powered by Streamlit

---------------------------------------------------



🚀 Installation Guide
----------------------

1. **Create and Activate a Virtual Environment**

   ```bash
   # Create a new virtual environment
   python -m venv chatBot

   # Activate the environment
   # Windows
   chatBot\Scripts\activate

   # macOS/Linux
   source chatBot/bin/activate
   ```

2. **Install Required Packages**

   ```bash
   # Create a cache folder to optimize installations
   mkdir .pip_cache

   # Install required dependencies
   pip install --cache-dir=.pip_cache streamlit python-dotenv langdetect nltk langchain langchain-google-genai uuid

   # If google-genai fails to install properly
   pip install -U langchain-google-genai
   ```

3. **Set Up API Key**

   Since the GitHub repo is public:

   - Create a `.env` file in your project directory.
   - Inside `.env`, paste your Gemini API key like this:

     ```
     API_KEY="your-api-key"
     ```

4. **Fixing Interpreter Issues (Optional)**

   - Press `Ctrl + Shift + P`
   - Type: `Python: Select Interpreter`
   - Choose the one pointing to your virtual environment (e.g., `chatBot\Scripts\python.exe`)

---------------------------------------------------



📬 Contact & Acknowledgments
-----------------------------

This chatbot was developed by students of **Mapúa Malayan Colleges Mindanao** for academic purposes. Special thanks to our instructor and the Gemini and LangChain communities for their tools and support.
