import sqlite3

import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html
import asyncio


async def run_dashboard():
    app = dash.Dash(__name__)

    def fetch_data():
        localdb = sqlite3.connect("files.db")
        return pd.read_sql_query('SELECT * FROM files WHERE time_deleted IS NULL', localdb)

    df = fetch_data()
    app.layout = html.Div([
        dcc.Graph(
            id='file_size_bar',
            figure=px.bar(df, x='name', y='file_size', title='file_size_bar')
        ),
        dcc.Graph(
            id='text_or_binary_files',
            figure=px.pie(df, names='is_text', title='text_or_binary_files')
        ),
        dcc.Graph(
            id='file_type_pie',
            figure=px.pie(df, names='file_type', title='file_type_pie')
        ),
        dcc.Interval(id='updates', interval=10 * 1000, n_intervals=0)
    ])

    @app.callback(
        dash.dependencies.Output('file_size_bar', 'figure'),
        dash.dependencies.Output('text_or_binary_files', 'figure'),
        dash.dependencies.Output('file_type_pie', 'figure'),
        [dash.dependencies.Input('updates', 'n_intervals')]
    )
    def update_graph(n):
        update_df = fetch_data()
        change_bar = px.bar(update_df, x='name', y='file_size', title='file_size_bar')
        change_pie = px.pie(update_df, names='is_text', title='text_or_binary_files')
        change_pie2 = px.pie(update_df, names='file_type', title='file_type_pie')
        return change_bar, change_pie, change_pie2

    # await asyncio.sleep(10)
    app.run_server(debug=True, use_reloader=False)


if __name__ == '__main__':
    run_dashboard()
