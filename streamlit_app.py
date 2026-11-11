from pathlib import Path
import io, json
import pandas as pd
import plotly.express as px
px.defaults.template='plotly_white'
import streamlit as st
import streamlit.components.v1 as components
from src.housing.cleaning import FIELDS, clean_data
from src.housing.storage import add_record, delete_records, read_all, replace_all, update_record

ROOT=Path(__file__).parent; DATA=ROOT/'data'; DB=DATA/'housing.db'; DATA.mkdir(exist_ok=True)
st.set_page_config(page_title='Hanoi Housing Lab',page_icon='🏠',layout='wide',initial_sidebar_state='expanded')
st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}h1,h2,h3{font-family:'Manrope',sans-serif}.stApp{background:#f5f7fa}.block-container{padding-top:1.5rem;max-width:1500px}.hero{background:linear-gradient(120deg,#0c3340,#146c69);padding:1.6rem 2rem;border-radius:18px;color:white;margin-bottom:1rem}.hero h1{color:white;margin:0}.hero p{color:#d1e7e6;margin:.3rem 0 0}.kpi{background:white;border:1px solid #e6ebf0;border-radius:14px;padding:1rem 1.1rem;box-shadow:0 4px 14px #15374708}.kpi-label{font-size:.82rem;color:#627282}.kpi-value{font-size:1.55rem;font-weight:800;color:#133d4a}.footnote{font-size:.82rem;color:#657789}
</style>''',unsafe_allow_html=True)

def seed():
 if not DB.exists() or read_all(DB).empty:
  p=DATA/'hanoi_housing_clean.csv'
  if p.exists(): replace_all(DB,pd.read_csv(p))
seed()

def fmt(n): return f'{n:,.2f}'
def filtered(df):
 if df.empty: return df
 st.sidebar.header('Bộ lọc dữ liệu')
 q=st.sidebar.text_input('Tìm kiếm quận / loại nhà / mã')
 districts=['Tất cả']+sorted(df.district.dropna().unique().tolist())
 types=['Tất cả']+sorted(df.property_type.dropna().unique().tolist())
 district=st.sidebar.selectbox('Quận',districts); typ=st.sidebar.selectbox('Loại nhà',types)
 low,high=float(df.area_m2.min()),float(df.area_m2.max()); area=st.sidebar.slider('Diện tích (m²)',min_value=low,max_value=high,value=(low,high))
 out=df.copy()
 if q:
  mask=out.astype(str).apply(lambda c:c.str.contains(q,case=False,na=False)).any(axis=1); out=out[mask]
 if district!='Tất cả':out=out[out.district==district]
 if typ!='Tất cả':out=out[out.property_type==typ]
 return out[out.area_m2.between(*area)]

def record_form(rec=None):
 rec=rec or {}; st.subheader('Chỉnh sửa bản ghi' if rec else 'Thêm bản ghi')
 with st.form('record_form',clear_on_submit=True):
  c1,c2,c3=st.columns(3)
  district=c1.selectbox('Quận',['Ba Đình','Hoàn Kiếm','Đống Đa','Hai Bà Trưng','Cầu Giấy','Thanh Xuân','Tây Hồ','Long Biên','Hà Đông','Nam Từ Liêm','Bắc Từ Liêm','Hoàng Mai'],index=0 if not rec else ['Ba Đình','Hoàn Kiếm','Đống Đa','Hai Bà Trưng','Cầu Giấy','Thanh Xuân','Tây Hồ','Long Biên','Hà Đông','Nam Từ Liêm','Bắc Từ Liêm','Hoàng Mai'].index(rec['district']) if rec['district'] in ['Ba Đình','Hoàn Kiếm','Đống Đa','Hai Bà Trưng','Cầu Giấy','Thanh Xuân','Tây Hồ','Long Biên','Hà Đông','Nam Từ Liêm','Bắc Từ Liêm','Hoàng Mai'] else 0)
  typ=c2.selectbox('Loại nhà',['Nhà phố','Nhà trong ngõ','Chung cư','Biệt thự'],index=['Nhà phố','Nhà trong ngõ','Chung cư','Biệt thự'].index(rec['property_type']) if rec.get('property_type') in ['Nhà phố','Nhà trong ngõ','Chung cư','Biệt thự'] else 0)
  area=c3.number_input('Diện tích (m²)',min_value=1.0,max_value=5000.0,value=float(rec.get('area_m2',75.0)),step=1.0)
  c1,c2,c3=st.columns(3); bedrooms=c1.number_input('Phòng ngủ',0,30,int(rec.get('bedrooms',2))); bathrooms=c2.number_input('Phòng tắm',0,30,int(rec.get('bathrooms',2))); age=c3.number_input('Tuổi nhà (năm)',0,200,int(rec.get('house_age_years',5)))
  c1,c2,c3=st.columns(3); parking=c1.selectbox('Chỗ đỗ xe',['Có','Không'],index=0 if rec.get('has_parking')=='Có' else 1); elevator=c2.selectbox('Thang máy',['Có','Không'],index=0 if rec.get('has_elevator')=='Có' else 1); balcony=c3.selectbox('Ban công',['Có','Không'],index=0 if rec.get('has_balcony')=='Có' else 1)
  total=c1.number_input('Giá tổng (tỷ đồng)',min_value=.01,max_value=10000.0,value=float(rec.get('price_billion_vnd',5.0)),step=.1); unit=c2.number_input('Đơn giá (triệu đồng/m²)',min_value=.1,max_value=100000.0,value=float(rec.get('price_million_vnd_m2',65.0)),step=1.0); year=c3.number_input('Năm đăng tin',2000,2100,int(rec.get('listed_year',2026)))
  submit=st.form_submit_button('Lưu bản ghi',type='primary')
  if submit:
   r=dict(district=district,property_type=typ,area_m2=area,bedrooms=bedrooms,bathrooms=bathrooms,house_age_years=age,has_parking=parking,has_elevator=elevator,has_balcony=balcony,price_billion_vnd=total,price_million_vnd_m2=unit,listed_year=year)
   if rec: update_record(DB,int(rec['id']),r); st.success('Đã cập nhật bản ghi.')
   else: add_record(DB,r); st.success('Đã thêm bản ghi.')
   st.rerun()

st.sidebar.title('🏠 Hanoi Housing Lab')
page=st.sidebar.radio('Điều hướng',['Tổng quan phân tích','Quản lý dữ liệu','Làm sạch dữ liệu','Tableau'])
all_df=read_all(DB)
st.markdown('<div class="hero"><h1>Phân tích giá nhà Hà Nội</h1><p>Khám phá dữ liệu, kiểm tra giả thuyết và chuẩn bị dữ liệu Tableau</p></div>',unsafe_allow_html=True)
st.info('Bộ dữ liệu đi kèm là dữ liệu mô phỏng có chủ ý, không phải tin đăng hay giao dịch thực tế. Kết quả chỉ dùng minh họa quy trình phân tích.')
if page=='Tổng quan phân tích':
 df=filtered(all_df)
 c=st.columns(5); vals=[(f'{len(df):,}','Bản ghi đang xem'),(fmt(df.price_billion_vnd.median()) if len(df) else '0','Trung vị giá tổng (tỷ)'),(fmt(df.area_m2.mean()) if len(df) else '0','Diện tích TB (m²)'),(fmt(df.house_age_years.mean()) if len(df) else '0','Tuổi nhà TB (năm)'),(f'{df.area_m2.corr(df.price_billion_vnd):.2f}' if len(df)>1 else '—','Tương quan diện tích–giá')]
 for col,(v,l) in zip(c,vals): col.markdown(f'<div class="kpi"><div class="kpi-label">{l}</div><div class="kpi-value">{v}</div></div>',unsafe_allow_html=True)
 if len(df):
  st.subheader('Giá nhà theo diện tích, vị trí và đặc điểm')
  a,b=st.columns(2)
  a.plotly_chart(px.scatter(df,x='area_m2',y='price_billion_vnd',color='property_type',hover_data=['district','house_age_years','has_parking'],title='Diện tích và giá tổng'),width="stretch")
  b.plotly_chart(px.box(df,x='district',y='price_million_vnd_m2',color='district',title='Đơn giá theo quận'),width="stretch")
  a,b=st.columns(2)
  a.plotly_chart(px.violin(df,x='property_type',y='price_billion_vnd',color='property_type',box=True,title='Giá tổng theo loại hình nhà'),width="stretch")
  b.plotly_chart(px.scatter(df,x='house_age_years',y='price_million_vnd_m2',color='property_type',size='area_m2',hover_data=['district'],title='Tuổi nhà và đơn giá'),width="stretch")
  a,b=st.columns(2)
  a.plotly_chart(px.histogram(df,x='area_m2',nbins=24,title='Phân bố diện tích'),width="stretch")
  amenity=df.melt(id_vars=['price_million_vnd_m2'],value_vars=['has_parking','has_elevator','has_balcony'],var_name='Tiện ích',value_name='Trạng thái')
  amenity['Tiện ích']=amenity['Tiện ích'].map({'has_parking':'Chỗ đỗ xe','has_elevator':'Thang máy','has_balcony':'Ban công'})
  a2=amenity.groupby(['Tiện ích','Trạng thái'],as_index=False).price_million_vnd_m2.median()
  b.plotly_chart(px.bar(a2,x='Tiện ích',y='price_million_vnd_m2',color='Trạng thái',barmode='group',title='Đơn giá trung vị theo tiện ích'),width="stretch")
  corr=df.drop(columns=['id'],errors='ignore').select_dtypes('number').corr(); st.plotly_chart(px.imshow(corr,text_auto='.2f',color_continuous_scale='RdBu',zmin=-1,zmax=1,title='Ma trận tương quan Pearson'),width="stretch")
  st.subheader('Thống kê nhóm')
  tab=df.groupby('district').agg(So_can=('id','count'),Dien_tich_TB=('area_m2','mean'),Gia_tong_trung_vi=('price_billion_vnd','median'),Don_gia_trung_vi=('price_million_vnd_m2','median'),Tuoi_nha_TB=('house_age_years','mean')).round(2).sort_values('Don_gia_trung_vi',ascending=False)
  st.dataframe(tab,width="stretch")
 else: st.warning('Không có bản ghi theo bộ lọc hiện tại.')
elif page=='Quản lý dữ liệu':
 st.subheader('Tìm kiếm, lọc và quản lý hồ sơ')
 q=st.text_input('Tìm theo quận hoặc loại nhà'); district=st.selectbox('Lọc quận',['Tất cả']+sorted(all_df.district.unique())); typ=st.selectbox('Lọc loại nhà',['Tất cả']+sorted(all_df.property_type.unique()))
 view=all_df.copy()
 if q:view=view[view.astype(str).apply(lambda col:col.str.contains(q,case=False,na=False)).any(axis=1)]
 if district!='Tất cả':view=view[view.district==district]
 if typ!='Tất cả':view=view[view.property_type==typ]
 st.caption(f'{len(view)} bản ghi')
 st.dataframe(view,width="stretch",hide_index=True)
 c1,c2=st.columns([1,2])
 with c1:
  st.download_button('Tải CSV',view.to_csv(index=False).encode('utf-8-sig'),'hanoi_housing_export.csv','text/csv')
  bio=io.BytesIO(); view.to_excel(bio,index=False,engine='openpyxl'); st.download_button('Tải Excel',bio.getvalue(),'hanoi_housing_export.xlsx','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
 with c2:
  if st.session_state.get('import_notice'):
   st.success(st.session_state.pop('import_notice'))
  uploaded=st.file_uploader('Nhập CSV hoặc Excel',type=['csv','xlsx'])
  if uploaded and st.button('Làm sạch và thay dữ liệu hiện tại',type='primary'):
   try:
    source=pd.read_excel(uploaded) if uploaded.name.endswith('.xlsx') else pd.read_csv(uploaded); result,rep=clean_data(source); replace_all(DB,result); st.session_state['import_notice']=f"Đã nhập {len(result)} dòng sau làm sạch."; st.rerun()
   except Exception as exc: st.error(f'Không nhập được dữ liệu: {exc}')
 st.markdown('#### Thêm, sửa hoặc xóa')
 action=st.radio('Thao tác',['Thêm','Sửa','Xóa'],horizontal=True)
 if action=='Thêm':record_form()
 elif action=='Sửa' and len(all_df):
  rid=st.selectbox('Chọn ID để sửa',all_df.id.astype(int));record_form(all_df.loc[all_df.id==rid].iloc[0].to_dict())
 elif action=='Xóa' and len(all_df):
  ids=st.multiselect('Chọn ID cần xóa',all_df.id.astype(int).tolist());
  if st.button('Xóa các bản ghi đã chọn',type='primary'):
   n=delete_records(DB,ids);st.success(f'Đã xóa {n} bản ghi.');st.rerun()
elif page=='Làm sạch dữ liệu':
 st.subheader('Quy trình chuẩn hóa')
 up=st.file_uploader('Tải CSV hoặc Excel nguồn',type=['csv','xlsx'],key='cleaner')
 if up:
  source=pd.read_excel(up) if up.name.endswith('.xlsx') else pd.read_csv(up); cleaned,rep=clean_data(source)
  st.write('Bản xem trước nguồn');st.dataframe(source.head(12),width="stretch")
  st.write('Bản xem trước đã chuẩn hóa');st.dataframe(cleaned.head(12),width="stretch")
  st.json(rep);st.download_button('Tải CSV đã làm sạch',cleaned.to_csv(index=False).encode('utf-8-sig'),'hanoi_housing_clean.csv','text/csv')
else:
 st.subheader('Tableau Dashboard')
 st.markdown('Tải bảng dữ liệu hiện tại để kết nối Tableau Desktop. Sau khi tạo dashboard, dán URL nhúng có quyền truy cập vào ô bên dưới.')
 c1,c2=st.columns([1,2]); bio=io.BytesIO();all_df.to_excel(bio,index=False,engine='openpyxl')
 c1.download_button('Tải CSV cho Tableau',all_df.to_csv(index=False).encode('utf-8-sig'),'tableau_hanoi_housing.csv','text/csv')
 c1.download_button('Tải Excel cho Tableau',bio.getvalue(),'tableau_hanoi_housing.xlsx','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
 url=st.text_input('Tableau embed URL',placeholder='https://public.tableau.com/views/...')
 if url:
  if url.startswith('https://'): components.iframe(url,height=700,scrolling=True)
  else: st.error('URL nhúng cần bắt đầu bằng https://')
 else: st.info('Khu vực dashboard sẽ hiển thị khi cung cấp URL nhúng Tableau hợp lệ.')
st.markdown('<p class="footnote">Ứng dụng phục vụ học tập; dữ liệu mẫu mô phỏng và các thống kê không đại diện giá thị trường thực.</p>',unsafe_allow_html=True)
