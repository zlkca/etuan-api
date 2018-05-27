use rdshop;

SET FOREIGN_KEY_CHECKS=0;
alter table accounts_user add column `source` VARCHAR(64) NULL after `type`; 
alter table accounts_user add column `portrait` VARCHAR(256) NULL after `source`; 
SET FOREIGN_KEY_CHECKS=1;