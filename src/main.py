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
        escaped_new_text = html.escape(guardrail.new_text).replace("\n", " ")

        if role == "user":
            if guardrail.triggered:
                # Original user text is shown, but we add an icon with a tooltip showing guardrail.new_text
                final_display = f"**User**: {escaped_content} "
                if not guardrail.exclude:
                    final_display += f"""
                                <span style="color:red;" title="Guardrail replaced text with: {escaped_new_text}">
                                    &#9888;
                                </span>
                            """
                else:
                    final_display += f"""
                                <span style="color:red;" title="Guardrail: {escaped_new_text}">
                                    &#9888;
                                </span>
                            """
                st.markdown(final_display, unsafe_allow_html=True)
            else:
                st.markdown(f"**User**: {escaped_content}", unsafe_allow_html=True)
        else:
            # role == "assistant"
            if guardrail.triggered:
                # Display guardrail.new_text, but the tooltip reveals original text
                final_display = f"**Assistant**: {escaped_new_text} "
                if not guardrail.exclude:
                    final_display += f"""
                                <span style="color:red;" title="Original text was: {escaped_content}">
                                    &#9888;
                                </span>
                            """
                else:
                    final_display += f"""
                                <span style="color:red;" title="Guardrail: {escaped_new_text}">
                                    &#9888;
                                </span>
                            """
                st.markdown(final_display, unsafe_allow_html=True)
            else:
                st.markdown(f"**Assistant**: {escaped_content}", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
