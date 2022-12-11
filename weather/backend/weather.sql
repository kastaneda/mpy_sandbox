CREATE TABLE `weather` (
  `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `station` varchar(12) CHARACTER SET ascii DEFAULT NULL,
  `temperature` decimal(4,2) DEFAULT NULL,
  `pressure` int(6) UNSIGNED DEFAULT NULL,
  `humidity` decimal(5,2) UNSIGNED DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
