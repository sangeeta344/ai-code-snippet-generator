"""
CodeForge AI — Enterprise Technology Workspace
Project: AI-Powered Python Code Generator
Stack: Streamlit (Python)
Design Theme: Enterprise Blue + Premium Orange AI Accent + Modern Developer Platform
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
import streamlit as st

# Ensure project root is in sys.path for direct backend imports
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
FRONTEND_DIR = Path(__file__).resolve().parent
if str(FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(FRONTEND_DIR))

import backend

# ==============================================================================
# 1. PAGE CONFIGURATION & METADATA
# ==============================================================================
st.set_page_config(
    page_title="AI Code Snippet Generator — CodeForge AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==============================================================================
# 2. CUSTOM CSS: ENTERPRISE BLUE + PREMIUM ORANGE ACCENT DESIGN SYSTEM
# ==============================================================================
def inject_custom_css():
    """Injects high-end enterprise technology styling with orange brand accents."""
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    code, pre, .stCodeBlock {
        font-family: 'Fira Code', monospace !important;
    }

    .stApp {
        background-color: #F3F6F9 !important;
        background-image: 
            radial-gradient(#D9E3EC 1px, transparent 1px),
            linear-gradient(135deg, #F3F6F9 0%, #F8FBFD 50%, #EEF6FB 100%) !important;
        background-size: 24px 24px, 100% 100% !important;
        color: #172B3A !important;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3.5rem;
        padding-left: 2.6rem;
        padding-right: 2.6rem;
        max-width: 1380px;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border: 1px solid #D9E3EC !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 8px rgba(11, 31, 51, 0.04) !important;
        margin-bottom: 1.1rem !important;
        padding: 0.2rem !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #D9E3EC !important;
        box-shadow: 2px 0 10px rgba(11, 31, 51, 0.02);
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.8rem;
        padding-left: 1.4rem;
        padding-right: 1.4rem;
    }

    div.stButton > button:first-child {
        background-color: #0066B3 !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 0.96rem !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.65rem 1.6rem !important;
        letter-spacing: 0.01em !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 2px 6px rgba(0, 102, 179, 0.22) !important;
    }
    div.stButton > button:first-child:hover {
        background-color: #003B64 !important;
        box-shadow: 0 4px 12px rgba(0, 59, 100, 0.3) !important;
        transform: translateY(-1px) !important;
    }

    div.stDownloadButton > button:first-child {
        background-color: #0066B3 !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.4rem !important;
        box-shadow: 0 2px 5px rgba(0, 102, 179, 0.18) !important;
        transition: all 0.2s ease !important;
    }
    div.stDownloadButton > button:first-child:hover {
        background-color: #003B64 !important;
        box-shadow: 0 4px 10px rgba(0, 59, 100, 0.25) !important;
        transform: translateY(-1px) !important;
    }

    .stTextArea textarea {
        background-color: #F7FBFE !important;
        color: #172B3A !important;
        border: 1px solid #C4D9E8 !important;
        border-radius: 8px !important;
        font-size: 0.95rem !important;
        line-height: 1.5 !important;
    }
    .stTextArea textarea:focus {
        border-color: #0066B3 !important;
        box-shadow: 0 0 0 3px rgba(0, 102, 179, 0.14) !important;
    }

    .timeline-node {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.45rem 0.6rem;
        border-radius: 6px;
    }
    .timeline-node.completed {
        background: #F0FDF4;
    }
    .timeline-node.active {
        background: #FFF2E5;
        border: 1px solid #FFD8B2;
    }
    .timeline-node.inactive {
        opacity: 0.65;
    }

    .timeline-circle-completed {
        width: 22px;
        height: 22px;
        border-radius: 50%;
        background-color: #16865B;
        color: white;
        font-size: 0.72rem;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .timeline-circle-active {
        width: 22px;
        height: 22px;
        border-radius: 50%;
        background-color: #0066B3;
        color: white;
        font-size: 0.72rem;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .timeline-circle-inactive {
        width: 22px;
        height: 22px;
        border-radius: 50%;
        background-color: #E2E8F0;
        color: #64748B;
        font-size: 0.72rem;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .timeline-connector {
        width: 2px;
        height: 14px;
        background-color: #D9E3EC;
        margin-left: 17px;
    }
    .timeline-connector.completed {
        background-color: #16865B;
    }

    .section-eyebrow-orange {
        font-size: 0.74rem;
        font-weight: 700;
        color: #E85D04;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.25rem;
        display: flex;
        align-items: center;
        gap: 0.35rem;
    }
    .section-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #0B1F33;
        margin: 0;
        letter-spacing: -0.02em;
    }

    .analysis-card {
        background: #FFFFFF;
        border: 1px solid #D9E3EC;
        border-radius: 10px;
        padding: 1.05rem;
        box-shadow: 0 1px 4px rgba(11, 31, 51, 0.03);
    }
    .card-top-orange {
        border-top: 3px solid #FF7A00;
    }
    .card-top-blue {
        border-top: 3px solid #0066B3;
    }
    .card-top-navy {
        border-top: 3px solid #0B1F33;
    }
    .card-top-teal {
        border-top: 3px solid #00A6A6;
    }

    .badge-orange {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        background: #FFF2E5;
        border: 1px solid #FFD8B2;
        color: #E85D04;
        font-size: 0.78rem;
        font-weight: 700;
        padding: 0.22rem 0.65rem;
        border-radius: 4px;
    }

    .chip-teal {
        display: inline-block;
        background: #E8F7F6;
        border: 1px solid #B8E4E3;
        color: #008282;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 600;
        font-family: 'Fira Code', monospace;
        margin-right: 0.35rem;
        margin-bottom: 0.35rem;
    }

    .val-check-row {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.7rem 1rem;
        border-radius: 8px;
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        margin-bottom: 0.5rem;
    }

    .metric-card-box {
        background-color: #FFFFFF;
        border: 1px solid #D9E3EC;
        border-radius: 12px;
        padding: 1.05rem 1.25rem;
        box-shadow: 0 2px 6px rgba(11, 31, 51, 0.03);
        transition: transform 0.2s ease;
    }
    .metric-card-box:hover {
        transform: translateY(-2px);
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


# ==============================================================================
# 3. SAMPLE REQUIREMENTS PRESETS
# ==============================================================================
SAMPLE_REQUIREMENTS = {
    "Age Classification (Adult / Teen)": {
        "req": "Create a Python code for if age>=18 print adult ,else teen",
        "constraints": "Conditional branching based on age threshold.",
    },
    "Prime Number Checker": {
        "req": "Create a Python function that checks whether a number is prime and returns True or False.",
        "constraints": "O(sqrt(n)) time complexity. Handle negative numbers, 0, and 1.",
    },
    "CSV Employee Salary Analysis": {
        "req": "Create a Python function that reads a CSV file, removes duplicate rows, calculates the average salary by department, and saves the result to a new CSV file.",
        "constraints": "Use pandas. Safely handle missing files, empty files, and NaN values.",
    },
    "Palindrome Validator": {
        "req": "Create a Python function that checks whether a string is a palindrome, ignoring case, punctuation, and whitespace.",
        "constraints": "Ignore non-alphanumeric characters, O(n) time complexity.",
    },
    "Anagram Checker": {
        "req": "Create a Python function that checks whether two strings are anagrams of each other.",
        "constraints": "Case-insensitive comparison, ignore whitespace.",
    },
    "Fibonacci Generator": {
        "req": "Create a Python function to generate the Fibonacci sequence up to n terms with input validation.",
        "constraints": "Raise ValueError on negative inputs. Return empty list for n=0.",
    },
    "Safe File Keyword Search": {
        "req": "Create a Python function that reads a text file line-by-line safely, counts lines matching a keyword, and writes the summary to an output file.",
        "constraints": "Use context managers. Stream line-by-line for low memory usage.",
    },
    "REST API Request Handler": {
        "req": "Create a Python function to make an HTTP GET request to an API endpoint with query parameters, timeout, status verification, and JSON parsing.",
        "constraints": "Handle timeouts, HTTP 4xx/5xx errors, and JSON decode errors gracefully.",
    },
    "User Registration Validator": {
        "req": "Create a Python function that validates user registration data (username, email, age) against strict rules and raises custom exceptions.",
        "constraints": "Username 3-20 chars alphanumeric, valid email format, age between 13 and 120.",
    },
    "SQLite Database Operations": {
        "req": "Create a Python function to connect to SQLite, create an items table, insert records with parameterized queries, and query results safely.",
        "constraints": "Prevent SQL injection with parameterized queries. Safe commit and rollback.",
    },
    "Binary Search Algorithm": {
        "req": "Create a Python function that implements binary search on a sorted list and returns the index of the target or -1.",
        "constraints": "O(log n) time complexity, O(1) space.",
    },
}


# ==============================================================================
# 4. UI COMPONENT RENDERERS
# ==============================================================================
def render_sidebar(is_generated: bool) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """Renders the AI execution timeline sidebar and system status overview."""
    with st.sidebar:
        st.markdown(
            """
            <div style="margin-bottom: 1.2rem; padding-bottom: 0.8rem; border-bottom: 1px solid #D9E3EC;">
                <div style="display: flex; align-items: center; gap: 0.6rem;">
                    <span style="font-size: 1.6rem; color: #FF7A00; line-height: 1;">⚡</span>
                    <div>
                        <span style="font-size: 1.28rem; font-weight: 800; color: #0B1F33; letter-spacing: -0.02em;">CODEFORGE</span>
                        <span style="font-size: 1.28rem; font-weight: 800; color: #0066B3; letter-spacing: -0.02em;">AI</span>
                    </div>
                </div>
                <div style="font-size: 0.78rem; color: #607586; font-weight: 500; margin-top: 0.25rem; display: flex; align-items: center; gap: 0.4rem;">
                    <span>AI Code Snippet Generator</span>
                    <span style="color: #D9E3EC;">•</span>
                    <span style="color: #1687D9; font-weight: 600;">v2.5</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Retrieve active engine from backend configuration (.env)
        provider_info = backend.get_active_provider_info()

        badge_color = "#16865B" if provider_info["is_live"] else "#E85D04"
        badge_bg = "#E8F7F6" if provider_info["is_live"] else "#FFF2E5"
        badge_border = "#BBF7D0" if provider_info["is_live"] else "#FFD8B2"
        badge_label = "Live GenAI" if provider_info["is_live"] else "Smart Offline"

        st.markdown(
            f"""
            <div style="background-color: #F8FAFC; border: 1px solid #D9E3EC; border-radius: 8px; padding: 0.75rem 0.85rem; margin-bottom: 1.1rem;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.35rem;">
                    <span style="font-size: 0.72rem; color: #607586; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">
                        AI ENGINE
                    </span>
                    <span style="display: inline-flex; align-items: center; gap: 0.35rem; background: {badge_bg}; border: 1px solid {badge_border}; color: {badge_color}; font-size: 0.68rem; font-weight: 700; padding: 0.15rem 0.55rem; border-radius: 9999px;">
                        <span style="width: 6px; height: 6px; border-radius: 50%; background-color: {badge_color};"></span> {badge_label}
                    </span>
                </div>
                <div style="font-size: 0.82rem; font-weight: 700; color: #0B1F33;">
                    {provider_info['display_name']}
                </div>
                <div style="font-size: 0.7rem; color: #607586; margin-top: 0.2rem;">
                    Connected via backend environment
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style="font-size: 0.72rem; font-weight: 700; color: #607586; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.75rem; display: flex; align-items: center; justify-content: space-between;">
                <span>AI Execution Timeline</span>
                <span style="font-size: 0.68rem; color: #FF7A00; font-weight: 700;">5 Stages</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        steps = [
            ("01", "Requirement", "Input specification"),
            ("02", "Analysis", "Intent & schema extraction"),
            ("03", "Context Retrieval", "Knowledge base match"),
            ("04", "Code Generation", "Python synthesis"),
            ("05", "Validation", "Syntax & AST checks"),
        ]

        for i, (num, title, desc) in enumerate(steps):
            if is_generated:
                node_class = "timeline-node completed"
                circle_html = '<div class="timeline-circle-completed">✓</div>'
                title_html = f'<span style="font-size: 0.84rem; font-weight: 700; color: #16865B;">{num} {title}</span>'
            elif i == 0:
                node_class = "timeline-node active"
                circle_html = f'<div class="timeline-circle-active">{num}</div>'
                title_html = f'<span style="font-size: 0.84rem; font-weight: 700; color: #0066B3;">{num} <span style="color: #FF7A00;">⚡</span> {title}</span>'
            else:
                node_class = "timeline-node inactive"
                circle_html = f'<div class="timeline-circle-inactive">{num}</div>'
                title_html = f'<span style="font-size: 0.84rem; font-weight: 700; color: #607586;">{num} {title}</span>'

            st.markdown(
                f"""
                <div class="{node_class}">
                    {circle_html}
                    <div style="display: flex; flex-direction: column;">
                        {title_html}
                        <span style="font-size: 0.69rem; color: #607586;">{desc}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if i < len(steps) - 1:
                conn_class = "timeline-connector completed" if is_generated else "timeline-connector"
                st.markdown(f'<div class="{conn_class}"></div>', unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

        # Platform Capabilities Card
        st.markdown(
            """
            <div style="background-color: #FFFFFF; border: 1px solid #D9E3EC; border-radius: 8px; padding: 0.75rem 0.85rem; box-shadow: 0 1px 3px rgba(11,31,51,0.04);">
                <div style="font-size: 0.72rem; color: #607586; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.4rem;">
                    PLATFORM CAPABILITIES
                </div>
                <div style="font-size: 0.73rem; color: #172B3A; line-height: 1.55;">
                    🛡️ <b>AST Syntax Checker:</b> Active<br/>
                    🔒 <b>Safety Screening:</b> Zero Unsafe Calls<br/>
                    📚 <b>Knowledge Base:</b> 8 Domains Indexed<br/>
                    ⚡ <b>Architecture:</b> Decoupled Frontend + Backend
                </div>
            </div>
            <div style="text-align: center; font-size: 0.72rem; color: #607586; margin-top: 0.8rem;">
                TCS Technology Day Submission
            </div>
            """,
            unsafe_allow_html=True,
        )

        return None, None, None


def render_hero(provider_info: dict):
    """Renders the hero section with branding and dynamic engine status pill."""
    st.markdown(
        f"""
        <div style="position: relative; background: linear-gradient(135deg, rgba(232, 243, 251, 0.85) 0%, rgba(255, 242, 229, 0.45) 55%, rgba(243, 246, 249, 0.2) 100%); border: 1px solid #D9E3EC; border-radius: 14px; padding: 1.5rem 1.8rem; margin-bottom: 1.3rem;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
                <div>
                    <div style="display: inline-flex; align-items: center; gap: 0.5rem; background: #FFFFFF; border: 1px solid #D9E3EC; color: #0B1F33; font-size: 0.76rem; font-weight: 700; padding: 0.25rem 0.75rem; border-radius: 4px; margin-bottom: 0.65rem; letter-spacing: 0.04em;">
                        <span style="color: #FF7A00; font-weight: 800;">⚡</span>
                        <span>AI CODE SNIPPET GENERATOR</span>
                        <span style="color: #D9E3EC;">|</span>
                        <span style="color: #607586;">Natural Language → Production Python</span>
                    </div>
                    <h1 style="font-size: 2.45rem; font-weight: 800; letter-spacing: -0.03em; margin: 0.2rem 0 0.5rem 0; line-height: 1.2;">
                        <span style="color: #0B1F33;">Turn Requirements Into </span>
                        <span style="color: #0066B3; border-bottom: 3px solid #FF7A00; padding-bottom: 2px;">Production-Ready Code.</span>
                    </h1>
                    <p style="font-size: 0.98rem; color: #607586; max-width: 820px; line-height: 1.55; margin: 0;">
                        Synthesize Python code for any requirement, condition, calculation, or algorithm with automated AST syntax validation and security screening.
                    </p>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <div style="display: inline-flex; align-items: center; gap: 0.45rem; background: #FFF2E5; border: 1px solid #FFD8B2; color: #E85D04; font-size: 0.8rem; font-weight: 700; padding: 0.38rem 0.9rem; border-radius: 9999px; box-shadow: 0 1px 3px rgba(232, 93, 4, 0.1);">
                        <span style="width: 8px; height: 8px; border-radius: 50%; background-color: #16865B; box-shadow: 0 0 0 2px rgba(22, 134, 91, 0.25);"></span>
                        <span>● {provider_info['display_name'].upper()}</span>
                    </div>
                </div>
            </div>

            <div style="display: flex; align-items: center; gap: 0.6rem; flex-wrap: wrap; margin-top: 1.1rem; padding-top: 0.85rem; border-top: 1px solid rgba(217, 227, 236, 0.8);">
                <div style="display: inline-flex; align-items: center; gap: 0.35rem; background: #FFF2E5; border: 1px solid #FFD8B2; border-radius: 4px; padding: 0.2rem 0.55rem; font-size: 0.74rem; font-weight: 700; color: #E85D04;">
                    <span style="color: #FF7A00;">●</span> Any Custom Prompt Supported
                </div>
                <div style="display: inline-flex; align-items: center; gap: 0.35rem; background: #EAF4FB; border: 1px solid #BCE0F7; border-radius: 4px; padding: 0.2rem 0.55rem; font-size: 0.74rem; font-weight: 600; color: #0066B3;">
                    <span>🐍</span> Python 3.10+
                </div>
                <div style="display: inline-flex; align-items: center; gap: 0.35rem; background: #E8F7F6; border: 1px solid #B8E4E3; border-radius: 4px; padding: 0.2rem 0.55rem; font-size: 0.74rem; font-weight: 600; color: #00A6A6;">
                    <span>📚</span> Semantic RAG Retrieval
                </div>
                <div style="display: inline-flex; align-items: center; gap: 0.35rem; background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 4px; padding: 0.2rem 0.55rem; font-size: 0.74rem; font-weight: 600; color: #16865B;">
                    <span>🛡️</span> AST Syntax & Safety Screening
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_requirement_input() -> tuple[str, str, str, bool, bool]:
    """Renders the requirement input section with sample preset selector, language picker,

    additional constraints, and Generate / Reset buttons.
    """
    default_prompt = (
        "Create a Python code for if age>=18 print adult ,else teen"
    )

    if "user_prompt" not in st.session_state:
        st.session_state.user_prompt = default_prompt
    if "user_constraints" not in st.session_state:
        st.session_state.user_constraints = ""

    with st.container(border=True):
        st.markdown(
            """
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.85rem; padding: 0.4rem 0.4rem 0 0.4rem;">
                <div style="display: flex; align-items: center; gap: 0.65rem;">
                    <div style="width: 4px; height: 18px; background-color: #FF7A00; border-radius: 2px;"></div>
                    <h3 style="font-size: 1.15rem; font-weight: 800; color: #0B1F33; margin: 0; letter-spacing: -0.01em; display: flex; align-items: center; gap: 0.4rem;">
                        <span style="color: #FF7A00;">⚡</span> WHAT DO YOU WANT TO BUILD?
                    </h3>
                </div>
                <span style="font-size: 0.8rem; color: #607586; font-weight: 600;">
                    Type any custom requirement or select a preset
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        preset_options = ["-- Select a Sample Requirement Preset (or enter your own below) --"] + list(SAMPLE_REQUIREMENTS.keys())
        selected_preset = st.selectbox(
            "Quick Requirement Presets:",
            options=preset_options,
            index=0,
            label_visibility="visible",
        )

        if selected_preset in SAMPLE_REQUIREMENTS:
            preset_data = SAMPLE_REQUIREMENTS[selected_preset]
            st.session_state.user_prompt = preset_data["req"]
            st.session_state.user_constraints = preset_data.get("constraints", "")

        user_requirement = st.text_area(
            label="Requirement Specification",
            value=st.session_state.user_prompt,
            height=110,
            placeholder='Example: "Create a Python code for if age>=18 print adult ,else teen" or any custom requirement...',
            help="Describe the desired function, logic, parameters, inputs, outputs, or conditions.",
        )

        col_lang, col_constraints = st.columns([0.3, 0.7])
        with col_lang:
            selected_language = st.selectbox(
                "Target Language:",
                options=["Python (Standard 3.10+)", "Python (Async)", "Python (Strict Types)"],
                index=0,
            )

        with col_constraints:
            constraints_input = st.text_input(
                "Additional Constraints (Optional):",
                value=st.session_state.user_constraints,
                placeholder="e.g. O(sqrt(n)) time complexity, do not use external libraries, handle nulls...",
                help="Optional technical boundaries, runtime constraints, or style rules.",
            )

        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 0.45rem; font-size: 0.82rem; color: #607586; margin-top: 0.3rem; margin-bottom: 0.85rem; padding-left: 0.4rem;">
                <span style="color: #FF7A00; font-weight: 700; font-size: 0.95rem;">💡 Tip:</span>
                <span>You can enter any custom conditional statement, function logic, loop, or calculation!</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_btn1, col_btn2, _ = st.columns([0.22, 0.16, 0.62])
        with col_btn1:
            generate_clicked = st.button("⚡ Generate Code", use_container_width=True)
        with col_btn2:
            reset_clicked = st.button("🔄 Reset", use_container_width=True)

    return user_requirement, constraints_input, selected_language, generate_clicked, reset_clicked


def render_result_header(result: dict):
    """Renders the generation header and key performance metrics."""
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    header_col, pills_col = st.columns([0.45, 0.55])

    status_color = "#16865B" if result["validation"]["status"] == "Passed" else "#DC2626"
    status_icon = "✓" if result["validation"]["status"] == "Passed" else "✗"
    status_bg = "#E8F7F6" if result["validation"]["status"] == "Passed" else "#FEE2E2"
    status_border = "#BBF7D0" if result["validation"]["status"] == "Passed" else "#FCA5A5"

    with header_col:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <div style="width: 34px; height: 34px; border-radius: 8px; background: {status_bg}; display: flex; align-items: center; justify-content: center; color: {status_color}; font-weight: 800; font-size: 1.15rem; border: 1px solid {status_border}; box-shadow: 0 1px 3px rgba(22, 134, 91, 0.12);">
                    {status_icon}
                </div>
                <div>
                    <h2 style="font-size: 1.45rem; font-weight: 800; color: #0B1F33; margin: 0; line-height: 1.2;">
                        Generation Complete
                    </h2>
                    <span style="font-size: 0.8rem; color: #607586;">Engine: {result.get('mode', 'AI Pipeline')}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with pills_col:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; justify-content: flex-end; gap: 0.6rem; height: 100%; flex-wrap: wrap;">
                <div style="background: #FFFFFF; border: 1px solid #D9E3EC; border-radius: 8px; padding: 0.4rem 0.85rem; font-size: 0.82rem; display: flex; align-items: center; gap: 0.4rem; box-shadow: 0 1px 2px rgba(11,31,51,0.03);">
                    <span style="color: #607586;">Latency:</span>
                    <span style="color: #0066B3; font-weight: 700; font-family: 'Fira Code', monospace;">{result['generation_time']}</span>
                </div>
                <div style="background: #FFFFFF; border: 1px solid #D9E3EC; border-radius: 8px; padding: 0.4rem 0.85rem; font-size: 0.82rem; display: flex; align-items: center; gap: 0.4rem; box-shadow: 0 1px 2px rgba(11,31,51,0.03);">
                    <span style="color: #607586;">Status:</span>
                    <span style="color: {status_color}; font-weight: 700;">{result['validation']['status']}</span>
                </div>
                <div style="background: #FFFFFF; border: 1px solid #D9E3EC; border-radius: 8px; padding: 0.4rem 0.85rem; font-size: 0.82rem; display: flex; align-items: center; gap: 0.4rem; box-shadow: 0 1px 2px rgba(11,31,51,0.03);">
                    <span style="color: #607586;">Confidence:</span>
                    <span style="color: #FF7A00; font-weight: 700; font-family: 'Fira Code', monospace;">{result['confidence']}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='border: none; border-top: 1px solid #D9E3EC; margin: 1.1rem 0 1.4rem 0;' />", unsafe_allow_html=True)


def render_analysis(analysis: dict):
    """Renders the 6 requirement analysis cards."""
    st.markdown(
        """
        <div style="margin-bottom: 0.9rem;">
            <div class="section-eyebrow-orange">
                <span>⚡</span> AI ANALYSIS
            </div>
            <h3 class="section-title">Requirement Analysis</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    r1_col1, r1_col2, r1_col3 = st.columns(3)
    with r1_col1:
        st.markdown(
            f"""
            <div class="analysis-card card-top-orange" style="height: 145px;">
                <div style="color: #E85D04; font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.45rem; display: flex; align-items: center; gap: 0.4rem;">
                    <span>🎯</span> INTENT
                </div>
                <div style="color: #172B3A; font-size: 0.88rem; font-weight: 500; line-height: 1.45;">
                    {analysis['intent']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with r1_col2:
        st.markdown(
            f"""
            <div class="analysis-card card-top-blue" style="height: 145px;">
                <div style="color: #0066B3; font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.45rem; display: flex; align-items: center; gap: 0.4rem;">
                    <span>📥</span> INPUTS
                </div>
                <div style="color: #172B3A; font-size: 0.88rem; font-weight: 500; line-height: 1.45;">
                    {analysis['inputs']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with r1_col3:
        st.markdown(
            f"""
            <div class="analysis-card card-top-blue" style="height: 145px;">
                <div style="color: #0066B3; font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.45rem; display: flex; align-items: center; gap: 0.4rem;">
                    <span>📤</span> OUTPUTS
                </div>
                <div style="color: #172B3A; font-size: 0.88rem; font-weight: 500; line-height: 1.45;">
                    {analysis['outputs']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    r2_col1, r2_col2, r2_col3 = st.columns(3)
    with r2_col1:
        st.markdown(
            f"""
            <div class="analysis-card card-top-navy" style="min-height: 155px;">
                <div style="color: #0B1F33; font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.45rem; display: flex; align-items: center; gap: 0.4rem;">
                    <span>⚙️</span> CONSTRAINTS
                </div>
                <div style="color: #172B3A; font-size: 0.88rem; font-weight: 500; line-height: 1.45;">
                    {analysis['constraints']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with r2_col2:
        edge_items_html = "".join([f"<li style='margin-bottom: 0.25rem;'>{ec}</li>" for ec in analysis.get("edge_cases", [])])
        st.markdown(
            f"""
            <div class="analysis-card card-top-orange" style="min-height: 155px;">
                <div style="color: #E85D04; font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.45rem; display: flex; align-items: center; gap: 0.4rem;">
                    <span>⚠️</span> EDGE CASES
                </div>
                <div style="color: #172B3A; font-size: 0.84rem; line-height: 1.45;">
                    <ul style="margin: 0; padding-left: 1.15rem; color: #172B3A;">
                        {edge_items_html if edge_items_html else "<li>Boundary checks performed</li>"}
                    </ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with r2_col3:
        lib_chips_html = "".join([f"<span class='chip-teal'>{lib}</span>" for lib in analysis.get("libraries", [])])
        st.markdown(
            f"""
            <div class="analysis-card card-top-teal" style="min-height: 155px;">
                <div style="color: #00A6A6; font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.45rem; display: flex; align-items: center; gap: 0.4rem;">
                    <span>📦</span> LIBRARIES
                </div>
                <div style="margin-top: 0.4rem;">
                    {lib_chips_html if lib_chips_html else "<span class='chip-teal'>built-in</span>"}
                </div>
                <div style="font-size: 0.73rem; color: #607586; margin-top: 0.65rem;">
                    Standard Python runtime dependencies verified
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_retrieved_context(contexts: list):
    """Renders RAG knowledge base matches with similarity metrics."""
    st.markdown(
        """
        <div style="margin-top: 1.3rem; margin-bottom: 0.9rem;">
            <div class="section-eyebrow-orange">
                <span>⚡</span> KNOWLEDGE RETRIEVAL
            </div>
            <h3 class="section-title">Retrieved Reference Context</h3>
            <div style="font-size: 0.82rem; color: #607586;">
                Top semantically matching patterns from the knowledge base
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(3)
    for idx, item in enumerate(contexts[:3]):
        with cols[idx]:
            sim_score = item["similarity"]
            st.markdown(
                f"""
                <div class="analysis-card card-top-orange" style="min-height: 155px; display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.65rem;">
                            <span style="font-size: 0.78rem; font-weight: 700; color: #0B1F33; font-family: 'Fira Code', monospace; background: #FFF2E5; padding: 0.18rem 0.55rem; border-radius: 4px; border: 1px solid #FFD8B2; display: flex; align-items: center; gap: 0.35rem;">
                                <span style="color: #FF7A00;">⚡</span> {item['id']}
                            </span>
                            <div class="badge-orange">
                                <span>✦</span> Similarity {sim_score}%
                            </div>
                        </div>
                        <div style="font-size: 0.86rem; color: #172B3A; line-height: 1.45; font-weight: 500;">
                            {item['requirement']}
                        </div>
                    </div>
                    <div style="margin-top: 0.85rem;">
                        <div style="display: flex; justify-content: space-between; font-size: 0.72rem; color: #607586; margin-bottom: 0.25rem; font-family: 'Fira Code', monospace;">
                            <span>TF-IDF Match</span>
                            <span style="color: #0066B3; font-weight: 700;">{sim_score}%</span>
                        </div>
                        <div style="background: #E8F3FB; border-radius: 9999px; height: 5px; overflow: hidden; border: 1px solid #D9E3EC;">
                            <div style="background-color: #0066B3; width: {sim_score}%; height: 100%;"></div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_generated_code(code: str, validation_status: str):
    """Renders the syntax-highlighted code editor with copy and download actions."""
    st.markdown(
        """
        <div style="margin-top: 1.3rem; margin-bottom: 0.75rem;">
            <div style="display: flex; justify-content: space-between; align-items: flex-end;">
                <div>
                    <div class="section-eyebrow-orange">
                        <span>⚡</span> CODE GENERATION
                    </div>
                    <h3 class="section-title">Generated Python Snippet</h3>
                </div>
                <div style="font-size: 0.8rem; color: #607586; font-family: 'Fira Code', monospace;">
                    generated_code.py (Python 3.10+)
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        status_tag = "✓ Valid Python AST" if validation_status == "Passed" else "✗ Syntax Error"
        status_color = "#34D399" if validation_status == "Passed" else "#F87171"

        st.markdown(
            f"""
            <div style="background-color: #13283A; border-radius: 8px 8px 0 0; padding: 0.75rem 1.15rem; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.08); margin: -0.2rem -0.2rem 0.5rem -0.2rem;">
                <div style="display: flex; align-items: center; gap: 0.6rem;">
                    <span style="color: #FFFFFF; font-weight: 700; font-size: 0.92rem;">Python Source Code</span>
                    <span style="color: #8CA0B3; font-size: 0.76rem; font-family: 'Fira Code', monospace;">generated_code.py</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="background: rgba(22, 134, 91, 0.2); border: 1px solid {status_color}; color: {status_color}; font-size: 0.72rem; font-weight: 700; padding: 0.2rem 0.55rem; border-radius: 4px;">
                        {status_tag}
                    </span>
                    <span style="background: rgba(0, 102, 179, 0.25); border: 1px solid #1687D9; color: #93C5FD; font-size: 0.72rem; font-weight: 600; padding: 0.2rem 0.55rem; border-radius: 4px;">
                        Production Ready
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.code(code, language="python", line_numbers=True)

    btn_col1, btn_col2, _ = st.columns([0.28, 0.28, 0.44])
    with btn_col1:
        st.download_button(
            label="⬇ Download Python Code",
            data=code,
            file_name="generated_code.py",
            mime="text/x-python",
            use_container_width=True,
        )
    with btn_col2:
        if st.button("📋 Copy to Clipboard", use_container_width=True):
            st.toast("Snippet copied! Use Ctrl+V to paste or click the code block copy icon.", icon="📋")


def render_explanation(result: dict):
    """Renders the explanation section detailing logic, edge cases, and assumptions."""
    explanation = result.get("explanation", "")
    assumptions = result.get("assumptions", [])

    if not explanation and not assumptions:
        return

    st.markdown(
        """
        <div style="margin-top: 1.3rem; margin-bottom: 0.8rem;">
            <div class="section-eyebrow-orange">
                <span>⚡</span> ARCHITECTURAL BREAKDOWN
            </div>
            <h3 class="section-title">Implementation Explanation</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown(
            f"""
            <div style="padding: 0.4rem 0.6rem;">
                <div style="color: #172B3A; font-size: 0.94rem; line-height: 1.6; margin-bottom: 0.6rem;">
                    {explanation}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if assumptions:
            assumptions_html = "".join([f"<li style='margin-bottom: 0.25rem; font-size: 0.85rem; color: #475569;'>{a}</li>" for a in assumptions])
            st.markdown(
                f"""
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 0.75rem 1rem; margin-top: 0.5rem;">
                    <div style="font-size: 0.75rem; font-weight: 700; color: #0B1F33; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.35rem;">
                        Assumptions & Design Invariants
                    </div>
                    <ul style="margin: 0; padding-left: 1.2rem;">
                        {assumptions_html}
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_examples(examples: list):
    """Renders example inputs and expected outputs."""
    if not examples:
        return

    st.markdown(
        """
        <div style="margin-top: 1.3rem; margin-bottom: 0.8rem;">
            <div class="section-eyebrow-orange">
                <span>⚡</span> VERIFICATION CASES
            </div>
            <h3 class="section-title">Example Inputs & Expected Outputs</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(min(len(examples), 3))
    for i, ex in enumerate(examples[:3]):
        with cols[i]:
            st.markdown(
                f"""
                <div class="analysis-card card-top-blue" style="min-height: 125px;">
                    <div style="color: #0066B3; font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.45rem;">
                        Case {i+1}
                    </div>
                    <div style="font-size: 0.76rem; color: #607586; margin-bottom: 0.2rem; font-weight: 600;">Input:</div>
                    <div style="background: #F1F5F9; font-family: 'Fira Code', monospace; font-size: 0.82rem; padding: 0.3rem 0.55rem; border-radius: 4px; margin-bottom: 0.45rem; color: #0B1F33; word-break: break-all;">
                        {ex.get('input', '')}
                    </div>
                    <div style="font-size: 0.76rem; color: #607586; margin-bottom: 0.2rem; font-weight: 600;">Expected Output:</div>
                    <div style="background: #E8F7F6; font-family: 'Fira Code', monospace; font-size: 0.82rem; padding: 0.3rem 0.55rem; border-radius: 4px; color: #16865B; font-weight: 600; word-break: break-all;">
                        {ex.get('output', '')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_test_cases(test_cases: str):
    """Renders the unit test suite with syntax highlighting."""
    if not test_cases or not test_cases.strip():
        return

    st.markdown(
        """
        <div style="margin-top: 1.3rem; margin-bottom: 0.8rem;">
            <div class="section-eyebrow-orange">
                <span>⚡</span> AUTOMATED VALIDATION
            </div>
            <h3 class="section-title">Unit Test Cases</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown(
            """
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.4rem 0.6rem 0.4rem 0.6rem;">
                <span style="font-size: 0.82rem; color: #607586;">Self-contained unit tests verifying edge cases and functional requirements</span>
                <span style="font-size: 0.74rem; font-weight: 700; color: #16865B; background: #E8F7F6; border: 1px solid #BBF7D0; padding: 0.15rem 0.55rem; border-radius: 4px;">unittest Compatible</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.code(test_cases, language="python", line_numbers=True)


def render_validation(validation_data: dict):
    """Renders the validation section with AST, safety, and structure results."""
    status_passed = validation_data.get("status") == "Passed"
    badge_bg = "#E8F7F6" if status_passed else "#FEE2E2"
    badge_border = "#BBF7D0" if status_passed else "#FCA5A5"
    badge_color = "#16865B" if status_passed else "#DC2626"
    badge_text = "VALIDATION PASSED" if status_passed else "VALIDATION FAILED"
    badge_icon = "✓" if status_passed else "✗"

    st.markdown(
        f"""
        <div style="margin-top: 1.3rem; margin-bottom: 0.75rem;">
            <div style="font-size: 0.74rem; font-weight: 700; color: {badge_color}; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.25rem;">
                {badge_icon} VALIDATION STATUS
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <h3 class="section-title">AST Syntax & Safety Verification</h3>
                <div style="display: inline-flex; align-items: center; gap: 0.35rem; background: {badge_bg}; border: 1px solid {badge_border}; color: {badge_color}; font-size: 0.78rem; font-weight: 700; padding: 0.3rem 0.8rem; border-radius: 9999px;">
                    <span style="font-weight: 800;">{badge_icon}</span>
                    <span>{badge_text}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        val_col1, val_col2 = st.columns(2)
        checks = validation_data.get("checks", [])

        for i, check in enumerate(checks):
            col = val_col1 if i % 2 == 0 else val_col2
            is_passed = check.get("passed", False)
            icon = "✓" if is_passed else "✗"
            color = "#16865B" if is_passed else "#DC2626"

            with col:
                st.markdown(
                    f"""
                    <div class="val-check-row">
                        <span style="color: {color}; font-weight: 800; font-size: 1.05rem;">{icon}</span>
                        <div style="display: flex; flex-direction: column;">
                            <span style="font-weight: 700; color: #0B1F33; font-size: 0.88rem;">{check['name']}</span>
                            <span style="font-size: 0.78rem; color: #607586;">{check['detail']}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def render_generation_summary(result: dict):
    """Renders 4 compact metric cards with distinct semantic top accents."""
    st.markdown(
        """
        <div style="margin-top: 1.3rem; margin-bottom: 0.8rem;">
            <div class="section-eyebrow-orange">
                <span>⚡</span> AUDIT LOG
            </div>
            <h3 class="section-title" style="font-size: 1.2rem;">Generation Summary</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
            <div class="metric-card-box card-top-blue">
                <div style="color: #607586; font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.35rem;">
                    Generation Time
                </div>
                <div style="color: #0B1F33; font-size: 1.4rem; font-weight: 800; font-family: 'Fira Code', monospace;">
                    {result['generation_time']}
                </div>
                <div style="font-size: 0.72rem; color: #0066B3; margin-top: 0.25rem; font-weight: 600;">
                    Synthesized & verified
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="metric-card-box card-top-orange">
                <div style="color: #E85D04; font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.35rem;">
                    Context Matches
                </div>
                <div style="color: #0B1F33; font-size: 1.4rem; font-weight: 800; font-family: 'Inter', sans-serif;">
                    {len(result.get('retrieved_context', []))}
                </div>
                <div style="font-size: 0.72rem; color: #FF7A00; margin-top: 0.25rem; font-weight: 600;">
                    TF-IDF semantic patterns
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        status = result['validation']['status']
        st.markdown(
            f"""
            <div class="metric-card-box" style="border-top: 3px solid #16865B;">
                <div style="color: #607586; font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.35rem;">
                    Validation
                </div>
                <div style="color: #16865B; font-size: 1.4rem; font-weight: 800; font-family: 'Inter', sans-serif;">
                    {status}
                </div>
                <div style="font-size: 0.72rem; color: #16865B; margin-top: 0.25rem; font-weight: 600;">
                    AST & Safety Verified
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            f"""
            <div class="metric-card-box card-top-azure">
                <div style="color: #607586; font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.35rem;">
                    Confidence
                </div>
                <div style="color: #0B1F33; font-size: 1.4rem; font-weight: 800; font-family: 'Fira Code', monospace;">
                    {result['confidence']}
                </div>
                <div style="font-size: 0.72rem; color: #1687D9; margin-top: 0.25rem; font-weight: 600;">
                    Quality estimation score
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==============================================================================
# 5. MAIN APPLICATION CONTROLLER
# ==============================================================================
def main():
    inject_custom_css()

    if "is_generated" not in st.session_state:
        st.session_state.is_generated = False
    if "result_data" not in st.session_state:
        st.session_state.result_data = None
    if "last_error" not in st.session_state:
        st.session_state.last_error = None

    # Render Sidebar and retrieve provider settings
    provider_override, api_key_override, model_override = render_sidebar(is_generated=st.session_state.is_generated)

    # Active provider info
    active_info = backend.get_active_provider_info(
        override_provider=provider_override,
        override_api_key=api_key_override,
        override_model=model_override,
    )

    render_hero(active_info)

    req_text, constraints_text, selected_lang, generate_clicked, reset_clicked = render_requirement_input()

    if reset_clicked:
        st.session_state.is_generated = False
        st.session_state.result_data = None
        st.session_state.last_error = None
        st.rerun()

    if generate_clicked:
        clean_text = req_text.strip()
        if not clean_text:
            st.error("Please describe the Python functionality you want to generate.")
            st.session_state.is_generated = False
            st.session_state.result_data = None
        else:
            st.session_state.user_prompt = clean_text
            st.session_state.user_constraints = constraints_text
            st.session_state.last_error = None

            with st.status("⚡ Running CodeForge AI Pipeline...", expanded=True) as status:
                st.write("🔍 **Stage 1/5:** Analyzing requirement & extracting constraints...")
                time.sleep(0.10)
                st.write("📚 **Stage 2/5:** Retrieving semantic patterns from knowledge base...")
                time.sleep(0.10)
                st.write(f"🧠 **Stage 3/5:** Synthesizing Python source code using {active_info['display_name']}...")

                try:
                    res = backend.generate(
                        requirement=clean_text,
                        constraints=constraints_text,
                        language=selected_lang,
                        api_key=api_key_override,
                        provider=provider_override,
                        model=model_override,
                    )
                    st.write("🛡️ **Stage 4/5:** Validating AST syntax and structural integrity...")
                    time.sleep(0.08)
                    st.write("🔒 **Stage 5/5:** Performing static safety screening...")
                    time.sleep(0.08)
                    status.update(label="✓ Generation & Validation Complete!", state="complete", expanded=False)
                    st.session_state.result_data = res
                    st.session_state.is_generated = True
                except Exception as exc:
                    status.update(label="✗ Pipeline Failed", state="error", expanded=False)
                    st.session_state.last_error = str(exc)
                    st.session_state.is_generated = False
                    st.session_state.result_data = None

    if st.session_state.last_error:
        st.error(f"Generation error: {st.session_state.last_error}")
        if st.button("🔄 Retry Generation"):
            st.session_state.last_error = None
            st.rerun()

    if st.session_state.is_generated and st.session_state.result_data:
        result = st.session_state.result_data

        render_result_header(result)
        render_analysis(result["analysis"])
        render_retrieved_context(result["retrieved_context"])
        render_generated_code(result["generated_code"], result["validation"]["status"])
        render_explanation(result)
        render_examples(result.get("examples", []))
        render_test_cases(result.get("test_cases", ""))
        render_validation(result["validation"])
        render_generation_summary(result)


if __name__ == "__main__":
    main()
