import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
from streamlit_gsheets import GSheetsConnection
from streamlit_option_menu import option_menu

from plots import get_rating_dist, get_rating_breakdown, reviews_wordcloud, review_length_dist
from template.html import card_view, review_card
from utils import pre_process_data, create_map

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
        height: 450px;
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

data = conn.read(spreadsheet="Pharmacies")
reviews_data = conn.read(spreadsheet="AllReviews")

# data = pd.read_json("./data/Pharmacies.json")
# data = data.transpose()
# reviews_data = pd.read_json("./data/AllReviews.json")
# reviews_data = reviews_data.transpose()

data, reviews_data = pre_process_data(data, reviews_data)

# ----------------------------------- Menu --------------------------------------
menu = option_menu(menu_title=None, menu_icon=None, orientation="horizontal",
                   options=["Pharmacies Map", "List View", "Reviews Analysis"])

if menu == "Pharmacies Map":
    pharmacies_map = create_map(data)
    st_data = folium_static(pharmacies_map, width=1500, height=650)

if menu == "List View":
    filters = st.columns(3)
    stars = filters[0].multiselect(label="Rating", options=[5, 4, 3, 2, 1], placeholder="All")
    reviews = filters[1].multiselect(label="Min. Reviewers",
                                     options=["Up-to 50", "50 to 100", "100-200", "More than 200"],
                                     placeholder="All")
    city = filters[2].multiselect(label="City", options=data["city"].unique(), placeholder="All")

    if not stars:
        stars = [5, 4, 3, 2, 1]
    if not reviews:
        reviews = data["adjustedReview"].unique()
    if not city:
        city = data["city"].unique()

    df = data.copy()
    df = df[df["adjustedRating"].isin(stars)]
    df = df[df["adjustedReview"].isin(reviews)]
    df = df[df["city"].isin(city)]

    st.write("# ")

    pharmacies = df.sort_values(by="averageRating", ascending=False)

    for i, pharmacy in pharmacies.iterrows():
        upper_row = st.columns(2)
        pharmacy_reviews = reviews_data[reviews_data.place_Name == pharmacy["name"]]
        with upper_row[0]:
            row = st.columns((1, 5))
            row[0].image(r"./assets/icon-min.png")
            row[1].markdown(card_view(pharmacy["name"], pharmacy["address"],
                                      f"{pharmacy['averageRating']:.1f}", pharmacy["totalReviews"],
                                      pharmacy["contact"]),
                            unsafe_allow_html=True)
        with upper_row[1]:
            review_bar = st.expander(label="Reviews")
            with review_bar:
                for _, review in pharmacy_reviews.iterrows():
                    row_ = st.columns((1, 6))
                    row_[0].image(r"./assets/reviewer.png")
                    row_[1].markdown(review_card(review['reviewer'], review['date'],
                                                 review['rating']),
                                     unsafe_allow_html=True)
                    st.write(f"{review['text']}")
                    st.write("---")
        st.write("---")


if menu == "Reviews Analysis":
    with st.sidebar:
        st.write("# ")
        st.write("# ")
        pharmacy = st.selectbox(label="Pharmacy", options=reviews_data["place_Name"].unique())
        # Slider for period selection
        reviews_data['datetime'] = reviews_data['datetime'].dt.date
        start_date, end_date = st.slider(
            "Select the period",
            value=(reviews_data['datetime'].min(), reviews_data['datetime'].max()),
            format="MM/DD/YYYY"
        )

    filtered_data = reviews_data[
        (reviews_data['datetime'] >= start_date) & (reviews_data['datetime'] <= end_date) &
        (reviews_data['place_Name'] == pharmacy)]
    filtered_data = filtered_data[["datetime", "place_Name", "rating", "reviewer", "text"]]
    filtered_data["datetime"] = pd.to_datetime(filtered_data["datetime"])

    # --------------------------------- KPIs --------------------------------------------------

    total_reviews = len(filtered_data)
    average_ratings = filtered_data['rating'].mean()

    # --------------- yearly ratio calculations --------------------------------------
    filtered_data["year"] = filtered_data["datetime"].dt.year
    total_years = filtered_data['year'].nunique()
    yearly_reviews_rate_percentage = (total_reviews / total_years)

    # --------------- ratio ratio calculations ------------------------------

    rating_ratio = (average_ratings*total_reviews/len(reviews_data)) * 100

    filters_row = st.columns(4)
    filters_row[0].metric(label="Average Rating", value=f"{average_ratings:.1f}")
    filters_row[1].metric(label="Total Reviews", value=f"{total_reviews}")
    filters_row[2].metric(label="Review Frequency", value=f"{rating_ratio :.2f} %")
    filters_row[3].metric(label="Yearly Reviews Rate", value=f"{yearly_reviews_rate_percentage:.2f} %")

    # --------------------------------- visuals --------------------------------------------------

    charts_row = st.columns(2)
    charts_row[0].plotly_chart(get_rating_dist(filtered_data), use_container_width=True)
    charts_row[1].plotly_chart(get_rating_breakdown(filtered_data), use_container_width=True)

    charts_row[0].pyplot(reviews_wordcloud(filtered_data), use_container_width=True)
    charts_row[1].plotly_chart(review_length_dist(filtered_data), use_container_width=True)


