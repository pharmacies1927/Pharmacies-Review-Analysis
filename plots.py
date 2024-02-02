import json

import pandas as pd
import plotly.graph_objects as go
from matplotlib import pyplot as plt
from wordcloud import WordCloud

from utils import insert_sentiment_scores

COLORS = ["#fdfcdc", "#0081a7", "#00afb9", "#fed9b7", "#f07167"]


def get_rating_dist(df: pd.DataFrame) -> go.Figure:
    """
    Generate a bar chart to visualize the distribution of total ratings over the years.
    :param df: The input DataFrame containing review data.
    :return: A Plotly Figure representing the distribution of total ratings over the years.
    """
    df.reset_index(inplace=True)
    df["year"] = df["datetime"].dt.year
    df = df.groupby("year")["rating"].sum().reset_index()
    fig = go.Figure(
        go.Bar(
            x=df["year"],
            y=df["rating"],
            name="Total Rating",
            marker=dict(color="#264653"),
            text=df["rating"],
            hovertext=df["rating"].astype(str) + " Reviews in Year " + df["year"].astype(str)
        )
    )
    fig = update_layout(fig, "Year", "Total Ratings", "Reviews' Yearly Distribution")

    return fig


def get_rating_breakdown(df: pd.DataFrame) -> go.Figure:
    """
    Generate a bar chart to visualize the breakdown of reviews by rating.
    :param df: The input DataFrame containing review data.
    :return: A Plotly Figure representing the breakdown of reviews by rating.
    """
    df = df.groupby("rating")["text"].count().reset_index()
    df.sort_values(by="rating", ascending=True, inplace=True)
    fig = go.Figure(
        go.Bar(
            x=df["rating"],
            y=df["text"],
            name="Reviews Count",
            marker=dict(color="#2a9d8f"),
            text=df["text"],
            hovertext=df["text"].astype(str) + " Reviews with Ratings of " + df["rating"].astype(str) + " stars"
        )
    )
    fig = update_layout(fig, "Rating", "Review Count", "Reviews' per Rating")

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


def review_length_dist(df: pd.DataFrame) -> go.Figure:
    """
    Generate a histogram to visualize the distribution of review lengths in a DataFrame.

    :param df: The input DataFrame containing review data.
    :return: A Plotly Figure representing the distribution of review lengths.
    """
    # Calculate the length of each review
    df['review_length'] = df['text'].apply(len)

    fig = go.Figure(
        go.Histogram(
            x=df["review_length"],
            name="Review Length",
            marker=dict(color="#003049"),
            hovertemplate='%{y} Reviews with length %{x} words<extra></extra>',
        )
    )
    fig = update_layout(fig, "Review Length", "Number of Reviews", "Distribution of Review Lengths")
    return fig


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


def average_rating_overtime(df):
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


def rating_breakdown_pie(df: pd.DataFrame) -> go.Figure:
    """
    Generate a bar chart to visualize the breakdown of reviews by rating.
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
        mapbox_zoom=8,
        mapbox_center={"lat": 46.8, "lon": 8.2},
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
    df = df.dropna(subset=["averageRating"])
    df.sort_values(by="averageRating", ascending=True, inplace=True)
    top_places = df.head(20)
    fig = go.Figure(
        go.Bar(
            y=top_places["name"],
            x=top_places["averageRating"],
            orientation="h",
            marker=dict(color="#2a9d8f")
        )
    )

    fig = update_layout(fig, "Rating", "Pharmacy", None)
    fig.update_layout(height=700)

    return fig
