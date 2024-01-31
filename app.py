import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

from utils import pre_process_data, pre_process_reviews

# ------------------------------ Page Configuration------------------------------
st.set_page_config(page_title="Pharmacies Listings", page_icon="📊", layout="wide")

# ----------------------------------- Page Styling ------------------------------

with open("css/style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

st.markdown("""
<style>
    [data-testid=stHeader] {
        display:none;
    }
    [data-testid=stSidebar] {
        padding-top: 10px;
    }
    [data-testid=block-container] {
        padding-top: 0px;
    }
    [data-testid="stExpanderDetails"] {
        overflow: scroll;
        height: 400px;
    }
    [data-testid="stImage"] {
        border-radius: 50%;
    }
   [data-testid=stSidebarUserContent]{
      margin-top: -75px;
      margin-top: -75px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------- Data Loading ------------------------------

conn = st.connection("gsheets", type=GSheetsConnection)

data = conn.read(worksheet="Pharmacies")
reviews_data = conn.read(worksheet="AllReviews")
# data = pd.read_json("./data/Pharmacies.json")
data = pre_process_data(data)
# reviews_data = pd.read_json("./data/AllReviews.json")
reviews_data = pre_process_reviews(reviews_data)


st.dataframe(data, use_container_width=True)

