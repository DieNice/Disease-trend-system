# disease-trend-system

## Описание

Заказчик ПО: Алексей Владимирович Тарасов - научный сотрудник института автоматики ДВО РАН.

Описание задачи третьей подсистемы:
1. Существует три сервиса, которые взаимодействуют между собой
2. Интеграция между двумя подсистемами представляется по REST API (MySQL, Postgresql)
3. Тренд формируется на основе увлечения или уменьшения симптомокомлексов на определенных промежутках

* **Тестовые данные для сервиса генерируются нами(разработчиками)**

```
Примечание: Данные тренда берутся из второй подсистемы. 

```

* **Сотрудники инфраструктуры имеют компетенции для разрвертывания и сопровождения системы такие, как MySQL, Docker, Docker-compose.** 

Алгоритм добавления нового симптомокомплекса:
1. Парсим JSON файл в словарь;
2. Преобразуем всё текстовое в нижни регистр, сортируем ключи
3. Высчитываем хеш
4. Если такой хеш существует в БД, сохраняем, иначе "поиск пересечений"

* **Описание входных данных в сервис**
Симптомокомплексы - совокупность признаков и процент людей (которые встречаются минимум у 30%).
SimpA - 1 день
SimpB - 2 день
SimpC - 3 день


Шаблон описания Симптомокомплекса в программе:
| Признаки | Значение |
| ----------- | ----------- |
| Симптом | Название |
| Процент пациентов | Процент |
| Общее количество людей | Число |
| Дата регистрации симптома | Дата и время |

***Визуализация трендов* - простой график трендов**

Пример
| Признаки | Значение |
| ----------- | ----------- |
| Температура | Супфидрильная |
| Головная боль | Есть |
| Стреляет в спину | Есть |
| Процент людей c симптомокомплексом | 30 |
| Общее число людей | 100 |
| Дата выявленного симптомокопмлекса | 30-03-2023 |




**Порог тренда** - Количество дней для формирования тренда;

Необходимо сохранять исторические данные трендов.
К примеру:
Дата начала тренда
Дата конца тренда

То что не является трендом - не сохранять в БД.

Доступ к сервису осуществляется с помощбю системы доступа.

* **Описание выходных данных из сервиса**
1. Тренды симптомокомлекса;
2. Детализация симптомокомлекса (страница симптомокомлексов);
3. Алертинг (отчёт с рейтингом симптомокомлексов);

* **Правила построения тренда;**
Пользователь задаёт параметр жизни симптомокомплекса по умолчанию 5 дней.
Если не увеличивается - выкидывается.
Если уменьшается в течении 5 дней - выкидываем.
Если увеличивается - присваиваем временные метки динамики.
Если из 5 дней 3 дня идут на увелечение или стоячий - это тренд.
Если не тренд в течении 5 дней - это уже не является трендом и удаляется.

Система мониторинга в течении определенного промежутка времени.

Важно:
Если симптомокомлекс пересекается по 3-м и более признакам с другим симптомокомлексом (является надмножеством), помечать их как похожие симптомокомлексы. При учете тренда похожие симптомокомлексы дублировать в разные тренды.

Хранить хеш самого симптомокомлекса, каждая строка - это ключ, значение симптомокомлекса

Пример:
Начало недели симптомокомплекс 5 человек  - конец недели симптомокомплекс 100 человек;

```
Примечание: симтомокомлекс считается похожим если он отличается на 1-2 признака (можно сделать параметром)

```

....

## Структура проекта

* disease_trend_system/ (папка dash приложения)

    * callbacks/ (Папка с колбэками)

        * auth_callbalcks.py (Модуль колбэков авторизации)
        * raiting_callbacks.py (Модуль колбеков для страницы рейтингов)
        * trends_callbacks.py (Модуль колбеков для страницы трендов)
        * trends_callbacks_detail.py (Модуль колбеков для страницы детализации)
    * assets/ (Ресурсы)

        * images/ (Иконки)
        * style.css (Стили)
    
    * layouts/ (Части макета приложения)
        * auth_layout.py
        * navbar.py
        * raiting_layout.py
        * trends_layout.py
        * trends_layout_detail.py
 
    * services/ (Части макета приложения)
    
        * create_data_trend.py
        * symptom_complexes_dao.py
        * symptom_complex_transform.py

    * app.py (Приложение)
    * config.py (Конфиг)
    * database.py (Конфиг базы данных)
    * endpoints.py (Ендпоинт для сохранения сиптомокомлексов)
    
* tests/ (Тесты, тестовые данные)
* Dockerfile
* pyproject.toml
* main.py (точка входа для сервиса)

## Как развернуть для разработки

Целевой платформой является linux, для развертывание контейнера на машине необходимо наличие актуальной версии docker-engine а также git.

Установка git
```
$ apt install git
```

Получить проект с репозитория git
```
$ git clone https://github.com/DieNice/disease-trend-system.git

$ cd disease-trend-system

$ git checkout dev
```

Сборка докер образа
```
$ docker build . --tag trend-system:latest
```

Запуск контейнера
```
$ docker run -d --rm -e HOSTNAME_DB=disease-trend-system_db_1 -e USERNAME_DB=developer -e PASSWORD_DB=dev_password -e NAME_DB=disease-trend -e SERCRET_KEY=super_secret_key -p 8050:8050 --name trend-system-container trend-system:latest
```

* В данной строке фигурируют следующие аргументы используемые для подключения к базе данных:
    * **HOSTNAME_DB** - ip адрес базы данных
    * **USERNAME_DB** - имя пользователя владеющего правами доступа к базе данных
    * **PASSWORD_DB** - пароль пользователя
    * **NAME_DB** - название базы данных
    * **SERCRET_KEY** - ключ шифрования
    * **8050:8050** - пара из внешнего и внутреннего порта используемых образом. Изменив внешний порт можно задать через какой порт будет осуществляться доступ к сервису.