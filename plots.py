import json

import pandas as pd
import plotly.graph_objects as go
from matplotlib import pyplot as plt
from wordcloud import WordCloud

from utils import insert_sentiment_scores

COLORS = ["#0081a7", "#00afb9", "#f07167", "#e9c46a",
          "#264653", "#f4a261", "#e76f51", "#ef233c", "#fed9b7"
          "#f6bd60", "#84a59d", "#f95738", "#fdfcdc", ]


def update_layout(fig: go.Figure, x_label: str, y_label: str, title: str) -> go.Figure:
    """
    Updates the layout of a Plotly figure with specified labels and title.

    :param fig: plotly fig to be updated
    :param x_label: title for x-axis
    :param y_label: title for y-axis
    :param title: title for the plotly fig
    :return: The updated Plotly figure
    """
    fig = fig.update_layout(xaxis_title=x_label, yaxis_title=y_label,
                            title=title,
                            hovermode="x unified",
                            hoverlabel=dict(
                                bgcolor="white",
                                font_color="black",
                                font_size=16,
                                font_family="Rockwell"
                            )
                            )
    return fig


def reviews_wordcloud(df: pd.DataFrame) -> plt.figure:
    """
    Generate a word cloud to visualize frequent words in a DataFrame of reviews.

    :param df: The input DataFrame containing review data.
    :return: A matplotlib figure representing the word cloud
    """
    wordcloud = WordCloud(background_color='white', min_font_size=5).generate(
        ' '.join(df['text']))

    # Convert the word cloud to an image
    fig = plt.figure(facecolor=None)
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=10)
    plt.title("Frequent Words in Reviews")

    return fig


def average_rating_overtime(df):
    """
    Function to plot Bar Chart to visualize average rating
    w.r.t Quarters for each year
    :param df: The input DataFrame containing review data.
    :return: A Plotly Figure representing average distribution overtime.
    """
    # Calculate the length of each review
    df['year'] = df['datetime'].dt.year
    df['quarter'] = df['datetime'].dt.quarter

    # Calculate average rating for each year and quarter
    avg_rating = df.groupby(['year', 'quarter'])['rating'].mean().reset_index()

    # Create a Plotly Go figure
    fig = go.Figure()

    # Add a bar trace for each quarter
    for quarter in range(1, 5):
        quarter_data = avg_rating[avg_rating['quarter'] == quarter]
        fig.add_trace(go.Bar(
            x=quarter_data['year'],
            y=quarter_data['rating'],
            name=f'Quarter {quarter}',
            marker=dict(color=COLORS[quarter])
        ))

    # Customize the layout
    fig.update_layout(barmode='group', legend=dict(title='Quarter'))

    fig = update_layout(fig, "Time", "Average Rating", "Average Rating overtime")
    return fig


def average_rating_wrt_month_year(df):
    """
    Function to plot Bar Chart to visualize average rating
    w.r.t Months for each year
    :param df: The input DataFrame containing review data.
    :return: A Plotly Figure representing average distribution overtime.
    """
    df['year'] = df['datetime'].dt.year
    df['month_num'] = df['datetime'].dt.month
    df['month_year'] = df['datetime'].dt.strftime("%b %Y")

    # Calculate average rating for each year and month
    avg_rating = df.groupby(['year', 'month_num', 'month_year'])['rating'].mean().reset_index()

    # Create a Plotly go figure
    fig = go.Figure()

    years = sorted(list(avg_rating['year'].unique()))
    # Add a bar trace for each month
    for year in years:
        year_data = avg_rating[avg_rating['year'] == year]
        year_data.sort_values(by='month_num', inplace=True)
        fig.add_trace(go.Bar(
            x=year_data['month_year'],
            y=year_data['rating'],
            name=f'{year}',
        ))

    # Customize the layout
    fig.update_layout(barmode='group', legend=dict(title='Year'))

    fig = update_layout(fig, "Time", "Average Rating", "Average Rating overtime w.r.t Month-Year")
    return fig


def rating_breakdown_pie(df: pd.DataFrame) -> go.Figure:
    """
    Generate a pie chart to visualize the breakdown of reviews by rating.
    :param df: The input DataFrame containing review data.
    :return: A Plotly Figure representing the breakdown of reviews by rating.
    """
    df = df.groupby("rating")["text"].count().reset_index()
    df["rating"] = df["rating"].astype(int)
    df["Rating-Formatted"] = df["rating"].map({
        5: "⭐ 5 😊", 4: "⭐ 4 🙂", 3: "⭐ 3 😕", 2: "⭐ 2 😒", 1: "⭐ 1 😑"
    })
    df.sort_values(by="rating", ascending=True, inplace=True)
    fig = go.Figure(
        go.Pie(
            labels=df["Rating-Formatted"],
            values=df["text"],
            hole=0.3,
            sort=False
        )
    )
    fig.update_traces(hoverinfo='label+value', textinfo='percent', textfont_size=15,
                      marker=dict(colors=COLORS))
    fig = update_layout(fig, "Rating", "Review Count", "Rating Distribution")

    return fig


def sentiment_score_overtime(df):
    """
    Function to plot a scatter chart to visualize sentiment score
    w.r.t time
    :param df: The input DataFrame containing review data.
    :return: A Plotly Figure representing sentiment score overtime.
    """
    df = insert_sentiment_scores(df)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["datetime"],
            y=df["sentiment_score"],
            name="Sentiment Score",
            mode="markers",
            marker=dict(color="#84a59d", size=20),
        )
    )
    fig.add_hrect(y0=0.05, y1=1.05, line_width=0, fillcolor="#57cc99", opacity=0.2)
    fig.add_hrect(y0=-0.05, y1=-1.05, line_width=0, fillcolor="#ef233c", opacity=0.2)

    fig = update_layout(fig, "Time", "Sentiment Score", "Sentiment Analysis overtime")

    return fig


def pharmacies_choropleth(df):
    """
    Function to plot map plot based on average rating w.r.t region
    :param df: The input DataFrame containing review data.
    :return: A Plotly Figure showing rating density per region.
    """
    # LOAD geojson FILE
    with open("data/georef-switzerland-kanton.geojson") as response:
        geo = json.load(response)

    # Geographic Map
    fig = go.Figure(
        go.Choroplethmapbox(
            geojson=geo,
            locations=df["city"],
            featureidkey="properties.kan_name",
            z=df["averageRating"],
            colorscale="sunsetdark",
            marker_opacity=0.8,
            marker_line_width=1,
        )
    )
    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=7.4,
        mapbox_center={"lat": 46.9, "lon": 7.44},
        height=600,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        title="Geographical Distribution of Ratings",
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="white",
            font_color="black",
            font_size=16,
            font_family="Rockwell"
        )
    )

    return fig


def top_performing_places(df):
    """
    Function to plot Bar Chart to get top ranked pharmacies
    :param df: The input DataFrame containing review data.
    :return: A Plotly Figure representing top 30 pharmacies
    based on reviews and ratings.
    """
    df = df.dropna(subset=["averageRating"])
    df = df.groupby("name").agg({
        "averageRating": "mean",
        "totalReviews": "sum"
    }).reset_index()

    thresh = df["totalReviews"].mean()
    df = df[df["totalReviews"] >= thresh]
    df["rank"] = (df["averageRating"] / df["totalReviews"]) * 100
    df.sort_values(by="rank", ascending=False, inplace=True)
    top_places = df.head(30)
    top_places["SatisfactionLevel"] = top_places["rank"].apply(lambda x: f"{round(100 - x, 2):.2f}%")

    fig = go.Figure(
        go.Bar(
            y=top_places["name"],
            x=top_places["rank"],
            marker=dict(color="#2a9d8f"),
            orientation="h",
            text=top_places["SatisfactionLevel"],
            hovertext=top_places["averageRating"].astype(str) +
                      " stars(" + top_places["totalReviews"].astype(str) +
                      ") | Satisfaction Level= " + top_places["SatisfactionLevel"]
        )
    )

    fig.update_layout(height=700,
                      xaxis_title="Rank",
                      yaxis_title="Pharmacy",
                      yaxis=dict(autorange="reversed"),
                      # hovermode="x unified",
                      hoverlabel=dict(
                          bgcolor="white",
                          font_color="black",
                          font_size=16,
                          font_family="Rockwell"
                      ))

    return fig
