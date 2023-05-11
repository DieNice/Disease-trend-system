START TRANSACTION;
create temporary table if not exists `symptom_complexes_temp` (
  `total_number` int unsigned NOT NULL,
  `date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `percent_people` double NOT NULL,
  `extra` json NOT NULL,
  `symptom_hash` varchar(32) NOT NULL,
  `symptom_complex_hash` varchar(32) NOT NULL
);
truncate symptom_complexes_temp;
create temporary table if not exists `symptom_complexes_hash_temp` (
  `symptom_complex_hash` varchar(32) NOT NULL
);
truncate symptom_complexes_hash_temp;
insert
	into
	symptom_complexes_temp (total_number,
	date,
	percent_people,
	extra,
	symptom_hash,
	symptom_complex_hash
	)
values
	(
	100,
"2023-04-11T00:00:00",
32.0,
'{"test_1": 1}',
'6fe4850c0aaed75920471477896176c3',
'4322c4c809527a57152c37bac2a0d89d'
	),
	(
	100,
"2023-04-11T00:00:00",
32.0,
'{"test_2": 2}',
'05aebfe84f3de48202949b110e920b65',
'4322c4c809527a57152c37bac2a0d89f'
	),
		(	
	100,
"2023-04-11T00:00:00",
32.0,
'{"test_M": 3}',
'7e2dbcfe509fc291621040270a1c0ff4',
'7e2dbcfe509fc291621040270a1c0ef4'
	);
insert
	into
	symptom_complexes_hash_temp (symptom_complex_hash)
with cte as (
select
	sc.*,
	sct.total_number as '_total_number',
	sct.`date` as '_date',
	sct.percent_people as '_percent_people',
	sct.extra as '_extra',
	sct.symptom_hash as '_symptom_hash',
	sct.symptom_complex_hash as '_symptom_complex_hash'
from
	symptom_complexes_temp sct
left join symptom_complexes sc on
	sct.symptom_hash = sc.symptom_hash
order by
	sct.symptom_hash),
cte_2 as (
select
	distinct symptom_complex_hash as symptom_complex_hash
from
	(
	select
		cte.*,
		count(1) over (partition by symptom_complex_hash) as `concurrency`
	from
		cte) mt
where
	mt.concurrency BETWEEN 2 and 4)
select
	symptom_complex_hash
from
	cte_2;
insert
	into
	symptom_complexes (total_number,
	`date`,
	percent_people,
	extra,
	symptom_hash,
	symptom_complex_hash
) select
	sct.total_number,
	sct.`date`,
	sct.percent_people,
	sct.extra,
	sct.symptom_hash,
	scht.symptom_complex_hash
from
	symptom_complexes_hash_temp scht
cross join symptom_complexes_temp sct;
insert into symptom_complexes (total_number,
	`date`,
	percent_people,
	extra,
	symptom_hash,
	symptom_complex_hash)
select total_number,
	`date`,
	percent_people,
	extra,
	symptom_hash,
	symptom_complex_hash from symptom_complexes_temp;
truncate symptom_complexes_temp;
truncate symptom_complexes_hash_temp;
drop table if exists symptom_complexes_temp;
drop table if exists symptom_complexes_hash_temp;
COMMIT;
