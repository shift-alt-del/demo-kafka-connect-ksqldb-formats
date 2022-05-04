CREATE TABLE IF NOT EXISTS event_int (id int not null auto_increment, user_id INT, reason TEXT, duration_seconds INT, PRIMARY KEY (id));
CREATE TABLE IF NOT EXISTS event_str (id int not null auto_increment, user_id TEXT, reason TEXT, duration_seconds INT, PRIMARY KEY (id));
TRUNCATE TABLE event_int;
TRUNCATE TABLE event_str;


CREATE TABLE IF NOT EXISTS dim_user (user_id VARCHAR(32), user_attribute TEXT, PRIMARY KEY (user_id));
TRUNCATE TABLE dim_user;

CREATE TABLE IF NOT EXISTS dim_user_reason (user_id VARCHAR(32), reason_id VARCHAR(32), user_reason_attribute TEXT, PRIMARY KEY (user_id, reason_id));
TRUNCATE TABLE dim_user_reason;