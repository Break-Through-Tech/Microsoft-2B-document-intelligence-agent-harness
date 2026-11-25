from pathlib import Path
import sys
import hashlib

import streamlit as st


# --------------------------------------------------
# 1. Project setup
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ingestion import ingest_uploaded_file, clear_uploaded_documents
from workflow import build_workflow


st.set_page_config(
    page_title="MS2B Document Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# --------------------------------------------------
# 2. Cache the LangGraph workflow
# --------------------------------------------------

@st.cache_resource
def get_workflow():
    return build_workflow()


# --------------------------------------------------
# 3. Session state initialization
# --------------------------------------------------

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {}

if "processed_hashes" not in st.session_state:
    st.session_state.processed_hashes = set()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "clear_all_flag" not in st.session_state:
    st.session_state.clear_all_flag = False

if "uploader_version" not in st.session_state:
    st.session_state.uploader_version = 0


# --------------------------------------------------
# 4. Custom CSS
# --------------------------------------------------

st.markdown(
    """
    <style>
    .main-content {
        padding: 10px;
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


# --------------------------------------------------
# 5. Sidebar: Document uploads and sources
# --------------------------------------------------

with st.sidebar:

    st.header("Sources")

    uploaded_file = st.file_uploader(
        "Upload Documents",
        type=["pdf", "txt", "docx"],
        accept_multiple_files=False,
        key=f"document_uploader_{st.session_state.uploader_version}",
    )

    # Process a newly uploaded document only once.
    if uploaded_file is not None:

        file_bytes = uploaded_file.getvalue()
        file_hash = hashlib.sha256(file_bytes).hexdigest()

        if file_hash not in st.session_state.processed_hashes:

            with st.spinner(f"Processing {uploaded_file.name}..."):

                try:
                    result = ingest_uploaded_file(uploaded_file)

                    st.session_state.uploaded_files[
                        result["filename"]
                    ] = result

                    st.session_state.processed_hashes.add(file_hash)

                    st.success(
                        f"Successfully indexed {result['filename']}!"
                    )

                    st.caption(
                        f"{result['chunks_added']} chunks added."
                    )

                except Exception as error:
                    st.error(f"Could not process document: {error}")

    st.divider()

    st.write("**Uploaded Documents:**")

    if st.session_state.uploaded_files:

        for filename, details in st.session_state.uploaded_files.items():

            st.write(f"📄 {filename}")

            st.caption(
                f"{details['chunks_added']} indexed chunks"
            )

    else:
        st.info("No uploaded documents yet.")

    st.divider()


# --------------------------------------------------
# 6. Clear uploaded documents
# --------------------------------------------------

    if st.button("Clear All", use_container_width=True):
        st.session_state.clear_all_flag = True

    if st.session_state.clear_all_flag:

        st.warning(
            "Are you sure you want to delete all uploaded documents?"
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "Confirm",
                key="confirm_clear",
                use_container_width=True,
            ):

                try:
                    deleted_chunks = clear_uploaded_documents()

                    st.session_state.uploaded_files.clear()
                    st.session_state.processed_hashes.clear()
                    st.session_state.clear_all_flag = False

                    # Reset the file uploader.
                    st.session_state.uploader_version += 1

                    st.success(
                        f"Deleted {deleted_chunks} uploaded chunks."
                    )

                    st.rerun()

                except Exception as error:
                    st.error(f"Could not clear documents: {error}")

        with col2:
            if st.button(
                "Cancel",
                key="cancel_clear",
                use_container_width=True,
            ):
                st.session_state.clear_all_flag = False
                st.rerun()


# --------------------------------------------------
# 7. Main chatbot interface
# --------------------------------------------------

st.title("MS2B Chatbot")

st.write("Ask questions about your documents.")

if not st.session_state.messages:

    with st.chat_message("assistant"):
        st.write(
            "Hello human – how can i help you? (¬`‸´¬)"
        )


# Display previous messages.
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# --------------------------------------------------
# 8. Chat input connected to LangGraph
# --------------------------------------------------

if prompt := st.chat_input("Ask away..."):

    # Display and save the user's question.
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate an answer using the backend workflow.
    with st.chat_message("assistant"):

        with st.spinner("Searching documents and generating an answer..."):

            try:
                workflow = get_workflow()

                output = workflow.invoke({
                    "question": prompt
                })

                result = output.get("result", {})

                answer_text = result.get(
                    "answer",
                    "I couldn't generate an answer."
                )

                st.markdown(answer_text)

                # Display source information separately.
                citations = result.get("citations", [])

                if citations:

                    with st.expander("View Sources"):
                        for citation in citations:
                            st.write(f"- {citation}")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer_text,
                })

            except Exception as error:

                error_message = (
                    "Something went wrong while generating the answer. "
                    "Please check that Ollama and the backend are running."
                )

                st.error(error_message)
                st.exception(error)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message,
                })