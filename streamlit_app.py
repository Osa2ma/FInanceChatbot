import re
from dataclasses import dataclass
from typing import Literal
import streamlit as st
import html

from langchain import OpenAI
from langchain.callbacks import get_openai_callback
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationSummaryMemory
import streamlit.components.v1 as components

# Define some basic investment options with expected annual returns
investment_options = {
    "الأسهم": 0.08,  # 8% annual return
    "السندات": 0.04,  # 4% annual return
    "العقارات": 0.06,  # 6% annual return
    "الصناديق المشتركة": 0.05  # 5% annual return
}

# Detailed breakdown of investment types (example companies or assets)
investment_details = {
    "الأسهم": "تستثمر في شركات مثل Apple، Microsoft، أو الشركات المحلية.",
    "السندات": "تستثمر في سندات حكومية مثل السندات الأمريكية أو الأوروبية.",
    "العقارات": "يمكنك شراء عقار سكني أو استثماري في مناطق نامية مثل العاصمة الإدارية الجديدة أو القاهرة الجديدة.",
    "الصناديق المشتركة": "استثمارات متنوعة في أسهم وسندات مختلفة لتحقيق توازن في المخاطر."
}

@dataclass
class Message:
    """Class for keeping track of a chat message."""
    origin: Literal["human", "ai"]
    message: str

def load_css():
    with open("static/styles.css", "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)

def initialize_session_state():
    if "history" not in st.session_state:
        st.session_state.history = []
    if "token_count" not in st.session_state:
        st.session_state.token_count = 0
    if "conversation" not in st.session_state:
        llm = OpenAI(
            temperature=0,
            openai_api_key=st.secrets["openai_api_key"],
            model_name="text-davinci-003"
        )
        st.session_state.conversation = ConversationChain(
            llm=llm,
            memory=ConversationSummaryMemory(llm=llm),
        )

def on_click_callback():
    with get_openai_callback() as cb:
        human_prompt = st.session_state.human_prompt
        llm_response = st.session_state.conversation.run(human_prompt)
        st.session_state.history.append(Message("human", human_prompt))
        st.session_state.history.append(Message("ai", llm_response))
        st.session_state.token_count += cb.total_tokens

def extract_financial_info(text):
    salary_match = re.search(r'(\d+(\.\d+)?)\s*(جنيه|دولار|يورو|جنيه استرليني)?', text.lower())
    salary = float(salary_match.group(1)) if salary_match else None
    currency = salary_match.group(3).upper() if salary_match and salary_match.group(3) else 'جنيه'
    return salary, currency

def calculate_profit(investment_amount, investment_type, years=1):
    investment_type = investment_type.lower()
    annual_return = investment_options.get(investment_type)
    if annual_return is None:
        return None
    total_profit = investment_amount * (1 + annual_return) ** years - investment_amount
    return total_profit

def explain_investment_options():
    explanation = """
    💼 إليك بعض الخيارات الاستثمارية للنظر فيها:\n
    📈 - الأسهم: العائد السنوي المتوقع 8%. مخاطرة عالية، ولكن عوائد محتملة عالية.
    💵 - السندات: العائد السنوي المتوقع 4%. مخاطرة أقل، وعوائد ثابتة.
    🏠 - العقارات: العائد السنوي المتوقع 6%. استثمار آمن، مع نمو طويل الأجل.
    📊 - الصناديق المشتركة: العائد السنوي المتوقع 5%. استثمارات متنوعة ومخاطرة معتدلة.
    
    يمكنك اختيار واحدة بناءً على مستوى المخاطرة الذي تتحمله وأهدافك.
    """.strip()
    return explanation

def provide_investment_details(investment_type):
    details = investment_details.get(investment_type, "لا تتوفر لدينا معلومات إضافية حول هذا النوع من الاستثمار.")
    return details

def sanitize_text(text):
    return html.escape(text)

load_css()
initialize_session_state()

st.title("Finance Chatbot 🤖")

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
        "Chat",
        value="Hello bot",
        label_visibility="collapsed",
        key="human_prompt",
    )
    cols[1].form_submit_button(
        "Submit", 
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
