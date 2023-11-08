from dataclasses import dataclass
from typing import Literal
#pip install streamlit --user
import streamlit as st

#streamlit
#openai
#langchain
#dataclass
#typing_extensions


#pip install openai --user
#pip install langchain --user
#from langchain import OpenAI
import langchain
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationSummaryMemory
import streamlit.components.v1 as components

@dataclass
class Message:
    """Class for keeping track of a chat message."""
    origin: Literal["human", "ai"]
    message: str

def load_css():
    with open("static/styles.css", "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)

def generate_revised_content(content):
    response = OpenAI.completions.create(
        model="davinci",  # Your desired model
        prompt=content,
        max_tokens=30000,  # Extended for longer responses
        temperature=0.5,  # Adjust for creativity
        top_p=1,  # Control response diversity
        frequency_penalty=0,  # Fine-tune word frequency
        presence_penalty=0  # Fine-tune word presence
    )
    return response.choices[0].text

def initialize_session_state():
    if "history" not in st.session_state:
        st.session_state.history = []
    if "token_count" not in st.session_state:
        st.session_state.token_count = 0
    if "conversation" not in st.session_state:
        #llm = OpenAI(
        llm = OpenAI.ChatCompletion.create(
            temperature=0,
            #openai_api_key=st.secrets["openai_api_key"],
            openai_api_key="sk-sS5zs2j2MFysOcvh64vLT3BlbkFJDDanIvNwdKLKc08vMfu",
            model_name="text-davinci-003"
            #text-davinci-003：這是一個通用的文字模型，可以用來生成文字、翻譯語言、寫不同類型的創意內容等
            #code-davinci-002：這是一個程式碼生成模型，可以用來生成程式碼、翻譯程式碼、寫不同類型的程式碼等
            #summarization-davinci-002：這是一個文字摘要模型，可以用來生成文字摘要、翻譯文字摘要、寫不同類型的文字摘要等pip install --upgrade openai
        )
        st.session_state.conversation = ConversationChain(
            llm=llm,
            memory=ConversationSummaryMemory(llm=llm),
        )

def on_click_callback():
    with get_openai_callback() as cb:
        human_prompt = st.session_state.human_prompt
        llm_response = st.session_state.conversation.run(
            human_prompt
        )
        st.session_state.history.append(
            Message("human", human_prompt)
        )
        st.session_state.history.append(
            Message("ai", llm_response)
        )
        st.session_state.token_count += cb.total_tokens

load_css()
#initialize_session_state()
st.session_state.history = []
st.session_state.token_count = 0
st.session_state.conversation = None



st.title("您好，我是小智，您的購物好幫手 🤖")

chat_placeholder = st.container()
prompt_placeholder = st.form("chat-form")
credit_card_placeholder = st.empty()

with chat_placeholder:
    for chat in st.session_state.history:
        div = f"""
<div class="chat-row 
    {'' if chat.origin == 'ai' else 'row-reverse'}">
    <img class="chat-icon" src="app/static/{
        'ai_icon.png' if chat.origin == 'ai' 
                      else 'user_icon.png'}"
         width=32 height=32>
    <div class="chat-bubble
    {'ai-bubble' if chat.origin == 'ai' else 'human-bubble'}">
        &#8203;{chat.message}
    </div>
</div>
        """
        st.markdown(div, unsafe_allow_html=True)
    
    for _ in range(3):
        st.markdown("")

with prompt_placeholder:
    st.markdown("**Chat**")
    cols = st.columns((6, 1))
    cols[0].text_input(
        "與小智聊聊",
        value="小智您好",
        label_visibility="collapsed",
        key="human_prompt",
    )
    cols[1].form_submit_button(
        "送出", 
        type="primary", 
        on_click=on_click_callback, 
    )

credit_card_placeholder.caption(f"""
Used {st.session_state.token_count} tokens \n
Debug Langchain conversation: 
{st.session_state.conversation.memory.buffer}
""")

components.html("""
<script>
const streamlitDoc = window.parent.document;

const buttons = Array.from(
    streamlitDoc.querySelectorAll('.stButton > button')
);
const submitButton = buttons.find(
    el => el.innerText === 'Submit'
);

streamlitDoc.addEventListener('keydown', function(e) {
    switch (e.key) {
        case 'Enter':
            submitButton.click();
            break;
    }
});
</script>
""", 
    height=0,
    width=0,
)
