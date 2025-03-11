import html
import streamlit as st
from backend import ChatBotBackend

def main():
    st.title("LLM Chat.")

    # Initialize session state objects
    if "chatbot" not in st.session_state:
        st.session_state["chatbot"] = ChatBotBackend()

    # Use a form so pressing Enter also submits
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Your message:")
        submitted = st.form_submit_button("Send")

    # If the user submitted (either by pressing Enter or clicking "Send")
    if submitted:
        text_to_send = user_input.strip()
        if text_to_send:
            st.session_state["chatbot"].generate(text_to_send)

    # Display the conversation from the chatbot
    history = st.session_state["chatbot"].get_conversation_history()

    st.markdown("## Conversation")
    for idx, message in enumerate(history):
        role = message["role"]
        content = message["content"]
        guardrail = message["guardrail"]

        # Escape text so quotes and newlines don’t break our HTML or tooltip
        escaped_content = html.escape(content).replace("\n", " ")
        escaped_rewritten = html.escape(guardrail.rewritten).replace("\n", " ")
        escaped_fallback = html.escape(guardrail.fallback).replace("\n", " ") if guardrail.fallback else None
        escaped_reason = html.escape(guardrail.reason).replace("\n", " ") if guardrail.reason else None

        if role == "user":
            if guardrail.triggered:
                if guardrail.fallback is not None:
                    final_display = f"""
                        <span style="color:red; font-weight:bold;">
                            {escaped_fallback}
                        </span>
                    """
                else:
                    # Original user text is shown, but we add an icon with a tooltip showing guardrail.rewritten
                    final_display = f"**User**: {escaped_content} "
                    final_display += f"""
                                <span style="color:red;" title="Guardrail replaced text with: {escaped_rewritten}. Reason: {escaped_reason}">
                                    &#9888;
                                </span>
                            """
                st.markdown(final_display, unsafe_allow_html=True)
            else:
                st.markdown(f"**User**: {escaped_content}", unsafe_allow_html=True)
        else:
            # role == "assistant"
            if guardrail.triggered:
                if guardrail.fallback is not None:
                    final_display = f"""
                        <span style="color:red; font-weight:bold;">
                            {escaped_fallback}
                        </span>
                    """
                else:
                    # Display guardrail.rewritten, but the tooltip reveals original text
                    final_display = f"**Assistant**: {escaped_rewritten} "
                    final_display += f"""
                                <span style="color:red;" title="Original text was: {escaped_content}. Reason: {escaped_reason}">
                                    &#9888;
                                </span>
                            """
                st.markdown(final_display, unsafe_allow_html=True)
            else:
                st.markdown(f"**Assistant**: {escaped_content}", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
