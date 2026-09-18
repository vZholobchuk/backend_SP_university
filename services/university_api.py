import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
import urllib.parse

logger = logging.getLogger(__name__)

PNU_SCHEDULE_URL = "https://asu-srv.pnu.edu.ua/cgi-bin/timetable.cgi?n=700"

async def fetch_pnu_schedule(group_name: str):
    """
    Спроба отримати розклад з ПНУ. Використовує логіку скрейпінгу.
    """
    try:
        async with httpx.AsyncClient() as client:
            # Виправляємо часту помилку: заміна латинських літер на кириличні
            # (користувачі часто вводять англійську 'I' замість української 'І' на мобільних)
            group_name = group_name.upper()
            translit = {"I": "І", "A": "А", "O": "О", "E": "Е", "C": "С", "P": "Р", "B": "В", "M": "М", "T": "Т", "X": "Х"}
            for lat, cyr in translit.items():
                group_name = group_name.replace(lat, cyr)

            current_date = datetime.now()
            # Починаємо з понеділка поточного тижня
            start_of_week = current_date - timedelta(days=current_date.weekday())
            sdate_str = start_of_week.strftime("%d.%m.%Y")
            
            # 1 семестр до кінця січня, 2 семестр до кінця липня
            if current_date.month >= 8:
                end_of_semester = datetime(current_date.year + 1, 1, 31)
            elif current_date.month == 1:
                end_of_semester = datetime(current_date.year, 1, 31)
            else:
                end_of_semester = datetime(current_date.year, 7, 31)
                
            edate_str = end_of_semester.strftime("%d.%m.%Y")
            
            data = urllib.parse.urlencode({
                "faculty": "0",
                "teacher": "".encode("windows-1251"),
                "group": group_name.encode("windows-1251"),
                "sdate": sdate_str.encode("windows-1251"),
                "edate": edate_str.encode("windows-1251"),
                "n": 700
            }).encode('ascii')
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            response = await client.post(PNU_SCHEDULE_URL, content=data, headers=headers, timeout=10.0)
            html_content = response.content.decode("windows-1251", errors="ignore")
            
            if "<table" in html_content:
                soup = BeautifulSoup(html_content, "html.parser")
                
                parsed_schedule = []
                current_date_str = ""
                
                for el in soup.find_all(['h4', 'tr']):
                    if el.name == 'h4' and el.find('small'):
                        # Знайшли заголовок нового дня
                        current_date_str = el.contents[0].strip()
                        small = el.find('small')
                        day_name = small.text.strip() if small else ""
                    
                    elif el.name == 'tr' and current_date_str:
                        cells = el.find_all("td")
                        if len(cells) >= 3:
                            # Пропускаємо порожні вікна (пари)
                            info_str = cells[2].get_text(separator=" ", strip=True)
                            if not info_str:
                                continue

                            time_str = cells[1].text.strip()
                            lesson_num = cells[0].text.strip()
                            
                            content_td = cells[2]
                            subgroup_span = content_td.find('span', class_='gr2_name')
                            subject_span = content_td.find('span', class_='p_name')
                            type_span = content_td.find('span', class_='p_type_name')
                            room_span = content_td.find('span', class_='room_name')
                            teacher_span = content_td.find('span', class_='t_name')
                            
                            # Пошук посилання на онлайн пару
                            a_tag = content_td.find('a')
                            link = a_tag.get('href') if a_tag else None

                            subject = subject_span.text.strip() if subject_span else ""
                            lesson_type = type_span.text.strip() if type_span else ""
                            room = room_span.text.strip() if room_span else ""
                            teacher = teacher_span.text.strip() if teacher_span else ""
                            subgroup = subgroup_span.text.strip() if subgroup_span else ""
                            
                            # Якщо сайт ПНУ не віддає час, беремо стандартний час пар за їх номером
                            if not time_str and lesson_num.isdigit():
                                times = {
                                    1: ("09:00", "10:20"),
                                    2: ("10:35", "11:55"),
                                    3: ("12:20", "13:40"),
                                    4: ("13:50", "15:10"),
                                    5: ("15:20", "16:40"),
                                    6: ("16:50", "18:10"),
                                    7: ("18:15", "19:35"),
                                    8: ("19:40", "21:00")
                                }
                                t_s, t_e = times.get(int(lesson_num), ("09:00", "10:20"))
                            elif time_str and "-" in time_str:
                                t_s, t_e = [t.strip() for t in time_str.split("-", 1)]
                            else:
                                t_s, t_e = "09:00", "10:20"

                            # Намагаємося розпарсити дату та час
                            try:
                                h_s, m_s = map(int, t_s.split(":"))
                                h_e, m_e = map(int, t_e.split(":"))
                                
                                # Парсимо дату з date_str (напр. "17.09.2024")
                                d, m, y = map(int, current_date_str.strip().split(" ")[0].split("."))
                                start_dt = datetime(y, m, d, h_s, m_s)
                                end_dt = datetime(y, m, d, h_e, m_e)
                            except Exception:
                                start_dt = current_date
                                end_dt = current_date + timedelta(hours=1)
                                
                            parsed_schedule.append({
                                "subject": subject,
                                "type": lesson_type,
                                "start_time": start_dt,
                                "end_time": end_dt,
                                "room": room, 
                                "teacher": teacher,
                                "subgroup": subgroup,
                                "lesson_number": lesson_num,
                                "link": link
                            })
                
                if len(parsed_schedule) > 0:
                    return parsed_schedule
            
            # Якщо таблиць не знайдено
            return []

    except Exception as e:
        logger.error(f"Помилка отримання розкладу ПНУ: {e}")
        return []
