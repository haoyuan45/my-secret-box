import streamlit as st
from supabase import create_client
import uuid
from streamlit.web.server.websocket_headers import _get_websocket_headers

# 連線設定
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
ADMIN_PASS = st.secrets["ADMIN_PASSWORD"]
supabase = create_client(URL, KEY)

st.title("📮 哈哈隨便用 ")

# 抓取 IP 位址的函數
def get_remote_ip():
    headers = _get_websocket_headers()
    if headers:
        return headers.get("X-Forwarded-For", "未知 IP")
    return "無法抓取"

# 投稿區
with st.form("my_form", clear_on_submit=True):
    msg = st.text_area("想說的話")
    img = st.file_uploader("圖片", type=['jpg','png','jpeg'])
    if st.form_submit_button("送出"):
        user_ip = get_remote_ip() # 抓取位置
        final_url = ""
        if img:
            fname = f"{uuid.uuid4()}.png"
            supabase.storage.from_("uploads").upload(fname, img.getvalue())
            final_url = supabase.storage.from_("uploads").get_public_url(fname)
        
        # 存入資料庫，包含 user_ip
        supabase.table("inbox").insert({
            "content": msg, 
            "image_url": final_url,
            "user_ip": user_ip
        }).execute()
        st.success(f"送出成功！

# 管理員登入
if st.sidebar.text_input("管理員密碼", type="password") == ADMIN_PASS:
    res = supabase.table("inbox").select("*").order("created_at", desc=True).execute()
    for i in res.data:
        st.write(f"⏰ {i['created_at']} | 📍 來源：{i.get('user_ip', '無紀錄')}")
        st.info(i['content'])
        if i['image_url']: st.image(i['image_url'])
        st.divider()
