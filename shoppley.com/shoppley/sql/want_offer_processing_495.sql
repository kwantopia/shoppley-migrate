-- iwantrequest
alter table shoppleyuser_iwantrequest add column processed boolean;

-- to handle logical delete
alter table offer_offer add column date_created timestamp with time zone not null;
alter table offer_offer add column date_modified timestamp with time zone not null;
alter table offer_offer add column date_removed timestamp with time zone;
alter table offer_offer alter column expired_time TYPE timestamp with time zone;

