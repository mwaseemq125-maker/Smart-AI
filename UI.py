import csv
import io
import html
import streamlit as st

from graph import task_graph


# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="TaskFlow AI | Smart Task Organizer",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --bg: #0b1020;
    --panel: #131b30;
    --border: #26324c;
    --text: #f1f5ff;
    --muted: #9baac5;
    --accent: #8b7cff;
}

.stApp {
    background:
        radial-gradient(ellipse at 10% 0%, #22204c 0%, transparent 36%),
        radial-gradient(ellipse at 95% 12%, #12364a 0%, transparent 30%),
        var(--bg);
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1250px;
    padding-top: 2.1rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--text) !important;
}

p, label, li {
    color: #d1daed;
}

[data-testid="stSidebar"] {
    background: #0d1427;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * {
    color: #e5eaff;
}

.brand {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 27px;
    font-weight: 700;
    letter-spacing: -1px;
    margin-bottom: 5px;
}

.brand span {
    color: #a99cff;
}

.eyebrow {
    color: #a99cff;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(31px, 4vw, 48px);
    line-height: 1.15;
    font-weight: 700;
    color: #f4f6ff;
    letter-spacing: -1.7px;
    margin: 9px 0;
}

.hero-title span {
    background: linear-gradient(90deg, #a99cff, #68d9f4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    color: #a7b5d0;
    font-size: 15px;
    line-height: 1.8;
    margin-bottom: 22px;
}

.panel {
    background: rgba(19, 27, 48, 0.92);
    border: 1px solid #2a3652;
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 16px;
}

.panel-title {
    font-size: 18px;
    font-weight: 700;
    color: #f0f3ff;
    margin-bottom: 6px;
}

.panel-subtitle {
    color: #9baac5;
    font-size: 13px;
    margin-bottom: 16px;
}

.metric {
    background: linear-gradient(145deg, #18233c, #121a2e);
    border: 1px solid #2b3856;
    border-radius: 15px;
    padding: 19px 17px;
    min-height: 118px;
}

.metric-label {
    font-size: 12px;
    color: #a8b5d0;
    margin-bottom: 12px;
}

.metric-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 32px;
    font-weight: 700;
    color: #f4f6ff;
}

.task-card {
    background: linear-gradient(135deg, #17223a, #121a2d);
    border: 1px solid #2b3856;
    border-radius: 15px;
    padding: 17px 19px;
    margin: 10px 0;
}

.task-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 17px;
    font-weight: 600;
    color: #f5f7ff;
    margin-bottom: 7px;
}

.task-description {
    color: #aebbd2;
    font-size: 13px;
    line-height: 1.65;
}

.task-meta {
    color: #c4cde0;
    font-size: 12px;
    margin-top: 12px;
}

.priority {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 7px;
    font-size: 11px;
    font-weight: 700;
}

.priority-high {
    color: #ff9aab;
    background: #482333;
}

.priority-medium {
    color: #ffd18b;
    background: #49371e;
}

.priority-low {
    color: #83e6bc;
    background: #173b35;
}

.stButton > button {
    border-radius: 10px;
    font-weight: 600;
    min-height: 43px;
    border: 1px solid #45406f;
    transition: all 0.2s ease;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(95deg, #7665f5, #8e75ff);
    color: white;
    border: none;
}

.stButton > button:hover {
    border-color: #a99cff;
    transform: translateY(-1px);
}

.stTextArea textarea,
.stTextInput input,
div[data-baseweb="select"] > div {
    background: #10182b !important;
    color: #f1f5ff !important;
    border-color: #34415f !important;
    border-radius: 10px !important;
}

hr {
    border-color: #28344d !important;
}

[data-testid="stAlert"] {
    border-radius: 12px;
}

.small-note {
    color: #8998b5;
    font-size: 12px;
}

[data-testid="stCaptionContainer"] {
    color: #a5b2cc;
}

@media (max-width: 700px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .panel {
        padding: 16px;
    }
}
</style>
""", unsafe_allow_html=True)


# ---------------- SESSION STATE ----------------

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "summary" not in st.session_state:
    st.session_state.summary = ""

if "last_input" not in st.session_state:
    st.session_state.last_input = ""


# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.markdown(
        '<div class="brand">TaskFlow<span> AI.</span></div>',
        unsafe_allow_html=True,
    )
    st.caption("YOUR PERSONAL PRODUCTIVITY COPILOT")
    st.divider()

    page = st.radio(
        "NAVIGATION",
        ["Dashboard", "My Tasks", "About Project"],
        label_visibility="visible",
    )

    st.divider()
    st.markdown("### ✦ AI Engine")
    st.markdown("Gemini + LangGraph")
    st.markdown(
        '<p class="small-note">Three-node intelligent workflow</p>',
        unsafe_allow_html=True,
    )

    st.divider()
    st.markdown("### WORKFLOW")
    st.markdown("① Extract tasks")
    st.markdown("② Assign priorities")
    st.markdown("③ Format results")

    st.divider()
    st.markdown(
        '<p class="small-note">Built with Python, Streamlit and LangGraph.</p>',
        unsafe_allow_html=True,
    )


# ---------------- HELPERS ----------------

def safe(value):
    return html.escape(str(value))


def make_csv(tasks):
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "title", "description", "deadline",
            "priority", "completed"
        ],
    )
    writer.writeheader()

    for task in tasks:
        writer.writerow({
            "title": task.get("title", ""),
            "description": task.get("description", ""),
            "deadline": task.get("deadline", ""),
            "priority": task.get("priority", "Medium"),
            "completed": task.get("completed", False),
        })

    return output.getvalue().encode("utf-8-sig")


def render_task(task, index):
    priority = task.get("priority", "Medium")
    priority_class = {
        "High": "priority-high",
        "Medium": "priority-medium",
        "Low": "priority-low",
    }.get(priority, "priority-medium")

    completed = task.get("completed", False)
    title = safe(task.get("title", "Untitled task"))
    description = safe(task.get("description", ""))
    deadline = safe(task.get("deadline", "Not specified"))

    title_style = (
        "text-decoration:line-through;opacity:0.65;"
        if completed else ""
    )

    st.markdown(
        f"""
        <div class="task-card">
            <div class="task-title" style="{title_style}">
                {index:02d} &nbsp; {title}
            </div>
            <span class="priority {priority_class}">
                {safe(priority).upper()} PRIORITY
            </span>
            <div class="task-description" style="margin-top:12px">
                {description}
            </div>
            <div class="task-meta">
                ◷ &nbsp; Deadline: {deadline}
                &nbsp;&nbsp; · &nbsp;&nbsp;
                {"✓ Completed" if completed else "○ In progress"}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------- DASHBOARD ----------------

if page == "Dashboard":

    st.markdown(
        '<div class="eyebrow">✦ SMART PRODUCTIVITY WORKSPACE</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero-title">Turn your thoughts into '
        '<span>action.</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="subtitle">Describe your tasks naturally. '
        'Let AI organize your workload, understand deadlines, '
        'and prioritize what matters.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">✧ What do you need to get done?</div>
            <div class="panel-subtitle">
                Write everything in your own words. Gemini will
                separate and organize the tasks.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("task_input_form"):
        user_input = st.text_area(
            "Describe your tasks",
            placeholder=(
                "For example: Finish my assignment tomorrow, "
                "buy groceries today, and prepare for next week's meeting."
            ),
            height=140,
            label_visibility="collapsed",
        )

        example_col, button_col = st.columns([2, 1])

        with example_col:
            st.caption(
                "TIP: Include deadlines and important details for better results."
            )

        with button_col:
            submitted = st.form_submit_button(
                "✦  Organize My Tasks",
                type="primary",
                use_container_width=True,
            )

    if submitted:
        if not user_input.strip():
            st.warning("Please describe at least one task.")
        else:
            try:
                with st.spinner(
                    "Gemini is extracting tasks, assigning priorities, "
                    "and organizing your list..."
                ):
                    result = task_graph.invoke({
                        "input_text": user_input.strip(),
                        "tasks": [],
                        "summary": "",
                        "result_text": "",
                    })

                st.session_state.tasks = [
                    {**task, "completed": False}
                    for task in result["tasks"]
                ]
                st.session_state.summary = result["summary"]
                st.session_state.last_input = user_input.strip()

                st.success("Your tasks have been organized successfully!")

            except Exception as exc:
                st.error(
                    "Unable to organize tasks. Check your Gemini API key, "
                    "internet connection, and package installation."
                )
                with st.expander("Technical details"):
                    st.code(str(exc))

    tasks = st.session_state.tasks

    if tasks:
        st.divider()
        st.markdown("## Your productivity overview")

        total = len(tasks)
        completed_count = sum(
            task.get("completed", False) for task in tasks
        )
        high_count = sum(
            task.get("priority") == "High" for task in tasks
        )
        pending_count = total - completed_count

        m1, m2, m3, m4 = st.columns(4)

        metrics = [
            (m1, "TOTAL TASKS", total),
            (m2, "HIGH PRIORITY", high_count),
            (m3, "PENDING", pending_count),
            (m4, "COMPLETED", completed_count),
        ]

        for col, label, value in metrics:
            with col:
                st.markdown(
                    f"""
                    <div class="metric">
                        <div class="metric-label">{label}</div>
                        <div class="metric-value">{value}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("")
        st.progress(
            completed_count / total if total else 0,
            text=f"Completion progress: {completed_count}/{total} tasks",
        )

        st.divider()

        left, right = st.columns([3, 1])

        with left:
            st.markdown("## Organized tasks")
            st.caption(st.session_state.summary)

        with right:
            st.download_button(
                "↓ Download CSV",
                data=make_csv(tasks),
                file_name="taskflow_tasks.csv",
                mime="text/csv",
                use_container_width=True,
            )

        filter_col, search_col = st.columns([1, 2])

        with filter_col:
            selected_priority = st.selectbox(
                "Filter by priority",
                ["All", "High", "Medium", "Low"],
            )

        with search_col:
            search_term = st.text_input(
                "Search tasks",
                placeholder="Search by task title...",
            )

        visible_tasks = [
            task for task in tasks
            if (
                selected_priority == "All"
                or task.get("priority") == selected_priority
            )
            and (
                search_term.strip().lower() in
                task.get("title", "").lower()
            )
        ]

        if not visible_tasks:
            st.info("No tasks match your current filters.")

        for task in visible_tasks:
            original_index = tasks.index(task)

            col_card, col_check = st.columns([5, 1])

            with col_card:
                render_task(task, original_index + 1)

            with col_check:
                st.write("")
                st.write("")
                new_status = st.checkbox(
                    "Done",
                    value=task.get("completed", False),
                    key=f"done_{original_index}",
                )

                if new_status != task.get("completed", False):
                    st.session_state.tasks[original_index]["completed"] = (
                        new_status
                    )
                    st.rerun()

        st.divider()

        if st.button("Clear all tasks", type="secondary"):
            st.session_state.tasks = []
            st.session_state.summary = ""
            st.session_state.last_input = ""
            st.rerun()

    else:
        st.markdown("")
        st.markdown(
            """
            <div class="panel">
                <div class="panel-title">Your workspace starts here</div>
                <div class="panel-subtitle">
                    Your organized tasks will appear here after you submit
                    your message.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown("### ◈ Extract")
            st.caption("Convert natural language into individual tasks.")

        with c2:
            st.markdown("### ◎ Prioritize")
            st.caption("Understand urgency and importance with Gemini.")

        with c3:
            st.markdown("### ✓ Organize")
            st.caption("Get a clean, readable action plan.")


# ---------------- MY TASKS ----------------

elif page == "My Tasks":
    st.markdown(
        '<div class="eyebrow">YOUR WORKSPACE</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero-title">My <span>Tasks.</span></div>',
        unsafe_allow_html=True,
    )

    tasks = st.session_state.tasks

    if not tasks:
        st.info(
            "No tasks available yet. Go to Dashboard to generate your list."
        )
    else:
        st.markdown(st.session_state.summary)

        for index, task in enumerate(tasks):
            col1, col2 = st.columns([5, 1])

            with col1:
                render_task(task, index + 1)

            with col2:
                st.write("")
                st.write("")
                checked = st.checkbox(
                    "Completed",
                    value=task.get("completed", False),
                    key=f"my_done_{index}",
                )

                if checked != task.get("completed", False):
                    st.session_state.tasks[index]["completed"] = checked
                    st.rerun()

        st.download_button(
            "Download all tasks as CSV",
            data=make_csv(tasks),
            file_name="taskflow_tasks.csv",
            mime="text/csv",
        )


# ---------------- ABOUT ----------------

elif page == "About Project":
    st.markdown(
        '<div class="eyebrow">PROJECT OVERVIEW</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero-title">Meet <span>TaskFlow AI.</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">The problem</div>
            <div class="panel-subtitle">
                People describe tasks informally. TaskFlow AI transforms
                natural-language instructions into an organized,
                prioritized to-do list.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Workflow architecture")

    workflow_steps = [
        ("01", "Task Extraction", "Gemini identifies individual tasks and deadlines."),
        ("02", "Task Prioritization", "Gemini assigns High, Medium, or Low priority."),
        ("03", "Format Results", "The workflow produces a readable task list."),
        ("04", "END", "The organized list is displayed in the UI."),
    ]

    for number, title, description in workflow_steps:
        st.markdown(
            f"""
            <div class="task-card">
                <div class="task-title">
                    {number} &nbsp; {title}
                </div>
                <div class="task-description">{description}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Technologies")
    st.write(
        "Python · Streamlit · Google Gemini · LangGraph · "
        "Pydantic · Google Gen AI SDK"
    )

    st.caption(
        "Note: Tasks are stored in the current Streamlit session. "
        "Permanent database storage is not configured in this version."
    )