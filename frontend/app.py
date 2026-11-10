import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="MS2B Document Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Add custom CSS for layout
st.markdown(
    """
    <style>
    .main-content {
        margin-top: 60px; /* Push content below the menu bar */
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

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Define a callback function to handle user input
def handle_user_input():
    user_input = st.session_state["user_input"]  # Get the current input
    if user_input:
        # Simulate a bot response (replace this with actual logic or API call)
        bot_response = f"I'm a bot, and you said: {user_input}"
        # Append the conversation to chat history
        st.session_state["chat_history"].append({"user": user_input, "bot": bot_response})
        # Clear the input box
        st.session_state["user_input"] = ""

# Tutorial Test - BEGIN
prompt = st.chat_input("Say something")
if prompt:
    st.write(f"User has sent the following prompt: {prompt}")
# Tutorial Test - END

st.markdown('</div>', unsafe_allow_html=True)