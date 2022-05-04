
-- event data with str/int keys to demo the differences between each other.
INSERT INTO event_str (user_id, reason, duration_seconds) VALUES ("111", "purchase", 540);
INSERT INTO event_int (user_id, reason, duration_seconds) VALUES (111, "purchase", 540);

-- dimension data
REPLACE INTO dim_user (user_id, user_attribute) VALUES ("111", "***AAA");
REPLACE INTO dim_user_reason (user_id, reason_id, user_reason_attribute) VALUES ("111", "purchase", "***AAA***purchase");