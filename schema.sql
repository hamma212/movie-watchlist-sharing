-- tables

create table users(
  user_id text PRIMARY KEY,
  username varchar(50) NOT NULL,
  bio text,
  public boolean NOT NULL,
  picture text
);


create table media(
  media_id text PRIMARY KEY,
  media_type varchar(50) NOT NULL,
  media_title text,
  media_poster_path text
);

create table watched(
  user_id text,
  media_id text,
  PRIMARY KEY (user_id, media_id),
  FOREIGN KEY (media_id) references media(media_id),
  FOREIGN KEY (user_id) references users(user_id)
);

create table watching(
  user_id text,
  media_id text,
  PRIMARY KEY (user_id, media_id),
  FOREIGN KEY (media_id) references media(media_id),
  FOREIGN KEY (user_id) references users(user_id)
);

create table will_watch(
  user_id text,
  media_id text,
  PRIMARY KEY (user_id, media_id),
  FOREIGN KEY (media_id) references media(media_id),
  FOREIGN KEY (user_id) references users(user_id)
);

create table follow(
  follower text,
  followee text,
  PRIMARY KEY (follower, followee),
  FOREIGN KEY (follower) references users(user_id),
  FOREIGN KEY (followee) references users(user_id),
  CHECK (follower <> followee)
);




-- sample data

insert into users values ('1', 'user1', 'hello', 'true');
insert into users values ('2', 'user2', 'bye', 'false');

insert into media values ('001');
insert into media values ('002');
insert into media values ('999');

insert into watched values ('1', '001');
insert into watching values ('1', '002');
insert into will_watch values ('2', '999');

-- sample queries

select media_id from watched where user_id = '1';
select media_id from watching where user_id = '1';
select media_id from will_watch where user_id = '2';

SELECT * FROM follow INNER JOIN users ON follow.followee = users.user_id WHERE follow.follower = 'google-oauth2|117239604153286155360' ORDER BY users.username;
SELECT users.* FROM follow INNER JOIN users ON follow.followee = users.user_id WHERE follow.follower = 'google-oauth2|117239604153286155360' ORDER BY users.username;
