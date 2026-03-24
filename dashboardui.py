"""
dashboardui.py - WhatsApp-style Persona Cloak Command Center
Integrated with: BaitGenerator, ChatEngine, ScamGenerator, Safety, RateLimiter, DB
"""

import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import time
import sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bait_generator import BaitGenerator
from core.chat_engine import ChatEngine
from scam_generator import generate_scam
from scam_templates import generate_template, TEMPLATES
from safety import safety_check, SAFE_WATERMARK
from rate_limiter import RateLimiter
from logging_config import get_logger
from core.database_module import save_profile, init_db

# ─── Init ────────────────────────────────────────────────────────────────────
init_db()
logger = get_logger()
limiter = RateLimiter(max_requests=20, window_seconds=60)
bait_gen = BaitGenerator()
chat_engine = ChatEngine()

TRAITS = [
    "high_neuroticism",
    "high_agreeableness",
    "high_extraversion",
    "low_conscientiousness",
    "high_openness",
    "average",
]

SCAM_KINDS = list(TEMPLATES.keys())

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Persona Cloak",
    page_icon="🛡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── WhatsApp-style CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #111b21 !important;
    color: #e9edef !important;
    font-family: 'Segoe UI', sans-serif;
}
[data-testid="stSidebar"] { background: #202c33 !important; }

/* ── Header bar ── */
.wa-header {
    background: #202c33;
    padding: 12px 20px;
    border-radius: 10px 10px 0 0;
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 0;
}
.wa-avatar {
    width: 42px; height: 42px;
    border-radius: 50%;
    background: #00a884;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
}
.wa-name { font-weight: 600; font-size: 16px; color: #e9edef; }
.wa-status { font-size: 12px; color: #8696a0; }

/* ── Chat window ── */
.chat-window {
    background: #0b141a;
    background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23182229' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    min-height: 420px;
    max-height: 420px;
    overflow-y: auto;
    padding: 16px;
    border-left: 1px solid #2a3942;
    border-right: 1px solid #2a3942;
}

/* ── Bubbles ── */
.bubble-out {
    display: flex; justify-content: flex-end; margin: 6px 0;
}
.bubble-out .bubble-body {
    background: #005c4b;
    color: #e9edef;
    padding: 8px 12px;
    border-radius: 12px 0px 12px 12px;
    max-width: 65%;
    font-size: 14px;
    position: relative;
}
.bubble-in {
    display: flex; justify-content: flex-start; margin: 6px 0;
}
.bubble-in .bubble-body {
    background: #202c33;
    color: #e9edef;
    padding: 8px 12px;
    border-radius: 0px 12px 12px 12px;
    max-width: 65%;
    font-size: 14px;
}
.bubble-meta {
    font-size: 10px;
    color: #8696a0;
    margin-top: 3px;
    text-align: right;
}
.bubble-sender {
    font-size: 11px;
    color: #00a884;
    font-weight: 600;
    margin-bottom: 2px;
}

/* ── Input bar ── */
.wa-input-bar {
    background: #202c33;
    padding: 10px 16px;
    border-radius: 0 0 10px 10px;
    border-top: 1px solid #2a3942;
}

/* ── Sidebar list item ── */
.contact-item {
    background: #202c33;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 6px;
    cursor: pointer;
    border-left: 3px solid #00a884;
}
.contact-item:hover { background: #2a3942; }

/* ── Metric cards ── */
.metric-card {
    background: #202c33;
    border-radius: 10px;
    padding: 14px 18px;
    text-align: center;
    border-top: 3px solid #00a884;
}
.metric-val { font-size: 28px; font-weight: 700; color: #00a884; }
.metric-lbl { font-size: 12px; color: #8696a0; margin-top: 2px; }

/* ── Buttons ── */
div.stButton > button {
    background: #00a884 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 20px !important;
    padding: 6px 20px !important;
    font-weight: 600 !important;
}
div.stButton > button:hover {
    background: #017561 !important;
}

/* ── Selectbox / text input ── */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div > input {
    background: #2a3942 !important;
    color: #e9edef !important;
    border-color: #3b4a54 !important;
    border-radius: 8px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #111b21; }
::-webkit-scrollbar-thumb { background: #374045; border-radius: 4px; }

/* ── Safety badge ── */
.badge-ok   { background:#00a884; color:#fff; padding:2px 8px; border-radius:10px; font-size:11px; }
.badge-fail { background:#e74c3c; color:#fff; padding:2px 8px; border-radius:10px; font-size:11px; }

/* ── Section label ── */
.section-label {
    font-size: 11px;
    color: #8696a0;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 10px 0 4px 0;
}
</style>
""", unsafe_allow_html=True)

# ─── Session state ────────────────────────────────────────────────────────────
for key, default in {
    "chat_history": [],
    "profile": None,
    "trait": TRAITS[0],
    "total_sessions": 0,
    "total_messages": 0,
    "safety_blocks": 0,
    "input_key": 0,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Helpers ─────────────────────────────────────────────────────────────────
def ts():
    return time.strftime("%H:%M")

def render_bubble(sender, text, outgoing=False):
    side = "bubble-out" if outgoing else "bubble-in"
    sender_html = "" if outgoing else f"<div class='bubble-sender'>{sender}</div>"
    return f"""
    <div class='{side}'>
      <div class='bubble-body'>
        {sender_html}
        {text}
        <div class='bubble-meta'>{ts()} {'✓✓' if outgoing else ''}</div>
      </div>
    </div>"""

def render_radar(scores: dict):
    labels = [k.capitalize() for k in scores]
    vals = list(scores.values()) + [list(scores.values())[0]]
    lbls = labels + [labels[0]]
    fig = go.Figure(go.Scatterpolar(
        r=vals, theta=lbls, fill='toself',
        line_color='#00a884', fillcolor='rgba(0,168,132,0.2)'
    ))
    fig.update_layout(
        polar=dict(
            bgcolor='#0b141a',
            radialaxis=dict(visible=True, range=[0, 1],
                            gridcolor='#2a3942', color='#8696a0'),
            angularaxis=dict(gridcolor='#2a3942', color='#e9edef')
        ),
        paper_bgcolor='#111b21',
        plot_bgcolor='#111b21',
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        height=260,
    )
    return fig

# ─── Layout ───────────────────────────────────────────────────────────────────
# Top header
st.markdown("""
<div class='wa-header'>
  <div class='wa-avatar'>🛡</div>
  <div>
    <div class='wa-name'>Persona Cloak — Command Center</div>
    <div class='wa-status'>Scam Simulation Lab · Research Mode</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── Metric row ────────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-val'>{st.session_state.total_sessions}</div>
        <div class='metric-lbl'>Sessions</div></div>""", unsafe_allow_html=True)
with m2:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-val'>{st.session_state.total_messages}</div>
        <div class='metric-lbl'>Messages</div></div>""", unsafe_allow_html=True)
with m3:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-val'>{len(st.session_state.chat_history)}</div>
        <div class='metric-lbl'>This Chat</div></div>""", unsafe_allow_html=True)
with m4:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-val'>{st.session_state.safety_blocks}</div>
        <div class='metric-lbl'>Safety Blocks</div></div>""", unsafe_allow_html=True)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ── Main columns ──────────────────────────────────────────────────────────────
left, mid, right = st.columns([1, 1.6, 1.1])

# ══════════════════════════════════════════════════════════════════════════════
# LEFT — Profile Generator
# ══════════════════════════════════════════════════════════════════════════════
with left:
    st.markdown("<div class='section-label'>🎭 Bait Profile</div>", unsafe_allow_html=True)

    trait = st.selectbox("Personality Trait", TRAITS, key="trait_select",
                         label_visibility="collapsed")

    gen_btn = st.button("✨ Generate Profile", use_container_width=True)

    if gen_btn:
        allowed, wait = limiter.allow("profile_gen")
        if not allowed:
            st.error(f"Rate limit hit. Wait {wait}s.")
        else:
            with st.spinner("Generating…"):
                profile = bait_gen.generate_profile(trait)
                st.session_state.profile = profile
                st.session_state.trait = trait
                st.session_state.chat_history = []
                st.session_state.total_sessions += 1
                logger.info(f"Profile generated | trait={trait}")

                # Save to DB (map keys to what DB expects)
                scores = profile.get("personality_scores", {})
                save_profile({
                    "bio": profile["bio"],
                    "personality": {
                        "openness": scores.get("openness", 0.5),
                        "conscientiousness": scores.get("conscientiousness", 0.5),
                        "extraversion": scores.get("extraversion", 0.5),
                        "agreeableness": scores.get("agreeableness", 0.5),
                        "neuroticism": scores.get("neuroticism", 0.5),
                    }
                })

    if st.session_state.profile:
        p = st.session_state.profile
        demo = p.get("demographics", {})
        scores = p.get("personality_scores", {})

        # Contact card
        st.markdown(f"""
        <div class='contact-item'>
          <div style='font-weight:600;font-size:15px'>
            {demo.get('name','Unknown')}
          </div>
          <div style='font-size:12px;color:#8696a0'>
            {demo.get('occupation','')} · {demo.get('location','')} · Age {demo.get('age','')}
          </div>
          <div style='font-size:12px;color:#8696a0;margin-top:4px'>
            🎯 {st.session_state.trait.replace('_',' ').title()}
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='section-label'>📝 Bio</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:13px;color:#e9edef;background:#202c33;"
                    f"padding:10px;border-radius:8px'>{p['bio']}</div>",
                    unsafe_allow_html=True)

        st.markdown("<div class='section-label'>📊 Personality Radar</div>",
                    unsafe_allow_html=True)
        st.plotly_chart(render_radar(scores), use_container_width=True,
                        config={"displayModeBar": False})

        # Score bars
        for k, v in scores.items():
            pct = int(v * 100)
            color = "#00a884" if v > 0.6 else ("#e74c3c" if v < 0.35 else "#f39c12")
            st.markdown(f"""
            <div style='margin:3px 0'>
              <div style='display:flex;justify-content:space-between;
                          font-size:11px;color:#8696a0'>
                <span>{k.capitalize()}</span><span>{pct}%</span>
              </div>
              <div style='background:#2a3942;border-radius:4px;height:5px'>
                <div style='width:{pct}%;background:{color};
                            height:5px;border-radius:4px'></div>
              </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("<div style='color:#8696a0;font-size:13px;padding:10px'>"
                    "Generate a profile to start a simulation.</div>",
                    unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MIDDLE — WhatsApp Chat
# ══════════════════════════════════════════════════════════════════════════════
with mid:
    # Chat header
    if st.session_state.profile:
        demo = st.session_state.profile.get("demographics", {})
        name = demo.get("name", "Bait Profile")
        status = f"🟢 {st.session_state.trait.replace('_',' ').title()}"
    else:
        name = "No profile loaded"
        status = "⚪ Idle"

    st.markdown(f"""
    <div class='wa-header' style='border-radius:10px 10px 0 0;margin-bottom:0'>
      <div class='wa-avatar'>👤</div>
      <div>
        <div class='wa-name'>{name}</div>
        <div class='wa-status'>{status}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Chat bubbles — use components.html to guarantee HTML renders, never leaks as text
    bubble_styles = """
    <style>
    body { margin:0; background:#0b141a; font-family:'Segoe UI',sans-serif; }
    .chat-window {
        min-height:400px; max-height:400px; overflow-y:auto;
        padding:16px;
        background:#0b141a;
    }
    .bubble-out { display:flex; justify-content:flex-end; margin:6px 0; }
    .bubble-out .bubble-body {
        background:#005c4b; color:#e9edef;
        padding:8px 12px; border-radius:12px 0 12px 12px;
        max-width:65%; font-size:14px;
    }
    .bubble-in { display:flex; justify-content:flex-start; margin:6px 0; }
    .bubble-in .bubble-body {
        background:#202c33; color:#e9edef;
        padding:8px 12px; border-radius:0 12px 12px 12px;
        max-width:65%; font-size:14px;
    }
    .bubble-meta { font-size:10px; color:#8696a0; margin-top:3px; text-align:right; }
    .bubble-sender { font-size:11px; color:#00a884; font-weight:600; margin-bottom:2px; }
    .empty-state { text-align:center; color:#8696a0; font-size:13px; padding-top:40px; }
    </style>
    """

    bubbles_html = bubble_styles + "<div class='chat-window'>"
    if not st.session_state.chat_history:
        bubbles_html += ("<div class='empty-state'>🔒 Messages are end-to-end encrypted"
                         "<br><small>Simulation mode only</small></div>")
    for msg in st.session_state.chat_history:
        outgoing = msg["sender"] == "Scammer"
        side = "bubble-out" if outgoing else "bubble-in"
        sender_tag = "" if outgoing else f"<div class='bubble-sender'>{msg['sender']}</div>"
        tick = "✓✓" if outgoing else ""
        bubbles_html += (
            f"<div class='{side}'><div class='bubble-body'>"
            f"{sender_tag}{msg['text']}"
            f"<div class='bubble-meta'>{ts()} {tick}</div>"
            f"</div></div>"
        )
    bubbles_html += "<div id='bottom'></div></div>"
    bubbles_html += "<script>document.getElementById('bottom').scrollIntoView();</script>"

    components.html(bubbles_html, height=420, scrolling=False)

    # Input bar — no wrapping div tags (Streamlit renders them as text)
    if st.session_state.profile:
        col_inp, col_send = st.columns([5, 1])
        with col_inp:
            user_msg = st.text_input(
                "message", placeholder="Type a message…",
                label_visibility="collapsed",
                key=f"msg_input_{st.session_state.input_key}"
            )
        with col_send:
            send = st.button("➤", use_container_width=True)

        if send and user_msg.strip():
            allowed, wait = limiter.allow("chat")
            if not allowed:
                st.error(f"Rate limit. Wait {wait}s.")
            else:
                # Only block real harmful content (links, emails, phones, payment words)
                # Don't require watermark for plain user chat messages
                import re
                LINK_RE = re.compile(r"https?://", re.I)
                EMAIL_RE = re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w+\b")
                PHONE_RE = re.compile(r"\b(\+?\d[\d\s-]{7,}\d)\b")
                PAYMENT_RE = re.compile(r"(upi|bank|otp|crypto|bitcoin|wallet)", re.I)

                blocked = False
                block_reason = ""
                if LINK_RE.search(user_msg):
                    blocked, block_reason = True, "Links not allowed in simulation"
                elif EMAIL_RE.search(user_msg):
                    blocked, block_reason = True, "Emails blocked"
                elif PHONE_RE.search(user_msg):
                    blocked, block_reason = True, "Phone numbers blocked"
                elif PAYMENT_RE.search(user_msg):
                    blocked, block_reason = True, "Payment keywords blocked"

                if blocked:
                    st.session_state.safety_blocks += 1
                    st.warning(f"🚫 Safety block: {block_reason}")
                    logger.warning(f"Safety block | {block_reason} | {user_msg[:60]}")
                else:
                    st.session_state.chat_history.append(
                        {"sender": "Scammer", "text": user_msg}
                    )
                    st.session_state.total_messages += 1
                    logger.info(f"Scammer msg | {user_msg[:60]}")

                    scores = st.session_state.profile.get("personality_scores", {})
                    reply = chat_engine.generate_chat_response(scores, user_msg)

                    st.session_state.chat_history.append(
                        {"sender": name, "text": reply}
                    )
                    st.session_state.total_messages += 1
                    logger.info(f"Profile reply | {reply[:60]}")
                    st.session_state.input_key += 1
                    st.rerun()
    else:
        st.markdown("<div style='color:#8696a0;font-size:13px;padding:6px'>"
                    "Generate a profile first to enable chat.</div>",
                    unsafe_allow_html=True)

    # Quick scam buttons
    if st.session_state.profile:
        st.markdown("<div class='section-label'>⚡ Quick Scam Inject</div>",
                    unsafe_allow_html=True)
        qc1, qc2, qc3 = st.columns(3)
        quick_scams = {
            "🎰 Random": None,
            "🎣 Phishing": "phishing",
            "💘 Romance": "romance",
        }
        for col, (label, kind) in zip([qc1, qc2, qc3], quick_scams.items()):
            with col:
                if st.button(label, use_container_width=True):
                    if kind is None:
                        msg = generate_scam()
                    else:
                        tpl = generate_template(kind)
                        msg = tpl["message"]

                    scores = st.session_state.profile.get("personality_scores", {})
                    reply = chat_engine.generate_chat_response(scores, msg)

                    st.session_state.chat_history.append(
                        {"sender": "Scammer", "text": msg}
                    )
                    st.session_state.chat_history.append(
                        {"sender": name if st.session_state.profile else "Profile",
                         "text": reply}
                    )
                    st.session_state.total_messages += 2
                    logger.info(f"Quick inject | kind={kind or 'random'}")
                    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# RIGHT — Controls & Analytics
# ══════════════════════════════════════════════════════════════════════════════
with right:
    st.markdown("<div class='section-label'>🎣 Scam Templates</div>",
                unsafe_allow_html=True)

    kind = st.selectbox("Template type", SCAM_KINDS,
                        label_visibility="collapsed", key="tpl_kind")

    if st.button("📋 Load Template", use_container_width=True):
        tpl = generate_template(kind)
        st.session_state["loaded_template"] = tpl["message"]

    if "loaded_template" in st.session_state:
        st.markdown(
            f"<div style='background:#202c33;border-radius:8px;padding:10px;"
            f"font-size:12px;color:#e9edef;margin-bottom:8px'>"
            f"{st.session_state['loaded_template']}</div>",
            unsafe_allow_html=True
        )
        ok, reason = safety_check(st.session_state["loaded_template"])
        badge = (f"<span class='badge-ok'>✓ {reason}</span>"
                 if ok else f"<span class='badge-fail'>✗ {reason}</span>")
        st.markdown(f"Safety: {badge}", unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-label'>🔬 Personality Analysis</div>",
                unsafe_allow_html=True)

    analyze_text = st.text_area(
        "Paste text to analyze", height=80,
        placeholder="Paste any text to detect personality…",
        label_visibility="collapsed"
    )
    if st.button("🧠 Analyze Text", use_container_width=True) and analyze_text:
        detected = chat_engine.analyze_personality_from_text(analyze_text)
        st.plotly_chart(render_radar(detected), use_container_width=True,
                        config={"displayModeBar": False})
        for k, v in detected.items():
            pct = int(v * 100)
            st.markdown(
                f"<div style='font-size:12px;color:#8696a0'>"
                f"{k.capitalize()}: <b style='color:#00a884'>{pct}%</b></div>",
                unsafe_allow_html=True
            )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-label'>⚙️ Session</div>",
                unsafe_allow_html=True)

    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    if st.button("🔄 New Session", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.profile = None
        st.rerun()

    # Rate limiter status
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-label'>📡 System Status</div>",
                unsafe_allow_html=True)

    allowed_probe, _ = limiter.allow("status_probe")
    status_color = "#00a884" if allowed_probe else "#e74c3c"
    st.markdown(
        f"<div style='font-size:12px;color:{status_color}'>"
        f"● Rate limiter: {'OK' if allowed_probe else 'Throttled'}</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='font-size:12px;color:#8696a0'>● DB: Connected</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='font-size:12px;color:#8696a0'>● Safety: Active</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='font-size:12px;color:#8696a0'>● Logger: Running</div>",
        unsafe_allow_html=True
    )
