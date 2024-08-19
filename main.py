from __init__ import localdb
from track_folder import track_changes
import graph

def main():

    path = r"C:\Users\shoam\OneDrive\Desktop\random folder"
    track_changes(path)
    print(localdb.cursor().fetchall())
    graph.run_dashboard()


if __name__ == '__main__':
    main()