CREATE TABLE IF NOT EXISTS event_int (id int not null auto_increment, user_id INT, reason TEXT, duration_seconds INT, PRIMARY KEY (id));
CREATE TABLE IF NOT EXISTS event_str (id int not null auto_increment, user_id TEXT, reason TEXT, duration_seconds INT, PRIMARY KEY (id));

TRUNCATE TABLE event_int;
TRUNCATE TABLE event_str;