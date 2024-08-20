import asyncio

import graph
from track_folder import track_changes


async def main():
    path = r"C:\Users\shoam\OneDrive\Desktop\random folder"
    await asyncio.gather(track_changes(path), graph.run_dashboard())


asyncio.run(main())
if __name__ == '__main__':
    main()
