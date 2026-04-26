-- 建表 + Mock 数据（MySQL 8+）
-- 用法示例：
--   mysql -h127.0.0.1 -uroot -p < db/init_schema_and_seed.sql
-- 或先建库再执行：
--   mysql -h127.0.0.1 -uroot -p -e "CREATE DATABASE IF NOT EXISTS nutrition_agent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
--   mysql -h127.0.0.1 -uroot -p nutrition_agent < db/init_schema_and_seed.sql

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS food_logs;
DROP TABLE IF EXISTS nutrition_goals;
DROP TABLE IF EXISTS health_information;
DROP TABLE IF EXISTS foods;
DROP TABLE IF EXISTS users;

SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE users (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  password VARCHAR(255) NOT NULL,
  created_at DATETIME(6) NOT NULL,
  updated_at DATETIME(6) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE health_information (
  id INT NOT NULL AUTO_INCREMENT,
  user_id VARCHAR(64) NOT NULL,
  height_cm DOUBLE NOT NULL,
  weight_kg DOUBLE NOT NULL,
  age INT NOT NULL,
  gender VARCHAR(64) NOT NULL,
  activity_level VARCHAR(64) NOT NULL,
  target_weight_kg DOUBLE NOT NULL,
  PRIMARY KEY (id),
  KEY ix_health_information_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE foods (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  calories DOUBLE NOT NULL,
  protein_g DOUBLE NOT NULL,
  fat_g DOUBLE NOT NULL,
  carb_g DOUBLE NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE food_logs (
  id INT NOT NULL AUTO_INCREMENT,
  user_id VARCHAR(64) NOT NULL,
  food_id INT NOT NULL,
  food_name VARCHAR(255) NOT NULL,
  amount_g DOUBLE NOT NULL,
  meal_type VARCHAR(64) NOT NULL,
  calories DOUBLE NOT NULL,
  protein_g DOUBLE NOT NULL,
  fat_g DOUBLE NOT NULL,
  carb_g DOUBLE NOT NULL,
  logged_at DATETIME(6) NOT NULL,
  confidence VARCHAR(32) NOT NULL DEFAULT 'low',
  dialog_timestamp VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  KEY ix_food_logs_user_id (user_id),
  KEY ix_food_logs_logged_at (logged_at),
  CONSTRAINT fk_food_logs_food_id FOREIGN KEY (food_id) REFERENCES foods (id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE nutrition_goals (
  id INT NOT NULL AUTO_INCREMENT,
  user_id VARCHAR(64) NOT NULL,
  daily_calories DOUBLE NOT NULL,
  daily_protein_g DOUBLE NOT NULL,
  daily_fat_g DOUBLE NOT NULL,
  daily_carb_g DOUBLE NOT NULL,
  updated_at DATETIME(6) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_nutrition_goals_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO users (id, name, email, password, created_at, updated_at) VALUES
  (1, '张三', 'zhangsan@example.com', '$2b$12$mockDoNotUseInProduction', '2026-01-10 09:00:00.000000', '2026-01-10 09:00:00.000000'),
  (2, '李四', 'lisi@example.com', '$2b$12$mockDoNotUseInProduction', '2026-01-11 10:00:00.000000', '2026-01-11 10:00:00.000000');

INSERT INTO health_information (id, user_id, height_cm, weight_kg, age, gender, activity_level, target_weight_kg) VALUES
  (1, '1', 175.0, 78.5, 28, 'male', 'moderate', 72.0),
  (2, '2', 162.0, 55.0, 24, 'female', 'light', 54.0);

INSERT INTO foods (id, name, calories, protein_g, fat_g, carb_g) VALUES
  (1, '燕麦片', 389.0, 13.2, 6.9, 66.3),
  (2, '鸡胸肉', 165.0, 31.0, 3.6, 0.0),
  (3, '香蕉', 89.0, 1.1, 0.3, 22.8),
  (4, '希腊酸奶', 97.0, 9.0, 5.0, 3.6);

INSERT INTO food_logs (id, user_id, food_id, food_name, amount_g, meal_type, calories, protein_g, fat_g, carb_g, logged_at, confidence, dialog_timestamp) VALUES
  (1, '1', 1, '燕麦片', 60.0, 'breakfast', 233.4, 7.9, 4.1, 39.8, '2026-04-24 08:15:00.000000', 'low', '2026-04-24T08:15:00'),
  (2, '1', 3, '香蕉', 120.0, 'breakfast', 106.8, 1.3, 0.4, 27.4, '2026-04-24 08:20:00.000000', 'low', '2026-04-24T08:20:00'),
  (3, '1', 2, '鸡胸肉', 150.0, 'lunch', 247.5, 46.5, 5.4, 0.0, '2026-04-24 12:30:00.000000', 'medium', '2026-04-24T12:30:00'),
  (4, '1', 4, '希腊酸奶', 100.0, 'snack', 97.0, 9.0, 5.0, 3.6, '2026-04-24 15:00:00.000000', 'low', '2026-04-24T15:00:00'),
  (5, '2', 2, '鸡胸肉', 100.0, 'lunch', 165.0, 31.0, 3.6, 0.0, '2026-04-24 12:00:00.000000', 'low', '2026-04-24T12:00:00');

INSERT INTO nutrition_goals (id, user_id, daily_calories, daily_protein_g, daily_fat_g, daily_carb_g, updated_at) VALUES
  (1, '1', 2100.0, 130.0, 70.0, 220.0, '2026-04-24 00:00:00.000000'),
  (2, '2', 1700.0, 95.0, 55.0, 180.0, '2026-04-24 00:00:00.000000');
