import os
from typing import Any, Dict, List

import requests
import streamlit as st


BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_PREFIX = "/api"


def _post_generate_database(request_text: str, rows: int) -> Dict[str, Any]:
    url = f"{BACKEND_URL}{API_PREFIX}/generate-database"
    resp = requests.post(url, json={"request": request_text, "rows": rows})
    resp.raise_for_status()
    return resp.json()


def _post_query(question: str) -> Dict[str, Any]:
    url = f"{BACKEND_URL}{API_PREFIX}/query"
    resp = requests.post(url, json={"question": question})
    resp.raise_for_status()
    return resp.json()


def _get_er_diagram() -> bytes:
    url = f"{BACKEND_URL}{API_PREFIX}/er-diagram"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.content


def _get_download_db() -> bytes:
    url = f"{BACKEND_URL}{API_PREFIX}/download-db"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.content


def main() -> None:
    st.set_page_config(
        page_title="AI Database Generator & Conversational Analyst",
        layout="wide",
    )

    st.title("AI Database Generator and Conversational Data Analyst")
    st.caption("Create databases from natural language and query them conversationally.")

    tab_gen, tab_query, tab_schema = st.tabs(
        ["🧱 Generate Database", "💬 Query Database", "📊 Schema & Export"]
    )

    with tab_gen:
        st.subheader("Natural Language → Database Generator")
        default_prompt = (
            "Create a database of 100 rows for hotels in Goa with columns "
            "hotel_name, rating, seasonal_price, rooms_available, guest_capacity."
        )
        request_text = st.text_area(
            "Describe the database you want to generate:",
            value=default_prompt,
            height=150,
        )
        rows = st.number_input(
            "Number of rows to generate (primary table):", min_value=1, max_value=10000, value=100
        )

        if st.button("Generate Database", type="primary"):
            if not request_text.strip():
                st.warning("Please enter a description.")
            else:
                with st.spinner("Generating schema, creating tables, and populating data..."):
                    try:
                        result = _post_generate_database(request_text, int(rows))
                        st.success("Database generated successfully.")
                        st.json(result.get("schema", {}))
                    except Exception as e:
                        st.error(f"Failed to generate database: {e}")

    with tab_query:
        st.subheader("Conversational Text-to-SQL Agent")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history: List[Dict[str, Any]] = []

        for msg in st.session_state.chat_history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                st.chat_message("user").markdown(content)
            else:
                st.chat_message("assistant").markdown(content)

        user_input = st.chat_input("Ask a question about your generated database...")
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            try:
                with st.spinner("Thinking and generating SQL..."):
                    resp = _post_query(user_input)
                sql = resp.get("sql_query")
                explanation = resp.get("explanation")
                rows = resp.get("rows", [])
                columns = resp.get("columns", [])

                answer_md = f"**SQL Query:**\n```sql\n{sql}\n```\n\n"
                answer_md += f"**Explanation:** {explanation}\n\n"
                if rows:
                    answer_md += "**Result preview:**"
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": answer_md}
                )

                st.chat_message("assistant").markdown(answer_md)
                if rows:
                    st.dataframe(rows)
            except Exception as e:
                error_msg = f"Error running query: {e}"
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": error_msg}
                )
                st.chat_message("assistant").markdown(error_msg)

    with tab_schema:
        st.subheader("Schema Visualization & Download")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**ER Diagram**")
            if st.button("Refresh ER Diagram"):
                try:
                    img_bytes = _get_er_diagram()
                    st.image(img_bytes, caption="Current database ER diagram")
                except Exception as e:
                    st.error(f"Could not load ER diagram: {e}")

        with col2:
            st.markdown("**Download Dataset**")
            if st.button("Download Primary Table as CSV"):
                try:
                    csv_bytes = _get_download_db()
                    st.download_button(
                        label="Download CSV",
                        data=csv_bytes,
                        file_name="dataset.csv",
                        mime="text/csv",
                    )
                except Exception as e:
                    st.error(f"Could not download dataset: {e}")


if __name__ == "__main__":
    main()

