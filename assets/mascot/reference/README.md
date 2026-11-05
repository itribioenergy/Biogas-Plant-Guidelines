# 吉祥物官方參考圖檔清單｜待上傳

使用者於 2026-11-05 重新提供兩張原始 PNG。已檢查原始檔案並整理為可直接解壓後提交的 ZIP，兩張均為 1448×1086。

| 目標位置 | SHA-256 |
|---|---|
| `assets/mascot/reference/mascot-character-sheet-v0.1.png` | `b546e162beb2bdffdc25b128cc900cf60e572cc41c5adf081b42dc4cb7570a63` |
| `assets/mascot/reference/mascot-pose-sheet-v0.1.png` | `9c694a3d5678751225be82cd69e5446a1b99a758682106333c79ae5b87cce06f` |

**目前狀態：待將二進位檔案真正提交 GitHub。** 現有 GitHub connector 提供 Base64 blob/文字 contents API，但此流程無法直接將本地上傳 PNG bytes 傳入連接器；不得將本檔視為圖片已上傳成功。

工作模式接續：附件 `biogas-mascot-official-reference.zip` 解壓縮後上傳兩張 PNG；上傳後再讀取 GitHub raw blob 驗證雜湊及顯示。
