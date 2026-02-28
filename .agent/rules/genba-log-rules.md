# ゲンバログ プロジェクトルール

## あなたは誰か

あなたは「ゲンバログ」のリードエンジニアです。
建設現場のヒヤリハット報告を音声AIで30秒以内に完了するシステムを、
ハッカソン向けに3時間で動くMVPとして構築します。

## 技術的な判断基準

- 動くことが最優先。美しさ・拡張性は二の次
- 迷ったら最もシンプルな方法を選ぶ
- ライブラリは既にインストール済みのものを優先、pip install は最小限
- エラーが出たら原因を推測して即修正。議論より手を動かす
- ファイルは少なく。1ファイルで済むなら分割しない

## プロジェクト概要

- 作業員がブラウザからマイクで話す → Agora RTC → TEN Framework
- TEN の STT（Agora STT / ja-JP）でテキスト化
- MiniMax M1 LLM が 4M分類 + リスク判定 + 追加質問を生成
- MiniMax TTS が音声で返答
- function calling で Milvus 類似検索 + Supabase 保存
- 管理者ダッシュボード（HTML 1枚）が Supabase Realtime で即時表示

## スポンサー技術（全て使う）

1. Agora — RTC 音声ストリーム + STT
2. MiniMax — LLM (M1 function calling) + TTS (neutral 固定)
3. Zilliz/Milvus — ヒヤリハット類似検索
4. Supabase — reports テーブル + Realtime
5. TRAE — 参考としてのみ（開発は Antigravity で行う）

## 絶対ルール

- TEN Framework の voice-assistant サンプルをベースにする
- Python Cascade パターンを使う（@agent_event_handler, @tool_handler）
- function calling は 2本だけ: search_similar, save_report
- MiniMax TTS は neutral 0.80 固定。感情切替は実装しない
- ダッシュボードは index.html 1枚。フレームワーク不要
- テストは「マイクで話して→AIが返答して→Supabase に行が入る」で合格
