import __init__
import asyncio
from graph import run_dashboard
from track_folder import track_changes


async def main():
    path = r"C:\Users\shoam\OneDrive\Desktop\random folder"
    await asyncio.gather(track_changes(path), run_dashboard())  # both function run indefently


asyncio.run(main())
if __name__ == '__main__':
    main()
