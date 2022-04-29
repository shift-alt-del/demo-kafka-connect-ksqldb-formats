CREATE TABLE IF NOT EXISTS table_key_int (user_id INT, reason TEXT, duration_seconds INT);
CREATE TABLE IF NOT EXISTS table_key_str (user_id TEXT, reason TEXT, duration_seconds INT);

TRUNCATE TABLE table_key_int;
TRUNCATE TABLE table_key_str;