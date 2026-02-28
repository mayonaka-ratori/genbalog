# フォルダ構成

genba-log/
├── .agent/
│   ├── rules/
│   │   ├── genba-log-rules.md        # プロジェクトルール（Always On）
│   │   └── project-structure.md       # この構成ファイル（Always On）
│   └── workflows/
│       ├── setup-tonight.md           # 今夜の事前準備ワークフロー
│       ├── build-core.md              # 当日 Phase 1-2 ワークフロー
│       ├── build-dashboard.md         # 当日 Phase 3 前半ワークフロー
│       └── test-and-fix.md            # 当日 Phase 3 後半ワークフロー
├── .env                               # API キー
├── docker-compose.yml                 # TEN Framework 起動用
│
├── agents/
│   └── examples/
│       └── genba-log/
│           ├── property.json          # グラフ定義（STT→LLM→TTS 接続）
│           └── tenapp/
│               └── ten_packages/
│                   └── extension/
│                       └── main_python/
│                           └── extension.py   # メインロジック
│
├── tools/
│   ├── milvus_client.py               # search_similar の実装
│   └── supabase_client.py             # save_report の実装
│
├── seed/
│   ├── seed_cases.json                # ヒヤリハット 5件
│   └── setup_milvus.py               # Milvus にシードを投入
│
├── dashboard/
│   └── index.html                     # 管理者ダッシュボード
│
└── prompts/
    └── system_prompt.md               # LLM システムプロンプト
