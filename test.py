import asyncio
import sys
import time
sys.path.insert(0, 'c:/unik/TO-DO/backend')
from services.university_api import fetch_pnu_schedule

async def main():
    start = time.time()
    # Change it in test to see if 120 days works?
    # Wait, fetch_pnu_schedule hardcodes 30 days. 
    # I will redefine it locally.
    pass

if __name__ == '__main__':
    asyncio.run(main())
