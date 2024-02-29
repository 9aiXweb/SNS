--  Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS friendrequest;
DROP TABLE IF EXISTS friendship;
DROP TABLE IF EXISTS message;
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  details TEXT  NOT NULL
  
);

CREATE TABLE friendrequest (

  request_id INTEGER,
  friend_id INTEGER,
  PRIMARY KEY (request_id, friend_id),
  FOREIGN KEY (request_id) REFERENCES user(id),
  FOREIGN KEY (friend_id) REFERENCES user(id)
);

CREATE TABLE friendship (

  my_id INTEGER,
  friend_id INTEGER,
  message_content TEXT,
  PRIMARY KEY (my_id, friend_id),
  FOREIGN KEY (my_id) REFERENCES user(id),
  FOREIGN KEY (friend_id) REFERENCES user(id)
);

CREATE TABLE message (

  sender_id INTEGER,
  receiver_id INTEGER,
  message_content TEXT,
  FOREIGN KEY (sender_id) REFERENCES friendship (my_id),
  FOREIGN KEY (receiver_id) REFERENCES friendship (friend_id)
);


CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);
