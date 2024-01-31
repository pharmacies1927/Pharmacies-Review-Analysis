from typing import Tuple

import pandas as pd
import folium
from template.html import POPUP


def pre_process_data(data: pd.DataFrame, reviews: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Pre-processes data related to pharmacy listings and reviews.
    :param data: DataFrame containing information about pharmacy listings.
    :param reviews: DataFrame containing reviews data.
    :return: A tuple containing pre-processed DataFrames for listings and reviews.
    """
    data = pre_process_listings_data(data)
    reviews = pre_process_reviews(reviews)
    return data, reviews


def pre_process_listings_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Pre-processes pharmacy listings data.
    :param data: The input DataFrame containing pharmacy listings data.
    :return: Processed DataFrame with adjusted column datatypes, filled NaN values,
    added markerColor based on totalReviews, adjustedReview, and adjustedRating columns.
    """
    # data = data.transpose()
    data.reset_index(inplace=True)
    data = adjust_column_datatypes(data)
    data.fillna(0, inplace=True)
    data["markerColor"] = data["totalReviews"].apply(
        lambda x: "green" if x >= 100 else ("orange" if x >= 50 else ("lightgray" if x >= 25 else "red")))
    data["totalReviews"] = data["totalReviews"].astype(int)
    data["city"] = data["address"].apply(lambda x: x.split(', ')[-2].split(' ')[-1])
    data["adjustedReview"] = data["totalReviews"].apply(adjusted_reviews)
    data["adjustedRating"] = data["averageRating"].apply(lambda x: int(x // 1))
    # Create a new column 'ranking' based on the total number of reviews and average ratings
    data['rank'] = data['totalReviews'].rank(ascending=False, method='min') + \
                   data['averageRating'].rank(ascending=False, method='min')

    # Sort the DataFrame based on 'ranking'
    data.sort_values(by='rank', inplace=True)
    data.reset_index(drop=True, inplace=True)

    return data


def adjusted_reviews(review: int) -> str:
    """
    Categorizes the number of reviews into different groups based on provided values.

    :param review: The total number of reviews.
    :return: A string indicating the category of the number of reviews.
    """
    if review >= 200:
        return "More than 200"
    elif 100 < review <= 200:
        return "100-200"
    elif 50 < review <= 100:
        return "50 to 100"
    else:
        return "Up-to 50"


def adjust_column_datatypes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adjusts the data types of specified columns in the DataFrame.
    The function performs the following transformations:
        - Converts numeric columns ('averageRating', 'latitude', 'longitude', 'totalReviews', 'id') to float,
          handling errors by coercing to NaN.
        - Converts the 'createdAt' column to datetime.
        - Extracts numeric characters from the 'contact' column, ensuring it contains only digits.

    :param df: The input DataFrame.
    :return: The DataFrame with adjusted column data types.
    """
    numeric_cols = ['averageRating', 'latitude', 'longitude', 'totalReviews', 'id']
    for column in numeric_cols:
        df[column] = pd.to_numeric(df[column], errors='coerce', downcast='float')
    df['createdAt'] = pd.to_datetime(df['createdAt'])
    df["contact"] = df["contact"].apply(lambda x: ''.join(filter(str.isdigit, str(x))))
    return df


def pre_process_reviews(data: pd.DataFrame) -> pd.DataFrame:
    """
    Pre-processes the reviews data by performing the following steps:

        - Transposes the DataFrame.
        - Resets the index for consistency.
        - Adjusts column datatypes.
        - Fills missing values with 0.
        - Converts the 'datetime' column to a formatted 'date' column.
        - Sorts the DataFrame by the 'datetime' column in ascending order.

    :param data: The input DataFrame containing reviews data.
    :return: The pre-processed DataFrame with transformations.
    """
    # data = data.transpose()
    data.reset_index(inplace=True)
    data = adjust_column_datatypes_of_reviews(data)
    data.fillna(0, inplace=True)
    data["date"] = data["datetime"].dt.strftime("%d-%m-%Y")
    data.sort_values(by="datetime", ascending=True, inplace=True)
    return data


def adjust_column_datatypes_of_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adjusts the data types of columns in a DataFrame related to reviews.
    This function specifically handles the following columns:
        - 'datetime': Converts to datetime format.
        - 'text': Converts to string type.
        - 'rating': Converts to numeric type with float precision.

    :param df: The input DataFrame containing review data.
    :return: The DataFrame with adjusted data types.
    """
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["text"] = df["text"].astype(str)
    df["rating"] = pd.to_numeric(df["rating"], errors='coerce', downcast='float')
    return df


def create_map(data: pd.DataFrame) -> folium.Map:
    """
    Creates a Folium map with markers for pharmacies based on the provided DataFrame.

    :param data: The DataFrame containing pharmacy data.
    :return: The Folium map with pharmacy markers.
    """
    if len(data) == 0:
        return folium.Map(location=[46.9480, 7.4474], zoom_start=8, control_scale=True, prefer_canvas=True, )

    map_center = [data["latitude"].mean(), data["longitude"].mean()]
    # map_center = [46.9480, 7.4474]
    my_map = folium.Map(location=map_center, zoom_start=15, control_scale=True, prefer_canvas=True, )

    for i, row in data.iterrows():
        iframe = folium.IFrame(POPUP.format(
            str(row["name"]),
            str(row["address"]),
            str(round(row["averageRating"], 1)),
            str(row["totalReviews"]),
            row["contact"]
        ), width=300, height=250)

        popup = folium.Popup(iframe, min_width=150, max_width=300)
        # Add each row to the map
        folium.Marker(location=[row['latitude'], row['longitude']],
                      tooltip=row["name"],
                      # icon=folium.features.CustomIcon(icon_image=r"img0.png", icon_size=(70, 70)),
                      icon=folium.Icon(color=row['markerColor'],
                                       icon="medkit",
                                       prefix='fa'),
                      popup=popup,
                      ).add_to(my_map)

    return my_map


def get_star_ratings(rating_list: list) -> list:
    """
    Function to map customized string representation
    of ratings to corresponding integer representation
    :param rating_list: list of customized rating description
    :return: list of equivalent integer description of star ratings
    """
    int_rating_list = []
    for star in rating_list:
        if star == "⭐ 5 😊":
            int_rating_list.append(5)
        elif star == "⭐ 4 🙂":
            int_rating_list.append(4)
        elif star == "⭐ 3 😕":
            int_rating_list.append(3)
        elif star == "⭐ 1 😑":
            int_rating_list.append(2)
        else:
            int_rating_list.append(1)
    return int_rating_list
