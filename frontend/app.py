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

    # Initialize uploaded files in session state
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

    if "clear_all_flag" not in st.session_state:
        st.session_state.clear_all_flag = False

    # File uploader
    uploaded_file = st.file_uploader("Upload Documents", type=["pdf", "txt", "docx"], accept_multiple_files=False)

    # Add the uploaded file to the session state list
    if uploaded_file is not None:
        st.session_state.uploaded_files.append(uploaded_file.name)

    # Display uploaded files
    st.write("Uploaded Documents:")
    if st.session_state.uploaded_files:
        for file in st.session_state.uploaded_files:
            st.write(f"- {file}")
    else:
        st.write("No files uploaded yet.")

    # File selection for deletion
    selected_files = st.multiselect("Select files to delete:", st.session_state.uploaded_files)

    # Delete selected files with confirmation
    if st.button("Delete Selected"):
        if selected_files:
            confirm = st.warning(
                f"Are you sure you want to delete the selected files: {', '.join(selected_files)}?",
                icon="⚠️",
            )
            if st.button("Confirm Delete"):
                # Remove selected files from the list
                st.session_state.uploaded_files = [
                    file for file in st.session_state.uploaded_files if file not in selected_files
                ]
                st.success("Selected files have been deleted.")
        else:
            st.warning("No files selected for deletion.")

    # Clear all files button with confirmation
    if st.button("Clear All"):
        st.session_state.clear_all_flag = True  # Turn on the Clear All switch

    # Handle confirmation logic
    if st.session_state.clear_all_flag:
        confirm = st.warning(
            "Are you sure you want to clear all uploaded files?",
            icon="⚠️",
        )
        # Use unique keys for buttons to avoid interference
        confirm_clear = st.button("Confirm Clear All", key="confirm_clear_all")
        cancel_clear = st.button("Cancel", key="cancel_clear_all")

        if confirm_clear:
            st.session_state.uploaded_files.clear()  # Clear the toy box (files)
            st.session_state.files_cleared = True  # Turn on the Files Cleared light
            st.session_state.clear_all_flag = False  # Turn off the Clear All switch
        elif cancel_clear:
            st.session_state.clear_all_flag = False  # Turn off the Clear All switch

    # Display success message if files were cleared
    if "files_cleared" in st.session_state and st.session_state.files_cleared:
        st.success("All files have been cleared.")
        # Do NOT reset files_cleared immediately; let it persist for one rerun
        st.session_state.files_cleared = False  # Reset AFTER the success message is shown in the next rerun

    # Debugging logs
    st.write(f"Clear All Flag: {st.session_state.clear_all_flag}")
    st.write(f"Files Cleared: {st.session_state.get('files_cleared', False)}")
    st.write(f"Uploaded Files: {st.session_state.uploaded_files}")

    # Main content area
    st.markdown('<div class="main-content">', unsafe_allow_html=True)

st.title("MS2B Chatbot")
st.write("Ask questions about your documents.")

message = st.chat_message("assistant")
message.write("Hello human – how can i help you? (¬`‸´¬)")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask away..."):
    # Display user message to chat container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = f"Echo: {prompt}"
    # Display assistant message to chat container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant message to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})


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


st.markdown('</div>', unsafe_allow_html=True)