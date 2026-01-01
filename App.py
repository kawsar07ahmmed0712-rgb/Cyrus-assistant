import streamlit as st
import uuid
import json
import subprocess
import sys
import os
from datetime import datetime
import re
import html as html_lib
from typing import List, Dict, Optional, Any


from config.settings import Settings
from core.prompt_controller import PromptBuilder
from core.memory import MemoryManager
from core.assistant import JarvisAssistant
from core.command_engine import CommandEngine
from core.utils import is_command

from core.gemini_engine import GeminiEngine
from core.ollama_engine import OllamaEngine


try:
    from core.voice_engine import VoiceEngine
    VOICE_AVAILABLE = True
except Exception:
    VoiceEngine = None
    VOICE_AVAILABLE = False


def now_str() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

def short_id() -> str:
    return uuid.uuid4().hex[:8]

def is_definition_question(text: str) -> bool:
    keywords = ["what is", "define", "definition of", "explain", "who is", "tell me about"]
    txt = (text or "").lower().strip()
    return any(txt.startswith(k) for k in keywords)

def run_python_code_safely(code: str, timeout: int = 10) -> Dict[str, str]:
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {"stdout": result.stdout, "stderr": result.stderr, "rc": str(result.returncode)}
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Execution timed out.", "rc": "-1"}
    except Exception as e:
        return {"stdout": "", "stderr": f"Execution failed: {e}", "rc": "-1"}

def safe_highlight(content: str, query: str) -> str:
    """
    Escape content safely and highlight 'query' occurrences (case-insensitive).
    Returns HTML string (with <br> for newlines).
    """
    if not content:
        return ""
    if not query:
        return html_lib.escape(content).replace("\n", "<br>")
    pat = re.compile(re.escape(query), flags=re.IGNORECASE)
    last = 0
    out = []
    for m in pat.finditer(content):
        out.append(html_lib.escape(content[last:m.start()]))
        out.append(f'<span style="background-color:#fff176;color:#000;">{html_lib.escape(m.group(0))}</span>')
        last = m.end()
    out.append(html_lib.escape(content[last:]))
    return "".join(out).replace("\n", "<br>")

def rerun():
    if hasattr(st, "rerun"):
        return st.rerun()
    if hasattr(st, "experimental_rerun"):
        return st.experimental_rerun()
    raise RuntimeError("Streamlit rerun is not available in this environment.")


st.set_page_config(page_title="Jarvis — Enhanced Assistant", layout="wide", page_icon="🤖")
st.title("Jarvis — Enhanced Assistant — More Features & Fascinating UI")


if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

bg_color = "#121212" if st.session_state.dark_mode else "#FFFFFF"
text_color = "#FFFFFF" if st.session_state.dark_mode else "#000000"
bubble_user_bg = "#1E88E5" if st.session_state.dark_mode else "#E8F5E9"
bubble_assist_bg = "#424242" if st.session_state.dark_mode else "#F4F6F8"
highlight_bg = "#FFEB3B" if st.session_state.dark_mode else "#fff176"
code_bg = "#333333" if st.session_state.dark_mode else "#f6f6f6"
code_text = "#FFFFFF" if st.session_state.dark_mode else "#000000"

st.markdown(
    f"""
    <style>
    /* Base theme */
    body {{ background-color: {bg_color}; color: {text_color}; }}
    .jarvis-bubble, .jarvis-bubble * {{ color: {text_color} !important; }}
    .jarvis-user {{ background: {bubble_user_bg}; color: {text_color}; }}
    .jarvis-assistant {{ background: {bubble_assist_bg}; color: {text_color}; }}
    /* Inputs */
    textarea, input, .stTextArea textarea, .stTextInput input {{ color: {text_color} !important; background-color: {bg_color}; }}
    /* Code blocks */
    pre, code {{ color: {code_text} !important; background: {code_bg} !important; }}
    /* Animations for bubbles */
    .jarvis-bubble {{ padding: 12px; border-radius: 12px; margin: 8px 0; animation: fadeIn 0.5s ease-in-out; }}
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    /* Highlight */
    span[style*="background-color:{highlight_bg}"] {{ background-color: {highlight_bg} !important; color: {text_color} !important; }}
    </style>
    """,
    unsafe_allow_html=True
)

settings = Settings()
memory = MemoryManager(file_path=settings.history_file, max_messages=1000)  # Increased max messages
commands = CommandEngine()

def load_engine():
    if settings.api_key:
        try:
            return GeminiEngine(api_key=settings.api_key, model_name=settings.gemini_model_name)
        except Exception:
            pass
    try:
        return OllamaEngine(base_url=settings.ollama_url)
    except Exception:
        return None

engine = load_engine()
engine_status = "Available" if engine else "Unavailable (set JARVIS_API_KEY or run Ollama)"

voice = VoiceEngine() if VOICE_AVAILABLE else None


if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "pending_compose_value" not in st.session_state:
    st.session_state.pending_compose_value = ""
if "editing_idx" not in st.session_state:
    st.session_state.editing_idx = None
if "copied_code" not in st.session_state:
    st.session_state.copied_code = ""
if "enable_code_execution" not in st.session_state:
    st.session_state.enable_code_execution = False
if "enable_voice_output" not in st.session_state:
    st.session_state.enable_voice_output = False
if "quick_prompts" not in st.session_state:
    st.session_state.quick_prompts = {
        "Explain simply": "Explain {topic} in simple terms with examples.",
        "Give steps": "Give step-by-step instructions to accomplish: {topic}",
        "Summarize": "Summarize {topic} concisely.",
        "Translate to English": "Translate the following to English: {topic}",
        "Generate ideas": "Brainstorm 5 creative ideas for {topic}.",
        "Debug code": "Debug and fix this code: {topic}",
    }  

with st.sidebar:
    st.header("Controls")
    st.checkbox("Dark mode", key="dark_mode", value=st.session_state.dark_mode, on_change=rerun)
    st.markdown(f"**Engine:** {engine_status}")
    role = st.selectbox("Role", ["tutor", "coding_assistant", "career_helper", "interviewer", "language_teacher", "math_tutor", "summarizer", "writer", "creative_writer", "researcher"])  # Added more roles
    tone = st.selectbox("Tone", ["friendly", "formal", "encouraging", "humorous", "concise", "enthusiastic", "professional"])  # Added more tones
    avoid_direct_default = st.checkbox("Avoid direct answers by default", value=False)
    st.checkbox("Enable voice output (if available)", key="enable_voice_output", value=st.session_state.enable_voice_output)
    st.checkbox("Allow code execution (dangerous)", key="enable_code_execution", value=st.session_state.enable_code_execution)
    st.slider("Code execution timeout (seconds)", min_value=5, max_value=30, value=10, key="code_timeout")  # New: adjustable timeout

    st.markdown("---")
    st.markdown("### Quick prompts")
    qp_choice = st.selectbox("Apply quick prompt", options=["_none_"] + list(st.session_state.quick_prompts.keys()))
    if qp_choice != "_none_":
        if st.button("Insert quick prompt"):
            st.session_state.pending_compose_value = st.session_state.quick_prompts[qp_choice]
            rerun()

    with st.form("add_qp_form", clear_on_submit=True):
        new_qp_name = st.text_input("Name")
        new_qp_text = st.text_area("Template", height=80)
        if st.form_submit_button("Save quick prompt"):
            if new_qp_name and new_qp_text:
                st.session_state.quick_prompts[new_qp_name] = new_qp_text
                st.success("Saved quick prompt")
            else:
                st.warning("Provide both name & template.")

    st.markdown("---")
    st.markdown("### Sessions")
    raw = memory._load()
    sessions = list(raw.get("sessions", {}).keys())
    session_ids_sorted = sorted(
        sessions,
        key=lambda s: (raw.get("sessions", {}).get(s, [{}])[-1].get("timestamp") if raw.get("sessions", {}).get(s) else ""),
        reverse=True
    )
    sel = st.selectbox("Open session", options=["_new_"] + session_ids_sorted, index=0)
    if sel == "_new_":
        if st.button("Create new session"):
            new_sid = str(uuid.uuid4())
            st.session_state.session_id = new_sid
            memory.clear_session(new_sid)
            st.balloons()  
            rerun()
    else:
        if sel != st.session_state.session_id:
            st.session_state.session_id = sel
            rerun()

    if st.button("Clear current session"):
        memory.clear_session(st.session_state.session_id)
        st.success("Cleared session")
        rerun()

    if st.button("Export current session"):
        ctx = memory.get_context(st.session_state.session_id)
        payload = {"session_id": st.session_state.session_id, "exported_at": now_str(), "messages": ctx}
        st.download_button("Download JSON", data=json.dumps(payload, indent=2), file_name=f"jarvis_{st.session_state.session_id[:8]}.json")

    if st.button("Summarize session"):  
        if engine is None:
            st.error("No engine available for summary.")
        else:
            ctx = memory.get_context(st.session_state.session_id)
            summary_prompt = "Summarize the following conversation concisely:\n" + "\n".join([f"{m['role']}: {m['content']}" for m in ctx])
            with st.spinner("Generating summary..."):
                try:
                    summary = engine.generate(summary_prompt, max_tokens=200)
                    memory.add_message(st.session_state.session_id, "system", f"Session summary: {summary}")
                    st.success("Summary added to session.")
                    rerun()
                except Exception as e:
                    st.error(f"Summary failed: {e}")

left, right = st.columns([3, 1])

with left:
    st.subheader("Conversation")
    messages = memory.get_context(st.session_state.session_id) or []


    search_text = st.text_input("Search in session", value="", key="search_text")
    role_filter = st.selectbox("Filter by role", options=["all", "user", "assistant", "system"], index=0, key="role_filter")
    show_only_pinned = st.checkbox("Only pinned", value=False, key="only_pinned")
    sort_order = st.selectbox("Sort by", ["timestamp (newest first)", "timestamp (oldest first)"], index=0)  # New: sort order

    def matches_search(msg: Dict[str, Any]) -> bool:
        if not search_text.strip():
            return True
        return search_text.lower() in (msg.get("content") or "").lower()

    filtered: List[tuple] = []
    for i, m in enumerate(messages):
        role_m = m.get("role", "user")
        pinned = m.get("pinned", False)
        if role_filter != "all" and role_m != role_filter:
            continue
        if show_only_pinned and not pinned:
            continue
        if not matches_search(m):
            continue
        filtered.append((i, m))


    if sort_order == "timestamp (oldest first)":
        filtered.sort(key=lambda x: messages[x[0]].get("timestamp", ""))

    for idx, msg in filtered:
        r = msg.get("role", "user")
        content = msg.get("content", "") or ""
        timestamp = msg.get("timestamp", "")
        pinned = msg.get("pinned", False)
        avatar = "👤" if r == "user" else "🤖" if r == "assistant" else "⚙️"  # New: avatars
        bubble_class = "jarvis-bubble jarvis-user" if r == "user" else "jarvis-bubble jarvis-assistant" if r == "assistant" else "jarvis-bubble"
        display_html = safe_highlight(content, search_text)

        st.markdown(
            f"<div style='display:flex;justify-content:space-between;align-items:center'>"
            f"<div style='font-weight:600'>{avatar} {html_lib.escape(r.capitalize())}</div>"
            f"<div style='font-size:12px;color:#666'>{html_lib.escape(timestamp)} {'🔖' if pinned else ''}</div>"
            f"</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            f"<div class='{bubble_class}' style='padding:10px;border-radius:8px;margin:6px 0;'>"
            f"{display_html}"
            f"</div>",
            unsafe_allow_html=True
        )

        if "```" in content:
            parts = content.split("```")
            for part_i in range(1, len(parts), 2):
                code_block = parts[part_i].strip()
                st.code(code_block, language="python")
                c1, c2 = st.columns([1, 1])
                with c1:
                    if st.button("Copy code", key=f"copy_{idx}_{part_i}"):
                        st.session_state.copied_code = code_block
                        st.success("Code copied to session clipboard.")
                with c2:
                    if st.button("Run code (local)", key=f"run_{idx}_{part_i}"):
                        if not st.session_state.enable_code_execution:
                            st.error("Code execution disabled in sidebar.")
                        else:
                            out = run_python_code_safely(code_block, timeout=st.session_state.code_timeout)
                            st.text_area("stdout", out.get("stdout", ""), height=120)
                            st.text_area("stderr", out.get("stderr", ""), height=60)
                            if out["rc"] == "0":
                                st.snow()  

        a1, a2, a3, a4, a5, a6 = st.columns([1,1,1,1,1,1])
        with a1:
            if st.button("✏️ Edit", key=f"edit_{idx}"):
                st.session_state.pending_compose_value = content
                st.session_state.editing_idx = idx
                rerun()
        with a2:
            if st.button("🗑️ Delete", key=f"del_{idx}"):
                all_data = memory._load()
                sess = all_data.get("sessions", {}).get(st.session_state.session_id, [])
                if 0 <= idx < len(sess):
                    sess.pop(idx)
                    all_data["sessions"][st.session_state.session_id] = sess
                    memory._save(all_data)
                    st.success("Message deleted.")
                    rerun()
        with a3:
            if st.button("📌 Pin" if not pinned else "📍 Unpin", key=f"pin_{idx}"):
                all_data = memory._load()
                sess = all_data.get("sessions", {}).get(st.session_state.session_id, [])
                if 0 <= idx < len(sess):
                    sess[idx]["pinned"] = not sess[idx].get("pinned", False)
                    all_data["sessions"][st.session_state.session_id] = sess
                    memory._save(all_data)
                    rerun()
        with a4:
            if r == "assistant":
                if st.button("🔄 Regenerate", key=f"regen_{idx}"):
                    all_data = memory._load()
                    sess = all_data.get("sessions", {}).get(st.session_state.session_id, [])
                    if 0 <= idx < len(sess) and sess[idx]["role"] == "assistant":
                        sess.pop(idx)
                        all_data["sessions"][st.session_state.session_id] = sess
                        memory._save(all_data)
                        rerun()
        with a5:
            if st.button("👍", key=f"up_{idx}"):
                all_data = memory._load()
                sess = all_data.get("sessions", {}).get(st.session_state.session_id, [])
                if 0 <= idx < len(sess):
                    sess[idx]["reaction"] = "up"
                    memory._save(all_data)
                    rerun()
        with a6:
            if st.button("👎", key=f"down_{idx}"):
                all_data = memory._load()
                sess = all_data.get("sessions", {}).get(st.session_state.session_id, [])
                if 0 <= idx < len(sess):
                    sess[idx]["reaction"] = "down"
                    memory._save(all_data)
                    rerun()

        st.markdown("---")

    if st.session_state.copied_code:
        st.info("Session clipboard: code available.")
        st.code(st.session_state.copied_code, language="python")

    st.markdown("### Compose")
    with st.form("composer_form"):
        initial = st.session_state.pending_compose_value or ""
        text = st.text_area("Message / question", value=initial, height=140)
        uploaded_file = st.file_uploader("Attach file (text only)", type=["txt", "md", "py"])  # New: file upload
        submitted = st.form_submit_button("Send")
        if submitted:
            text = (text or "").strip()
            file_content = ""
            if uploaded_file:
                file_content = uploaded_file.read().decode("utf-8")
                text += f"\n\nAttached file content:\n{file_content}"
            if not text:
                st.warning("Please type a message or upload a file.")
            else:
                if st.session_state.editing_idx is not None:
                    all_data = memory._load()
                    sess = all_data.get("sessions", {}).get(st.session_state.session_id, [])
                    idx = st.session_state.editing_idx
                    if 0 <= idx < len(sess):
                        sess[idx]["content"] = text
                        sess[idx]["edited_at"] = now_str()
                        all_data["sessions"][st.session_state.session_id] = sess
                        memory._save(all_data)
                        st.success("Message edited.")
                    else:
                        st.error("Edit index out of range.")
                    st.session_state.editing_idx = None
                    st.session_state.pending_compose_value = ""
                    rerun()
                else:
                    memory.add_message(st.session_state.session_id, "user", text)
                    st.session_state.pending_compose_value = ""
                    rerun()

with right:
    st.markdown("### Session info")
    ctx = memory.get_context(st.session_state.session_id)
    st.write(f"Messages: {len(ctx)}")
    if ctx:
        st.write(f"Last: {ctx[-1].get('timestamp','')}")
    st.markdown("---")
    st.markdown("### Prompt preview")
    last_msgs = memory.get_context(st.session_state.session_id)
    sample_topic = ""
    if last_msgs and last_msgs[-1].get("role") == "user":
        sample_topic = last_msgs[-1].get("content","")
    pb = PromptBuilder(topic=sample_topic or "<no topic>", tone=tone)
    pb.add_context_messages([m for m in last_msgs if m.get("role") in ("user","assistant")])
    try:
        preview_prompt = pb.build_for_definition() if is_definition_question(sample_topic) else pb.build(role)
    except Exception as e:
        preview_prompt = f"Prompt build failed: {e}"
    st.text_area("Prompt preview", value=preview_prompt, height=240)

    st.markdown("---")
    st.markdown("### Engine")
    st.write(f"Engine status: {engine_status}")
    if st.button("Test engine"):
        if engine is None:
            st.error("No engine available.")
        else:
            try:
                test = engine.generate("Say hello in one word.", max_tokens=10)
                st.success(f"Engine replied: {str(test)[:200]}")
            except Exception as e:
                st.error(f"Engine test failed: {e}")


msgs = memory.get_context(st.session_state.session_id)
if msgs and msgs[-1].get("role") == "user":
    recent = msgs[-3:] if len(msgs) >= 3 else msgs
    last_roles = [m.get("role") for m in recent]
    if "assistant" not in last_roles or last_roles[-1] != "assistant":
        last_user = msgs[-1].get("content","")
        if is_command(last_user):
            res = commands.execute(last_user)
            memory.add_message(st.session_state.session_id, "assistant", f"🧭 {res}")
            rerun()

        direct_needed = is_definition_question(last_user)
        pb = PromptBuilder(topic=last_user, tone=tone)
        pb.avoid_direct_answer = avoid_direct_default and (not direct_needed)
        pb.add_context_messages([m for m in msgs if m.get("role") in ("user","assistant")])
        role_to_use = "coding_assistant" if direct_needed else role
        final_prompt = pb.build(role_to_use)

        with st.spinner("Jarvis is thinking..."):
            if engine is None:
                ai_response = "No LLM engine available. Check configuration."
            else:
                assistant = JarvisAssistant(engine=engine, prompt_controller=pb, memory=memory)
                try:
                    ai_response = assistant.respond(final_prompt, max_tokens=512, temperature=0.0)
                except Exception as e:
                    ai_response = f"Model call failed: {e}"

            memory.add_message(st.session_state.session_id, "assistant", ai_response)

            if VOICE_AVAILABLE and st.session_state.enable_voice_output:
                try:
                    voice.speak(ai_response)
                except Exception:
                    pass

            st.balloons()  
            rerun()

st.markdown("---")
st.caption("Cyrus- dark mode, avatars, animations, file uploads, session summary, more prompts/roles/tones, adjustable timeouts, sort order, downvote.")