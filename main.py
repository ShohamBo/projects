import asyncio
from src.graph import run_dashboard
from src.track_folder import track_changes


async def main():
    path = 'local_data'
    await asyncio.gather(track_changes(path), run_dashboard())  # both function run indefinitely


asyncio.run(main())
if __name__ == '__main__':
    main()
