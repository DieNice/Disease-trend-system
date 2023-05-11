-- Таблица симптомокомлексов
create table symptom_complexes (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	primary key(`id`),
	total_number INT unsigned NOT NULL,
	date DATETIME NOT NULL DEFAULT now(),
	percent_people DOUBLE NOT NULL,
	extra JSON NOT NULL,
	symptom_hash VARCHAR(32) NOT NULL,
	symptom_complex_hash VARCHAR(32) NOT NULL);