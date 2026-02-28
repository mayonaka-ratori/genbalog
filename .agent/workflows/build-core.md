---
name: build-core
description: 当日 Phase 1-2。TEN Agent コア実装。目標105分。
---

# Step 1: property.json 構築

voice-assistant の property.json をコピーして agents/examples/genba-log/property.json を作成。以下を変更:

- STT: Agora STT (lang: ja-JP)
- LLM: MiniMax M1（OpenAI互換エンドポイント <https://api.minimax.chat/v1/text/chatcompletion_v2）>
  - model: MiniMax-M1
  - system prompt: prompts/system_prompt.md の内容を埋め込む
  - tools: system_prompt.md 内の JSON スキーマを tools フィールドに設定
- TTS: MiniMax TTS
  - voice: Japanese_KindLady
  - emotion: neutral
  - speed: 0.80

# Step 2: extension.py 実装（Python Cascade パターン）

agents/examples/genba-log/tenapp/ten_packages/extension/main_python/extension.py を実装。

1. @tool_handler("search_similar") を実装:
   - tools/milvus_client.py の search_similar(query_text) を呼ぶ
   - 結果の text と case_id を返す

2. @tool_handler("save_report") を実装:
   - tools/supabase_client.py の save_report(text, category_4m, risk_level, follow_up_answer, similar_case_id) を呼ぶ
   - 成功/失敗を返す

# Step 3: tools/milvus_client.py

- Zilliz Cloud に pymilvus で接続（.env から取得）
- search_similar(query_text: str) → dict:
  - query_text を embedding 化（MiniMax embedding API。失敗時はハッシュフォールバック）
  - hiyarihatto コレクションで similarity search (top_k=1)
  - {"case_id": "case_001", "text": "...", "score": 0.85} を返す
  - 接続エラー時は {"case_id": "none", "text": "類似事例なし", "score": 0} を返す

# Step 4: tools/supabase_client.py

- supabase-py で接続（.env から取得）
- save_report(text, category_4m, risk_level, follow_up_answer=None, similar_case_id=None) → bool:
  - reports テーブルに INSERT
  - 成功で True、失敗で False（例外キャッチしてログ出力）

# Step 5: 結合テスト

マイクで「3階の足場で板がズレた」と話して:

1. AIが「なるほど、確認させてください。高さは何メートルくらいでしたか？」と返答する
2. 「7メートル」と答えると、AIが4M分類とリスクレベルを伝えて締める
3. Supabase の reports テーブルに行が入る
この3つが確認できたら完了。
