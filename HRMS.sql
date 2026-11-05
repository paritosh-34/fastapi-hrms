-- HR system schema (SQLite)
-- Revision 2. Changes from revision 1 are marked [CHANGED] / [ADDED].

PRAGMA foreign_keys = ON;   -- SQLite does not enforce FKs unless you ask, per connection
PRAGMA journal_mode = WAL;  -- readers (a GUI) don't block the writer

CREATE TABLE IF NOT EXISTS `departments` (
	`id` INTEGER PRIMARY KEY,
	`department_name` TEXT NOT NULL UNIQUE,
	`description` TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS `employees` (
	`id` INTEGER PRIMARY KEY,
	`name` TEXT NOT NULL,
	`work_email` TEXT NOT NULL UNIQUE,
	`job_title` TEXT NOT NULL,
	`date_joined` DATE NOT NULL,              -- [CHANGED] was date_joined_utc REAL
	`salary` INTEGER NOT NULL,
	`role` TEXT NOT NULL,
	`emp_status` TEXT NOT NULL,
	`department_id` INTEGER,                  -- [CHANGED] now nullable
	`manager_id` INTEGER,
	`password_hash` TEXT NOT NULL,            -- [ADDED] required by Part 2 auth
	FOREIGN KEY (`department_id`) REFERENCES `departments`(`id`),
	FOREIGN KEY (`manager_id`) REFERENCES `employees`(`id`)
);

CREATE TABLE IF NOT EXISTS `leave_types` (    -- [CHANGED] was `leave`
	`id` INTEGER PRIMARY KEY,
	`type` TEXT NOT NULL UNIQUE,
	`days` INTEGER NOT NULL                   -- default yearly entitlement for this type
);

CREATE TABLE IF NOT EXISTS `leave_balances` ( -- [CHANGED] was `employee_leave`
	`id` INTEGER PRIMARY KEY,
	`employee_id` INTEGER NOT NULL,
	`leave_type_id` INTEGER NOT NULL,         -- [CHANGED] was leave_id
	`entitled_days` INTEGER NOT NULL,         -- [CHANGED] replaces leaves_remaining
	`used_days` INTEGER NOT NULL DEFAULT 0,   -- [CHANGED] replaces leaves_remaining
	`consumed_year_in` INTEGER NOT NULL,
	FOREIGN KEY (`employee_id`) REFERENCES `employees`(`id`),
	FOREIGN KEY (`leave_type_id`) REFERENCES `leave_types`(`id`),
	-- [ADDED] one balance row per employee, per leave type, per year
	UNIQUE (`employee_id`, `leave_type_id`, `consumed_year_in`)
);

CREATE TABLE IF NOT EXISTS `leave_requests` ( -- [CHANGED] was `leave_request`
	`id` INTEGER PRIMARY KEY,
	`employee_id` INTEGER NOT NULL,
	`leave_type_id` INTEGER NOT NULL,         -- [CHANGED] was leave_id
	`start_date` DATE NOT NULL,               -- [CHANGED] was start_date_utc REAL
	`end_date` DATE NOT NULL,                 -- [CHANGED] was end_date_utc REAL
	`reason` TEXT NOT NULL,
	`no_of_days` INTEGER NOT NULL,
	`approver_id` INTEGER,                    -- [CHANGED] now nullable: unset until decided
	`request_status` TEXT NOT NULL,
	FOREIGN KEY (`employee_id`) REFERENCES `employees`(`id`),
	FOREIGN KEY (`leave_type_id`) REFERENCES `leave_types`(`id`),
	FOREIGN KEY (`approver_id`) REFERENCES `employees`(`id`)
);

-- [ADDED] indexes: the UNIQUE constraints above create their own, these cover the joins
CREATE INDEX IF NOT EXISTS ix_employees_department_id   ON `employees` (`department_id`);
CREATE INDEX IF NOT EXISTS ix_employees_manager_id      ON `employees` (`manager_id`);
CREATE INDEX IF NOT EXISTS ix_leave_balances_employee   ON `leave_balances` (`employee_id`);
CREATE INDEX IF NOT EXISTS ix_leave_requests_employee   ON `leave_requests` (`employee_id`);
CREATE INDEX IF NOT EXISTS ix_leave_requests_status     ON `leave_requests` (`request_status`);
