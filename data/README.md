# Dataset catalogue

- `hanoi_housing_raw.csv`: 600 synthetic records with deliberately missing values and inconsistent district/type spellings for cleaning practice.
- `hanoi_housing_clean.csv`: cleaned 600-row analytical dataset.
- `hanoi_housing_sample.xlsx`: same cleaned data in Excel workbook form.
- `housing.db`: created at runtime; persistent application data.

All records are programmatically simulated with fixed random seed `20261111`. Location/type factors, random noise and a modest age adjustment produce sample variation. There is no real listing or transaction source. The dataset is unsuitable for market pricing, investment, lending, legal decisions or claims about actual district rankings.

Prices use total billion VND and unit million VND per square metre. For source code and processing rules see `../generate_data.py` and `../src/housing/cleaning.py`.
