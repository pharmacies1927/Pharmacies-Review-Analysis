import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
from streamlit_gsheets import GSheetsConnection
from streamlit_option_menu import option_menu

from plots import reviews_wordcloud, average_rating_overtime, \
    rating_breakdown_pie, sentiment_score_overtime, pharmacies_choropleth, top_performing_places, \
    average_rating_wrt_month_year
from template.html import card_view, review_card
from utils import pre_process_data, create_map, get_star_ratings
# from sqlalchemy import create_engine

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

data = conn.read(worksheet="Pharmacies")
reviews_data = conn.read(worksheet="AllReviews")

# data = pd.read_json("./data/Pharmacies.json")
# data = data.transpose()
# reviews_data = pd.read_json("./data/AllReviews.json")
# reviews_data = reviews_data.transpose()

data, reviews_data = pre_process_data(data, reviews_data)

# name = st.secrets['credentials']['database']
# end_point = st.secrets['credentials']['end_point']
# username = st.secrets['credentials']['username']
# password = st.secrets['credentials']['password']
# port = st.secrets['credentials']['port']
# db_url = f'postgresql://{username}:{password}@{end_point}:{port}/{name}'
# engine = create_engine(db_url).connect()
# Load data from the database into DataFrames
# pharmacies_df = pd.read_sql_table('Pharmacies', con=engine)
# reviews_df = pd.read_sql_table('Reviews', con=engine)
# data, reviews_data = pre_process_data(pharmacies_df, reviews_df)


# ----------------------------------- Main App ----------------------------------
def main():
    # ----- Menu -----
    menu = option_menu(menu_title=None, menu_icon=None, orientation="horizontal",
                       options=["Pharmacies Map", "List View", "Reviews Analytics", "Market Analysis"],
                       icons=['map', 'view-list', 'bar-chart', 'graph-up-arrow']
                       )

    # ----- Tab for Map View -----
    if menu == "Pharmacies Map":
        pharmacies_map = map_view()
        st_data = folium_static(pharmacies_map, width=1500, height=650)

    # ----- Tab for List View -----
    elif menu == "List View":
        list_view()

    # ----- Tab for Reviews Analysis -----
    elif menu == "Reviews Analytics":
        review_analytics_page()

    # ----- Tab for Pharmaceutical Market Analysis -----
    elif menu == "Market Analysis":
        market_analysis_page()


def map_view():
    """
    Function to customize view of the map tab
    - Have filters for choosing preferred location.
    - Map with custom markers, popup and frames for displaying results.
    :return: Map view
    """
    filtered_data = data.copy()

    map_filters = st.columns((1, 2, 1))
    name = map_filters[0].multiselect(label="Search by Name", options=data["name"].unique(), placeholder="All")
    if name:
        filtered_data = filtered_data[(filtered_data["name"].isin(name))]
    address = map_filters[1].multiselect(label="Address", options=data["address"].unique(), placeholder="All")
    if address:
        filtered_data = filtered_data[(filtered_data["address"].isin(address))]
    city = map_filters[2].multiselect(label="City", options=data["city"].unique(), placeholder="All")
    if city:
        filtered_data = filtered_data[(filtered_data["city"].isin(city))]

    pharmacies_map = create_map(filtered_data)

    return pharmacies_map


def list_view():
    """
    Function to create a view to list Pharmacies for smooth user interaction
    Functionalities include:
    - filters for rating, reviews and city.
    - Data filtration based on user selection.
    - Data view in list with pharmacy detail on left and its reviews on right.
    """
    filters = st.columns((1, 2, 2, 2))
    names = list(data["name"].unique())
    names.insert(0, "All")
    stars = filters[0].multiselect(label="Rating", options=[5, 4, 3, 2, 1], placeholder="All")
    reviews = filters[1].multiselect(label="Min. Reviewers",
                                     options=["Up-to 50", "50 to 100", "100-200", "More than 200"],
                                     placeholder="All")
    name = filters[2].selectbox(label="Search by Name", options=names)
    city = filters[3].multiselect(label="City", options=data["city"].unique(), placeholder="All")

    if not stars:  # if user chooses 'All'
        stars = [5, 4, 3, 2, 1]
    if not reviews:  # if user selected 'All'
        reviews = data["adjustedReview"].unique()
    if not city:  # If selected option is 'All'
        city = data["city"].unique()

    df = filter_data(stars, reviews, name, city)
    display_list_view(df)


def filter_data(stars: list, reviews: list, name: str, city: list) -> pd.DataFrame:
    """
    Filter data based on provided parameters.
    :param stars: list of values that filtered data should have in ratings columns
    :param reviews: list of values that filtered data should have in review columns
    :param name: name of the pharmacy
    :param city: list of values that filtered data should have in city columns
    :return: filtered dataframe with values that are in provided lists.
    """
    df = data.copy()
    df = df[df["adjustedRating"].isin(stars)]
    df = df[df["adjustedReview"].isin(reviews)]
    df = df[df["city"].isin(city)]
    if name != "All":
        df = df[df["name"] == name]
    df.dropna(axis=0, inplace=True)
    return df


def display_list_view(df: pd.DataFrame):
    """
    function to iterate over data after sorted to display it on individual rows
    :param df: dataframe of pharmacies data
    :return: None
    """
    st.write("# ")
    # sorting listings by 'rank' column
    pharmacies = df.sort_values(['totalReviews', 'averageRating'], ascending=[False, False])
    pharmacies.reset_index(drop=True, inplace=True)
    # pharmacies = df.sort_values(by="rank", ascending=True)

    if len(pharmacies) == 0:
        # if there is no pharmacy after filtering
        st.info("No Listed Pharmacy found!", icon="🚨")
    else:
        for i, pharmacy in pharmacies.iterrows():
            display_pharmacy(i, pharmacy)


def display_pharmacy(i: int, pharmacy: pd.Series):
    """
    function to list pharmacy details in a card view
    :param i: index/rank of pharmacy
    :param pharmacy: Details of pharmacy
    :return: None
    """
    upper_row = st.columns(2)
    # filtering pharmacy data based on current pharmacy
    pharmacy_reviews = reviews_data[reviews_data.place_Name == pharmacy["name"]]
    with upper_row[0]:
        row = st.columns((1, 2, 8))
        # card view
        row[0].write(f"# ")
        row[0].write(f"### {i + 1}")
        # image on left
        row[1].image(r"./assets/icon-min.png")
        # info on right
        row[2].markdown(card_view(pharmacy["name"], pharmacy["address"],
                                  f"{pharmacy['averageRating']:.1f}", pharmacy["totalReviews"],
                                  pharmacy["contact"]),
                        unsafe_allow_html=True)
    with upper_row[1]:
        # Pharmacy Reviews Tab
        review_bar = st.expander(label=f"Reviews ({len(pharmacy_reviews)})")
        with review_bar:
            # filter to choose results based on star rating
            review_star = st.multiselect(label=" ",
                                         options=["⭐ 5 😊", "⭐ 4 🙂", "⭐ 3 😕", "⭐ 2 😒", "⭐ 1 😑"],
                                         placeholder="All ⭐",
                                         key=f"{pharmacy['id']}-star")
            # reviews display
            display_reviews(review_star, pharmacy_reviews)
    st.write("---")


def display_reviews(review_star: list, pharmacy_reviews: pd.DataFrame):
    """
    Function to display reviews in customized html cards on individual rows.
    :param review_star: list containing filtered rating.
    :param pharmacy_reviews: dataframe containing pharmacies reviews.
    :return:
    """
    if len(review_star) == 0:  # if user selects 'All'
        star_rating_list = [5, 4, 3, 2, 1]
    else:
        star_rating_list = get_star_ratings(review_star)  # get mapped equivalent list

    # filtering data based on user selected ratings
    filtered_reviews_df = pharmacy_reviews[pharmacy_reviews["rating"].isin(star_rating_list)]

    # if no reviews found for current rating selection
    if len(filtered_reviews_df) == 0:
        st.info("No reviews found!", icon="🚨")
    else:
        filtered_reviews_df = filtered_reviews_df.sort_values(by="datetime", ascending=False)
        # displaying reviews info one by one
        for _, review in filtered_reviews_df.iterrows():
            row_ = st.columns((1, 6))
            # reviewer image on left
            row_[0].image(r"./assets/reviewer.png")
            # review detail on right
            row_[1].markdown(review_card(review['reviewer'], review['date'],
                                         review['rating']),
                             unsafe_allow_html=True)
            # review text on bottom
            if review["text"] != "nan":
                st.write(f"{review['text']}")
            st.write("---")


def calculate_kpis(filtered_data: pd.DataFrame):
    """
    Function to calculate KPI values
    :param filtered_data: filtered data based on user preferences
    :return: Tuple(int, float, float, float)
    """
    # total reviews of a pharmacy
    total_reviews = len(filtered_data)
    # average rating for a pharmacy
    average_ratings = filtered_data['rating'].mean()
    # total number of unique years
    total_years = filtered_data['datetime'].dt.year.nunique()
    # yearly review rate/frequency
    yearly_reviews_rate_percentage = (total_reviews / total_years)
    # rating ratio
    rating_ratio = (average_ratings * total_reviews / len(reviews_data)) * 100

    return total_reviews, average_ratings, yearly_reviews_rate_percentage, rating_ratio


def display_reviews_analysis(filtered_data: pd.DataFrame) -> None:
    """
    Function to display reviews analytics.
    :param filtered_data: filtered data based on user preferences.
    :return: None
    """

    charts_row = st.columns((4, 3))
    # Chart to display Reviews Distribution w.r.t Quarter-Year
    charts_row[0].plotly_chart(average_rating_overtime(filtered_data), use_container_width=True)
    # Chart to display Reviews per Rating
    charts_row[1].plotly_chart(rating_breakdown_pie(filtered_data), use_container_width=True)

    # scatter plot to display sentiment score over the time
    charts_row[0].plotly_chart(sentiment_score_overtime(filtered_data), use_container_width=True)
    # Wordcloud figure to analyze frequently occurring words in review text
    charts_row[1].pyplot(reviews_wordcloud(filtered_data), use_container_width=True)

    # chart to display the varying rating over the time
    st.plotly_chart(average_rating_wrt_month_year(filtered_data), use_container_width=True)


def review_analytics_page():
    """
    Function to show filter, display KPIs and analytics for a pharmacy
    Functionalities:
     - Filters for choosing pharmacy by name.
     - KPIs for Total Reviews, Avg. Rating, Review Frequency and Yearly Review Rate.
     - Wordcloud to analyze frequent occurring words in reviews.
     - Plotly bar chart for analyzing average reviews w.r.t Quarters for every year.
     - Plotly Scatter chart to analyze sentiment score over the time.
     - Plotly Pie Chart to get distribution of review per rating.
    :return: Streamlit frame/view
    """
    filter_kpi_row = st.columns((4, 1, 2, 2, 2, 2))
    place = filter_kpi_row[0].selectbox("Select Pharmacy", options=reviews_data["place_Name"].unique())

    filtered_data = reviews_data[(reviews_data['place_Name'] == place)]

    total_reviews, average_ratings, yearly_reviews_rate_percentage, rating_ratio = calculate_kpis(filtered_data)
    # Average rating for the selected pharmacy
    filter_kpi_row[2].metric(label="Average Rating", value=f"{average_ratings:.1f}")
    # Total reviews of the selected pharmacy
    filter_kpi_row[3].metric(label="Total Reviews", value=f"{total_reviews}")
    # Rating ratio
    filter_kpi_row[4].metric(label="Review Frequency", value=f"{rating_ratio :.2f} %")
    # Yearly review rate/frequency
    filter_kpi_row[5].metric(label="Yearly Reviews Rate", value=f"{yearly_reviews_rate_percentage:.2f} %")

    # calling function to display analytics charts based on selected place
    display_reviews_analysis(filtered_data)


@st.cache_resource
def market_analysis_page():
    """
    Function to create view for the 'Market Analysis' tab
    :return: Analytics charts
    """
    cols = st.columns(2)
    cols[0].write("#### Geographical Distribution of Ratings")
    cols[0].plotly_chart(pharmacies_choropleth(data), use_container_width=True)
    cols[1].write("#### Top Rated Pharmacies")
    cols[1].plotly_chart(top_performing_places(data), use_container_width=True)


if __name__ == "__main__":
    main()
