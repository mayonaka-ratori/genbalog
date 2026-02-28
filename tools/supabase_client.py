import os
from supabase import create_client, Client
from dotenv import load_dotenv

# dotenv を読み込み
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_ANON_KEY", "")

# supabaseへの接続のグローバル変数
_supabase: Client = None

def get_supabase() -> Client:
    global _supabase
    if _supabase is None:
        try:
            if url and key:
                _supabase = create_client(url, key)
            else:
                 print("Supabase credentials not found in env.")
        except Exception as e:
            print(f"Supabase connection error: {e}")
    return _supabase

def save_report(text: str, category_4m: str, risk_level: str, follow_up_answer: str = None, similar_case_id: str = None) -> bool:
    """ヒヤリハット報告をSupabaseのreportsテーブルに保存する"""
    print(f"Saving report... text='{text}', category_4m='{category_4m}', risk_level='{risk_level}'")
    
    try:
        supabase = get_supabase()
        if not supabase:
             return False
        
        data = {
            "text": text,
            "category_4m": category_4m,
            "risk_level": risk_level
        }
        
        # オプショナルなフィールドを追加
        if follow_up_answer:
            data["follow_up_answer"] = follow_up_answer
        if similar_case_id and similar_case_id != "none":
            data["similar_case_id"] = similar_case_id
            
        result = supabase.table("reports").insert(data).execute()
        
        # 挿入成功
        if result and result.data:
            print(f"Report saved successfully. ID: {result.data[0].get('id')}")
            return True
            
        return False
    except Exception as e:
        print(f"Error saving report to Supabase: {e}")
        return False
