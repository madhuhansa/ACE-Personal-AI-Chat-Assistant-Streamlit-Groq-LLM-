import streamlit as st
from dotenv import load_dotenv
from chat_manager import get_chat_list, create_chat, load_chat, save_chat, delete_chat
from llm import stream_reply, generate_chat_title
import time

# Load environment variables
load_dotenv()

# --- Page Config ---
st.set_page_config(page_title="AI Chat", layout="wide")

# --- Custom Sidebar CSS ---
st.markdown("""
<style>
[data-testid="stSidebar"] > div:first-child {
    display: flex;
    flex-direction: column;
    height: calc(100vh - 2rem); 
}

.chat-list-container {
    flex-grow: 1; 
    overflow-y: auto; 
    margin-top: 1rem;
    margin-bottom: 1rem;
}

.delete-container {
    margin-top: auto; 
}
</style>
""", unsafe_allow_html=True)


# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_file" not in st.session_state:
    st.session_state.chat_file = None
if "title" not in st.session_state:
    st.session_state.title = "New Chat"


# --- Helper Function ---
def load_selected_chat(filename):
    """Loads a chat file into the session state."""
    st.session_state.chat_file = filename
    st.session_state.title, st.session_state.messages = load_chat(filename)

# ------------------------------
# SIDEBAR — Chat Selection & Management
# ------------------------------

st.sidebar.title("ACE 🤖")

# (Req 2) "New Chat" button
if st.sidebar.button("➕ New Chat", use_container_width=True):
    filename = create_chat()
    load_selected_chat(filename)
    st.rerun()

# (Req 3) Scrollable chat list
st.sidebar.markdown("<div class='chat-list-container'>", unsafe_allow_html=True)
chat_list = get_chat_list() 

if not chat_list:
    st.sidebar.write("No chats yet.")
else:
    # Iterate over {filename: title} and create a button for each
    for filename, title in chat_list.items():
        is_selected = (filename == st.session_state.chat_file)
        button_type = "primary" if is_selected else "secondary"
        
        if st.sidebar.button(title, use_container_width=True, type=button_type, key=f"chat_{filename}"):
            # If a different chat is clicked, load it
            if not is_selected:
                load_selected_chat(filename)
                st.rerun()

st.sidebar.markdown("</div>", unsafe_allow_html=True) # Close the chat-list container


# (Req 4) "Delete Chat" button at the bottom
st.sidebar.markdown("<div class='delete-container'>", unsafe_allow_html=True)
if st.sidebar.button("Delete Chat", use_container_width=True, type="secondary"):
    if st.session_state.chat_file:
        delete_chat(st.session_state.chat_file)
        st.session_state.clear() 
        st.rerun()
st.sidebar.markdown("</div>", unsafe_allow_html=True) # Close the delete-container




# --- Load default chat on first run (if no chat is selected) ---
if not st.session_state.chat_file:
    chat_files = list(chat_list.keys())
    if chat_files:
        load_selected_chat(chat_files[0]) # Load the first chat
    else:
        # No chats exist, create one
        filename = create_chat()
        load_selected_chat(filename)
        st.rerun()

# ------------------------------
# Main Chat UI
# ------------------------------

# Display the title of the current chat
st.title(st.session_state.get("title", "AI Chat"))

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# Sticky chat input
if user_input := st.chat_input("Your Message"):
    
    is_new_chat = st.session_state.get("title", "New Chat") == "New Chat"

    # Add and display the user's message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # --- Stream bot reply ---
    with st.chat_message("assistant"):
        bot_box = st.empty()
        reply_text = ""
        
        for token in stream_reply(st.session_state.messages):
            reply_text += token
            bot_box.markdown(reply_text + "▌")   
            time.sleep(0.015)

        bot_box.markdown(reply_text)  


    # Add the full bot reply to session state
    st.session_state.messages.append({"role": "assistant", "content": reply_text})

    # --- Title Generation ---
    new_title = None
    if is_new_chat:
        new_title = generate_chat_title(user_input)
        st.session_state.title = new_title
    
    # Save the chat
    save_chat(st.session_state.chat_file, st.session_state.messages, title=new_title)

    # Rerun to update the sidebar list if a new title was generated
    if new_title:
        st.rerun()


