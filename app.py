import streamlit as st

from ragbot import rag

st.title("Docs Chatbot")

store = st.cache_resource(rag.get_store)()
if store.count() == 0:
    st.warning("The document index is empty. Run: python -m ragbot.ingest docs")

if "history" not in st.session_state:
    st.session_state.history = []  # list of {"role", "content", "sources"}

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("sources"):
            with st.expander("Sources"):
                st.caption(", ".join(msg["sources"]))

question = st.chat_input("Ask a question about the documents")
if question:
    with st.chat_message("user"):
        st.write(question)
    # The model only needs role and content, not our sources field.
    past = [{"role": m["role"], "content": m["content"]} for m in st.session_state.history]
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            text, sources = rag.answer(question, past, store)
        st.write(text)
        if sources:
            with st.expander("Sources"):
                st.caption(", ".join(sources))
    st.session_state.history.append({"role": "user", "content": question})
    st.session_state.history.append(
        {"role": "assistant", "content": text, "sources": sources}
    )
