---
name: setup-tonight
description: 今夜30分の事前準備。フォルダ・シードデータ・プロンプト・Milvusスクリプト・SQL・ダッシュボードを生成する。
---

# Step 1: フォルダとファイルの作成

@/project-structure.md に記載されたフォルダ構成を作成してください。
.env は以下のテンプレートで空ファイルとして作成:
AGORA_APP_ID=
AGORA_APP_CERTIFICATE=
MINIMAX_API_KEY=
MINIMAX_GROUP_ID=
ZILLIZ_CLOUD_URI=
ZILLIZ_CLOUD_TOKEN=
SUPABASE_URL=
SUPABASE_ANON_KEY=

# Step 2: シードデータ作成

seed/seed_cases.json を作成してください。
建設現場のヒヤリハット事例 5件を JSON 配列で。
各事例のスキーマ:
{
  "id": "case_001",
  "text": "（口語調の日本語）",
  "category_4m": "Man,Method",
  "risk_level": "HIGH",
  "location": "足場",
  "height_m": 7
}
5件の内容:

1. 足場板ズレ（高所、HIGH）
2. クレーン吊り荷の揺れ（重機、CRITICAL）
3. 脚立からの降り際にスリップ（低所、MEDIUM）
4. 釘が飛散して顔面近くを通過（飛来落下、HIGH）
5. 電動工具のコードに足を引っかけた（つまずき、LOW）
現場作業員が口語で話した風の日本語で。

# Step 3: システムプロンプト作成

prompts/system_prompt.md を作成。
建設現場ヒヤリハット報告AIのLLMシステムプロンプト（MiniMax M1用）。
3ステージ構成:

- Stage 1（受付）: AIが先制で「お疲れ様です。ヒヤリハットの報告をどうぞ」
- Stage 2（追加質問1問だけ）: 最も重要な不足情報を1つ質問。前置き「なるほど、確認させてください。」必須。2問目は絶対に出さない。
- Stage 3（分類・保存・締め）: 4M分類、リスクレベル判定、search_similar呼出、save_report呼出、「報告ありがとうございます。安全第一で」で締め。
function calling 定義（tools JSON スキーマ）も含める:
- search_similar: query_text(string, required)
- save_report: text(string), category_4m(string), risk_level(string), follow_up_answer(string, optional)
トーン: 簡潔丁寧、専門用語なし、30〜45秒で完了する発話量。

# Step 4: Milvus セットアップスクリプト

seed/setup_milvus.py を作成。

1. Zilliz Cloud接続（環境変数から URI, Token 取得）
2. "hiyarihatto" コレクション作成: id(VARCHAR primary), text(VARCHAR), category_4m(VARCHAR), risk_level(VARCHAR), embedding(FLOAT_VECTOR dim=1536)
3. seed_cases.json読み込み
4. 各textを embedding 化（MiniMax embedding API。失敗時は文字列ハッシュでダミーベクトル生成するフォールバック）
5. コレクションに insert
ライブラリ: pymilvus, requests, json, os, python-dotenv

# Step 5: Supabase DDL 生成

以下のSQLを prompts/supabase_ddl.sql として出力:
テーブル: reports

- id: uuid, PK, default gen_random_uuid()
- text: text, not null
- category_4m: text, not null
- risk_level: text, not null
- follow_up_answer: text (nullable)
- similar_case_id: text (nullable)
- created_at: timestamptz, default now()
Realtime有効化の ALTER 文含む。RLS は OFF。

# Step 6: ダッシュボード HTML

dashboard/index.html を作成。

- 単一HTMLファイル、外部フレームワーク不要
- Supabase JS v2 を CDN で読み込み
- ページ読み込み時に reports 全件取得して表示
- Supabase Realtime で INSERT を購読、新報告をカード先頭に追加
- 各カードに: 報告テキスト、4M分類バッジ、リスクレベル色分け、類似事例ID、時刻
- CSS色分け:
  .risk-CRITICAL { border-left: 6px solid #9b59b6; background: #f5eef8; }
  .risk-HIGH     { border-left: 6px solid #e74c3c; background: #fdf0ef; }
  .risk-MEDIUM   { border-left: 6px solid #f39c12; background: #fef9ef; }
  .risk-LOW      { border-left: 6px solid #27ae60; background: #edfaf3; }
- ヘッダー:「ゲンバログ — ヒヤリハット ダッシュボード」
- 日本語 UI、PC表示のみでOK
- Supabase URL と anon key は JS冒頭に定数（あとで埋める）
