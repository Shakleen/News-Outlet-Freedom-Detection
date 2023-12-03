import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objs as go

def plot_class(fig, df, column_name, source_type, name, offsetgroup, column):
    classes = df[column_name][df.source_type==source_type]
    uniques = classes.unique()
    values = classes.value_counts()

    fig.add_trace(
        go.Bar(name=name, x=uniques, y=values, offsetgroup=offsetgroup, text=values),
        row=1, col=column
    )
        
def plot_class_distribution(df, title, subtitle, height=500, width=800):
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True)

    plot_class(fig, df, "sentiment_class", "local", "Local Sentiment", 1, 1)
    plot_class(fig, df, "sentiment_class", "international", "International Sentiment", 1, 1)
    plot_class(fig, df, "stance_class", "local", "Local Stance", 2, 2)
    plot_class(fig, df, "stance_class", "international", "International Stance", 2, 2)

    fig.update_layout(height=height, width=width, title_x=0.5,
                    title_text=f"{title}<br><sup>{subtitle}</sup>",
                    legend=dict(orientation='h',yanchor='top',xanchor='center',y=-0.1,x=0.5),
                    barmode='stack')
    fig.show()


def plot_score(fig, df, column_name, source_type, name, offsetgroup, row):
    classes = df[column_name][df.source_type==source_type]
    uniques = classes.unique()
    values = classes.value_counts()

    fig.add_trace(
        go.Histogram(name=name, x=uniques, y=values, 
                    offsetgroup=offsetgroup, text=values,
                    nbinsx=4),
        row=row, col=1
    )
    
def plot_score_distribution(df, title, subtitle, height=500, width=800):
    fig = make_subplots(rows=2, cols=1, shared_yaxes=True)

    plot_score(fig, df, "sentiment_score", "local", "Local Sentiment Score", 1, 1)
    plot_score(fig, df, "sentiment_score", "international", "International Sentiment Score", 1, 1)
    plot_score(fig, df, "stance_score", "local", "Local Stance Score", 2, 2)
    plot_score(fig, df, "stance_score", "international", "International Stance Score", 2, 2)

    fig.update_layout(height=height, width=width, title_x=0.5,
                    title_text=f"{title}<br><sup>{subtitle}</sup>",
                    legend=dict(orientation='h',yanchor='top',xanchor='center',y=-0.1,x=0.5),
                    barmode='stack')
    fig.show()
    
def plot_scatter(df, title, subtitle, height=500, width=800):
    fig = px.scatter(df, 
                 x = "sentiment_score", 
                 y = "stance_score", 
                 color = "source_type")

    fig.update_traces(marker_size=10)
    fig.update_layout(height=height, width=width, title_x=0.5,
                    title_text=f"{title}<br><sup>{subtitle}</sup>",
                    legend=dict(orientation='h',yanchor='top',xanchor='center',y=-0.1,x=0.5))
    fig.show()