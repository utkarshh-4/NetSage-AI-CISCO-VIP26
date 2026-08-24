"""NetSage AI - Network Troubleshooting Dashboard."""

import sys
from pathlib import Path

# Add parent directory to Python path to enable imports
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

from data.data_loader import load_cases
from rules.checker import run_all_checks
from ai.diagnose import diagnose_case
from review.review_manager import ReviewManager
from review.schemas import ReviewDecision
from analytics.metrics import (
    calculate_total_cases,
    calculate_cases_by_issue_type,
    calculate_cases_by_severity,
    calculate_ai_review_distribution,
    calculate_ai_agreement_rate,
    calculate_corrected_diagnoses,
    calculate_insufficient_evidence_cases,
    calculate_osi_layer_distribution,
    calculate_rule_checker_findings,
    get_ai_vs_human_comparison
)
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="NetSage AI",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
def init_session_state():
    """Initialize Streamlit session state variables."""
    if "cases_df" not in st.session_state:
        try:
            st.session_state.cases_df = load_cases()
        except Exception as e:
            st.error(f"Error loading cases: {e}")
            st.session_state.cases_df = pd.DataFrame()
    
    if "selected_case" not in st.session_state:
        st.session_state.selected_case = None
    
    if "rule_results" not in st.session_state:
        st.session_state.rule_results = None
    
    if "ai_diagnosis" not in st.session_state:
        st.session_state.ai_diagnosis = None
    
    if "ai_diagnosis_error" not in st.session_state:
        st.session_state.ai_diagnosis_error = None
    
    if "review_decision" not in st.session_state:
        st.session_state.review_decision = None
    
    if "review_notes" not in st.session_state:
        st.session_state.review_notes = ""
    
    if "review_reason" not in st.session_state:
        st.session_state.review_reason = ""
    
    if "corrected_diagnosis" not in st.session_state:
        st.session_state.corrected_diagnosis = None
    
    if "verification_status" not in st.session_state:
        st.session_state.verification_status = "NOT_YET_TESTED"
    
    if "verification_notes" not in st.session_state:
        st.session_state.verification_notes = ""
    
    if "developer_mode" not in st.session_state:
        st.session_state.developer_mode = False
    
    if "review_manager" not in st.session_state:
        st.session_state.review_manager = ReviewManager()
    
    if "case_ready" not in st.session_state:
        st.session_state.case_ready = False

# Initialize session state
init_session_state()

# Sidebar
st.sidebar.title("NetSage AI")
st.sidebar.markdown("Network Troubleshooting Assistant")

# Developer mode toggle
st.sidebar.checkbox(
    "Developer/Evaluator Mode",
    value=st.session_state.developer_mode,
    key="developer_mode_toggle",
    help="Show expected fault and additional debugging information"
)
st.session_state.developer_mode = st.session_state.developer_mode_toggle

# Navigation
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigate",
    ["Case Selection", "Rule Checks", "AI Diagnosis", "Human Review", "Verification", "Responsible AI", "Analytics Dashboard"]
)

# Helper functions
def display_case_info(case: Dict[str, str]):
    """Display case information."""
    st.subheader("Case Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Case ID:** {case['case_id']}")
        st.markdown(f"**Symptom:** {case['symptom']}")
    
    with col2:
        st.markdown(f"**OSI Layer:** {case['osi_layer']}")
        st.markdown(f"**Severity:** {case['severity']}")
    
    st.markdown(f"**Topology Note:**")
    st.info(case['topology_note'])
    
    st.markdown(f"**Show Command Evidence:**")
    st.info(case['show_outputs'])
    
    if st.session_state.developer_mode:
        st.markdown(f"**Expected Fault:**")
        st.warning(case['expected_fault'])
        st.markdown(f"**Concept Tag:** {case['concept_tag']}")

def display_rule_results(results):
    """Display rule checker results."""
    st.subheader("Deterministic Rule Check Results")
    
    detected = []
    not_detected = []
    insufficient = []
    
    for result in results:
        if result.status == "DETECTED":
            detected.append(result)
        elif result.status == "NOT_DETECTED":
            not_detected.append(result)
        else:
            insufficient.append(result)
    
    # Detected
    if detected:
        st.markdown("### 🔴 Detected Problems")
        for result in detected:
            with st.expander(f"{result.check_name.replace('_', ' ').title()}", expanded=True):
                st.markdown(f"**Status:** {result.status}")
                st.markdown(f"**Severity:** {result.severity}")
                st.markdown(f"**Message:** {result.message}")
                if result.evidence:
                    st.markdown("**Evidence:**")
                    for ev in result.evidence:
                        st.markdown(f"- {ev}")
    
    # Not Detected
    if not_detected:
        st.markdown("### ✅ No Issues Detected")
        for result in not_detected:
            with st.expander(f"{result.check_name.replace('_', ' ').title()}"):
                st.markdown(f"**Status:** {result.status}")
                st.markdown(f"**Message:** {result.message}")
    
    # Insufficient Evidence
    if insufficient:
        st.markdown("### ⚠️ Insufficient Evidence")
        for result in insufficient:
            with st.expander(f"{result.check_name.replace('_', ' ').title()}"):
                st.markdown(f"**Status:** {result.status}")
                st.markdown(f"**Message:** {result.message}")

def display_ai_diagnosis(diagnosis: Dict[str, Any]):
    """Display AI diagnosis results."""
    st.subheader("AI Diagnosis")
    
    # Root Cause
    st.markdown("### Root Cause")
    st.success(diagnosis.get('root_cause', 'Not provided'))
    
    # Metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Confidence", diagnosis.get('confidence', 'N/A'))
    with col2:
        st.metric("OSI Layer", diagnosis.get('osi_layer', 'N/A'))
    with col3:
        st.metric("Issue Type", diagnosis.get('issue_type', 'N/A'))
    
    # Evidence
    st.markdown("### Evidence")
    evidence_list = diagnosis.get('evidence', [])
    if evidence_list:
        for i, ev in enumerate(evidence_list, 1):
            st.markdown(f"{i}. **Source:** {ev.get('source', 'N/A')}")
            st.markdown(f"   **Content:** {ev.get('content', 'N/A')}")
            st.markdown(f"   **Type:** {ev.get('type', 'N/A')}")
            st.markdown("---")
    else:
        st.info("No evidence provided")
    
    # Next Command
    next_cmd = diagnosis.get('next_command')
    if next_cmd:
        st.markdown("### Next Diagnostic Command")
        st.code(next_cmd, language='bash')
    
    # Fix Steps
    fix_steps = diagnosis.get('fix_steps', [])
    if fix_steps:
        st.markdown("### Recommended Fix Steps")
        for i, step in enumerate(fix_steps, 1):
            with st.expander(f"Step {i}: {step.get('command', 'N/A')}", expanded=False):
                st.markdown(f"**Explanation:** {step.get('explanation', 'N/A')}")
                if step.get('verification'):
                    st.markdown(f"**Verification:** {step.get('verification')}")
    
    # Alternative Causes
    alt_causes = diagnosis.get('alternative_causes', [])
    if alt_causes:
        st.markdown("### Alternative Possible Causes")
        for i, cause in enumerate(alt_causes, 1):
            st.markdown(f"{i}. **Description:** {cause.get('description', 'N/A')}")
            st.markdown(f"   **Likelihood:** {cause.get('likelihood', 'N/A')}")
            if cause.get('evidence'):
                st.markdown(f"   **Evidence:** {', '.join(cause['evidence'])}")
    
    # Limitations
    limitations = diagnosis.get('limitations', [])
    if limitations:
        st.markdown("### Limitations")
        for lim in limitations:
            st.markdown(f"- {lim}")
    
    # Notes
    if diagnosis.get('notes'):
        st.markdown("### Additional Notes")
        st.info(diagnosis['notes'])

# Page 1: Case Selection
if page == "Case Selection":
    st.title("📋 Case Selection")
    st.markdown("Select a network troubleshooting case to analyze.")
    
    if st.session_state.cases_df.empty:
        st.error("No cases available. Please check cases.csv file.")
    else:
        # Case selector
        case_options = st.session_state.cases_df['case_id'].tolist()
        selected_id = st.selectbox("Select a Case", case_options)
        
        if selected_id:
            case_row = st.session_state.cases_df[st.session_state.cases_df['case_id'] == selected_id].iloc[0]
            st.session_state.selected_case = case_row.to_dict()
            
            display_case_info(st.session_state.selected_case)
            
            # Reset downstream state when case changes
            if st.button("🔍 Analyze This Case", type="primary"):
                st.session_state.rule_results = None
                st.session_state.ai_diagnosis = None
                st.session_state.ai_diagnosis_error = None
                st.session_state.review_decision = None
                st.session_state.review_notes = ""
                st.session_state.review_reason = ""
                st.session_state.corrected_diagnosis = None
                st.session_state.verification_status = "NOT_YET_TESTED"
                st.session_state.verification_notes = ""
                st.session_state.case_ready = True
                st.success(f"✅ Case **{selected_id}** selected! Use the sidebar to navigate through the analysis steps.")
                st.info("👉 **Next step:** Go to **Rule Checks** in the sidebar to run deterministic analysis, then **AI Diagnosis** for AI-powered root cause analysis.")
            
            if st.session_state.get("case_ready"):
                st.success(f"✅ Case **{st.session_state.selected_case.get('case_id')}** is ready for analysis.")
                st.info("👉 Use the sidebar to navigate: **Rule Checks** → **AI Diagnosis** → **Human Review**")

# Page 2: Rule Checks
elif page == "Rule Checks":
    st.title("🔍 Rule Checks")
    st.markdown("Deterministic rule checker results.")
    
    if not st.session_state.selected_case:
        st.warning("Please select a case from the Case Selection page first.")
        st.page_link("Case Selection", label="Go to Case Selection")
    else:
        if st.button("Run Rule Checks") or st.session_state.rule_results is None:
            with st.spinner("Running deterministic rule checks..."):
                st.session_state.rule_results = run_all_checks(st.session_state.selected_case)
        
        if st.session_state.rule_results:
            display_rule_results(st.session_state.rule_results)
        else:
            st.info("No rule results available.")

# Page 3: AI Diagnosis
elif page == "AI Diagnosis":
    st.title("🤖 AI Diagnosis")
    st.markdown("AI-powered network troubleshooting diagnosis.")
    
    if not st.session_state.selected_case:
        st.warning("Please select a case from the Case Selection page first.")
        st.page_link("Case Selection", label="Go to Case Selection")
    else:
        # Check for API key
        import os
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.warning("OpenAI API key not found. AI diagnosis will not be available.")
            st.info("Set OPENAI_API_KEY environment variable to enable AI diagnosis.")
            st.info("The application will remain functional for rule-based analysis.")
        
        if st.button("Run AI Diagnosis"):
            with st.spinner("Running AI diagnosis..."):
                try:
                    # Convert rule results to dict format
                    rule_results_dict = None
                    if st.session_state.rule_results:
                        rule_results_dict = {
                            r.check_name: r.to_dict()
                            for r in st.session_state.rule_results
                        }
                    
                    result = diagnose_case(
                        st.session_state.selected_case,
                        rule_results=rule_results_dict
                    )
                    
                    if hasattr(result, 'root_cause'):
                        st.session_state.ai_diagnosis = result.model_dump()
                        st.session_state.ai_diagnosis_error = None
                        st.success("AI diagnosis completed successfully!")
                    else:
                        st.session_state.ai_diagnosis_error = result.model_dump()
                        st.session_state.ai_diagnosis = None
                        st.error(f"AI diagnosis failed: {result.message}")
                except Exception as e:
                    st.session_state.ai_diagnosis_error = str(e)
                    st.session_state.ai_diagnosis = None
                    st.error(f"Error running AI diagnosis: {e}")
        
        if st.session_state.ai_diagnosis:
            display_ai_diagnosis(st.session_state.ai_diagnosis)
        elif st.session_state.ai_diagnosis_error:
            st.error("AI diagnosis failed. The application remains functional for rule-based analysis.")
            with st.expander("Error Details", expanded=False):
                st.json(st.session_state.ai_diagnosis_error)
        else:
            st.info("Click 'Run AI Diagnosis' to generate an AI diagnosis.")

# Page 4: Human Review
elif page == "Human Review":
    st.title("👥 Human Review")
    st.markdown("Review and approve, edit, or reject the AI diagnosis.")
    
    if not st.session_state.ai_diagnosis:
        st.warning("Please run AI diagnosis first.")
        st.page_link("AI Diagnosis", label="Go to AI Diagnosis")
    else:
        st.subheader("Original AI Diagnosis")
        with st.expander("View Original AI Diagnosis", expanded=False):
            st.json(st.session_state.ai_diagnosis)
        
        st.markdown("---")
        st.subheader("Review Decision")
        
        decision = st.radio(
            "Select Review Decision",
            ["ACCEPT", "EDIT", "REJECT"],
            help="ACCEPT: AI diagnosis is correct\nEDIT: AI needs correction\nREJECT: AI is incorrect"
        )
        
        if decision == "EDIT":
            st.markdown("### Corrected Diagnosis")
            corrected_json = st.text_area(
                "Enter corrected diagnosis (JSON format)",
                value=json.dumps(st.session_state.ai_diagnosis, indent=2),
                height=300,
                help="Modify the JSON to correct the AI diagnosis"
            )
            try:
                corrected_diagnosis = json.loads(corrected_json)
                st.session_state.corrected_diagnosis = corrected_diagnosis
            except json.JSONDecodeError:
                st.error("Invalid JSON format")
                st.session_state.corrected_diagnosis = None
        
        reviewer_notes = st.text_area(
            "Reviewer Notes",
            value=st.session_state.review_notes,
            help="Add any notes about this review"
        )
        
        reason_for_correction = st.text_area(
            "Reason for Correction/Rejection",
            value=st.session_state.review_reason,
            help="Explain why you are correcting or rejecting the AI diagnosis"
        )
        
        if st.button("Save Review"):
            try:
                review_manager = st.session_state.review_manager
                
                # Convert string enum to enum
                decision_enum = ReviewDecision(decision)
                
                review_manager.create_review(
                    case_id=st.session_state.selected_case['case_id'],
                    ai_diagnosis=st.session_state.ai_diagnosis,
                    reviewer_decision=decision_enum,
                    corrected_diagnosis=st.session_state.corrected_diagnosis,
                    reviewer_notes=reviewer_notes,
                    reason_for_correction=reason_for_correction
                )
                
                st.session_state.review_decision = decision
                st.session_state.review_notes = reviewer_notes
                st.session_state.review_reason = reason_for_correction
                
                st.success("Review saved successfully!")
            except Exception as e:
                st.error(f"Error saving review: {e}")

# Page 5: Verification
elif page == "Verification":
    st.title("✅ Verification")
    st.markdown("Record whether the fix was verified in Packet Tracer.")
    
    if not st.session_state.selected_case:
        st.warning("Please select a case first.")
        st.page_link("Case Selection", label="Go to Case Selection")
    else:
        st.subheader(f"Verification for Case: {st.session_state.selected_case['case_id']}")
        
        verification_status = st.radio(
            "Verification Status",
            ["NOT_YET_TESTED", "VERIFIED", "NOT_VERIFIED"],
            index=0,
            help="Record whether the fix was tested in Packet Tracer"
        )
        
        verification_notes = st.text_area(
            "Verification Notes",
            value=st.session_state.verification_notes,
            help="Describe the verification process and results"
        )
        
        if st.button("Save Verification"):
            st.session_state.verification_status = verification_status
            st.session_state.verification_notes = verification_notes
            st.success("Verification status saved!")
        
        st.info("Note: This is a local record. Actual verification must be performed manually in Packet Tracer.")

# Page 6: Responsible AI
elif page == "Responsible AI":
    st.title("🛡️ Responsible AI")
    st.markdown("Review AI performance and human agreement statistics.")
    
    review_manager = st.session_state.review_manager
    summary = review_manager.get_summary()
    
    # Summary Statistics
    st.subheader("Review Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Reviews", summary.total_reviews)
    with col2:
        st.metric("Accepted", summary.accepted_count)
    with col3:
        st.metric("Edited", summary.edited_count)
    with col4:
        st.metric("Rejected", summary.rejected_count)
    
    st.markdown(f"**AI-Human Agreement Rate:** {summary.agreement_rate:.1%}")
    
    # Corrected Cases
    if summary.corrected_cases:
        st.markdown("---")
        st.subheader("Corrected AI Cases")
        st.markdown("Cases where the AI diagnosis was corrected by a human reviewer:")
        
        for case_id in summary.corrected_cases:
            review = review_manager.get_review(case_id)
            if review:
                with st.expander(f"Case {case_id}", expanded=False):
                    st.markdown(f"**Reviewer Decision:** {review.reviewer_decision.value}")
                    st.markdown(f"**Reason for Correction:** {review.reason_for_correction or 'Not provided'}")
                    st.markdown(f"**Reviewer Notes:** {review.reviewer_notes or 'Not provided'}")
                    
                    if review.corrected_diagnosis:
                        st.markdown("**Corrected Diagnosis:**")
                        st.json(review.corrected_diagnosis)
    else:
        st.info("No corrected cases recorded yet.")
    
    # All Reviews
    st.markdown("---")
    st.subheader("All Reviews")
    
    all_reviews = review_manager.get_all_reviews()
    if all_reviews:
        for review in all_reviews:
            with st.expander(f"Case {review.case_id} - {review.reviewer_decision.value}", expanded=False):
                st.markdown(f"**Timestamp:** {review.timestamp}")
                st.markdown(f"**AI-Human Agreed:** {'Yes' if review.ai_human_agreed else 'No'}")
                st.markdown(f"**Reviewer Notes:** {review.reviewer_notes or 'Not provided'}")
                if review.reason_for_correction:
                    st.markdown(f"**Reason:** {review.reason_for_correction}")
    else:
        st.info("No reviews recorded yet.")

# Page 7: Analytics Dashboard
elif page == "Analytics Dashboard":
    st.title("📊 Analytics Dashboard")
    st.markdown("Comprehensive analytics for NetSage AI performance and case analysis.")
    
    # Load analytics data
    try:
        with st.spinner("Loading analytics data..."):
            total_cases = calculate_total_cases()
            cases_by_issue_type = calculate_cases_by_issue_type()
            cases_by_severity = calculate_cases_by_severity()
            ai_review_distribution = calculate_ai_review_distribution()
            ai_agreement_rate = calculate_ai_agreement_rate()
            corrected_diagnoses = calculate_corrected_diagnoses()
            insufficient_evidence_cases = calculate_insufficient_evidence_cases()
            osi_layer_distribution = calculate_osi_layer_distribution()
            rule_checker_findings = calculate_rule_checker_findings()
            ai_vs_human_comparison = get_ai_vs_human_comparison()
    except Exception as e:
        st.error(f"Error loading analytics data: {e}")
        st.info("Please ensure data files are available and properly formatted.")
        st.stop()
    
    # Key Metrics Overview
    st.subheader("Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Cases", total_cases)
    with col2:
        st.metric("AI Agreement Rate", f"{ai_agreement_rate:.1f}%")
    with col3:
        st.metric("Corrected Diagnoses", corrected_diagnoses)
    with col4:
        st.metric("Insufficient Evidence", insufficient_evidence_cases)
    
    st.markdown("---")
    
    # Case Distribution Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Cases by Issue Type")
        if cases_by_issue_type:
            fig_issue = px.bar(
                x=list(cases_by_issue_type.keys()),
                y=list(cases_by_issue_type.values()),
                title="Distribution by Issue Type",
                labels={"x": "Issue Type", "y": "Count"},
                color=list(cases_by_issue_type.values())
            )
            st.plotly_chart(fig_issue, use_container_width=True)
        else:
            st.info("No issue type data available.")
    
    with col2:
        st.subheader("Cases by Severity")
        if cases_by_severity:
            fig_severity = px.pie(
                values=list(cases_by_severity.values()),
                names=list(cases_by_severity.keys()),
                title="Distribution by Severity",
                color_discrete_map={"High": "red", "Medium": "yellow", "Low": "green"}
            )
            st.plotly_chart(fig_severity, use_container_width=True)
        else:
            st.info("No severity data available.")
    
    st.markdown("---")
    
    # AI Performance Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("AI Review Distribution")
        if ai_review_distribution:
            fig_review = px.bar(
                x=list(ai_review_distribution.keys()),
                y=list(ai_review_distribution.values()),
                title="AI Diagnosis Reviews",
                labels={"x": "Decision", "y": "Count"},
                color=list(ai_review_distribution.keys()),
                color_discrete_map={"ACCEPT": "green", "EDIT": "yellow", "REJECT": "red"}
            )
            st.plotly_chart(fig_review, use_container_width=True)
        else:
            st.info("No review data available.")
    
    with col2:
        st.subheader("OSI Layer Distribution")
        if osi_layer_distribution:
            fig_osi = px.bar(
                x=list(osi_layer_distribution.keys()),
                y=list(osi_layer_distribution.values()),
                title="Distribution by OSI Layer",
                labels={"x": "OSI Layer", "y": "Count"}
            )
            st.plotly_chart(fig_osi, use_container_width=True)
        else:
            st.info("No OSI layer data available.")
    
    st.markdown("---")
    
    # Rule Checker Findings
    st.subheader("Rule Checker Findings")
    if rule_checker_findings:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Problems Detected", rule_checker_findings['detected'])
        with col2:
            st.metric("No Issues Detected", rule_checker_findings['not_detected'])
        with col3:
            st.metric("Insufficient Evidence", rule_checker_findings['insufficient'])
        
        fig_rules = px.bar(
            x=list(rule_checker_findings.keys()),
            y=list(rule_checker_findings.values()),
            title="Rule Checker Results Summary",
            labels={"x": "Result Type", "y": "Count"},
            color=list(rule_checker_findings.keys()),
            color_discrete_map={
                "detected": "red",
                "not_detected": "green",
                "insufficient": "yellow"
            }
        )
        st.plotly_chart(fig_rules, use_container_width=True)
    else:
        st.info("No rule checker data available.")
    
    st.markdown("---")
    
    # AI vs Human Comparison Table
    st.subheader("AI vs Human Comparison")
    if ai_vs_human_comparison:
        comparison_df = pd.DataFrame(ai_vs_human_comparison)
        st.dataframe(
            comparison_df,
            column_config={
                "case_id": "Case ID",
                "ai_diagnosis": "AI Prediction",
                "human_decision": "Human Decision",
                "corrected_diagnosis": "Corrected Diagnosis",
                "agreement_status": "Agreement Status",
                "timestamp": "Review Timestamp"
            },
            use_container_width=True
        )
        
        # Agreement rate explanation
        st.info("""
        **Agreement Rate Definition:** The percentage of cases where human reviewers ACCEPTED the AI diagnosis.
        - ACCEPT cases count as agreement
        - EDIT and REJECT cases count as disagreement
        - Rate = (Accepted / Total Reviews) × 100
        """)
    else:
        st.info("No AI vs human comparison data available. Reviews need to be completed first.")
    
    st.markdown("---")
    
    # Data Sources and Notes
    st.subheader("Data Sources & Methodology")
    st.markdown("""
    **Data Sources:**
    - Case data: Loaded from `cases.csv`
    - Review data: Human review results from review manager
    - Rule checker results: Deterministic rule analysis
    
    **Key Distinctions:**
    - **AI Prediction:** Initial diagnosis generated by the AI system
    - **Human-Reviewed Result:** Final decision after human review (ACCEPT/EDIT/REJECT)
    - **Final Diagnosis:** The accepted diagnosis (either AI or human-corrected)
    
    **Metric Definitions:**
    - **Agreement Rate:** Percentage of AI diagnoses accepted by human reviewers
    - **Corrected Diagnoses:** Total number of EDIT + REJECT decisions
    - **Insufficient Evidence:** Cases where rule checks cannot determine status
    """)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.markdown("NetSage AI is a network troubleshooting assistant that combines deterministic rule checking with AI-powered diagnosis, with mandatory human review for responsible AI deployment.")
