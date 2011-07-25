-- iwantrequest
alter table shoppleyuser_iwantrequest add column processed boolean;

-- to handle logical delete
alter table offer_offer add column date_created timestamp with time zone;
alter table offer_offer add column date_modified timestamp with time zone;
update offer_offer set date_created=time_stamp;
update offer_offer set date_modified=time_stamp;
alter table offer_offer alter column date_created SET not null;
alter table offer_offer alter column date_modified SET not null;
alter table offer_offer add column date_removed timestamp with time zone;
alter table offer_offer alter column expired_time TYPE timestamp with time zone;

