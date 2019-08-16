-- Create syntax for TABLE 'alembic_version'
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) COLLATE utf8mb4_bin NOT NULL COMMENT 'Migration Version number',
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin ROW_FORMAT=COMPRESSED COMMENT='Track database migrations versions';

-- Create syntax for TABLE 'custom_record'
CREATE TABLE `custom_record` (
  `id` int(11) NOT NULL COMMENT 'Primary key, also a foreign key to the record table',
  `service_id` varchar(64) COLLATE utf8mb4_bin NOT NULL COMMENT 'An unique identifier of this record',
  `added_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_service_id` (`service_id`),
  CONSTRAINT `custom_record_fk_id` FOREIGN KEY (`id`) REFERENCES `record` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin ROW_FORMAT=COMPRESSED COMMENT='Meta table for user defined records';

-- Create syntax for TABLE 'record_audit'
CREATE TABLE record_audit (
    `id` int(11) NOT NULL COMMENT 'Primary key',
    `htmlurl_sha1` char(40) COLLATE utf8mb4_bin NOT NULL COMMENT 'A hexadecimal representation of the html_url',
    `changed_at` DATETIME DEFAULT NULL,
    `action` VARCHAR(50) DEFAULT NULL
);

-- Create syntax for TABLE 'record'
CREATE TABLE `record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `htmlurl_sha1` char(40) COLLATE utf8mb4_bin NOT NULL COMMENT 'A hexadecimal representation of the html_url',
  `name` varchar(1000) COLLATE utf8mb4_bin NOT NULL,
  `purged` datetime DEFAULT NULL,
  `count` int(11) NOT NULL,
  `last_checked` timestamp NULL DEFAULT NULL COMMENT 'Last time the record was checked for updated. Can be NULL if never checked',
  `added_on` datetime DEFAULT NULL,
  `type` varchar(25) NOT NULL COMMENT 'Type of record',
  PRIMARY KEY (`id`),
  KEY `IDX_record_added_on` (`added_on`),
  KEY `record_type` (`type`),
  KEY `recordurlsha1html` (`htmlurl_sha1`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin ROW_FORMAT=COMPRESSED;

CREATE OR REPLACE VIEW custom_record_view AS (
  SELECT
    c.id,
    r.id as subject_id
  FROM
    custom_record c
    INNER JOIN record r ON c.id = r.id
  WHERE
    r.type IN ('new', 'in_progress', 'complete')
    AND c.added_on IS NULL
);

DELIMITER $$
CREATE TRIGGER before_record_update
  BEFORE UPDATE ON record
  FOR EACH ROW
BEGIN
  INSERT INTO record_audit
  SET
    action = 'update',
    htmlurl_sha1 = OLD.htmlurl_sha1,
    changed_at = NOW();
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE count_record_by_type(
  IN type varchar(25),
  OUT total int)
BEGIN
  SELECT
    count(name)
  INTO
    total
  FROM
    record
  WHERE
    type = type;
END$$
DELIMITER ;
