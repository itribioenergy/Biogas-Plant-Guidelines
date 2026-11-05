"""Reproducible handbook export. Source of truth: content/handbook.json."""
from pathlib import Path
import base64, json, hashlib, threading, functools, http.server, subprocess, shutil, zipfile
import fitz, cairosvg
from docx import Document
from docx.shared import Mm, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
import os
os.chdir(ROOT)
OUT=ROOT/"output"; QA=ROOT/"qa"; DOWNLOAD=ROOT/"web/downloads"
for p in [OUT,QA,DOWNLOAD,QA/"raster",QA/"docx-render"]: p.mkdir(parents=True,exist_ok=True)
data=json.loads(Path("content/handbook.json").read_text(encoding="utf8"))
assert [p["id"] for p in data["pages"]]==[f"P{i:02}" for i in range(1,21)]
for p in data["pages"]:
    assert len(p["blocks"])==4 and p["warning"] and p["source"]
    if p["diagram"]: assert Path("assets/diagrams",p["diagram"]+".svg").is_file()
stem="Biogas-Plant-Health-Check-v1"
report={"version":data["version"],"date":data["date"],"content_sha256":hashlib.sha256(Path("content/handbook.json").read_bytes()).hexdigest(),"technical_review":"pending","mascot":"missing original attachment; not accepted","source_attachment_match":"not verified"}
expected={"mascot-character-sheet-v0.1.png":"b546e162beb2bdffdc25b128cc900cf60e572cc41c5adf081b42dc4cb7570a63","mascot-pose-sheet-v0.1.png":"9c694a3d5678751225be82cd69e5446a1b99a758682106333c79ae5b87cce06f"}
hashes={}
for name,h in expected.items():
    p=Path("assets/mascot/reference")/name
    if p.exists():
        hashes[name]=hashlib.sha256(p.read_bytes()).hexdigest()
        assert hashes[name]==h, "Immutable mascot mismatch"
report["mascot_original_hashes"]=hashes
if len(hashes)==2: report["mascot"]="originals verified; pose extraction and visual integration pending"

# Same data, style and renderer are bundled into a portable offline preview.
index=Path("web/index.html").read_text(encoding="utf8")
css=Path("web/style.css").read_text(encoding="utf8")
js=Path("web/app.js").read_text(encoding="utf8")
diagrams={}
for p in Path("assets/diagrams").glob("*.svg"):
    diagrams[p.stem]="data:image/svg+xml;base64,"+base64.b64encode(p.read_bytes()).decode()
payload="window.HANDBOOK="+json.dumps(data,ensure_ascii=False).replace("</","<\\/")+";window.DIAGRAMS="+json.dumps(diagrams)+";"
offline=index.replace('<link rel="stylesheet" href="style.css">',"<style>"+css+"</style>").replace('<script src="app.js"></script>',"<script>"+payload+"</script><script>"+js+"</script>")
# Offline download links point to the documents shipped beside the HTML.
offline=offline.replace('href="downloads/','href="')
# Documentation links are absolute, avoiding broken paths in a portable download.
offline=offline.replace('href="../docs/','href="https://github.com/itribioenergy/Biogas-Plant-Guidelines/blob/main/docs/').replace('href="../README.md"','href="https://github.com/itribioenergy/Biogas-Plant-Guidelines/blob/main/README.md"')
(OUT/"standalone.html").write_text(offline,encoding="utf8")

# Editable DOCX: native headings, body paragraphs and tables; only diagrams are images.
doc=Document()
sec=doc.sections[0];sec.page_width=Mm(210);sec.page_height=Mm(297)
sec.top_margin=sec.bottom_margin=Mm(18);sec.left_margin=sec.right_margin=Mm(17)
sec.header_distance=sec.footer_distance=Mm(8)
style=doc.styles["Normal"]
style.font.name="Noto Sans CJK TC";style.font.size=Pt(11)
style.element.rPr.rFonts.set(qn("w:eastAsia"),"Noto Sans CJK TC")
style.paragraph_format.line_spacing=1.45
style.paragraph_format.space_after=Pt(4)
for name,size in [("Title",32),("Heading 1",21),("Heading 2",13.5)]:
    s=doc.styles[name];s.font.name="Noto Sans CJK TC";s.font.size=Pt(size);s.font.color.rgb=RGBColor.from_string("2F6B45")
    s.element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"),"Noto Sans CJK TC")
    s.paragraph_format.space_before=Pt(7);s.paragraph_format.space_after=Pt(5)
    s.paragraph_format.line_spacing=1.2
footer=sec.footer.paragraphs[0];footer.text="沼氣場健康檢查手冊 · 會議討論版 · 尚待技術與工安審查"
for r in footer.runs:r.font.size=Pt(9.5)
def para(text,size=None,bold=False,container=doc,color=None):
    p=container.add_paragraph()
    r=p.add_run(text);r.bold=bold
    if size:r.font.size=Pt(size)
    if color:r.font.color.rgb=RGBColor.from_string(color)
    return p
def diagram(ident):
    if not ident:return
    path=QA/"raster"/(ident+".png")
    cairosvg.svg2png(url=str(Path("assets/diagrams")/(ident+".svg")),write_to=str(path),output_width=1360)
    p=doc.add_paragraph();p.paragraph_format.space_after=Pt(2)
    p.add_run().add_picture(str(path),width=Mm(174))
    para("圖示｜功能與判讀示意，非施工圖；現場配置依設備設計。",9.5)
def shade(cell,color):
    pr=cell._tc.get_or_add_tcPr();el=OxmlElement("w:shd");el.set(qn("w:fill"),color);pr.append(el)
def no_split(row):
    el=OxmlElement("w:cantSplit");row._tr.get_or_add_trPr().append(el)
para("BIOGAS PLANT · FIELD GUIDE",11,True,color="2F6B45")
doc.add_heading("沼氣場\n健康檢查手冊",0)
para(data["subtitle"],17)
diagram("plant")
para("給農民、牧場負責人與非環工背景業主的巡檢助手。",12)
para("從看得見的現象開始，找到下一個安全步驟。",12)
for line in ["P01–P03　導讀與快篩","P04–P08　生物系統","P09–P12　沼氣處理與安全","P13–P20　發電與實用工具"]:
    para(line,12,True)
para(data["status"],13,True,color="2F6B45")
para("第一版 · "+data["date"]+" · 封面＋20 頁",11)
para("技術數值、設備配置與安全程序尚待專業審查。",11)
para(data["mascotStatus"],10)
for page in data["pages"]:
    doc.add_page_break()
    para(page["chapter"]+" · "+page["id"],11,True,color="2F6B45")
    doc.add_heading(page["title"],1)
    para(page["key"],12,True)
    diagram(page["diagram"])
    if page.get("form"):para(page["form"])
    if page.get("table"):
        tdata=page["table"];t=doc.add_table(rows=1,cols=3);t.autofit=False;t.style="Table Grid"
        for i,title in enumerate(tdata["headers"]):
            c=t.rows[0].cells[i];c.text=title;shade(c,"DDEEDF")
        for row in tdata["rows"]:
            cells=t.add_row().cells
            for c,v in zip(cells,row):c.text=v or "＿＿＿＿"
        for row in t.rows:
            no_split(row)
            for c in row.cells:
                for p in c.paragraphs:
                    p.paragraph_format.space_after=Pt(3);p.paragraph_format.space_before=Pt(3);p.paragraph_format.line_spacing=1.2
                    for r in p.runs:r.font.size=Pt(11)
    t=doc.add_table(rows=2,cols=2);t.autofit=False
    t.columns[0].width=t.columns[1].width=Mm(88)
    for i,b in enumerate(page["blocks"]):
        c=t.cell(i//2,i%2);shade(c,["F3F5F6","F3F5F6","E8F4EA","EDF2F9"][i])
        h=c.paragraphs[0];h.style=doc.styles["Heading 2"];h.add_run(f"0{i+1} "+b["title"])
        for item in b["items"]:para("• "+item,container=c)
    for row in t.rows:no_split(row)
    if page.get("formula"):para(page["formula"],11)
    para("！安全界線",11,True,color="C6413B")
    para(page["warning"],11)
    para(page["tip"],10,color="2F6B45")
    para(page["source"],9.5)
    para("相關頁："+page["related"],9.5)
doc.save(OUT/(stem+".docx"))
reopen=Document(OUT/(stem+".docx"))
assert len(reopen.inline_shapes)==18
for page in data["pages"]:assert any(p.text==page["title"] for p in reopen.paragraphs)
report["docx_native_editable"]=True

# Browser checks and print PDF.
class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(("127.0.0.1",0),functools.partial(QuietHandler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
base=f"http://127.0.0.1:{server.server_port}"
with sync_playwright() as pw:
    browser=pw.chromium.launch()
    page=browser.new_page(viewport={"width":1200,"height":1000},device_scale_factor=1)
    errors=[];page.on("pageerror",lambda e:errors.append(str(e)))
    page.goto(base+"/web/",wait_until="networkidle");page.wait_for_function("window.handbookReady===true")
    page.evaluate("document.fonts.ready")
    assert page.locator(".page").count()==21
    assert page.evaluate("Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)")
    page.locator("#search").fill("發不動")
    assert page.locator(".page:not([hidden])").count()>0
    assert page.locator(".page[hidden]").count()>0
    # Print must include every page even while filtered.
    page.emulate_media(media="print")
    assert page.evaluate("Array.from(document.querySelectorAll('.page')).every(p=>getComputedStyle(p).display==='flex')")
    page.emulate_media(media="screen")
    page.locator("#search").fill("")
    page.locator("#mode").click()
    page.locator("#jump").select_option("P05")
    page.wait_for_function("document.querySelector('#P05').classList.contains('selected')")
    page.locator("#next").click()
    page.wait_for_function("document.querySelector('#P06').classList.contains('selected')")
    page.locator("#mode").click()
    for width in [390,768]:
        page.set_viewport_size({"width":width,"height":900})
        assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"),f"mobile horizontal overflow {width}"
    report["mobile_widths_passed"]=[390,768]
    page.set_viewport_size({"width":1200,"height":1000});page.emulate_media(media="print")
    overflow=page.evaluate("""()=>Array.from(document.querySelectorAll('.page')).map(p=>{
       const r=p.getBoundingClientRect(),s=getComputedStyle(p),bottom=r.bottom-parseFloat(s.paddingBottom);
       const f=p.querySelector('.page-footer')||p.querySelector('.cover-bottom');
       return {id:p.id,scroll:p.scrollHeight,client:p.clientHeight,footerBottom:f.getBoundingClientRect().bottom,allowedBottom:bottom};
    }).filter(x=>x.scroll>x.client+1||x.footerBottom>x.allowedBottom+2)""")
    report["print_overflow"]=overflow
    assert not overflow,json.dumps(overflow)
    page.pdf(path=str(OUT/(stem+".pdf")),format="A4",print_background=True,prefer_css_page_size=True)
    report["browser_errors"]=errors;assert not errors
    # Portable preview loads without network and uses only embedded diagrams/data.
    page.goto(base+"/output/standalone.html",wait_until="networkidle")
    page.wait_for_function("window.handbookReady===true")
    assert page.locator(".page").count()==21
    assert page.evaluate("Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)")
    report["standalone_load"]=True
    browser.close()
server.shutdown()
pdf=fitz.open(OUT/(stem+".pdf"))
report["pdf_pages"]=len(pdf);assert len(pdf)==21
assert all(abs(p.rect.width-595.28)<2 and abs(p.rect.height-841.89)<2 for p in pdf)
def normalized(s):return "".join(s.split())
for i,p in enumerate(data["pages"],1):
    t=normalized(pdf[i].get_text())
    assert normalized(p["title"]) in t,(p["id"],"missing PDF title")
    assert normalized(p["warning"]) in t,(p["id"],"missing PDF warning")
report["pdf_page_titles_and_warnings"]="21 pages, 20 titles and complete warnings verified"
# Contact sheets for human inspection.
from PIL import Image
sheet=Image.new("RGB",(3*260,7*370),"#dfe5e1")
for i,p in enumerate(pdf):
    pix=p.get_pixmap(matrix=fitz.Matrix(.42,.42),alpha=False)
    im=Image.frombytes("RGB",[pix.width,pix.height],pix.samples)
    sheet.paste(im,((i%3)*260,(i//3)*370))
sheet.save(QA/"contact.png")
for i in [0,5,10,19]:
    pdf[i].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False).save(QA/f"page-{i:02}.png")
pdf.close()
# LibreOffice must open and paginate the editable file; this does not claim Microsoft Word QA.
result=subprocess.run(["libreoffice","-env:UserInstallation=file:///tmp/handbook-lo-profile","--headless","--convert-to","pdf","--outdir",str(QA/"docx-render"),str(OUT/(stem+".docx"))],capture_output=True,text=True,timeout=120)
assert result.returncode==0,result.stderr
word_pdf=fitz.open(QA/"docx-render"/(stem+".pdf"))
report["docx_render_pages"]=len(word_pdf)
assert len(word_pdf)==21,("DOCX page overflow",len(word_pdf))
for i,p in enumerate(data["pages"],1):
    t=normalized(word_pdf[i].get_text())
    assert normalized(p["title"]) in t,(p["id"],"missing DOCX page title")
    assert normalized(p["warning"]) in t,(p["id"],"missing DOCX warning")
word_pdf.close()
report["docx_open_test"]="python-docx reopen and LibreOffice 21-page render passed; Microsoft Word not directly tested"
for ext in ["pdf","docx"]:
    shutil.copy2(OUT/(stem+"."+ext),DOWNLOAD/(stem+"."+ext))
report["files"]={p.name:{"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in OUT.iterdir() if p.is_file()}
report["overall"]="documents built; mascot, attachment comparison and professional review remain incomplete"
(QA/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf8")
with zipfile.ZipFile(OUT/"handbook-v1-bundle.zip","w",zipfile.ZIP_DEFLATED) as z:
    for name in [stem+".pdf",stem+".docx","standalone.html"]:z.write(OUT/name,name)
    for name in ["README.md","docs/source-map.md","docs/review-checklist.md"]:
        if Path(name).exists():z.write(name,name)
print(json.dumps(report,ensure_ascii=False,indent=2))

# Static deployment package contains only the public preview and supporting files.
site=QA/"site"
site.mkdir(exist_ok=True)
for name in ["web","content","assets","docs"]:
    shutil.copytree(ROOT/name,site/name,dirs_exist_ok=True)
for name in ["index.html","README.md"]:
    shutil.copy2(ROOT/name,site/name)
