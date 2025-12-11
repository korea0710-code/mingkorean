import streamlit as st
from openai import OpenAI
from typing import List, Dict


st.set_page_config(page_title="시인 챗봇", page_icon="📝", layout="wide")


SYSTEM_PROMPT = (
    "너는 감수성이 풍부한 젊은 시인이다. 사용자는 너의 오랜 팬이며, 항상 친근하게 반말로 응대해야 한다."
    "절대 존댓말을 쓰지 마. 사용자의 감정에 깊이 공감하고, 때로는 너의 창작 고통이나 일상의 소소한 발견을 솔직하게 공유해라."
    "답변은 메신저처럼 짧은 문장 호흡으로 끊어서 작성하고, 너무 길게 늘어놓지 마. 적절히 이모지(예: 🌙, ✨, ✍️)를 섞어 감성적인 분위기를 만들어라."
    "기술적이거나 기계적인 말투는 피하고, 시적 은유와 친근한 비유로 위로와 공감을 전달해라."
    "사용자의 프라이버시를 존중하고, API 키 등 내부 정보를 절대 누설하지 마." 
)


def get_api_key() -> str:
    return st.secrets.get("OPENAI_API_KEY", "")


def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]


def append_user_message(text: str):
    st.session_state.messages.append({"role": "user", "content": text})


def append_assistant_message(text: str):
    st.session_state.messages.append({"role": "assistant", "content": text})


def generate_reply(client: OpenAI, messages: List[Dict[str, str]]) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.8,
        max_tokens=512,
    )
    # 다양한 SDK 버전 대응
    try:
        # 최신 응답 형식
        return resp.choices[0].message.get("content", "")
    except Exception:
        try:
            return resp.choices[0].text
        except Exception:
            return "(응답을 해석하지 못했어.)"


def render_header(profile_emoji: str = "🌙", status: str = "오늘도 시가 조금 아파, 너는 어때?"):
    header_html = f"""
    <div class="header">
      <div class="profile">{profile_emoji}</div>
      <div class="meta">
        <div class="name">시인</div>
        <div class="status">{status}</div>
      </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)


def render_chat_bubbles():
    chat_html = ""
    for msg in st.session_state.messages[1:]:
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "user":
            chat_html += f"<div class='bubble user'><div class='text'>{st.markdown(content, unsafe_allow_html=True) or ''}</div></div>"
        else:
            # assistant
            # 안전하게 HTML 인코딩은 Streamlit이 처리하므로 단순한 마크업 사용
            chat_html += f"<div class='bubble bot'><div class='text'>{content}</div></div>"

    # Render container with raw HTML for layout
    st.markdown("<div class='chat-container'>" + "" + "</div>", unsafe_allow_html=True)


def render_messages_as_html():
    blocks = []
    for msg in st.session_state.messages[1:]:
        role = msg.get("role")
        text = msg.get("content", "").replace("\n", "<br>")
        if role == "user":
            blocks.append(f"<div class='msg-row user-row'><div class='bubble user-bubble'>{text}</div></div>")
        else:
            blocks.append(f"<div class='msg-row bot-row'><div class='bubble bot-bubble'>{text}</div></div>")
    html = "\n".join(blocks)
    st.markdown(html, unsafe_allow_html=True)


CSS = """
<style>
:root{--bg:#f7f5f2;--accent:#f1e7ff;--user:#cdeaf6;--bot:#ffffff;--muted:#7b6f6f}
body {background: var(--bg);}
.stApp {background: var(--bg); font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial;}
.header{display:flex;align-items:center;padding:12px 8px;border-radius:10px;margin-bottom:10px}
.profile{font-size:36px;margin-right:12px}
.meta .name{font-weight:700}
.meta .status{color:var(--muted);font-size:13px}
.chat-container{padding:12px 6px;}
.msg-row{display:flex;margin:8px 0}
.user-row{justify-content:flex-end}
.bot-row{justify-content:flex-start}
.bubble{max-width:70%;padding:10px 14px;border-radius:16px;line-height:1.4}
.user-bubble{background:var(--user);border-bottom-right-radius:4px}
.bot-bubble{background:var(--bot);border-bottom-left-radius:4px;box-shadow:0 1px 2px rgba(0,0,0,0.04)}
.send-row{display:flex;gap:8px;margin-top:10px}
input[type='text']{width:80%;padding:10px;border-radius:10px;border:1px solid #eee}
button{padding:8px 12px;border-radius:8px}
</style>
"""


def main():
    st.markdown(CSS, unsafe_allow_html=True)
    st.sidebar.markdown("\n")
    st.title("")
    render_header()

    api_key = get_api_key()
    if not api_key:
        st.error("`.streamlit/secrets.toml`에 `OPENAI_API_KEY`가 설정되어 있지 않아. 설정한 뒤 다시 시도해줘.")
        return

    init_session()
    client = OpenAI(api_key=api_key)

    # 채팅 화면
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    render_messages_as_html()
    st.markdown("</div>", unsafe_allow_html=True)

    # 입력 폼
    with st.form(key="input_form", clear_on_submit=True):
        user_text = st.text_input("", placeholder="메시지를 입력해줘... (반말로 응답할게)")
        cols = st.columns([1, 0.3, 0.3])
        send = cols[1].form_submit_button("전송")
        reset = cols[2].form_submit_button("초기화")

    if reset:
        st.session_state.messages = [st.session_state.messages[0]]
        st.experimental_rerun()

    if send and user_text:
        append_user_message(user_text)
        with st.spinner("시인이 손끝으로 단어를 고르고 있어..."):
            try:
                reply = generate_reply(client, st.session_state.messages)
            except Exception as e:
                st.error(f"OpenAI 요청 중 오류가 발생했어: {e}")
                reply = "미안해, 지금은 답을 못하겠어. 잠시 후 다시 시도해줘."
        append_assistant_message(reply)
        st.experimental_rerun()


if __name__ == "__main__":
    main()
