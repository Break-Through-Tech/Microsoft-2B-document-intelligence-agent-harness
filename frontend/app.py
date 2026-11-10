import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="MS2B Document Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Top Menu Bar
st.markdown(
    """
    <style>
    .menu-bar {
        background-color: #2B2117; /* Dark brown background */
        padding: 10px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        color: #F6F2EE; /* Light text color */
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        z-index: 1000;
    }
    .main-content {
        margin-top: 60px; /* Push content below the menu bar */
    }
    .user-input {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #f8f9fa;
        padding: 10px;
        border-top: 1px solid #ddd;
    }
    .user-input input {
        width: 100%;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 5px;
        outline: none;
    }
    .user-input input:focus {
        border: 1px solid #ddd; /* No red glow on focus */
    }
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 20px;
    }
    .user-message {
        text-align: right;
        color: #333;
        font-weight: bold;
    }
    .bot-message {
        text-align: left;
        color: #555;
    }
    </style>
    <div class="menu-bar">MS2B</div>
    """,
    unsafe_allow_html=True,
)

# Sidebar for Sources
with st.sidebar:
    st.header("Sources")
    st.file_uploader("Upload Documents", type=["pdf", "txt", "docx"], accept_multiple_files=True)
    st.write("Uploaded Documents:")
    st.write("- Document 1 (dummy)")
    st.write("- Document 2 (dummy)")
    st.button("Clear All")

# Main content area
st.markdown('<div class="main-content">', unsafe_allow_html=True)

st.title("MS2B Chatbot")
st.write("Ask a question about your documents:")

# Chat history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Display chat history
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for chat in st.session_state["chat_history"]:
    st.markdown(f'<div class="user-message">**You:** {chat["question"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="bot-message">**Bot:** {chat["answer"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# User input bar at the bottom
st.markdown('<div class="user-input">', unsafe_allow_html=True)
# user_input = st.text_input("", key="user_input", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# Define a callback function to handle user input
def handle_user_input():
    user_input = st.session_state["user_input"]  # Get the current input
    if user_input:
        dummy_answer = "This is a dummy answer. [Source: Document 1, Page 3]"
        st.session_state["chat_history"].append({"question": user_input, "answer": dummy_answer})
        st.session_state["user_input"] = ""  # Clear the input box

# User input bar at the bottom
st.markdown('<div class="user-input">', unsafe_allow_html=True)
st.text_input(
    "",
    key="user_input",
    label_visibility="collapsed",
    on_change=handle_user_input,  # Use the callback to handle input
)
st.markdown('</div>', unsafe_allow_html=True)



