import streamlit as st
from supabase import create_client
import uuid

# 從 Secrets 讀取連線資訊
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
ADMIN_PASS = st.secrets["ADMIN_PASSWORD"]
supabase = create_client(URL, KEY)

st.set_page_config(page_title="私密投稿箱")
st.title("📮 匿名投稿給浩原")

# --- 投稿介面 ---
with st.form("my_inbox", clear_on_submit=True):
    content = st.text_area("想對我說什麼？", placeholder="在這裡輸入文字...")
    img = st.file_uploader("也可以傳圖片喔", type=['jpg', 'png', 'jpeg'])
    submit = st.form_submit_button("安全送出")

    if submit:
        if content or img:
            img_url = ""
            if img:
                # 處理圖片上傳
                file_ext = img.name.split(".")[-1]
                fname = f"{uuid.uuid4()}.{file_ext}"
                supabase.storage.from_("uploads").upload(fname, img.getvalue())
                img_url = supabase.storage.from_("uploads").get_public_url(fname)
            
            # 存入資料庫
            supabase.table("inbox").insert({"content": content, "image_url": img_url}).execute()
            st.success("✅ 送出成功！內容已加密。")
        else:
            st.warning("請輸入內容或上傳圖片。")

# --- 管理員檢視 (側邊欄) ---
st.sidebar.title("🔐 管理員區域")
pwd = st.sidebar.text_input("輸入通關密碼", type="password")

if pwd == ADMIN_PASS:
    st.sidebar.success("身分驗證成功")
    st.header("📋 收到所有訊息")
    # 從資料庫抓取資料
    res = supabase.table("inbox").select("*").order("created_at", desc=True).execute()
    
    for item in res.data:
        with st.container():
            st.write(f"📅 **時間：** {item['created_at']}")
            if item['content']:
                st.info(item['content'])
            if item['image_url']:
                st.image(item['image_url'])
            st.divider()
