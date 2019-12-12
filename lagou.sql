CREATE TABLE `lagou_company` (
  `url` varchar(255) NOT NULL,
  `url_object_id` varchar(64) NOT NULL,
  `company_name` varchar(255) DEFAULT NULL,
  `industry` varchar(255) DEFAULT NULL,
  `finance` varchar(255) DEFAULT NULL,
  `people_count` varchar(255) DEFAULT NULL,
  `city` varchar(255) DEFAULT NULL,
  `score` varchar(255) DEFAULT NULL,
  `create_date` varchar(255) DEFAULT NULL,
  `tags` varchar(255) DEFAULT NULL,
  `company_desc` text,
  `crawl_time` datetime DEFAULT NULL,
  `review_count` int(255) DEFAULT NULL,
  `job_count` int(255) DEFAULT NULL,
  PRIMARY KEY (`url_object_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `lagou_job` (
  `url` varchar(300) NOT NULL,
  `url_object_id` varchar(50) NOT NULL,
  `title` varchar(100) DEFAULT NULL,
  `max_salary` varchar(10) DEFAULT NULL,
  `min_salary` varchar(10) DEFAULT NULL,
  `city` varchar(10) DEFAULT NULL,
  `work_years` varchar(10) DEFAULT NULL,
  `degree_need` varchar(255) DEFAULT NULL,
  `job_type` varchar(255) DEFAULT NULL,
  `publish_time` varchar(20) NOT NULL,
  `tags` varchar(100) DEFAULT NULL,
  `job_advantage` varchar(1000) NOT NULL,
  `job_desc` longtext,
  `job_addr` varchar(255) DEFAULT NULL,
  `company_url` varchar(300) NOT NULL,
  `company_url_id` varchar(64) NOT NULL,
  `company_name` varchar(100) DEFAULT NULL,
  `crawl_time` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `lagou_review` (
  `id` bigint(20) NOT NULL COMMENT 'id',
  `review_comment` text NOT NULL COMMENT '面试评论',
  `company_url` varchar(255) DEFAULT NULL,
  `company_url_id` varchar(64) DEFAULT NULL,
  `company_name` varchar(255) DEFAULT NULL,
  `review_tags` varchar(255) DEFAULT NULL COMMENT '标签',
  `useful_count` varchar(255) DEFAULT NULL COMMENT '有用数',
  `score` float(2,1) DEFAULT NULL COMMENT '评分',
  `review_job` varchar(255) DEFAULT NULL,
  `comment_time` date DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `proxy_ip` (
  `ip` varchar(255) DEFAULT NULL,
  `port` varchar(255) DEFAULT NULL,
  `speed` double DEFAULT NULL,
  `proxy_type` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;