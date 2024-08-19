import __init__
from track_folder import track_changes
import graph
import threading


def main():
    path = r"C:\Users\shoam\OneDrive\Desktop\random folder"
    thread = threading.Thread(target=track_changes, args=(path,))
    thread.start()
    graph.run_dashboard()
    thread.join()


if __name__ == '__main__':
    main()
