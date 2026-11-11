"""Data validation, cleaning and normalization functions."""
from __future__ import annotations
import pandas as pd

FIELDS = ["district", "property_type", "area_m2", "bedrooms", "bathrooms", "house_age_years", "has_parking", "has_elevator", "has_balcony", "price_billion_vnd", "price_million_vnd_m2", "listed_year"]
NUMERIC = ["area_m2", "bedrooms", "bathrooms", "house_age_years", "price_billion_vnd", "price_million_vnd_m2", "listed_year"]
DISTRICT_MAP = {"cau giay":"Cầu Giấy", "cầu giấy":"Cầu Giấy", "ba dinh":"Ba Đình", "ba đình":"Ba Đình", "hoan kiem":"Hoàn Kiếm", "hoàn kiếm":"Hoàn Kiếm", "dong da":"Đống Đa", "đống đa":"Đống Đa", "tay ho":"Tây Hồ", "tây hồ":"Tây Hồ", "ha dong":"Hà Đông", "hà đông":"Hà Đông", "long bien":"Long Biên", "long biên":"Long Biên", "thanh xuan":"Thanh Xuân", "thanh xuân":"Thanh Xuân", "nam tu liem":"Nam Từ Liêm", "nam từ liêm":"Nam Từ Liêm", "bac tu liem":"Bắc Từ Liêm", "bắc từ liêm":"Bắc Từ Liêm", "hoang mai":"Hoàng Mai", "hoàng mai":"Hoàng Mai", "hai ba trung":"Hai Bà Trưng", "hai bà trưng":"Hai Bà Trưng"}
TYPE_MAP = {"chung cu":"Chung cư", "chung cư":"Chung cư", "nha pho":"Nhà phố", "nhà phố":"Nhà phố", "nha trong ngo":"Nhà trong ngõ", "nhà trong ngõ":"Nhà trong ngõ", "biet thu":"Biệt thự", "biệt thự":"Biệt thự"}
ALIASES = {"area":"area_m2", "area_sqm":"area_m2", "district_name":"district", "type":"property_type", "house_type":"property_type", "price":"price_billion_vnd", "price_billion":"price_billion_vnd", "age":"house_age_years"}

def clean_data(source: pd.DataFrame, *, current_year: int = 2026) -> tuple[pd.DataFrame, dict]:
    """Normalize columns/categories, coerce types, impute, remove duplicates/invalid records."""
    df=source.copy(); report={"input_rows":len(df), "renamed_columns":0, "imputed_cells":0, "duplicates_removed":0, "invalid_rows_removed":0}
    cols=[]
    for c in df.columns:
        n=str(c).strip().lower().replace(" ","_")
        n=ALIASES.get(n,n); cols.append(n)
    report["renamed_columns"]=sum(str(a)!=str(b) for a,b in zip(df.columns,cols)); df.columns=cols
    # Common Vietnamese labels from spreadsheets.
    vi={"quận":"district","loại_nhà":"property_type","diện_tích_m2":"area_m2","diện_tích":"area_m2","giá_tỷ":"price_billion_vnd","giá_tổng_tỷ":"price_billion_vnd","tuổi_nhà":"house_age_years","phòng_ngủ":"bedrooms","phòng_tắm":"bathrooms","đỗ_xe":"has_parking","thang_máy":"has_elevator","ban_công":"has_balcony","năm_đăng":"listed_year"}
    df=df.rename(columns={k:v for k,v in vi.items() if k in df.columns})
    for c in FIELDS:
        if c not in df: df[c]=pd.NA
    for c in ["district","property_type","has_parking","has_elevator","has_balcony"]:
        df[c]=df[c].astype("string").str.strip().replace("",pd.NA)
    df["district"]=df["district"].map(lambda x:DISTRICT_MAP.get(str(x).casefold(),str(x)) if pd.notna(x) else x)
    df["property_type"]=df["property_type"].map(lambda x:TYPE_MAP.get(str(x).casefold(),str(x)) if pd.notna(x) else x)
    for c in NUMERIC:
        # Handles formatted numeric text such as "65,5" and removes units/currency symbols.
        s=df[c].astype("string").str.replace(",",".",regex=False).str.replace(r"[^0-9.\-]","",regex=True)
        df[c]=pd.to_numeric(s,errors="coerce")
    # If total price exists but unit price is absent, derive it; likewise derive total from unit price.
    can_derive=df["price_million_vnd_m2"].isna() & df["price_billion_vnd"].notna() & df["area_m2"].gt(0)
    df.loc[can_derive,"price_million_vnd_m2"]=df.loc[can_derive,"price_billion_vnd"]*1000/df.loc[can_derive,"area_m2"]
    can_derive=df["price_billion_vnd"].isna() & df["price_million_vnd_m2"].notna() & df["area_m2"].gt(0)
    df.loc[can_derive,"price_billion_vnd"]=df.loc[can_derive,"price_million_vnd_m2"]*df.loc[can_derive,"area_m2"]/1000
    for c in ["area_m2","price_billion_vnd","price_million_vnd_m2"]:
        med=df[c].median(); before=df[c].isna().sum()
        if pd.notna(med): df[c]=df[c].fillna(med)
        report["imputed_cells"]+=int(before-df[c].isna().sum())
    for c in ["house_age_years","bedrooms","bathrooms"]:
        fill=0 if c in ["bedrooms","bathrooms"] else df[c].median()
        fill=0 if pd.isna(fill) else fill
        before=df[c].isna().sum(); df[c]=df[c].fillna(fill); report["imputed_cells"]+=int(before-df[c].isna().sum())
    defaults={"district":"Không rõ","property_type":"Khác","has_parking":"Không","has_elevator":"Không","has_balcony":"Không"}
    for c,val in defaults.items():
        before=df[c].isna().sum(); df[c]=df[c].fillna(val); report["imputed_cells"]+=int(before-df[c].isna().sum())
    before=df["listed_year"].isna().sum(); df["listed_year"]=df["listed_year"].fillna(current_year).astype(int); report["imputed_cells"]+=int(before)
    for c in ["bedrooms","bathrooms","house_age_years"]: df[c]=df[c].clip(lower=0).round().astype(int)
    df["area_m2"]=df["area_m2"].round(1); df["price_billion_vnd"]=df["price_billion_vnd"].round(2); df["price_million_vnd_m2"]=df["price_million_vnd_m2"].round(1)
    dup=df.duplicated(subset=["district","property_type","area_m2","price_billion_vnd"],keep="first"); report["duplicates_removed"]=int(dup.sum()); df=df.loc[~dup].copy()
    bad=df["area_m2"].le(0)|df["price_billion_vnd"].le(0)|df["price_million_vnd_m2"].le(0)
    report["invalid_rows_removed"]=int(bad.sum()); df=df.loc[~bad,FIELDS].reset_index(drop=True)
    report["output_rows"]=len(df); report["rows_removed"]=report["input_rows"]-report["output_rows"]
    return df,report
