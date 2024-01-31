import pandas as pd
from folium import folium


def pre_process_data(data):
    data = data.transpose()
    data.reset_index(inplace=True)
    data = adjust_column_datatypes(data)
    data.fillna(0, inplace=True)
    data["markerColor"] = data["totalReviews"].apply(
        lambda x: "green" if x >= 100 else ("orange" if x >= 50 else ("lightgray" if x >= 25 else "red")))
    data["totalReviews"] = data["totalReviews"].astype(int)
    data["city"] = data["address"].apply(lambda x: x.split(', ')[-2].split(' ')[-1])
    data["adjustedReview"] = data["totalReviews"].apply(adjusted_reviews)
    data["adjustedRating"] = data["averageRating"].apply(lambda x: int(x // 1))

    return data


def adjusted_reviews(review):
    if review >= 200:
        return "More than 200"
    elif 100 < review <= 200:
        return "100-200"
    elif 50 < review <= 100:
        return "50 to 100"
    else:
        return "Up-to 50"


def adjust_column_datatypes(df):
    numeric_cols = ['averageRating', 'latitude', 'longitude', 'totalReviews', 'id']
    for column in numeric_cols:
        df[column] = pd.to_numeric(df[column], errors='coerce', downcast='float')
    df['createdAt'] = pd.to_datetime(df['createdAt'])
    df["contact"] = df["contact"].apply(lambda x: ''.join(filter(str.isdigit, str(x))))
    return df


def pre_process_reviews(data):
    data = data.transpose()
    data.reset_index(inplace=True)
    data = adjust_column_datatypes_of_reviews(data)
    data.fillna(0, inplace=True)
    data["date"] = data["datetime"].dt.strftime("%d-%m-%Y")
    data.sort_values(by="datetime", ascending=True, inplace=True)
    return data


def adjust_column_datatypes_of_reviews(df):
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["text"] = df["text"].astype(str)
    df["rating"] = pd.to_numeric(df["rating"], errors='coerce', downcast='float')
    return df


def create_map(data):
    # map_center = [data["latitude"].mean(), data["longitude"].mean()]
    map_center = [46.9480, 7.4474]
    my_map = folium.Map(location=map_center, zoom_start=15, control_scale=True, prefer_canvas=True, )

    for i, row in data.iterrows():
        iframe = folium.IFrame(html.format(
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