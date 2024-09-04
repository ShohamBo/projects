import asyncio

import dash
import plotly.express as px
from dash import ctx
from dash import dcc, html
from sql_queries_frontend import df_count_by_binary_type, df_full_by_binary_count, fetch_data, get_count_files_waiting

global_mode = -2
global is_text_translator


async def run_dashboard():
    app = dash.Dash(__name__)
    global is_text_translator
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
        html.Div(get_count_files_waiting(), id='queue_count'),
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
        count_queue = get_count_files_waiting()
        print(count_queue)
        change_histogram = px.histogram(df_binary, y='count', x='file_size', title='file_size_histogram')
        change_pie = px.pie(update_df, names='is_text', title='text_or_binary_files')
        change_pie2 = px.pie(update_df, names='file_type', title='file_type_pie')
        return change_histogram, change_pie, change_pie2, f'queue Count: {count_queue}'

    loop = asyncio.get_event_loop()

    def run_my_server():
        app.run_server(port=8000, debug=True, use_reloader=False, host='0.0.0.0')

    loop.run_in_executor(None, run_my_server)


if __name__ == "__main__":
    asyncio.run(run_dashboard())
