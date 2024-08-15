import os
import time


def check_directory(path):
    return(os.listdir(path))


def track_chchchanges(path):
    prev_version = set(check_directory(path))
    print("initial files:", prev_version)
    while True:
        time.sleep(10)
        current_version = set(check_directory(path))
        if current_version != prev_version:
            added = current_version - prev_version
            removed = prev_version - current_version
            prev_version = current_version
            for file in added:
                print("new file! " + file)
            for file in removed:
                print("removed file! " + file)


def main():
    path = r"C:\Users\shoam\OneDrive\Desktop\random folder"
    track_chchchanges(path)


if __name__ == "__main__":
    main()