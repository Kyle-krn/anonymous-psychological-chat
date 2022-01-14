# Анонимный чат психологической помощи
---
Бот работающий на вебхуках предоставляет возможность анонимного чата с рандомными собеседниками из противоположной категории.

В боте реализовано
* Выбор между 2умя категориями (Те кто хочет помочь и те кто нуждается в помощи)

![Alt Text](https://s10.gifyu.com/images/categorya5ce0b881bc4618a.gif)
* Верификация дипломированных специалистов 
![Alt Text](https://s10.gifyu.com/images/ver.gif)
* Чат со случайным пользователем из противоположной категории
![Alt Text](https://s10.gifyu.com/images/start_dialog2036ab2d12441e14.gif)
* Начать платную консультацию
![Alt Text](https://s10.gifyu.com/images/start_premium_chat.gif)
* Отдельный рейтинг и отзывы для платных консультаций
![Alt Text](https://s10.gifyu.com/images/premium_rating.gif)
* Рейтинг пользователей и жалобы
![Alt Text](https://s10.gifyu.com/images/ratingg.gif)
* Возможность добавлять психолога в избранные чаты и связываться с ним на прямую через бота
![Alt Text](https://s10.gifyu.com/images/favorit.gif)
* Пополнение баланса и история счёта 
![Alt Text](https://s10.gifyu.com/images/get_money.gif)




В админке бота реализовано
* Поиск и сортировка юзеров
![Alt Text](https://s10.gifyu.com/images/searchfdfb5f3fc294da5e.gif) 
* Возможность отправлять персонализированное сообщение определенному пользователю
![Alt Text](https://s10.gifyu.com/images/message83aa9bfdd9c4740c.gif)
* Подвтреждение/отклонение верификации 
![Alt Text](https://s10.gifyu.com/images/verfee2783c7b474deb.gif)
* Блокировка/разблокировка пользователей
![Alt Text](https://s10.gifyu.com/images/block.gif) 
* Жалобы на пользователей
![Alt Text](https://s10.gifyu.com/images/complaint.gif) 
* История пополнений и запросы на вывод денег (Перевод денег осущеставляется в ручную)
![Alt Text](https://s10.gifyu.com/images/mone.gif) 
* Статистика каждого пользователя
  * Дата и время первого запуска ботапоследнего действия
  * Общее время использования бота
  * Среднее времяВсего времени проведенного в диалогах с другими пользователями
  * Количество диалогов
  * Количество диалогов заверешнных пользователем Количество диалогов завершенных собеседниками
  * Среднее/Общее количество сообщений написанных собеседнику
* Массовая рассылка сообщений с возможность прикрепить изображение
![Alt Text](https://s10.gifyu.com/images/mass60ba6b62ec6efc8d.gif)

# Установка
---
1. Клонируйте репозиторий с github
2. Создайте виртуальное окружение
3. Установите зависимости `pip install -r requarements.txt`
4. Измените название файла `settings.py.example`, убрав из него `.example` и впишите в него собственные ключи от телеграм бота, QIWI токены и ссылку на MongoDB, а так же в параметре HOST указать IP вашего сервера
5. Для работы через webhook неободимо создать SSL сертификат
   1. Перейдите в корневую папку проекта
   2. Выполните команды
   ```
   openssl genrsa -out webhook_pkey.pem 2048
   openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
   ```
   3. В строке common name введите IP адрес сервера
6. Запустите бота командой `python3 main_bot.py`

Если что-то пошло не так, проверьте открыт ли порт 8443, по возможности откройте его или поменяйте настройки порта в файле `webhhok_settings.py` в переменной `WEBHOOK_PORT`.
Так же на некоторых серверах необходимо в переменной `WEBHOOK_LISTEN` указать IP адрес сервера.

# Фоновый запуск
---
Для нового запуска бота на сервере можно использовать конфигурацию для supervisord
```
[program:anon_chat]
command=PATH/venv/bin/python main_bot.py
directory=PATH/
autostart=true
autorestart=true
redirect_stderr=true
```

# Пример ботв
---
https://t.me/Veleshelpbot
