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

# ISIC Tourism List (Policy-based)

# =================================================

TOURISM_ISIC_LIST = [

    "I551010", "I551020", "I551030", "I551090",

    "I552000", "I559010", "I559090",

    "I561010", "I561020", "I561030",

    "I562100", "I562910", "I562920", "I562990",

    "I563010", "I563020", "I563030", "I563040",

    "N771010", "N791100", "N791200",

    "N799010", "N799090",

    "N823010", "N823020",

    "R900010", "R900020",

    "R910110", "R910120", "R910200",

    "R910210", "R910220",

    "R910310", "R910320",

    "R932100", "R932910", "R932920",

    "R932930", "R932990"

]

 

# =================================================

# Utilities

# =================================================

def section_header(text):

    st.markdown(

        f"<h3 style='text-align:left;font-size:24px;font-weight:bold;color:#2C3E50;'>{text}</h3>",

        unsafe_allow_html=True

    )

 

# =================================================

# ขั้นตอนที่ 1 : Eligibility

# =================================================

section_header("ขั้นตอนที่ 1 : ตรวจสอบคุณสมบัติ")

 

c1, c2 = st.columns(2)

with c1:

    cond_thai = st.checkbox("มีบุคคลสัญชาติไทยถือหุ้น > 50% ของทุนจดทะเบียนที่ชำระแล้ว", value=True)

    cond_not_fin = st.checkbox("ไม่เป็นผู้ประกอบธุรกิจทางการเงิน", value=True)

with c2:

    cond_equity = st.checkbox("ไม่มีส่วนของผู้ถือหุ้นติดลบ ณ วันที่ยื่นคำขอสินเชื่อ", value=True)

    cond_npl = st.checkbox(

        "ทุกบัญชีต้องไม่อยู่ใน Stage 2 ที่เกิดจากวันค้างชำระและต้องไม่เป็นสินเชื่อด้อยคุณภาพ (State 3 / NPL)",

        value=True

    )

 

cond_non_listed = st.checkbox("จดทะเบียนใน LiVEExchange/ mai / Non-listed", value=True)

 

if not all([cond_thai, cond_not_fin, cond_equity, cond_npl, cond_non_listed]):

    st.error("❌ ไม่ผ่านเงื่อนไขบังคับเบื้องต้น")

    st.stop()

 

# =================================================

# ขั้นตอนที่ 2 : ISIC และ Supply Chain

# =================================================

section_header("ขั้นตอนที่ 2 : ISIC Code และ Supply Chain")

 

isic_input = str(st.text_input("กรอก ISIC Code ของผู้กู้")).upper().strip()

if not isic_input:

    st.stop()

 

row = isic_db[isic_db["ISIC_CODE"] == isic_input]

if row.empty:

    st.error("❌ ไม่พบ ISIC Code")

    st.stop()

 

r = row.iloc[0]

 

st.markdown(f"""

**ISIC Code:** {r["ISIC_CODE"]} 

**Sector:** {r["Sector"]} 

**นิยามธุรกิจ:** {r["Definition"]} 

**Quick Big Win:** {r["QBW"]} 

**กลุ่มประเภทธุรกิจตามนิยาม สสว.:** {r["กลุ่มประเภทธุรกิจตามนิยามสสว."]}

""")

 

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

            return "Corporate"

    else:

        if rev <= 1.8:

            return "Micro SME"

        elif rev <= 50:

            return "Small SME"

        elif rev <= 300:

            return "Medium SME"

        else:

            return "Corporate"

 

biz_size = calc_size(group, revenue)

st.info(f"ขนาดกิจการ: {biz_size}")

 

# =================================================

# ขั้นตอนที่ 4 : ประเภทสินเชื่อ

# =================================================

section_header("ขั้นตอนที่ 4 : ประเภทสินเชื่อที่ต้องการ")

 

is_sme = biz_size != "Corporate"

 

if is_sme:

    loan_types = st.multiselect(

        "เลือกประเภทสินเชื่อ (SME)",

        ["Term Loan", "Trade Finance", "Refinance"]

    )

else:

    loan_types = st.multiselect(

        "เลือกประเภทสินเชื่อ (Corporate)",

        ["Term Loan", "PN", "Trade Finance", "Refinance"]

    )

 

# =================================================

# ขั้นตอนที่ 5 : คุณสมบัติลูกค้า

# =================================================

section_header("ขั้นตอนที่ 5 : คุณสมบัติลูกค้า")

 

st.markdown(

    "<h2 style='font-size:20px;font-weight:bold;'>ความต้องการของลูกค้า</h2>",

    unsafe_allow_html=True

)

 

need_softloan = st.checkbox("ลูกค้าต้องการดอกเบี้ยพิเศษ")

need_bot = st.checkbox("ลูกค้ามีหลักประกันไม่เพียงพอ ต้องการเพิ่ม LTV / วงเงินสูงขึ้น")

 

st.markdown(

    "<h2 style='font-size:20px;font-weight:bold;'>คุณสมบัติของผู้ขอสินเชื่อ</h2>",

    unsafe_allow_html=True

)

 

qual_target_sector = st.checkbox(

    "อยู่ในกลุ่มอุตสาหกรรมเป้าหมายตามนโยบาย Reinvent Thailand "

    "(ท่องเที่ยว, การแพทย์และสุขภาพ, เกษตรและเกษตรแปรรูป, "

    "ยานยนต์และชิ้นส่วน, อิเล็กทรอนิกส์อัจฉริยะ, การค้า)"

)

 

qual_transform = st.checkbox(

    "มีแผนนำสินเชื่อไปยกระดับศักยภาพธุรกิจหรือพัฒนาความสามารถในการแข่งขัน "

    "เช่น ด้านดิจิทัลเทคโนโลยี, การดำเนินธุรกิจที่เป็นมิตรกับสิ่งแวดล้อม, "

    "นวัตกรรมแห่งโลกอนาคต หรือการเสริมสร้างมูลค่าเพิ่ม (Value Added) "

    "ต่อเศรษฐกิจไทย เช่น เพิ่มการจ้างแรงงานในระบบประกันสังคม, "

    "เพิ่มการใช้ทรัพยากรในประเทศ (local Content)"

)

 

qual_export_tariff = st.checkbox("ผู้ส่งออกที่ได้รับผลกระทบจากสินค้าที่อัตราภาษีนำเข้าสูงขึ้น")

qual_import_compete = st.checkbox("ผู้ประกอบธุรกิจที่ถูกกระทบจากการแข่งขันกับสินค้านำเข้าจากต่างประเทศ")

qual_tourism = st.checkbox("ผู้ประกอบธุรกิจในภาคการท่องเที่ยว")

qual_border = st.checkbox("ผู้ประกอบธุรกิจในพื้นที่ที่ได้รับผลกระทบจากสถานการณ์ข้อพิพาทชายแดน")

qual_sc_reinvent = st.checkbox(

    "เป็น Supply Chain ของกลุ่มอุตสาหกรรมเป้าหมายตามนโยบาย Reinvent Thailand "

    "(ท่องเที่ยว, การแพทย์และสุขภาพ, เกษตรและเกษตรแปรรูป, "

    "ยานยนต์และชิ้นส่วน, อิเล็กทรอนิกส์อัจฉริยะ, การค้า)"

)

 

# =================================================

# ประมวลผล + แสดงผล (เมื่อกดปุ่มเท่านั้น)

# =================================================

st.markdown("---")

 

if st.button("วิเคราะห์และแนะนำโครงการ"):

 

    # -------------------------------------------------

    # INIT FLAGS (กำหนดทุกตัวให้มีค่าเสมอ กัน NameError)

    # -------------------------------------------------

    qualify_bot  = False

    qualify_gsb1 = False

    qualify_gsb2 = False

    qualify_gsb3 = False

    qualify_gsb4 = False

 

    # -------------------------------------------------

    # BASIC FLAGS

    # -------------------------------------------------

    is_qbw = r["QBW"] == "Y"

    is_isic_tourism = isic_input in TOURISM_ISIC_LIST

    is_supply_chain_25 = qual_sc_reinvent and is_sc_25

    is_supply_chain_50 = qual_sc_reinvent and is_sc_50

 

    # -------------------------------------------------

    # Supply Chain : ข้อมูลไม่ครบ

    # -------------------------------------------------

    if qual_sc_reinvent and not sc_isic:

        st.error(

            "❌ ไม่ได้กรอก ISIC Code ของ Supply Chain\n"

            "ไม่สามารถพิจารณาสิทธิ์สินเชื่อได้"

        )

        st.stop()

 

    # -------------------------------------------------

    # GSB BASE LOGIC

    # -------------------------------------------------

    # GSB 1 : Mitigation

    if qual_export_tariff or qual_import_compete or qual_border:

        qualify_gsb1 = True

 

    # GSB 2 : Transformation

    if qual_transform:

        qualify_gsb2 = True

 

    # GSB 3 : Tourism

    # - ธุรกิจท่องเที่ยวโดยตรง

    # - หรือ Supply Chain ธุรกิจท่องเที่ยว >= 50%

    if qual_tourism or (qual_tourism and is_supply_chain_50):

        qualify_gsb3 = True

 

    # GSB 4 : Reinvent Thailand

    if qual_target_sector or is_supply_chain_25:

        qualify_gsb4 = True

 

    # -------------------------------------------------

    # BOT Credit Boost

    # -------------------------------------------------

    if need_bot and (

        qual_transform or

        is_supply_chain_25 or

        (qual_target_sector and is_qbw) or

        (qual_tourism and is_isic_tourism and is_qbw)

    ):

        qualify_bot = True

 

    # =================================================

    # POLICY BY LOAN TYPE (ต้องเป็น if / elif / else ชุดเดียว)

    # =================================================

 

    # ---------------- Refinance ----------------

    if "Refinance" in loan_types:

 

        # Refinance เข้าได้เฉพาะ GSB 1 เท่านั้น

        if not qualify_gsb1:

            st.error(

                "❌ Refinance สามารถเข้าได้เฉพาะโปรแกรม GSB 1 (Mitigation) เท่านั้น"

            )

            st.stop()

 

        # ตัดโปรแกรมอื่นทั้งหมด

        qualify_bot  = False

        qualify_gsb2 = False

        qualify_gsb3 = False

        qualify_gsb4 = False

 

    # ---------------- Trade Finance ----------------

    elif "Trade Finance" in loan_types:

 

        # Supply Chain >= 25% ปลด BOT

        if need_bot and is_supply_chain_25:

            qualify_bot = True

 

        if not qualify_bot:

            st.error(

                "❌ Trade Finance ใช้ได้เฉพาะกรณีเข้า BOT Credit Boost "

                "หรือ BOT Credit Boost + GSB 1"

            )

            st.stop()

 

        # Combo Trade Finance: GSB 1 เท่านั้น และรายได้ < 500

        if need_softloan and qualify_gsb1 and revenue >= 500:

            st.error(

                "❌ Trade Finance ในกรณี Combo Program "

                "รองรับเฉพาะรายได้ต่ำกว่า 500 ล้านบาท"

            )

            st.stop()

 

        # Filter GSB สำหรับ Trade Finance

        if need_softloan and qualify_gsb1:

            qualify_gsb2 = False

            qualify_gsb3 = False

            qualify_gsb4 = False

        else:

            qualify_gsb1 = False

            qualify_gsb2 = False

            qualify_gsb3 = False

            qualify_gsb4 = False

 

    # ---------------- Term Loan ----------------

    else:

        # Term Loan: ใช้ logic ปกติ ไม่ filter GSB ใด ๆ

        pass

 

    # -------------------------------------------------

    # SUMMARY

    # -------------------------------------------------

    st.header("สรุปผลการวิเคราะห์")

 

    gsb_result = []

    if qualify_gsb1:

        gsb_result.append("1 (Mitigation)")

    if qualify_gsb2:

        gsb_result.append("2 (Transformation)")

    if qualify_gsb3:

        gsb_result.append("3 (Tourism)")

    if qualify_gsb4:

        gsb_result.append("4 (Reinvent Thailand)")

 

    if need_bot and need_softloan:

        if qualify_bot and gsb_result:

            st.success(

                f"✅ แนะนำ Combo Program: BOT Credit Boost + GSB Soft Loan {', '.join(gsb_result)}"

            )

        elif qualify_bot:

            st.warning(

                "ℹ️ สามารถเข้าเงื่อนไข BOT Credit Boost ได้\n"

                "แต่ไม่สามารถเข้า Combo Program ได้ เนื่องจากไม่เข้าเงื่อนไข GSB 1 (Mitigation)"

            )

            st.success("✅ แนะนำ: BOT Credit Boost")

        elif gsb_result:

            st.success(f"✅ แนะนำ: GSB Soft Loan {', '.join(gsb_result)}")

        else:

            st.info("ℹ️ ไม่เข้าเงื่อนไข BOT Credit Boost และ GSB Soft Loan")

 

    elif qualify_bot:

        st.success("✅ แนะนำ: BOT Credit Boost")

 

    elif need_softloan and gsb_result:

        st.success(f"✅ แนะนำ: GSB Soft Loan {', '.join(gsb_result)}")

 

    else:

        st.info("ℹ️ ไม่เข้าเงื่อนไข")

 

# -------------------------------------------------

    # REMARK : Corporate + PN + BOT Credit Boost

    # -------------------------------------------------

    is_corporate = biz_size == "Corporate"

    is_pn = "PN" in loan_types

    has_bot = qualify_bot  # มี BOT Credit Boost เป็นส่วนหนึ่งของผลลัพธ์

 

    if is_corporate and is_pn and has_bot:

        st.info(

            "ℹ️ หมายเหตุ: ตั้งแต่ปีที่ 5 วงเงิน PN "

            "ต้องทยอย Run down ภายใน 2 ปี"

        )