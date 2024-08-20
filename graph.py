import asyncio
import sqlite3
from track_folder import return_count
import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html


async def run_dashboard():
    app = dash.Dash(__name__)
    is_text_translator = {0: 'text', 1: 'video', -1: 'no clue'}

    def fetch_data():
        localdb = sqlite3.connect("files.db")
        df = pd.read_sql_query('SELECT * FROM files WHERE time_deleted IS NULL', localdb)
        df['is_text'] = df['is_text'].map(is_text_translator)
        return df

    def count_by_file_size():
        localdb = sqlite3.connect("files.db")
        df = pd.read_sql_query('SELECT file_size, COUNT(*) as count FROM files WHERE time_deleted IS NULL GROUP BY file_size', localdb)
        df.sort_values(by=['file_size'], ascending=False, inplace=True)
        return df

    count_file_size_df = count_by_file_size()
    df = fetch_data()
    app.layout = html.Div([

        dcc.Graph(
            id='file_size_histogram',
            figure=px.histogram(count_file_size_df, x='file_size', y='count', title='file_size_histogram')
        ),
        dcc.Graph(
            id='text_or_binary_files',
            figure=px.pie(df, names='is_text', title='text_or_binary_files')
        ),
        dcc.Graph(
            id='file_type_pie',
            figure=px.pie(df, names='file_type', title='file_type_pie')
        ),
        html.Div(return_count(), id='count'),
        dcc.Interval(id='updates', interval=10 * 1000, n_intervals=0)
    ])

    @app.callback(
        dash.dependencies.Output('file_size_histogram', 'figure'),
        dash.dependencies.Output('text_or_binary_files', 'figure'),
        dash.dependencies.Output('file_type_pie', 'figure'),
        dash.dependencies.Output('count', 'children'),
        [dash.dependencies.Input('updates', 'n_intervals')]
    )
    def update_graph(n):
        update_df = fetch_data()
        count_file_size_df = count_by_file_size()
        count_queue = return_count()
        change_histogram = px.histogram(count_file_size_df, x='file_size', y='count', title='file_size_histogram')
        change_pie = px.pie(update_df, names='is_text', title='text_or_binary_files')
        change_pie2 = px.pie(update_df, names='file_type', title='file_type_pie')
        return change_histogram, change_pie, change_pie2,f'Total Count: {count_queue}'

    loop = asyncio.get_event_loop()

    def run_my_server():
        app.run_server(debug=True, use_reloader=False)

    loop.run_in_executor(None, run_my_server)


if __name__ == '__main__':
    asyncio.run(run_dashboard())
