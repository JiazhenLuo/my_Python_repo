import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as madates
import plotly.express as px
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

df = pd.read_csv("dbMovie2025.csv")

df['打分日期'] = pd.to_datetime(df['打分日期'],errors = 'coerce')
df['个人评分'] = pd.to_numeric(df['个人评分'], errors='coerce')

df = df.dropna(subset=['打分日期'])

grouped_titles = df.groupby('打分日期')['标题'].apply(lambda titles: '<br>'.join(titles)).reset_index()
grouped_titles.columns = ['date', 'titles']

# print(df[['标题','打分日期']].head())

daily_counts = df['打分日期'].value_counts().sort_index()

calendar_df = pd.DataFrame({
    'date': daily_counts.index,
    'count': daily_counts.values
})

# print(calendar_df.head())

date_range = pd.date_range(start=calendar_df['date'].min(),end=calendar_df['date'].max())

full_calendar = pd.DataFrame({'date':date_range})
full_calendar = full_calendar.merge(calendar_df, on='date',how='left')
full_calendar['count'] = full_calendar['count'].fillna(0)

full_calendar['week'] = full_calendar['date'].dt.isocalendar().week
full_calendar['weekday'] = full_calendar['date'].dt.weekday

plot_data = full_calendar.merge(grouped_titles, on='date', how='left')
plot_data['titles'] = plot_data['titles'].fillna('No movies')
plot_data['count'] = plot_data['count'].astype(int)

fig = px.scatter(
    plot_data,
    x="week",
    y="weekday",
    color=plot_data['count'],
    color_continuous_scale="Greens",
    hover_name="date",
    hover_data={"titles": False, "count": False, "week": False, "weekday": False},
    custom_data=["titles"],
    size=[500]*len(plot_data),
)

fig.update_traces(marker=dict(symbol='square', sizemode='area', sizeref=1))
fig.update_layout(
    title="🎬 2025 Movie Calendar(Jan - Mar)",
    plot_bgcolor='white',
    paper_bgcolor='white',
    xaxis=dict(showgrid=False),
    yaxis=dict(
        tickmode='array',
        tickvals=list(range(7)),
        ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        showgrid=False
    ),
    xaxis_title="Week Number",
    yaxis_title="Weekday",
    width=700,
    height=400,
    margin=dict(t=30, b=30, l=30, r=30),

)

fig.update_traces(hovertemplate="%{customdata[0]}")
fig.show()
fig.write_html("calendar_plot.html")

rating_counts = df["个人评分"].value_counts().sort_index()

bar_fig = go.Figure(data=[
    go.Bar(
        x=rating_counts.index.astype(str),
        y=rating_counts.values,
        marker=dict(color=rating_counts.values, colorscale='Greens'),
        hovertemplate="Rating: %{x}<br>Count: %{y}<extra></extra>"
    )
])

bar_fig.update_layout(
    title="🎞️ Distribution of Ratings of Movies I've Watched",
    xaxis_title="Rating",
    yaxis_title="Count",
    plot_bgcolor='white',
    paper_bgcolor='white',
    height=400,
    width=700,
    margin=dict(t=30, b=30, l=30, r=30),
)

# bar_fig.show()
bar_fig.write_html("rating_distribution.html")