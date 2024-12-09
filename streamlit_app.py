import re
from dataclasses import dataclass
import streamlit as st
import html
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
    origin: str  # "human" or "ai"
    message: str

# Load custom CSS
def load_css():
    try:
        with open("static/styles.css", "r") as f:
            css = f"<style>{f.read()}</style>"
            st.markdown(css, unsafe_allow_html=True)
    except FileNotFoundError:
        pass  # Skip if the CSS file is not available

# Initialize session state to track history
def initialize_session_state():
    if "history" not in st.session_state:
        st.session_state.history = []
    if "investment_type" not in st.session_state:
        st.session_state.investment_type = None
    if "salary" not in st.session_state:
        st.session_state.salary = None

# Function to parse and extract financial information
def extract_financial_info(text):
    salary_match = re.search(r'(\d+(\.\d+)?)\s*(جنيه|دولار|يورو|استرليني|ريال)?', text.lower())
    if salary_match:
        salary = float(salary_match.group(1))
        currency = salary_match.group(3).upper() if salary_match.group(3) else 'جنيه'
        return salary, currency
    return None, None  # Return None if no match


# Investment calculator
def calculate_profit(investment_amount, investment_type, years=1):
    investment_type = investment_type.lower()
    annual_return = investment_options.get(investment_type)
    if annual_return is None:
        return None
    total_profit = investment_amount * (1 + annual_return) ** years - investment_amount
    return total_profit

# Detailed breakdown of investment options
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

# Provide more details about the chosen investment type
def provide_investment_details(investment_type):
    details = investment_details.get(investment_type, "لا تتوفر لدينا معلومات إضافية حول هذا النوع من الاستثمار.")
    return details



def sanitize_text(text):
    return html.escape(text)
# Chatbot logic handler
def handle_input(user_message):
    salary, currency = extract_financial_info(user_message)

    if salary:
        st.session_state.salary = salary
        st.session_state.history.append(Message("ai", f"راتبك هو {salary} {currency}."))
        
        # Show investment options
        st.session_state.history.append(Message("ai", explain_investment_options()))
        st.session_state.history.append(Message("ai", "ما نوع الاستثمار الذي ترغب فيه؟ (الأسهم، السندات، العقارات، الصناديق المشتركة)"))
    elif user_message.strip().lower() in investment_options.keys():
        # Store investment type
        st.session_state.investment_type = user_message.strip().lower()
        st.session_state.history.append(Message("ai", provide_investment_details(st.session_state.investment_type)))
    else:
        st.session_state.history.append(Message("ai", "عذراً، لم أتمكن من فهم طلبك. هل يمكنك المحاولة مرة أخرى؟"))




# Streamlit Chatbot GUI
st.title("Finance Chatbot 🤖")
load_css()  # Load custom CSS
initialize_session_state()

# Display chat history
# Display chat history


# Modify the display of messages in the chat history
for chat in st.session_state.history:
    if chat.origin == "human":
        # Escape only the user's input
        st.markdown(f"<div style='text-align: left; direction: ltr;'><b>👤</b> {sanitize_text(chat.message)}</div>", unsafe_allow_html=True)
    else:
        # Directly render HTML for chatbot responses
        st.markdown(f"<div style='text-align: right; direction: rtl;'><b>🤖</b> {chat.message}</div>", unsafe_allow_html=True)



# User input form
with st.form("chat_form", clear_on_submit=True):
    user_message = st.text_input("اكتب رسالتك هنا...")
    submitted = st.form_submit_button("Send")

    # Handle user input and respond
    if submitted and user_message:
        st.session_state.history.append(Message("human", user_message))
        handle_input(user_message)

# If investment type was provided, ask for details about the investment
if st.session_state.investment_type:
    investment_type = st.selectbox("اختر نوع الاستثمار", list(investment_options.keys()))
    st.session_state.history.append(Message("human", f"لقد اخترت {investment_type}."))
    st.session_state.history.append(Message("ai", provide_investment_details(investment_type)))

# Show investment profit calculation after asking the relevant questions
if st.session_state.salary and st.session_state.investment_type:
    years = st.slider("كم عدد السنوات التي ترغب في الاستثمار خلالها؟", 1, 20)
    investment_amount = st.number_input(f"كم من {st.session_state.salary} تريد استثماره؟", min_value=1.0)

    if st.button("احسب الربح"):
        profit = calculate_profit(investment_amount, st.session_state.investment_type, years)
        if profit:
            st.session_state.history.append(
                Message("ai", f"بناءً على عائد سنوي قدره {investment_options[st.session_state.investment_type]} لمدة {years} سنوات، سيكون إجمالي الربح الخاص بك: {profit:.2f}.")
            )
