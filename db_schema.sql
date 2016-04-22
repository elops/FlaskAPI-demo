CREATE DATABASE apidb;
USE apidb;
-- server_ip is 45 because of possible IPv6 addr which is at best 45 chars long
-- root_key I've set it to 1000 chars, didn't use BLOB/TEXT because those can't be cached and figured 1000 is enough to store the key.
-- free space could have been int but figured we can go with float just for the fun of it
CREATE TABLE `servers` (
  `server_id` int(11) NOT NULL AUTO_INCREMENT,
  `server_ip` varchar(45) NOT NULL,
  `root_key` varchar(1000) NOT NULL,
  `free_space` float(10,1) NOT NULL,
  PRIMARY KEY (`server_id`)
)
