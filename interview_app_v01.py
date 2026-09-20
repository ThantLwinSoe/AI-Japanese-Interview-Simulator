import streamlit as st
from google import genai
from google.genai import types

# ... (API Key ထည့်ခြင်း) ...
#API_key
#AI generate 
# (အသစ်ပြင်ဆင်ထားသော အပိုင်း) ကွန်ရက်ကြိုး မပြတ်အောင် Cache လုပ်ထားခြင်း
@st.cache_resource
def get_ai_client():
    # ဒီနေရာမှာ သင့်ရဲ့ API Key အသစ်ကို ထည့်ပါ။ 
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Client ကို ခေါ်ယူခြင်း (ဒီ Client က ဘယ်တော့မှ Close မဖြစ်တော့ပါဘူး)
client = get_ai_client()

# (၁) မှတ်ဉာဏ်သေတ္တာ ဖန်တီးခြင်း
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("AI Japanese Interview Simulator")

# (၂) အင်တာဗျူး စတင်မည့် အပိုင်း (Sidebar မှာ ထားရင် ပိုသပ်ရပ်ပါတယ်)
with st.sidebar:
    st.header("အင်တာဗျူး ပြင်ဆင်ရန်")
    user_job = st.text_input("လျှောက်မည့်ရာထူး (ဥပမာ- Java Engineer):")
    if st.button("အင်တာဗျူး စတင်မည်"):
        if user_job:

            # ဤနေရာတွင် System instruction များရေးပြီး chat_session ကို တည်ဆောက်ပါ။
            # ပြီးလျှင် st.session_state.chat_session ထဲသို့ ထည့်သိမ်းပါ။
            #System Instruction
            system_instruction = f"""သင်ဟာ အသုံးပြုသူ ကို {user_job} ရာထူး အတွက် အင်တာဗျူး လမ်းညွှန်ပြီး လေ့ကျင့်ပေးမယ့် AI အကူတယာက်ဖြစ်တယ်။
            သင်ရဲ့ ရည်ရွယ်ချက်က အသုံးပြုသူရဲ့ {user_job} ရာထူးအတွက် ဂျပန် အင်တာဗျူး စကေးကို လေ့ကျင့်ပေးဖို့ပါပဲ့.
            တကြိမ်မှာ မေးခွန်းတခုပဲ့ မေးပါ. အသုံးပြုသူ ရဲ့ ပြန်လည် ဖြေကြားချက်ကို ကြည့်ပြီး လိုအပ်တာကို ထောက်ပြပေးပြီး မှားနေတာတွေကို လိုအပ်ရင် ပြင်ဆင်ပေး၊ အကြံပေးရပါမယ်။ 
            ဂျပန်တွေ အင်တာဗျူးချိန်မှာ တကယ် အသုံးပြုတဲ့ စကားလုံးတွေကို သုံးပေးပါ"""

            #System Instruction insert
            chat = client.chats.create(model='gemini-3.5-flash-lite',
                                           config=types.GenerateContentConfig(system_instruction=system_instruction)
                                           )
            st.session_state.chat_session = chat

            # ပထမဆုံး မေးခွန်းကို တောင်းပြီး st.session_state.messages ထဲ ထည့်ပါ။
            #User Prompt
            user_prompt = f"ကျနော် ဂျပန်နိုင်ငံမှာ ဒီ {user_job} ရာထူးနဲ့ အလုပ်လျှောက်ချင်ပါတယ်။ အင်တာဗျူး ကို သင်လေ့ကျင့်းပေးနိုင်မလား?"

            #Ai ကိုမေးခွန်းတောင်းမယ်
            response = chat.send_message(user_prompt)
            #st.session_state.messages ထဲမှာ မှတ်ထားမယ်
            st.session_state.messages.append({"role": "ai", "text": response.text})

# (၃) စကားပြော မှတ်တမ်းများကို မျက်နှာပြင်တွင် ပြသခြင်း
for msg in st.session_state.messages:
    # msg["role"] ဆိုတာ "user" လား "ai" လား ခွဲဖို့ပါ
    with st.chat_message(msg["role"]):
        st.write(msg["text"])

# (၄) User က အဖြေပြန်ရိုက်ရန် နေရာ
user_input = st.chat_input("သင့်အဖြေကို ရိုက်ထည့်ပါ...")
if user_input:
    # ၁။ User ရိုက်လိုက်တာကို မှတ်တမ်းထဲထည့်မယ်
    st.session_state.messages.append({"role": "user", "text": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    
    # ၂။ AI ဆီ ပို့မယ် (chat_session ရှိနေမှ ပို့လို့ရပါမယ်)
    if st.session_state.chat_session:
        with st.spinner("AI စဉ်းစားနေပါသည်..."):
            try:
                # AI ဆီ ပို့ပြီး အဖြေတောင်းပါ
                response = st.session_state.chat_session.send_message(user_input)
                
                # ၃။ ရလာတဲ့ AI ရဲ့ အဖြေကို မှတ်တမ်းထဲ ထပ်ထည့်ပါ (ဒီနေရာလေး ပြင်ထားပါတယ်)
                st.session_state.messages.append({"role": "ai", "text": response.text})
                
                # ၄။ AI ရဲ့ အဖြေကို မျက်နှာပြင်မှာ ပြပါ (Loop ထပ်ပတ်စရာ မလိုပါ)
                with st.chat_message("ai"):
                    st.write(response.text)
                    
            except Exception as e:
                st.error(f"Error တက်နေပါသည်: {e}")
    else:
        st.error("ကျေးဇူးပြု၍ ဘေးဘက်မှ 'အင်တာဗျူး စတင်မည်' ကို အရင်နှိပ်ပါ။")