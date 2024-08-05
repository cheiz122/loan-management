--
-- Create model Agent
--
CREATE TABLE `customer_management_app_agent` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `name` varchar(255) NOT NULL, `phone` varchar(20) NULL, `user_id` integer NOT NULL UNIQUE);
--
-- Create model Customer
--
CREATE TABLE `customer_management_app_customer` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `name` varchar(255) NOT NULL, `id_number` varchar(20) NOT NULL UNIQUE, `phone` varchar(20) NOT NULL, `email` varchar(254) NOT NULL, `active` bool NOT NULL, `agent_id` bigint NOT NULL);
--
-- Create model Loan
--
CREATE TABLE `customer_management_app_loan` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `amount` numeric(10, 2) NOT NULL, `date_borrowed` date NOT NULL, `due_date` date NOT NULL, `status` varchar(50) NOT NULL, `interest_rate` numeric(5, 2) NOT NULL, `customer_id` bigint NOT NULL);
--
-- Create model Payment
--
CREATE TABLE `customer_management_app_payment` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `amount` numeric(10, 2) NOT NULL, `date_paid` date NOT NULL, `loan_id` bigint NOT NULL);
ALTER TABLE `customer_management_app_agent` ADD CONSTRAINT `customer_management_app_agent_user_id_a8da07d2_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `customer_management_app_customer` ADD CONSTRAINT `customer_management__agent_id_8a53de0e_fk_customer_` FOREIGN KEY (`agent_id`) REFERENCES `customer_management_app_agent` (`id`);
ALTER TABLE `customer_management_app_loan` ADD CONSTRAINT `customer_management__customer_id_f4f36cf6_fk_customer_` FOREIGN KEY (`customer_id`) REFERENCES `customer_management_app_customer` (`id`);
ALTER TABLE `customer_management_app_payment` ADD CONSTRAINT `customer_management__loan_id_85333abb_fk_customer_` FOREIGN KEY (`loan_id`) REFERENCES `customer_management_app_loan` (`id`);
