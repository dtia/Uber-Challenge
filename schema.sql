drop table if exists favorites;
create table favorites (
  id integer primary key autoincrement,
  lat float not null,
  lng float not null,
  street string not null,
  city string not null,
  state string not null,
  zip integer not null,
  name string not null
);
