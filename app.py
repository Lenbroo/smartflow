import streamlit as st
import pandas as pd
from io import BytesIO

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="Smart Flow",
    layout="centered"
)

# --- عنوان الصفحة ---
st.title("✨ Smart Flow")

st.markdown("ارفع ملف Excel وسيتم معالجته تلقائيًا ✨")

# --- رفع الملف ---
uploaded_file = st.file_uploader("اختر ملف Excel", type=["xlsx"])

if uploaded_file is not None:
    try:
        # قراءة الملف
        df = pd.read_excel(uploaded_file)

        # معالجة البيانات
        df = df[df['packageprice'].notna() & (df['packageprice'] != 0)]
        df = df.reset_index(drop=True)

        output_df = pd.DataFrame()
        output_df['n'] = range(1, len(df) + 1)
        output_df['name'] = df['patientname']
        output_df['location'] = df['locationcenter']
        output_df['package'] = df['servicename']
        output_df['payment'] = ''
        output_df['time'] = df['billtime']
        output_df['shopify'] = df['transactionno']
        output_df['desc code'] = df['discountcode']
        output_df['price'] = df['netamt']
        output_df['hrs'] = ''
        output_df['under process'] = df['availeddatetime'].apply(
            lambda x: 'UNDER PROCESS' if pd.notnull(x) else 'SAMPLE PENDING'
        )

        # حفظ الملف في الذاكرة
        output = BytesIO()
        output_df.to_excel(output, index=False)
        output.seek(0)

        st.success("✅ تم معالجة الملف بنجاح! يمكنك تحميله من الزر أدناه.")

        # زر التحميل
        st.download_button(
            label="📥 تحميل الملف الناتج",
            data=output,
            file_name="output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"حدث خطأ أثناء المعالجة: {e}")

# --- الفوتر ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; font-size: small;'>"
    "Made with ❤️<br>All rights reserved to Khaled Abdelhamid"
    "</div>",
    unsafe_allow_html=True
)
