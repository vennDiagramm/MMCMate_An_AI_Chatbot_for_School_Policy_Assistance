# history managing
from ChatHistory import init_chat, add_message, display_chat

# for database and api
import sqlite3 
import os
from langchain_google_genai import ChatGoogleGenerativeAI

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
model = ChatGoogleGenerativeAI(model="gemini-1.5-flash-8b", memory=memory, api_key=api_key)

# Keywords for conversation || FACTS - Lists
GREETING_KEYWORDS = ["hi", "hello", "hey", "greetings", "whats up", "what's up", "yo", "how are you", "how are you doing"]
ACCEPTED_KEYWORDS = [
                    "offense", "offenses", "violation", "violations", "rules", "policies",
                    "rights", "responsibilities", "student rights", "classroom conduct", 
                    "discipline", "code of conduct", "sanction", "penalty", "freedom", "academic" ]
GOODBYE_KEYWORDS = ["thank you", "goodbye", "farewell", "thanks", "ty", "thank", "bye"]

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
    tone = (
        "Respond formally and professionally, providing only the requested information. "
        "If the requested offense level does not exist in the database, clearly state that and "
        "inform the user of how many levels are available. Do not guess or invent content. "
        "This is a policy handbook. IDs like '2.a', '3.b.1' represent numbered offenses, "
        "and letters/numbers denoting subcategories. Respond with the appropriate policy or rule "
        "based on these IDs. Provide clear and concise answers, no HTML, do not mention how the answer was generated, "
        "and **do not explicitly state that the information comes 'from the document' or similar phrases.**"
        " Do not say the IDs but the content of the IDs. "
    )

    user_input_clean = user_input.strip().lower()

    # Map word-based phrases to column names in the DB
    level_map = {
        "first offense": "1st offense",
        "1st offense": "1st offense",
        "second offense": "2nd offense",
        "2nd offense": "2nd offense",
        "third offense": "3rd offense",
        "3rd offense": "3rd offense",
        "fourth offense": "4th offense",
        "4th offense": "4th offense"
    }

    offense_level_detected = None
    for phrase, column_name in level_map.items():
        if phrase in user_input_clean:
            offense_level_detected = column_name
            break

    # Default full database content
    db_content = extract_raw_data_from_db(db_path)

    if offense_level_detected:
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Ensure proper quoting for column name
            query = f"SELECT Category, [{offense_level_detected}] FROM databaseBot WHERE [{offense_level_detected}] IS NOT NULL AND TRIM([{offense_level_detected}]) != ''"
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                return f"I'm sorry, there is no information available for a {offense_level_detected} in the handbook."

            db_content = "\n".join(f"{row[0]}: {row[1]}" for row in rows if row[0] and row[1])

        except Exception as e:
            return f"An error occurred while checking offense levels: {str(e)}"

    # Define the prompt
    prompt = PromptTemplate(
        input_variables=["db_content", "user_input", "tone"],
        template="{tone} Answer the query based on the following data: {user_input}. Limit up to 500 words if possible. Here is the data: {db_content}"
    )

    user_input = user_input.strip().lower()
    llm_chain = LLMChain(prompt=prompt, llm=model)

    if input_checker.contains_keywords(user_input, ACCEPTED_KEYWORDS):
        response = llm_chain.run({"db_content": db_content, "user_input": user_input, "tone": tone}) + "\n\n We recommend you to check the handbook for more details."
    elif input_checker.contains_keywords(user_input, GOODBYE_KEYWORDS):
        return "You are very much welcome! I am glad I could help!"
    elif input_checker.contains_keywords(user_input, GREETING_KEYWORDS) and len(user_input) <= 17:
        return "Hello! How may I assist you today?"
    elif any([
        input_checker.is_mathematical_expression(user_input),
        input_checker.is_nonsensical_input(user_input)
    ]):
        return "I'm sorry, I can't help you with that. Please ask questions regarding the handbook. Could you please ask something else or clarify your question?"
    else:
        response = llm_chain.run({"db_content": db_content, "user_input": user_input, "tone": tone}) + "\n\n We recommend you to check the handbook for more details."

    if "Not found" in response or "Unavailable" in response or not response.strip():
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
        with st.chat_message("user", avatar='https://raw.githubusercontent.com/vennDiagramm/admissionBot/refs/heads/main/Icons/student.ico'):
            st.markdown(user_input)

        # Get assistant response
        result_gen = query_gemini_api(db_path, user_input)

        # Display assistant response with typing effect
        with st.chat_message("assistant", avatar='https://raw.githubusercontent.com/vennDiagramm/admissionBot/refs/heads/main/Icons/mapua_icon_83e_icon.ico'):
            assistant_message = ""
            placeholder = st.empty()
            for word in result_gen:
                assistant_message += word
                placeholder.markdown(assistant_message)
                time.sleep(0.02)

        # Add assistant response to session state
        add_message("assistant", assistant_message)