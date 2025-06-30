# history managing
from ChatHistory import init_chat, add_message, display_chat

# for database and api
import sqlite3 
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from gemini_tone.tone import gem_tone
import re

# Import necessary LangChain components
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# to deal with gui and secret keys
import streamlit as st
from dotenv import load_dotenv
import time

load_dotenv()

# Initialize the input checker
import Checkers as input_checker
input_checker = input_checker.InputChecker()

# Access the API_KEY environment variable
api_key = os.getenv('API_KEY')

# Initialize memory (this is where the conversation will be stored) || Initialize model with memory
memory = ConversationBufferMemory(memory_key="messages", return_messages=True)
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-05-20", temperature=0.2, memory=memory, api_key=api_key)
#model = ChatGoogleGenerativeAI(model="gemini-1.5-flash-8b", memory=memory, api_key=api_key)

# Keywords for conversation || FACTS - Lists
GREETING_KEYWORDS = ["hi", "hello", "hey", "greetings", "whats up", "what's up", "yo", "how are you", "how are you doing"]
ACCEPTED_KEYWORDS = [ "offense", "offenses", "violation", "violations", "rules", "policies",
                    "rights", "responsibilities", "student rights", "classroom conduct", "dress code",
                    "discipline", "code of conduct", "sanction", "penalty", "freedom", "academic", "mcm", "mmcm"]
GOODBYE_KEYWORDS = ["thank you", "goodbye", "farewell", "thanks", "ty", "thank", "bye"]
IDENTITY_KEYWORDS = [ "what are you", "who are you", "are you a bot", "what is your name",  "what's your name",
                     "what can you do", "your purpose", "are you human",  "describe yourself", "tell me about yourself",
                     "what do you do", "what is your function", "what is your role", "what are you here for",]

# Connect to SQLite database and fetch the raw data
def extract_raw_data_from_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * from databaseBot") 
    rows = cursor.fetchall()

    # Joining the rows as a string for the API input
    db_content = "\n".join([" ".join(map(str, row)) for row in rows])
    
    conn.close()
    return db_content

# Modify your query_gemini_api function to utilize memory
def query_gemini_api(db_path, user_input):
    tone = gem_tone() 

    # Default full database content
    db_content = extract_raw_data_from_db(db_path)

    # Define the prompt
    prompt = PromptTemplate(
        input_variables=["db_content", "user_input", "tone"],
        template="{tone} Answer the query based on the following data: {user_input}. Limit up to 500 words. Here is the data: {db_content}"
    )

    user_input = user_input.strip().lower()
    llm_chain = LLMChain(prompt=prompt, llm=model)

    # Reject dangerous or nonsensical inputs
    if any([
        input_checker.is_mathematical_expression(user_input),
        input_checker.is_nonsensical_input(user_input),
        input_checker.is_sql_injection_attempt(user_input)
    ]):
        print("[DEBUG] Reject")
        return "I'm sorry, I can't help you with that. Please ask questions regarding the handbook. Could you please ask something else or clarify your question?"

    # Check for greetings, goodbye, keywords
    elif input_checker.contains_keywords(user_input, GOODBYE_KEYWORDS):
        print("[DEBUG] Goodbye")
        return "You are very much welcome! I am glad I could help!"

    elif input_checker.contains_keywords(user_input, GREETING_KEYWORDS) and len(user_input) <= 17:
        print("[DEBUG] Greeting")
        return "Hello! How may I assist you today?"
    
    # Identity queries
    elif any(phrase in user_input.lower() for phrase in IDENTITY_KEYWORDS):
        print("[DEBUG] Identity")
        return "I'm MMCMate, your AI chatbot assistant designed to help students understand Mapúa MCM’s school policies, rights, and responsibilities."

    # User ONLY typed "mmcm" or "mcm" (nothing else)
    elif user_input.strip() in {"mmcm", "mcm"}:
        print("[DEBUG] MMCM or MCM")
        return (
            "MMCM is the acronym for Mapúa Malayan Colleges Mindanao, a private educational institution in the Philippines. "
            "It is part of the Mapúa University system. If you have specific questions about MMCM, feel free to ask!"
        )

    # General identity query (but NOT handbook-related)
    elif (
        re.search(r"\b(what is|who.*is|tell me about)\b.*\b(mmcm|mcm)\b", user_input)
        and not input_checker.contains_keywords(user_input, ACCEPTED_KEYWORDS)
    ):
        print("[DEBUG] MMCM or MCM - General Identity")
        return (
            "MMCM is the acronym for Mapúa Malayan Colleges Mindanao, a private educational institution in the Philippines. "
            "It is part of the Mapúa University system. If you have specific questions about MMCM, feel free to ask!"
        )
    
    # Only now check for valid handbook-related queries
    elif input_checker.contains_keywords(user_input, ACCEPTED_KEYWORDS):
        print("[DEBUG] In LLM - acceppted keywords")
        response = llm_chain.run({"db_content": db_content, "user_input": user_input, "tone": tone})

    else:
        print("[DEBUG] In LLM - not accepted keywords")
        response = llm_chain.run({"db_content": db_content, "user_input": user_input, "tone": tone})

    # Catch vague LLM responses
    if "Unavailable" in response:
        print("[DEBUG] Unavailable response detected.")
        return "I'm sorry, I couldn't find an answer to your question. Could you please rephrase it or ask something else?"

    return response


def handle_conversation(db_path):
    # Initialize chat history
    init_chat()
    
    # Capture user input
    user_input = st.chat_input("Ask me anything about the school's handbook!")

    if user_input:
        # Add user message to session state
        add_message("user", user_input)
        
        # Display user message immediately
        with st.chat_message("user", avatar='https://raw.githubusercontent.com/vennDiagramm/MMCMate_An_AI_Chatbot_for_School_Policy_Assistance/main/icons/user_icon.ico'):
            st.markdown(user_input)

        # Get assistant response
        result_gen = query_gemini_api(db_path, user_input)

        # Display assistant response with typing effect
        with st.chat_message("assistant", avatar='https://raw.githubusercontent.com/vennDiagramm/MMCMate_An_AI_Chatbot_for_School_Policy_Assistance/main/icons/mapua_icon_83e_icon.ico'):
            assistant_message = ""
            placeholder = st.empty()
            for word in result_gen:
                assistant_message += word
                justified_html = f"<div style='text-align: justify;'>{assistant_message}</div>"
                placeholder.markdown(justified_html, unsafe_allow_html=True)
                time.sleep(0.02)

        # Add assistant response to session state
        add_message("assistant", assistant_message)