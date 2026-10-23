"""Streamlit interface for the OJT marketplace complaint project."""

import os

import streamlit as st
from dotenv import load_dotenv

from agents.resolution_agent import ResolutionAgent
from services.orchestrator import ComplaintOrchestrator


load_dotenv()

SAMPLE_COMPLAINTS = [
    "My order was delivered late.",
    "I received a damaged product.",
    "I was charged twice for the same order.",
    "My refund has not arrived.",
]


def _space_secrets():
    """Read Streamlit Community Cloud secrets when deployed; local .env still works."""
    try:
        return dict(st.secrets)
    except (FileNotFoundError, AttributeError):
        return {}


def _make_orchestrator():
    """Build the workflow with settings from env/.env or Streamlit secrets."""
    secrets = _space_secrets()
    api_key = os.getenv("OPENAI_API_KEY") or secrets.get("OPENAI_API_KEY", "")
    model = os.getenv("OPENAI_MODEL") or secrets.get("OPENAI_MODEL", "gpt-4o-mini")
    resolution_agent = ResolutionAgent(api_key=api_key, model=model)
    return ComplaintOrchestrator(resolution_agent=resolution_agent)


def _initialize_session():
    if "complaint_history" not in st.session_state:
        st.session_state.complaint_history = []
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "complaint_input" not in st.session_state:
        st.session_state.complaint_input = ""


def _apply_sample():
    selected = st.session_state.get("sample_choice")
    if selected and selected != "Choose a sample...":
        st.session_state.complaint_input = selected


def main():
    st.set_page_config(
        page_title="Marketplace Complaint Management",
        page_icon="M",
        layout="wide",
    )
    _initialize_session()

    st.markdown(
        """
        <style>
        .stApp { background: #10141c; color: #f7f9fc; }
        [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p {
            color: #ffffff !important;
            background: transparent !important;
        }
        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea {
            color: #ffffff !important;
            background: transparent !important;
        }
        [data-testid="stTextInput"] input::placeholder,
        [data-testid="stTextArea"] textarea::placeholder {
            color: #aab4c2 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Marketplace Customer Complaint Management System")
    st.caption(
        "A simple three-agent workflow that reviews marketplace complaints and suggests a next step. "
        "This prototype does not process real marketplace transactions."
    )

    left, right = st.columns([1, 1], gap="large")
    with left:
        st.subheader("Submit a complaint")
        st.selectbox(
            "Try a sample complaint",
            ["Choose a sample..."] + SAMPLE_COMPLAINTS,
            key="sample_choice",
            on_change=_apply_sample,
        )

        with st.form("complaint_form"):
            customer_name = st.text_input(
                "Customer name (optional)", placeholder="e.g. Alex"
            )
            order_id = st.text_input("Order ID (optional)", placeholder="e.g. ORD-1024")
            complaint_text = st.text_area(
                "Complaint", key="complaint_input", height=140,
                placeholder="Describe what happened in a sentence or two...",
            )
            submitted = st.form_submit_button(
                "Review complaint", type="primary", width="stretch"
            )

        if submitted:
            if not complaint_text.strip():
                st.warning("Please enter a complaint before submitting.")
            else:
                with st.spinner("The three agents are reviewing the complaint..."):
                    result = _make_orchestrator().process(
                        complaint_text.strip(), customer_name.strip(), order_id.strip()
                    )
                st.session_state.last_result = result
                st.session_state.complaint_history.insert(
                    0,
                    {
                        "Complaint ID": result["complaint_id"],
                        "Complaint": result["complaint_text"],
                        "Category": result["category"],
                        "Priority": result["priority"],
                    },
                )

    with right:
        st.subheader("Agent review")
        result = st.session_state.last_result
        if result:
            with st.container(border=True):
                st.markdown("#### Agent 1: Classification")
                st.write(f"**Category:** {result['category']}")
                st.write(f"**Reason:** {result['classification_reason']}")

            with st.container(border=True):
                st.markdown("#### Agent 2: Priority")
                st.write(f"**Priority:** {result['priority']}")
                st.write(f"**Reason:** {result['priority_reason']}")

            with st.container(border=True):
                st.markdown("#### Agent 3: Summary and recommendation")
                st.write(f"**Summary:** {result['summary']}")
                st.write(f"**Recommended resolution:** {result['resolution']}")

            st.caption(
                "Summary note: GPT is used when an API key is configured; otherwise, "
                "the app creates a short local summary."
            )

            with st.container(border=True):
                st.markdown("#### Complaint result")
                st.write(f"**Complaint ID:** {result['complaint_id']}")
                st.write(f"**Category:** {result['category']}  |  **Priority:** {result['priority']}")
                st.write(f"**Summary:** {result['summary']}")
                st.write(f"**Recommended resolution:** {result['resolution']}")
        else:
            st.info("Submit a complaint to see the three agents' results here.")

    st.divider()
    st.subheader("Complaint history for this session")
    clear_col, _ = st.columns([1, 5])
    with clear_col:
        if st.button("Clear history", width="stretch"):
            st.session_state.complaint_history = []
            st.rerun()

    if st.session_state.complaint_history:
        st.dataframe(
            st.session_state.complaint_history,
            hide_index=True,
            width="stretch",
        )
    else:
        st.caption("No complaints have been submitted in this session yet.")


if __name__ == "__main__":
    main()
