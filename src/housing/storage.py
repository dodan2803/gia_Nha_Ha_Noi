"""SQLite persistence helpers for housing records."""
from pathlib import Path
import sqlite3
import pandas as pd
from .cleaning import FIELDS

SCHEMA='''CREATE TABLE IF NOT EXISTS homes(
 id INTEGER PRIMARY KEY AUTOINCREMENT, district TEXT NOT NULL, property_type TEXT NOT NULL,
 area_m2 REAL NOT NULL, bedrooms INTEGER, bathrooms INTEGER, house_age_years INTEGER,
 has_parking TEXT, has_elevator TEXT, has_balcony TEXT,
 price_billion_vnd REAL NOT NULL, price_million_vnd_m2 REAL NOT NULL, listed_year INTEGER)'''

def get_conn(db_path:Path):
    conn=sqlite3.connect(db_path); conn.row_factory=sqlite3.Row; conn.execute(SCHEMA); return conn

def read_all(db_path:Path)->pd.DataFrame:
    with get_conn(db_path) as c: return pd.read_sql_query('SELECT * FROM homes ORDER BY id DESC',c)

def replace_all(db_path:Path,df:pd.DataFrame)->int:
    with get_conn(db_path) as c:
        c.execute('DELETE FROM homes')
        df[FIELDS].to_sql('homes',c,if_exists='append',index=False)
    return len(df)

def add_record(db_path:Path,record:dict)->int:
    with get_conn(db_path) as c:
        cur=c.execute('INSERT INTO homes('+','.join(FIELDS)+') VALUES('+','.join('?' for _ in FIELDS)+')',[record.get(k) for k in FIELDS]); return int(cur.lastrowid)

def update_record(db_path:Path,record_id:int,record:dict)->None:
    with get_conn(db_path) as c: c.execute('UPDATE homes SET '+','.join(f'{k}=?' for k in FIELDS)+' WHERE id=?',[*[record.get(k) for k in FIELDS],record_id])

def delete_records(db_path:Path,ids:list[int])->int:
    if not ids:return 0
    with get_conn(db_path) as c:
        cur=c.executemany('DELETE FROM homes WHERE id=?',[(int(i),) for i in ids]); return cur.rowcount
