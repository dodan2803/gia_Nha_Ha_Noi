"""Generate transparent synthetic Hanoi property listing examples (not transaction data)."""
from pathlib import Path
import random
import pandas as pd
from src.housing.cleaning import clean_data
ROOT=Path(__file__).parent; OUT=ROOT/'data'; OUT.mkdir(exist_ok=True)
rng=random.Random(20261111)
districts=['Ba Đình','Hoàn Kiếm','Đống Đa','Hai Bà Trưng','Cầu Giấy','Thanh Xuân','Tây Hồ','Long Biên','Hà Đông','Nam Từ Liêm','Bắc Từ Liêm','Hoàng Mai']
# Illustrative location multipliers only; not empirical market estimates.
levels={'Ba Đình':1.22,'Hoàn Kiếm':1.34,'Đống Đa':1.03,'Hai Bà Trưng':1.05,'Cầu Giấy':1.08,'Thanh Xuân':.98,'Tây Hồ':1.18,'Long Biên':.78,'Hà Đông':.70,'Nam Từ Liêm':.94,'Bắc Từ Liêm':.76,'Hoàng Mai':.79}
types=['Nhà phố','Nhà trong ngõ','Chung cư','Biệt thự']; multipliers={'Nhà phố':1.13,'Nhà trong ngõ':.88,'Chung cư':.83,'Biệt thự':1.48}
records=[]
for i in range(1,601):
 d=rng.choice(districts); t=rng.choices(types,[32,31,27,10])[0]; area=round(rng.uniform(38,210) if t!='Chung cư' else rng.uniform(42,150),1); age=rng.randint(0,48)
 rate=65*levels[d]*multipliers[t]*rng.uniform(.82,1.2)*(1-max(0,age-20)*.002)
 unit=round(rate,1); total=round(unit*area/1000,2); bedrooms=max(1,round(area/32)+rng.choice([-1,0,0,1]))
 records.append({'listing_code':f'HN{i:04d}','district':d,'property_type':t,'area_m2':area,'bedrooms':bedrooms,'bathrooms':max(1,bedrooms-1),'house_age_years':age,'has_parking':rng.choices(['Có','Không'],[.62,.38])[0],'has_elevator':rng.choices(['Có','Không'],[.65,.35])[0] if t in ['Chung cư','Biệt thự'] else 'Không','has_balcony':rng.choices(['Có','Không'],[.68,.32])[0],'price_billion_vnd':total,'price_million_vnd_m2':unit,'listed_year':rng.choices([2024,2025,2026],[.2,.48,.32])[0]})
raw=pd.DataFrame(records); raw['district']=raw['district'].replace({'Cầu Giấy':' Cau Giay '}); raw['property_type']=raw['property_type'].replace({'Chung cư':'Chung cu'})
for col,step in [('area_m2',47),('house_age_years',61),('has_parking',89),('price_million_vnd_m2',103)]: raw.loc[raw.index%step==0,col]=None
raw.to_csv(OUT/'hanoi_housing_raw.csv',index=False,encoding='utf-8-sig')
clean,report=clean_data(raw.drop(columns=['listing_code']))
clean.insert(0,'id',range(1,len(clean)+1)); clean.to_csv(OUT/'hanoi_housing_clean.csv',index=False,encoding='utf-8-sig')
try: clean.to_excel(OUT/'hanoi_housing_sample.xlsx',index=False)
except ImportError:
 import subprocess,sys
 subprocess.run([sys.executable,str(ROOT/'create_sample_xlsx.py')],check=True)
print(f"Raw rows={len(raw)}; clean rows={len(clean)}; report={report}")
