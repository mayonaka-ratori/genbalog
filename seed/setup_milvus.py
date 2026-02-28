import os
import json
import hashlib
import requests
from dotenv import load_dotenv
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility

# .env ファイルを読み込む
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

ZILLIZ_URI = os.getenv("ZILLIZ_CLOUD_URI")
ZILLIZ_TOKEN = os.getenv("ZILLIZ_CLOUD_TOKEN")
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")
MINIMAX_GROUP_ID = os.getenv("MINIMAX_GROUP_ID")

def get_embedding(text):
    """MiniMax の embedding API を使用してベクトルを取得する。失敗時はハッシュベースのダミーベクトルを返す"""
    if MINIMAX_API_KEY and MINIMAX_GROUP_ID:
        url = f"https://api.minimax.chat/v1/embeddings?GroupId={MINIMAX_GROUP_ID}"
        headers = {
            "Authorization": f"Bearer {MINIMAX_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "embo-01",
            "texts": [text]
        }
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                resp_json = response.json()
                if "vectors" in resp_json and len(resp_json["vectors"]) > 0:
                    return resp_json["vectors"][0]
        except Exception as e:
            print(f"Embedding API failed: {e}")
            
    # フォールバック: テキストのハッシュを使ってダミーベクトルを生成（1536次元）
    print(f"Using dummy embedding for: {text[:20]}...")
    h = hashlib.sha256(text.encode()).digest()
    dummy = []
    for i in range(1536):
        dummy.append((h[i % 32] / 255.0) * 2 - 1)  # -1 to 1 に正規化
    return dummy

def setup_milvus():
    if not ZILLIZ_URI or not ZILLIZ_TOKEN:
        print("ZILLIZ_CLOUD_URI または ZILLIZ_CLOUD_TOKEN が設定されていません。")
        return

    # Zilliz Cloud に接続
    print(f"Connecting to Zilliz Cloud: {ZILLIZ_URI}")
    connections.connect("default", uri=ZILLIZ_URI, token=ZILLIZ_TOKEN)

    collection_name = "hiyarihatto"

    # 古いコレクションがあれば削除
    if utility.has_collection(collection_name):
        print(f"Dropping existing collection: {collection_name}")
        utility.drop_collection(collection_name)

    # コレクションのスキーマ定義
    fields = [
        FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=1000),
        FieldSchema(name="category_4m", dtype=DataType.VARCHAR, max_length=100),
        FieldSchema(name="risk_level", dtype=DataType.VARCHAR, max_length=50),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536)
    ]
    schema = CollectionSchema(fields, description="ヒヤリハット類似検索用コレクション")
    
    print(f"Creating collection: {collection_name}")
    collection = Collection(collection_name, schema)

    # インデックス作成
    index_params = {
        "metric_type": "COSINE",
        "index_type": "AUTOINDEX",
        "params": {}
    }
    collection.create_index(field_name="embedding", index_params=index_params)
    print("Index created.")

    # シードデータの読み込み
    seed_file = os.path.join(os.path.dirname(__file__), "seed_cases.json")
    if not os.path.exists(seed_file):
        print(f"Seed file not found: {seed_file}")
        return
        
    with open(seed_file, "r", encoding="utf-8") as f:
        cases = json.load(f)

    # データの準備
    entities = [
        [], # id
        [], # text
        [], # category_4m
        [], # risk_level
        []  # embedding
    ]
    
    for case in cases:
        entities[0].append(case["id"])
        entities[1].append(case["text"])
        entities[2].append(case["category_4m"])
        entities[3].append(case["risk_level"])
        entities[4].append(get_embedding(case["text"]))

    # データの挿入
    print(f"Inserting {len(cases)} records...")
    collection.insert(entities)
    collection.flush()
    print("Data inserted and collection flushed.")
    
    # ロードして検索可能にする
    collection.load()
    print("Collection loaded.")

if __name__ == "__main__":
    setup_milvus()
