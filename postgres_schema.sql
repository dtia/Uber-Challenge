drop table if exists favorites;
create table favorites (
  id integer primary key,
  lat float not null,
  lng float not null,
  street text not null,
  city text not null,
  state text not null,
  zip integer not null,
  name text not null
);
