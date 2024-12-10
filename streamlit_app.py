import re
from dataclasses import dataclass
import streamlit as st
import html

# Define some basic investment options with expected annual returns
# Detailed investment options with individual company returns
investment_companies = {
    "microsoft": 0.10,  # 10% annual return
    "apple": 0.12,      # 12% annual return
    "local companies in egypt": 0.07  # 7% annual return
}

# Provide details about specific companies
company_details = {
    "microsoft": "شركة عالمية رائدة في مجال التكنولوجيا.",
    "apple": "أكبر شركة تصنيع للهواتف الذكية في العالم.",
    "local companies in egypt": "شركات محلية تعمل في قطاعات متنوعة مثل العقارات، الزراعة، والصناعة."
}

# Update investment explanation with companies
def explain_investment_companies():
    explanation = """
    🏢 إليك بعض خيارات الاستثمار في الشركات:\n
    🖥️ - Microsoft: العائد السنوي المتوقع 10%. استثمار في شركة رائدة في مجال التكنولوجيا.
    📱 - Apple: العائد السنوي المتوقع 12%. استثمار في شركة عالمية لصناعة الهواتف والكمبيوترات.
    🇪🇬 - الشركات المحلية في مصر: العائد السنوي المتوقع 7%. دعم الاقتصاد المحلي واستثمار في شركات نامية.
    
    اختر واحدة بناءً على أهدافك الاستثمارية.
    """
    return explanation

# Profit calculator for specific companies
def calculate_company_profit(investment_amount, company_name, years=1):
    company_name = company_name.lower()
    annual_return = investment_companies.get(company_name)
    if annual_return is None:
        return None
    total_profit = investment_amount * (1 + annual_return) ** years - investment_amount
    return total_profit

def load_css():
    try:
        with open("static/styles.css", "r") as f:
            css = f"<style>{f.read()}</style>"
            st.markdown(css, unsafe_allow_html=True)
    except FileNotFoundError:
        pass  # Skip if the CSS file is not available

# Chatbot logic handler update for companies
def handle_input(user_message):
    if st.session_state.salary is None:
        salary, currency = extract_financial_info(user_message)
        if salary:
            st.session_state.history.append(Message("ai", f"\n راتبك هو {salary} {currency}."))
            st.session_state.salary = salary

            # Show investment options including companies
            st.session_state.history.append(Message("ai", sanitize_text(explain_investment_companies())))

            # Ask for investment type
            st.session_state.history.append(Message("ai", "ما الشركة أو نوع الاستثمار الذي ترغب فيه؟ (Microsoft، Apple، الشركات المحلية في مصر)"))
        else:
            st.session_state.history.append(Message("ai", "عذراً، لم أتمكن من استخراج معلومات الراتب. هل يمكنك المحاولة مرة أخرى؟"))
    elif st.session_state.investment_type is None:
        st.session_state.investment_type = user_message
        st.session_state.history.append(Message("human", f"لقد اخترت {user_message}."))
        if user_message.lower() not in investment_companies:
            st.session_state.history.append(Message("ai", "هذا النوع من الاستثمار غير مدعوم. الرجاء اختيار من (Microsoft، Apple، الشركات المحلية في مصر)."))
            st.session_state.investment_type = None
        else:
            st.session_state.history.append(Message("ai", company_details.get(user_message.lower(), "لا توجد تفاصيل عن هذه الشركة.")))
            st.session_state.history.append(Message("ai", "كم من راتبك تريد استثماره؟"))
    elif st.session_state.investment_amount is None:
        try:
            investment_amount = float(user_message)
            st.session_state.investment_amount = investment_amount
            st.session_state.history.append(Message("human", f"أريد استثمار {investment_amount} جنيه."))
            st.session_state.history.append(Message("ai", "كم عدد السنوات التي ترغب في الاستثمار خلالها؟"))
        except ValueError:
            st.session_state.history.append(Message("ai", "يرجى إدخال مبلغ استثمار صالح."))
    elif st.session_state.years is None:
        try:
            years = int(user_message)
            st.session_state.years = years
            st.session_state.history.append(Message("human", f"أريد الاستثمار لمدة {years} سنوات."))
            profit = calculate_company_profit(st.session_state.investment_amount, st.session_state.investment_type, years)
            if profit is not None:
                st.session_state.history.append(
                    Message("ai", f"إذا استثمرت في {st.session_state.investment_type} بعائد سنوي قدره {investment_companies[st.session_state.investment_type.lower()] * 100:.1f}% لمدة {years} سنوات، سيكون إجمالي الربح الخاص بك: {profit:.2f} جنيه.")
                )
            else:
                st.session_state.history.append(Message("ai", "عذراً، حدث خطأ في حساب الربح."))
        except ValueError:
            st.session_state.history.append(Message("ai", "يرجى إدخال عدد سنوات صالح."))


# Streamlit Chatbot GUI
load_css()  # Load custom CSS
initialize_session_state()

st.title("Finance Chatbot 🤖")

# Display chat history
for chat in st.session_state.history:
    if chat.origin == "human":
        st.markdown(f"<div style='text-align: left; direction: ltr;'><b>👤</b> {sanitize_text(chat.message)}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='text-align: right; direction: rtl;'><b>🤖</b> {sanitize_text(chat.message)}</div>", unsafe_allow_html=True)

# User input form
with st.form("chat_form", clear_on_submit=True):
    user_message = st.text_input("اكتب رسالتك هنا...")
    submitted = st.form_submit_button("Send")

    # Handle user input and respond
    if submitted and user_message:
        st.session_state.history.append(Message("human", user_message))
        handle_input(user_message)
        st.rerun()  # Force rerun after handling input

# Debugging: Print session state
st.write(st.session_state)
