-- 已有库增量迁移：food_logs 增加 food_name / confidence / dialog_timestamp（MySQL 8+）
-- 执行前请备份。若某列已存在会报错，跳过对应行即可。

SET NAMES utf8mb4;

ALTER TABLE food_logs
  ADD COLUMN food_name VARCHAR(255) NOT NULL DEFAULT '' AFTER food_id;

ALTER TABLE food_logs
  ADD COLUMN confidence VARCHAR(32) NOT NULL DEFAULT 'low' AFTER logged_at;

ALTER TABLE food_logs
  ADD COLUMN dialog_timestamp VARCHAR(128) NOT NULL DEFAULT '' AFTER confidence;

-- 可选：用 foods 表回填历史 food_name
-- UPDATE food_logs fl INNER JOIN foods f ON f.id = fl.food_id SET fl.food_name = f.name WHERE fl.food_name = '';
