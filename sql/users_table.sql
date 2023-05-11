-- Таблица пользователей
create table users (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	primary key(`id`),
	username VARCHAR(100) NOT NULL,
	email VARCHAR(150) NOT NULL, 
    password VARCHAR(60) NOT NULL,
	role INT NOT NULL
    );