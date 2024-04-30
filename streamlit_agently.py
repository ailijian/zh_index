import queue
import threading
import time

import streamlit as st
import Agently


def agent_chat_generator(agent, message, session_id):
    """agent reply generator"""
    reply_queue = queue.Queue()
    agent.active_session(session_id)

    @agent.on_event("delta")
    def on_delta(data):
        reply_queue.put_nowait(data)

    @agent.on_event("done")
    def on_done(data):
        reply_queue.put_nowait("$STOP")

    agent_thread = threading.Thread(target=agent.input(message).start)
    agent_thread.start()
    while True:
        reply = reply_queue.get()
        if reply == "$STOP":
            break
        for r in list(reply):
            time.sleep(0.02)
            yield r
    agent_thread.join()
    agent.stop_session()


st.title("ChatBot based on Agently")

# instruct \ set_role (k, v) \

required_params = ["current_model", "base_url", "api_key", "session_id", "agent_id", "message_list", "store_agent_list"]
for param in required_params:
    if param not in st.session_state:
        if param.endswith("_list"):
            st.session_state[param] = []
        elif param.endswith("_dict"):
            st.session_state[param] = {}
        else:
            st.session_state[param] = ""

# Display chat history
for message in st.session_state.message_list:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

################
## Sidebar ##
################

with st.sidebar:
    st.title("Settings")
    st.session_state.current_model = st.selectbox("Current Model",
                                                  ["ERNIE", "Kimi", "OpenAI", "Claude3", "Gemini", "Zhipu"])
    st.session_state.base_url = st.text_input("Base URL",
                                              "If ERNIE is selected, this item does not need to be filled in")
    st.session_state.api_key = st.text_input("API Key",
                                             "",
                                             type="password")
    st.session_state.session_id = st.text_input("Session ID",
                                                "sess_1")
    st.session_state.agent_id = st.text_input("Agent ID",
                                              "demo_agent_1")

################
## Main Page ##
################

if prompt := st.chat_input("ask something..."):
    if not st.session_state.api_key:
        st.warning('Please enter API key!', icon='⚠')

    st.session_state.message_list.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        current_model = st.session_state.current_model
        api_key = st.session_state.api_key
        base_url = st.session_state.base_url
        # Get agent
        if current_model == "ERNIE":
            agent_factory = (
                Agently.AgentFactory()
                .set_settings("current_model", current_model)
                .set_settings(f"model.{current_model}.auth", {"aistudio": api_key})
            )
        else:
            agent_factory = (
                Agently.AgentFactory()
                .set_settings("current_model", current_model)
                .set_settings(f"model.{current_model}.auth", {"api_key": api_key})
                .set_settings(f"model.{current_model}.url", base_url)
            )
        agent = agent_factory.create_agent(agent_id=st.session_state.agent_id)
        # Stream agent reply
        response = st.write_stream(agent_chat_generator(agent=agent,
                                                        message=prompt,
                                                        session_id=st.session_state.session_id))
    st.session_state.message_list.append({"role": "assistant", "content": response})
