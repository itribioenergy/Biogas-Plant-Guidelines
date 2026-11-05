# 沼氣場健康檢查手冊
第一版會議討論稿｜2026-11-06｜封面＋20 頁。不是正式操作程序；工程與工安尚待審查。

## 開啟與下載
建置通過後產物在 [output](output/)：
- [A4 PDF](output/Biogas-Plant-Health-Check-v1.pdf)
- [可編輯 DOCX](output/Biogas-Plant-Health-Check-v1.docx)
- [離線網頁](output/standalone.html) — 下載後以瀏覽器開啟
- [會議用整包 ZIP](output/handbook-v1-bundle.zip) — 內含 PDF、Word、網頁與說明

**GitHub 顯示的是檔案頁，不會直接執行 HTML。** 請以 Raw／Download 下載 HTML，或使用下列本地預覽。GitHub Pages 是否已成功部署，以工作流程回報為準，不將預期網址視為已上線。

## 本地預覽
下載／clone 本儲存庫，在根目錄執行：
```bash
python -m http.server 8000
```
瀏覽 http://localhost:8000/web/ 。也可下載 output 的整包 ZIP、解壓後雙擊 standalone.html，不需安裝套件即可閱讀。

功能：症狀搜尋、頁次選擇、上一頁／下一頁、逐頁／全書、PDF 與 Word 下載。列印一律輸出完整封面＋20 頁，不受搜尋篩選影響。手動列印選 A4、100%、關閉瀏覽器頁首頁尾、開啟背景圖形。

## 內容與版型
- content/handbook.json：唯一文字內容來源，P01–P20、表格、提示、警語、來源。
- web/app.js：統一渲染器；web/style.css：A4 與手機版樣式。
- assets/diagrams/：自製 SVG 示意圖，不是施工圖。
- assets/mascot/reference/：原始角色指定位置；目前原 PNG **尚未上傳**。
- scripts/build.py：同來源輸出網頁、PDF、原生可編輯 DOCX。
- docs/source-map.md：逐頁來源與補充建議。
- docs/review-checklist.md：技術、工安與視覺未完成事項。
- qa/report.json：最新成功建置的實測檢查結果；包含內容雜湊，供核對版本。

## 自動建置與驗證
GitHub Actions「Build handbook」會安裝字體與輸出工具、核對公開原手冊，再執行：
1. 20 個唯一頁碼、必要圖檔與內容結構。
2. 網頁 21 頁載入、圖片載入、搜尋與換頁、390／768 px 手機寬度。
3. A4 列印內容邊界、PDF 21 頁、逐頁標題及完整安全警語。
4. DOCX 重新開啟，以及 LibreOffice 轉出 21 頁並核對標題及警語。
5. 產生離線 HTML、文件與 QA 預覽圖，成功後提交儲存庫。

這些是文件與程式檢查，**不是工程／安全審查，也不是 Microsoft Word 實機測試**。若建置失敗，Actions 保留輸出供排查，不能將該次結果當成通過。

本地完整建置（Linux）：
```bash
sudo apt-get install fonts-noto-cjk libreoffice-writer
pip install -r requirements.txt
python -m playwright install --with-deps chromium
python scripts/source_audit.py
python scripts/build.py
```
網頁不依賴 CDN 或外部字體；輸出端使用 Noto CJK，Office 可改成微軟正黑體後重新確認分頁。

## 吉祥物素材限制
附件雖已提供，但本次本地執行器不可用，無法讀取 ZIP 的位元組。尚未提交原始 PNG，也未宣稱圖像一致性驗收通過。未使用替代機器人或新生成角色冒充。匯入後需按 reference/README.md 雜湊驗證，再從正式姿態圖建立可重用素材。

## 版本更新
修改 content/handbook.json 後重新建置；不要直接手改產出 PDF。DOCX 內文可編輯，但若要使網頁與 PDF 一致，請將修改回填 JSON。檢查 qa/report.json 的 content_sha256，避免使用舊產物。
