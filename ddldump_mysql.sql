--
-- Table structure for table `alembic_version`
--

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) COLLATE utf8mb4_bin NOT NULL COMMENT 'Migration Version number',
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin ROW_FORMAT=COMPRESSED COMMENT='Track database migrations versions';

--
-- Table structure for table `record`
--

CREATE TABLE `record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `htmlurl_sha1` char(40) COLLATE utf8mb4_bin NOT NULL COMMENT 'A hexadecimal representation of the html_url',
  `name` varchar(1000) COLLATE utf8mb4_bin NOT NULL,
  `purged` datetime DEFAULT NULL,
  `count` int(11) NOT NULL,
  `last_checked` timestamp NULL DEFAULT NULL COMMENT 'Last time the record was checked for updated. Can be NULL if never checked',
  `added_on` datetime DEFAULT NULL,
  `type` int(11) NOT NULL COMMENT 'Type of record',
  PRIMARY KEY (`id`),
  KEY `record_type` (`record`),
  KEY `recordurlsha1html` (`htmlurl_sha1`),
  KEY `IDX_record_added_on` (`added_on`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin ROW_FORMAT=COMPRESSED;

--
-- Table structure for table `custom_record`
--

CREATE TABLE `custom_record` (
  `id` int(11) NOT NULL COMMENT 'Primary key, also a foreign key to the record table',
  `service_id` varchar(255) COLLATE utf8mb4_bin NOT NULL COMMENT 'An unique identifier of this record',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_service_id` (`service_id`),
  CONSTRAINT `custom_record_meta_fk_id` FOREIGN KEY (`id`) REFERENCES `record` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin ROW_FORMAT=COMPRESSED COMMENT='Meta table for user defined records';
