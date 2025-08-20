DROP TABLE IF EXISTS reference;
DROP TABLE IF EXISTS query;
DROP TABLE IF EXISTS cmd_queue;
--
-- Important to note that this file must not have any empty lines until the end, hence the comments.
--
CREATE TABLE reference (id INTEGER PRIMARY KEY AUTO_INCREMENT, name TEXT UNIQUE NOT NULL, display_name TEXT UNIQUE NOT NULL, path TEXT NOT NULL,  genome_count INTEGER NOT NULL,  arm_selection TEXT NOT NULL,  description TEXT, example TEXT);
--
CREATE TABLE query (id INTEGER PRIMARY KEY AUTO_INCREMENT, uid TEXT, reference TEXT, email TEXT, date TEXT, status TEXT);
--
CREATE TABLE cmd_queue (id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL, cmd TEXT NOT NULL, status TEXT NOT NULL);
--
