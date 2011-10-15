CREATE TABLE IF NOT EXISTS `nas_changes` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'change id',
  `when` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'when change occurred',
  `kind` varchar(6) NOT NULL COMMENT 'what happened',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;
