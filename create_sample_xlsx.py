"""Write a minimal valid XLSX workbook from the cleaned sample CSV (stdlib only)."""
from pathlib import Path
import csv, zipfile, xml.sax.saxutils as x
ROOT=Path(__file__).parent; source=ROOT/'data/hanoi_housing_clean.csv'; target=ROOT/'data/hanoi_housing_sample.xlsx'
with source.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.reader(f))
def col(n):
 s=''
 while n:
  n,r=divmod(n-1,26);s=chr(65+r)+s
 return s
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('[Content_Types].xml','''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>''')
 z.writestr('_rels/.rels','''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>''')
 z.writestr('xl/workbook.xml','''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Housing" sheetId="1" r:id="rId1"/></sheets></workbook>''')
 z.writestr('xl/_rels/workbook.xml.rels','''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>''')
 parts=[]
 for ri,row in enumerate(rows,1):
  cells=[]
  for ci,val in enumerate(row,1):
   addr=f'{col(ci)}{ri}'; escaped=x.escape(val)
   try: float(val); cells.append(f'<c r="{addr}"><v>{escaped}</v></c>')
   except ValueError: cells.append(f'<c r="{addr}" t="inlineStr"><is><t>{escaped}</t></is></c>')
  parts.append(f'<row r="{ri}">'+''.join(cells)+'</row>')
 sheet='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'+''.join(parts)+'</sheetData></worksheet>'
 z.writestr('xl/worksheets/sheet1.xml',sheet)
print(f'Wrote {target} with {len(rows)-1} data rows')
