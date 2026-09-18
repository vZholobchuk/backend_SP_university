import asyncio
import sys
import time
sys.path.insert(0, 'c:/unik/TO-DO/backend')
from services.university_api import fetch_pnu_schedule
from datetime import datetime, timedelta
import urllib.parse
import httpx
from bs4 import BeautifulSoup

async def fetch_120_days():
    start_time = time.time()
    group_name = "ІПЗ -41"
    
    current_date = datetime.now()
    start_of_week = current_date - timedelta(days=current_date.weekday())
    sdate_str = start_of_week.strftime("%d.%m.%Y")
    edate_str = (start_of_week + timedelta(days=120)).strftime("%d.%m.%Y")
    
    data = urllib.parse.urlencode({
        "faculty": "0",
        "teacher": "".encode("windows-1251"),
        "group": group_name.encode("windows-1251"),
        "sdate": sdate_str.encode("windows-1251"),
        "edate": edate_str.encode("windows-1251"),
        "n": 700
    }).encode('ascii')
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post("https://asu-srv.pnu.edu.ua/cgi-bin/timetable.cgi?n=700", content=data, headers=headers, timeout=20.0)
            html = resp.content.decode("windows-1251", errors="ignore")
            soup = BeautifulSoup(html, "html.parser")
            tr_count = len(soup.find_all('tr'))
            print(f"Success! Fetched in {time.time()-start_time:.2f}s. Rows found: {tr_count}")
            return True
        except Exception as e:
            print("Failed:", e)
            return False

if __name__ == '__main__':
    asyncio.run(fetch_120_days())
