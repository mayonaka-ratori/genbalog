import os
import hashlib
import requests
from pymilvus import connections, Collection
from dotenv import load_dotenv

# dotenv を読み込み
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

ZILLIZ_URI = os.getenv("ZILLIZ_CLOUD_URI")
ZILLIZ_TOKEN = os.getenv("ZILLIZ_CLOUD_TOKEN")
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")
MINIMAX_GROUP_ID = os.getenv("MINIMAX_GROUP_ID")

# Milvus への接続を維持するためのグローバル変数
_collection = None

def get_collection():
    global _collection
    if _collection is None:
        try:
            connections.connect("default", uri=ZILLIZ_URI, token=ZILLIZ_TOKEN)
            _collection = Collection("hiyarihatto")
            _collection.load()
        except Exception as e:
            print(f"Milvus connection error: {e}")
            return None
    return _collection

def get_embedding(text: str) -> list[float]:
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
    h = hashlib.sha256(text.encode()).digest()
    dummy = []
    for i in range(1536):
        dummy.append((h[i % 32] / 255.0) * 2 - 1)  # -1 to 1 に正規化
    return dummy
    

def search_similar(query_text: str) -> dict:
    """Milvusを使用して類似のヒヤリハット事例を検索する関数"""
    try:
        col = get_collection()
        if not col:
             return {"case_id": "none", "text": "類似事例なし(DB未接続)", "score": 0}

        vector = get_embedding(query_text)
        
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10},
        }

        results = col.search(
            data=[vector], 
            anns_field="embedding", 
            param=search_params,
            limit=1,
            output_fields=["id", "text"]
        )
        
        if not results or len(results[0]) == 0:
            return {"case_id": "none", "text": "類似事例なし", "score": 0}
            
        hit = results[0][0]
        return {
            "case_id": hit.entity.get("id"),
            "text": hit.entity.get("text"),
            "score": hit.distance
        }

    except Exception as e:
        print(f"Error in search_similar: {e}")
        return {"case_id": "none", "text": "類似事例なし(検索エラー)", "score": 0}
