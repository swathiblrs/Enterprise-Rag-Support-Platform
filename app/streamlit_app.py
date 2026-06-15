import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000/ask"


st.set_page_config(
    page_title="Enterprise RAG Support Assistant",
    page_icon="🤖",
    layout="wide",
)


st.title("Enterprise RAG Support Assistant")
st.write(
    "Ask an IT support question. The system will retrieve knowledge-base context, "
    "generate an answer, show sources, and recommend ticket routing."
)


question = st.text_area(
    "Enter your support question:",
    placeholder="Example: My VPN is not working after I reset my password",
    height=120,
)


if st.button("Ask Assistant"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Retrieving knowledge and generating answer..."):
            try:
                response = requests.post(
                    API_URL,
                    json={"question": question},
                    timeout=60,
                )

                if response.status_code != 200:
                    st.error(f"API error: {response.status_code}")
                    st.text(response.text)
                else:
                    data = response.json()

                    st.subheader("Answer")
                    st.write(data["answer"])

                    st.subheader("Sources")
                    if data["sources"]:
                        for source in data["sources"]:
                            st.write(f"- {source}")
                    else:
                        st.write("No sources found.")

                    st.subheader("Ticket Recommendation")
                    ticket = data["ticket"]

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Category", ticket["category"])

                    with col2:
                        st.metric("Priority", ticket["priority"])

                    with col3:
                        st.metric("Assigned Team", ticket["assigned_team"])

                    st.write("**Summary:**", ticket["summary"])

                    st.subheader("System Metadata")
                    st.write(f"Fallback Triggered: `{data['fallback_triggered']}`")
                    st.write(f"Latency: `{data['latency_ms']} ms`")

            except requests.exceptions.ConnectionError:
                st.error(
                    "Could not connect to the FastAPI backend. "
                    "Please start it using: uvicorn src.api:app --reload"
                )

            except Exception as error:
                st.error(f"Unexpected error: {error}")