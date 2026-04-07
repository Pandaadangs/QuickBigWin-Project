import os
import streamlit as st
import pandas as pd

# =================================================
# ตั้งค่าหน้าเว็บ
# =================================================
st.set_page_config(page_title="Quick Big Win Solution Selector", layout="wide")

st.markdown(
    """
    <h1 style='text-align: center; font-size: 54px; color: #2C3E50;'>
        Quick Big Win Solution Selector
    </h1>
    <h3 style='text-align: center; font-size: 20px; color: #7F8C8D;'>
        ระบบช่วยวิเคราะห์และเลือกโปรแกรมที่ใช่สำหรับโครงการ BOT Credit Boost และ GSB Soft Loan
    </h3>
    <h4 style='text-align: center; font-size: 18px; color: #7F8C8D;'>
        Powered by Commercial Credit Product
    </h4>
    <hr>
    """,
    unsafe_allow_html=True
)

# =================================================
# โหลดฐานข้อมูล ISIC
# =================================================
@st.cache_data
def load_isic():
    path = os.path.join(os.path.dirname(__file__), "ISIC_CODE_Claude.xlsx")
    df = pd.read_excel(path)
    df["ISIC_CODE"] = df["ISIC_CODE"].astype(str).str.strip().str.upper()
    return df

isic_db = load_isic()

# =================================================
# ขั้นตอนที่ 1 : Eligibility
# =================================================

def section_header(text):
    st.markdown(
        f"<h3 style='text-align: left; font-size:24px; font-weight:bold; color:#2C3E50;'>{text}</h3>",
        unsafe_allow_html=True
    )

# ใช้งาน
section_header("ขั้นตอนที่ 1 : ตรวจสอบคุณสมบัติ")

c1, c2 = st.columns(2)
with c1:
    cond_thai = st.checkbox("มีบุคคลสัญชาติไทยถือหุ้น > 50% ของทุนจดทะเบียนที่ชำระแล้ว", value=True)
    cond_not_fin = st.checkbox("ไม่เป็นผู้ประกอบธุรกิจทางการเงิน", value=True)
with c2:
    cond_equity = st.checkbox("ไม่มีส่วนของผู้ถือหุ้นติดลบ ณ วันที่ยื่นคำขอสินเชื่อ", value=True)
    cond_npl = st.checkbox("ทุกบัญชีต้องไม่อยู่ใน Stage 2 ที่เกิดจากวันค้างชำระและต้องไม่เป็นสินเชื่อด้อยคุณภาพ (State 3 / NPL)", value=True)

cond_non_listed = st.checkbox("จดทะเบียนใน LiVEExchange/ mai / Non-listed", value=True)

if not all([cond_thai, cond_not_fin, cond_equity, cond_npl, cond_non_listed]):
    st.error("❌ ไม่ผ่านเงื่อนไขบังคับเบื้องต้น")
    st.stop()

# =================================================
# ขั้นตอนที่ 2 : ISIC และ Supply Chain
# =================================================
# ใช้งาน
section_header("ขั้นตอนที่ 2 : ISIC Code และ Supply Chain")

isic_input = str(st.text_input("กรอก ISIC Code ของผู้กู้")).upper().strip()
if not isic_input:
    st.stop()

row = isic_db[isic_db["ISIC_CODE"] == isic_input]
if row.empty:
    st.error("❌ ไม่พบ ISIC Code")
    st.stop()

r = row.iloc[0]

# แสดงผลแนวตั้ง
st.markdown(f"""
**ISIC Code:** {r["ISIC_CODE"]}  
**Sector:** {r["Sector"]}  
**นิยามธุรกิจ:** {r["Definition"]}  
**Quick Big Win:** {r["QBW"]}  
**กลุ่มประเภทธุรกิจตามนิยาม สสว.:** {r["กลุ่มประเภทธุรกิจตามนิยามสสว."]}
""")

# ใช้งาน
section_header("ข้อมูล Supply Chain")

sc_isic = str(st.text_input("ธุรกิจของผู้กู้เป็น Supply Chain ของ ISIC Code ใด (ถ้ามี)")).upper().strip()
sc_pct = st.slider("สัดส่วนรายได้จาก Supply Chain (%)", 0, 100, 25)

if sc_isic:
    sc_row = isic_db[isic_db["ISIC_CODE"] == sc_isic]
    if not sc_row.empty:
        sc = sc_row.iloc[0]
        st.info(f"""
**Supply Chain ISIC:** {sc_isic}  
**Quick Big Win:** {sc["QBW"]}  
**Sector:** {sc["Sector"]}  
**นิยามธุรกิจ:** {sc["Definition"]}
""")
    else:
        st.warning("ไม่พบ ISIC ของ Supply Chain")

is_sc_25 = sc_pct >= 25
is_sc_50 = sc_pct > 50

# =================================================
# ขั้นตอนที่ 3 : ขนาดกิจการ
# =================================================
# ใช้งาน
section_header("ขั้นตอนที่ 3 : ขนาดกิจการ")

revenue = st.number_input("รายได้ต่อปี (ล้านบาท)", min_value=0.0, step=10.0)
group = r["กลุ่มประเภทธุรกิจตามนิยามสสว."]

def calc_size(group, rev):
    if "ผลิต" in group:
        if rev <= 1.8:
            return "Micro SME"
        elif rev <= 100:
            return "Small SME"
        elif rev <= 500:
            return "Medium SME"
        else:
            return "Large Enterprise"
    else:
        if rev <= 1.8:
            return "Micro SME"
        elif rev <= 50:
            return "Small SME"
        elif rev <= 300:
            return "Medium SME"
        else:
            return "Large Enterprise"

biz_size = calc_size(group, revenue)
st.info(f"ขนาดกิจการ: {biz_size}")

# =================================================
# ขั้นตอนที่ 4 : ประเภทสินเชื่อ
# =================================================
# ใช้งาน
section_header("ขั้นตอนที่ 4 : ประเภทสินเชื่อที่ต้องการ")

is_sme = biz_size != "Large Enterprise"

if is_sme:
    loan_types = st.multiselect(
        "เลือกประเภทสินเชื่อ (SME)",
        ["Term Loan", "Trade Finance", "e-GP (PN/TF) Pre-Financing", "Refinance"]
    )
else:
    loan_types = st.multiselect(
        "เลือกประเภทสินเชื่อ (Corporate)",
        ["Term Loan", "PN", "Trade Finance", "e-GP (PN/TF) Pre-Financing", "Refinance"]
    )

# =================================================
# ขั้นตอนที่ 5 : คุณสมบัติลูกค้า
# =================================================
# ใช้งาน
section_header("ขั้นตอนที่ 5 : คุณสมบัติลูกค้า")

st.markdown(
    "<h2 style='text-align: left; font-size:20px; font-weight:bold; color:#2C3E50;'>ความต้องการของลูกค้า</h2>",
    unsafe_allow_html=True
)

need_softloan = st.checkbox("ลูกค้าต้องการดอกเบี้ยพิเศษ")
need_bot = st.checkbox("ลูกค้ามีหลักประกันไม่เพียงพอ ต้องการเพิ่ม LTV / วงเงินสูงขึ้น")

st.markdown(
    "<h2 style='text-align: left; font-size:20px; font-weight:bold; color:#2C3E50;'>คุณสมบัติของผู้ขอสินเชื่อ</h2>",
    unsafe_allow_html=True
)

qual_target_sector = st.checkbox("อยู่ในกลุ่มอุตสาหกรรมเป้าหมายตามนโยบาย Reinvent Thailand (ท่องเที่ยว, การแพทย์และสุขภาพ, เกษตรและเกษตรแปรรูป, ยานยนต์และชิ้นส่วน, อิเล็กทรอนิกส์อัจฉริยะ, การค้า)")
qual_transform = st.checkbox("มีแผนนำสินเชื่อไปยกระดับศักยภาพธุรกิจหรือพัฒนาความสามารถในการแข่งขัน เช่น ด้านดิจิทัลเทคโนโลยี, การดำเนินธุรกิจที่เป็นมิตรกับสิ่งแวดล้อม, นวัตกรรมแห่งโลกอนาคต หรือการเสริมสร้างมูลค่าเพิ่ม (Value Added) ต่อเศรษฐกิจไทย เช่น เพิ่มการจ้างแรงงานในระบบประกันสังคม, เพิ่มการใช้ทรัพยากรในประเทศ (local Content)")
qual_export_tariff = st.checkbox("ผู้ส่งออกที่ได้รับผลกระทบจากสินค้าที่อัตราภาษีนำเข้าสูงขึ้น")
qual_import_compete = st.checkbox("ผู้ประกอบธุรกิจที่ถูกกระทบจากการแข่งขันกับสินค้านำเข้าจากต่างประเทศ")
qual_tourism = st.checkbox("ผู้ประกอบธุรกิจในภาคการท่องเที่ยว")
qual_border = st.checkbox("ผู้ประกอบธุรกิจในพื้นที่ที่ได้รับผลกระทบจากสถานการณ์ข้อพิพาทชายแดน")
qual_sc_reinvent = st.checkbox("เป็น Supply Chain ของกลุ่มอุตสาหกรรมเป้าหมายตามนโยบาย Reinvent Thailand (ท่องเที่ยว, การแพทย์และสุขภาพ, เกษตรและเกษตรแปรรูป, ยานยนต์และชิ้นส่วน, อิเล็กทรอนิกส์อัจฉริยะ, การค้า)")

# =================================================
# ประมวลผลคุณสมบัติ (Mapping)
# =================================================

# GSB Programs
qualify_gsb1 = any([qual_export_tariff, qual_import_compete, qual_tourism, qual_border, is_sc_50])
qualify_gsb2 = qual_transform
# GSB3: ท่องเที่ยว หรือ Supply Chain > 50%
qualify_gsb3 = qual_tourism or (is_sc_50 and qual_sc_reinvent)
# GSB4: อยู่ใน ISIC Reinvent หรือ Supply Chain > 25%
qualify_gsb4 = (qual_target_sector or qual_sc_reinvent) and is_sc_25

# BOT Credit Boost
if biz_size in ["Micro SME", "Small SME", "Medium SME"]:
    # SME เข้า BOT ได้ถ้าเลือก Target Sector หรือ SC Reinvent (โดย SC > 25%) หรือ Transformation
    qualify_bot = need_bot and (
        (qual_target_sector and is_sc_25) or
        (qual_sc_reinvent and is_sc_25) or
        qual_transform
    )
elif biz_size == "Large Enterprise":
    # Corporate เข้า BOT ได้ถ้ามี Transformation
    qualify_bot = need_bot and qual_transform
else:
    qualify_bot = False

# =================================================
# HARD POLICY VALIDATION + สรุปผล
# =================================================
st.markdown("---")
if st.button("วิเคราะห์และแนะนำโครงการ"):

    if "Refinance" in loan_types and not qualify_gsb1:
        st.error("❌ Refinance เข้าได้เฉพาะกรณีเข้าเงื่อนไข GSB 1 เท่านั้น")
        st.stop()

    if "Trade Finance" in loan_types:
        if revenue >= 500:
            st.error("❌ Trade Finance รองรับเฉพาะรายได้ต่ำกว่า 500 ล้านบาท")
            st.stop()
        if not qualify_bot:
            st.error("❌ Trade Finance ต้องใช้ควบคู่กับ BOT Credit Boost")
            st.stop()
        if need_softloan and not qualify_gsb1:
            st.error("❌ Trade Finance + ดอกเบี้ยพิเศษ ต้องเข้า GSB 1 เท่านั้น")
            st.stop()

    # =================================================
    # สรุปผลลัพธ์ (บอก GSB ช่องไหนชัดเจน)
# =================================================
st.header("สรุปผลการวิเคราะห์")

gsb_result = []
if qualify_gsb1:
    gsb_result.append("GSB 1")
if qualify_gsb2:
    gsb_result.append("GSB 2")
if qualify_gsb3:
    gsb_result.append("GSB 3")
if qualify_gsb4:
    gsb_result.append("GSB 4")

# ตรวจสอบ Combo Program
if need_bot and need_softloan:
    if qualify_bot and gsb_result:
        st.success(f"✅ แนะนำ Combo Program: BOT Credit Boost + GSB Soft Loan ({', '.join(gsb_result)})")
    elif qualify_bot:
        st.success("✅ แนะนำ: BOT Credit Boost (แต่ไม่เข้า GSB)")
    elif gsb_result:
        st.success(f"✅ แนะนำ: GSB Soft Loan ({', '.join(gsb_result)}) (แต่ไม่เข้า BOT)")
    else:
        st.info("ℹ️ ไม่เข้าเงื่อนไขทั้ง BOT และ GSB")
elif qualify_bot:
    st.success("✅ แนะนำ: BOT Credit Boost")
elif need_softloan and gsb_result:
    st.success(f"✅ แนะนำ: GSB Soft Loan ({', '.join(gsb_result)})")
else:
    st.info("ℹ️ แนะนำสินเชื่อปกติของธนาคาร")
