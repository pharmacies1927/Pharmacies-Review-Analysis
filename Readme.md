# Pharmacies Listings Analysis

This Streamlit app provides an interactive interface for exploring and analyzing listings containing pharmacies' data and their reviews.

## Installation

To run this project, make sure you have Python installed. Clone the repository and install the required packages using the following commands:

```bash
cd /Pharmacies-Listings-Analysis
pip install -r requirements.txt
```

## Running the Dashboard

Execute the following command in the terminal to run the Streamlit app:

```bash
streamlit run app.py
```

Open your web browser and navigate to the provided [URL](http://localhost:8501/) to interact with the dashboard.

## Project Structure

### Dependencies

- [Streamlit](https://www.streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [Folium](https://python-visualization.github.io/folium/)
- [Plotly](https://plotly.com/)
- [openpyxl]

### Files

- **plots.py**: Contains functions for generating various plots and visualizations for analysis tab.
- **template/html.py**: Includes HTML templates for creating customized components.
- **utils.py**: Utility functions for data preprocessing and map creation.
- **css/style.css**: Contains css styling script for the app.
- **requirements.txt**: Contains list of dependencies.

### Data

- **Pharmacies.json**: JSON file containing information about pharmacies.
- **AllReviews.json**: JSON file containing pharmacies' reviews data.

## Dashboard Features

### Page Configuration

- The dashboard title is set to "Pharmacies Listings".
- The layout is configured to be wide.
- The dashboard has a menu with options for 
  - "Pharmacies Map" 
  - "List View"
  - "Reviews Analysis"

#### Pharmacies Map

- Displays a map of pharmacies using Folium framework.

#### List View

- Provides a list view of pharmacies based on user-selected filters.
- Displays relevant pharmacy information, including 
  - Name
  - Address
  - Ratings
  - Detailed Reviews
  - Contact Details.

#### Reviews Analysis

- Allows users to analyze reviews for a selected pharmacy within a specified time period.
- Shows key performance indicators (KPIs) and visualizations related to reviews.

---