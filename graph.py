import asyncio
import sqlite3

import dash
import pandas as pd
import plotly.express as px
from dash import ctx
from dash import dcc, html
from track_folder import return_count
global_mode = -2

async def run_dashboard():
    app = dash.Dash(__name__)
    is_text_translator = {0: 'text', 1: 'video', -1: 'no clue'}

    def fetch_data():
        localdb = sqlite3.connect("files.db")
        df = pd.read_sql_query('SELECT * FROM files WHERE time_deleted IS NULL', localdb)
        df['is_text'] = df['is_text'].map(is_text_translator)
        return df

    def df_count_by_binary_type(is_text):
        localdb = sqlite3.connect("files.db")
        if is_text or is_text == 0:
            df_modified = pd.read_sql_query(
                'SELECT file_size, COUNT(*) as count FROM files WHERE time_deleted IS NULL AND is_text = ? GROUP BY file_size',
                localdb,
                params=(is_text,))
            return df_modified
        else:
            df = pd.read_sql_query(
                'SELECT file_size, COUNT(*) as count FROM files WHERE time_deleted IS NULL GROUP BY file_size', localdb)
            return df

        # bad function to get all the values by binary

    def df_full_by_binary_count(is_text):
        localdb = sqlite3.connect("files.db")
        if is_text or is_text == 0:
            df_modified = pd.read_sql_query(
                'SELECT * FROM files WHERE time_deleted IS NULL AND is_text = ?', localdb,
                params=(is_text,))
            df_modified['is_text'] = df_modified['is_text'].map(
                is_text_translator)  # change the description on the right
            return df_modified
        else:
            df_modified = pd.read_sql_query('SELECT * FROM files WHERE time_deleted IS NULL', localdb)
            df_modified['is_text'] = df_modified['is_text'].map(
                is_text_translator)  # change the description on the right
            return df_modified

    df = fetch_data()
    count_file_size_df = df_count_by_binary_type(None)
    app.layout = html.Div([

        dcc.Graph(
            id='file_size_histogram',
            figure=px.histogram(count_file_size_df, y='count', x='file_size', title='file_size_histogram')
        ),
        dcc.Graph(
            id='text_or_binary_files',
            figure=px.pie(df, names='is_text', title='text_or_binary_files')
        ),
        dcc.Graph(
            id='file_type_pie',
            figure=px.pie(df, names='file_type', title='file_type_pie')
        ),
        html.Div(return_count(), id='queue_count'),
        html.Div([
            html.Button('All Files', id='all_files', n_clicks=0),
            html.Button('Text Only', id='text_only', n_clicks=0),
            html.Button('Videos Only', id='videos_only', n_clicks=0)],
            id='histogram_buttons'),
        dcc.Interval(id='updates', interval=10 * 1000, n_intervals=0)
    ])

    @app.callback(
        dash.dependencies.Output('file_size_histogram', 'figure'),
        dash.dependencies.Output('text_or_binary_files', 'figure'),
        dash.dependencies.Output('file_type_pie', 'figure'),
        dash.dependencies.Output('queue_count', 'children'),
        [dash.dependencies.Input('updates', 'n_intervals'),
         dash.dependencies.Input('all_files', 'n_clicks'),
         dash.dependencies.Input('text_only', 'n_clicks'),
         dash.dependencies.Input('videos_only', 'n_clicks')]
    )
    def update_graph(n, btn1, btn2, btn3):
        update_df = fetch_data()
        global global_mode
        if 'all_files' == ctx.triggered_id:
            df_binary = df_count_by_binary_type(None)  # to bypass df_by_binary_type
            global_mode = -1
        elif 'text_only' == ctx.triggered_id:
            df_binary = df_count_by_binary_type(0)
            update_df = df_full_by_binary_count(0)
            global_mode = 0
        elif 'videos_only' == ctx.triggered_id:
            df_binary = df_count_by_binary_type(1)
            update_df = df_full_by_binary_count(1)
            global_mode = 1
        else:
            if global_mode == -1:
                df_binary = df_count_by_binary_type(None)  # to bypass df_by_binary_type
            elif not global_mode:
                df_binary = df_count_by_binary_type(0)
                update_df = df_full_by_binary_count(0)
            elif global_mode == 1:
                df_binary = df_count_by_binary_type(1)
                update_df = df_full_by_binary_count(1)
            else: df_binary = df_count_by_binary_type(None)

        count_queue = return_count()
        change_histogram = px.histogram(df_binary, y='count', x='file_size', title='file_size_histogram')
        change_pie = px.pie(update_df, names='is_text', title='text_or_binary_files')
        change_pie2 = px.pie(update_df, names='file_type', title='file_type_pie')
        return change_histogram, change_pie, change_pie2, f'queue Count: {count_queue}'

    loop = asyncio.get_event_loop()

    def run_my_server():
        app.run_server(debug=True, use_reloader=False)

    loop.run_in_executor(None, run_my_server)


if __name__ == '__main__':
    asyncio.run(run_dashboard())
