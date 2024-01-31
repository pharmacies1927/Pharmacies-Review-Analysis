import pandas as pd
import plotly.graph_objects as go
from matplotlib import pyplot as plt
from wordcloud import WordCloud


def get_rating_dist(df: pd.DataFrame) -> go.Figure:
    """
    Generate a bar chart to visualize the distribution of total ratings over the years.
    :param df: The input DataFrame containing review data.
    :return: A Plotly Figure representing the distribution of total ratings over the years.
    """
    df.reset_index(inplace=True)
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
