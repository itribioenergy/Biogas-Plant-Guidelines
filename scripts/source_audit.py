"""Read a publicly published source for provenance; do not republish the PDF."""
from pathlib import Path
import urllib.request, hashlib, json
import fitz
Path("qa").mkdir(exist_ok=True)
url="https://www.biogas.com.tw/ReadFile/?n=83f4917b-25df-4710-a230-4ffb26bb624c.pdf&p=Tech"
try:
    raw=urllib.request.urlopen(url,timeout=90).read()
    doc=fitz.open(stream=raw,filetype="pdf")
    metadata={"url":url,"sha256":hashlib.sha256(raw).hexdigest(),"pages":len(doc),"attachment_match":"not verified"}
    Path("qa/source-metadata.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding="utf8")
    print("SOURCE_METADATA",json.dumps(metadata,ensure_ascii=False))
    # Print selected passages for source review; source file remains unpublished.
    keywords=["目錄","故障","冷卻","機油","脫硫","酸鹼","溫度","排水"]
    selected=[]
    for i,p in enumerate(doc):
        t=p.get_text()
        if any(k in t for k in keywords):
            selected.append((i+1,t))
    for number,t in selected[:28]:
        print("\nPDF PAGE",number,"\n",t[:2600])
except Exception as e:
    Path("qa/source-metadata.json").write_text(json.dumps({"status":"unavailable","error":str(e)},ensure_ascii=False),encoding="utf8")
    print("SOURCE_UNAVAILABLE",str(e))
