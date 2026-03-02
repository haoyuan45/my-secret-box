import streamlit as st
from supabase import create_client
import uuid

# 連線設定
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
ADMIN_PASS = st.secrets["ADMIN_PASSWORD"]
supabase = create_client(URL, KEY)

st.title("📮 匿名投稿箱")

# 投稿區
with st.form("my_form", clear_on_submit=True):
    msg = st.text_area("想說的話")
    img = st.file_uploader("圖片", type=['jpg','png','jpeg'])
    if st.form_submit_button("送出"):
        final_url = ""
        if img:
            fname = f"{uuid.uuid4()}.png"
            supabase.storage.from_("uploads").upload(fname, img.getvalue())
            final_url = supabase.storage.from_("uploads").get_public_url(fname)
        supabase.table("inbox").insert({"content": msg, "image_url": final_url}).execute()
        st.success("送出成功！")

# 管理員登入 (側邊欄)
if st.sidebar.text_input("密碼", type="password") == ADMIN_PASS:
    res = supabase.table("inbox").select("*").order("created_at", desc=True).execute()
    for i in res.data:
        st.write(i['created_at'])
        st.info(i['content'])
        if i['image_url']: st.image(i['image_url'])
        st.divider()
