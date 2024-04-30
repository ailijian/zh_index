import os
import streamlit as st
from llama_index.core import Document, SummaryIndex, load_index_from_storage
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings

DEFAULT_TERM_STR = (
    "Make a list of terms and definitions that are defined in the context, "
    "with one pair on each line. "
    "If a term is missing it's definition, use your best judgment. "
    "Write each line as as follows:\nTerm: <term> Definition: <definition>"
)

st.title("🦙 Llama Index Term Extractor 🦙")

setup_tab, upload_tab = st.tabs(["Setup", "Upload/Extract Terms"])

with setup_tab:
    st.subheader("LLM Setup")
    api_key = st.text_input("Enter your OpenAI API key here", type="password")
    llm_name = st.selectbox(
        "Which LLM?", ["text-davinci-003", "gpt-3.5-turbo", "gpt-4"]
    )
    model_temperature = st.slider(
        "LLM Temperature", min_value=0.0, max_value=1.0, step=0.1
    )
    term_extract_str = st.text_area(
        "The query to extract terms and definitions with.",
        value=DEFAULT_TERM_STR,
    )





def get_llm(llm_name, model_temperature, api_key, max_tokens=256):
    os.environ["OPENAI_API_KEY"] = api_key
    return OpenAI(
        temperature=model_temperature, model=llm_name, max_tokens=max_tokens
    )


def extract_terms(
        documents, term_extract_str, llm_name, model_temperature, api_key
):
    llm = get_llm(llm_name, model_temperature, api_key, max_tokens=1024)

    temp_index = SummaryIndex.from_documents(
        documents,
    )
    query_engine = temp_index.as_query_engine(
        response_mode="tree_summarize", llm=llm
    )
    terms_definitions = str(query_engine.query(term_extract_str))
    terms_definitions = [
        x
        for x in terms_definitions.split("\n")
        if x and "Term:" in x and "Definition:" in x
    ]
    # parse the text into a dict
    terms_to_definition = {
        x.split("Definition:")[0]
        .split("Term:")[-1]
        .strip(): x.split("Definition:")[-1]
        .strip()
        for x in terms_definitions
    }
    return terms_to_definition

if "all_terms" not in st.session_state:
    st.session_state["all_terms"] = DEFAULT_TERMS


def insert_terms(terms_to_definition):
    for term, definition in terms_to_definition.items():
        doc = Document(text=f"Term: {term}\nDefinition: {definition}")
        st.session_state["llama_index"].insert(doc)


@st.cache_resource
def initialize_index(llm_name, model_temperature, api_key):
    """Create the VectorStoreIndex object."""
    Settings.llm = get_llm(llm_name, model_temperature, api_key)

    index = VectorStoreIndex([])

    return index, llm

with upload_tab:
    st.subheader("Extract and Query Definitions")
    if st.button("Initialize Index and Reset Terms"):
        st.session_state["llama_index"] = initialize_index(
            llm_name, model_temperature, api_key
        )
        st.session_state["all_terms"] = {}

    if "llama_index" in st.session_state:
        st.markdown(
            "Either upload an image/screenshot of a document, or enter the text manually."
        )
        document_text = st.text_area("Or enter raw text")
        if st.button("Extract Terms and Definitions") and (
            uploaded_file or document_text
        ):
            st.session_state["terms"] = {}
            terms_docs = {}
            with st.spinner("Extracting..."):
                terms_docs.update(
                    extract_terms(
                        [Document(text=document_text)],
                        term_extract_str,
                        llm_name,
                        model_temperature,
                        api_key,
                    )
                )
            st.session_state["terms"].update(terms_docs)

        if "terms" in st.session_state and st.session_state["terms"]:
            st.markdown("Extracted terms")
            st.json(st.session_state["terms"])

            if st.button("Insert terms?"):
                with st.spinner("Inserting terms"):
                    insert_terms(st.session_state["terms"])
                st.session_state["all_terms"].update(st.session_state["terms"])
                st.session_state["terms"] = {}
                st.experimental_rerun()
