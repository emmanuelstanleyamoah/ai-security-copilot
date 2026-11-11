from __future__ import annotations

import os

import requests
import streamlit as st

DEFAULT_ALERT = (
    "Mailbox alert: invoice attachment from a new sender domain. "
    "User reported a phishing message and a mailbox rule was created afterward."
)

st.set_page_config(page_title="Security Copilot", page_icon="🛡️", layout="wide")
st.title("AI Security Detection & Response Copilot")
st.caption("Local investigation graph. Alerts are untrusted content. Recommendations cite the knowledge base.")

api_url = os.environ.get("COPILOT_API_URL", "").rstrip("/")
alert = st.text_area("Alert", value=DEFAULT_ALERT, height=160)

if st.button("Investigate", type="primary"):
    if api_url:
        response = requests.post(f"{api_url}/investigate", json={"alert": alert}, timeout=30)
        response.raise_for_status()
        report = response.json()
    else:
        from agents.graph import run_investigation

        report = run_investigation(alert).as_dict()

    st.subheader(f"{report['status']} · {report['severity']}")
    if report["technique_ids"]:
        st.write("Techniques: " + ", ".join(report["technique_ids"]))
    st.markdown(report["narrative"])

    left, right = st.columns(2)
    with left:
        st.markdown("**Containment for analyst review**")
        for action in report["remediation"]:
            st.write(f"- {action}")
    with right:
        st.markdown("**Audit trail**")
        for step in report["steps"]:
            evidence = ", ".join(str(item) for item in step["evidence"])
            st.write(f"- {step['agent']}: {step['summary']} ({evidence})")

    if report["citations"]:
        st.markdown("**Citations**")
        for hit in report["citations"]:
            st.write(f"- {hit['title']} (`{hit['source']}`, score {hit['score']})")
    if report["detection_draft"]:
        st.markdown("**Draft detection**")
        st.code(report["detection_draft"], language="yaml")
