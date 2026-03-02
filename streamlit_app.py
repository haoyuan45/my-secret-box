import streamlit as st
from supabase import create_client
import uuid
import requests
from streamlit.web.server.websocket_headers import _get_websocket_headers

# 連線設定
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
ADMIN_PASS = st.secrets["ADMIN_PASSWORD"]
supabase = create_client(URL, KEY)

st.set_page_config(page_title="隨便用", page_icon="📮")
st.title("📮 隨便用")

# --- 強效抓取 IP 函數 ---
def get_remote_ip():
    try:
        # 優先使用外部 API 抓取公網 IP
        res = requests.get('https://api64.ipify.org?format=json', timeout=5)
        return res.json()['ip']
    except:
        # 如果失敗，回退到 Streamlit 標頭抓取
        headers = _get_websocket_headers()
        return headers.get("X-Forwarded-For", "未知 IP").split(',')[0]

# --- 投稿介面 ---
with st.form("my_form", clear_on_submit=True):
    msg = st.text_area("隨便打", placeholder="在這裡輸入文字...")
    img = st.file_uploader("也可以傳圖片喔", type=['jpg', 'png', 'jpeg'])
    submit = st.form_submit_button("安全送出")

    if submit:
        if msg or img:
            user_ip = get_remote_ip() # 抓取位置
            final_url = ""
            if img:
                # 處理圖片上傳
                fname = f"{uuid.uuid4()}.png"
                supabase.storage.from_("uploads").upload(fname, img.getvalue())
                final_url = supabase.storage.from_("uploads").get_public_url(fname)
            
            # 存入資料庫
            supabase.table("inbox").insert({
                "content": msg, 
                "image_url": final_url,
                "user_ip": user_ip
            }).execute()
            st.success(f"✅ 送出成功！")
        else:
            st.warning("請輸入內容或上傳圖片。")

# --- 管理員檢視 (側邊欄) ---
st.sidebar.title("🔐 管理員區域")
pwd = st.sidebar.text_input("通關密碼", type="password")

if pwd == ADMIN_PASS:
    st.sidebar.success("身分驗證成功")
    st.header("📋 收到所有訊息")
    # 從資料庫抓取資料
    res = supabase.table("inbox").select("*").order("created_at", desc=True).execute()
    
    for i in res.data:
        with st.container():
            st.write(f"📅 **時間：** {i['created_at']}")
            st.write(f"📍 **來源 IP：** `{i.get('user_ip', '無紀錄')}`")
            if i['content']:
                st.info(i['content'])
            if i['image_url']:
                st.image(i['image_url'])
            st.divider()
