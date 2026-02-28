CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    text TEXT NOT NULL,
    category_4m TEXT NOT NULL,
    risk_level TEXT NOT NULL,
    follow_up_answer TEXT,
    similar_case_id TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- RLS は OFF (デフォルトでOFFですが明示的に)
ALTER TABLE reports DISABLE ROW LEVEL SECURITY;

-- Realtime有効化
BEGIN;
  DROP PUBLICATION IF EXISTS supabase_realtime;
  CREATE PUBLICATION supabase_realtime;
COMMIT;
ALTER PUBLICATION supabase_realtime ADD TABLE reports;
