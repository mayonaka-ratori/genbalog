---
name: build-dashboard
description: 当日 Phase 3 前半。ダッシュボード接続テスト。目標30分。
---

# Step 1: Supabase 定数埋め込み

dashboard/index.html の Supabase URL と anon key を .env の値で埋めてください。

# Step 2: 動作テスト

ブラウザで index.html を開き、Supabase の reports に手動で INSERT:
INSERT INTO reports (text, category_4m, risk_level) VALUES ('テスト報告', 'Man', 'HIGH');
ダッシュボードに赤いカードがリアルタイムで出現することを確認。

# Step 3: 問題修正

Realtime が動かない場合:

- Supabase ダッシュボードで reports テーブルの Realtime が ON か確認
- RLS が OFF か確認
- それでもダメなら 5秒ポーリングに切り替え（setInterval で GET）
