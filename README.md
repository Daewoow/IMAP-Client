# **IMAP Client**

IMAP-клиент - приложение, которое позволяет Вам просматривать письма со своей почты, для чего как раз-таки и используется
протокол IMAP, а также сохранять вложения. Взаимодействие с почтовым сервисом происходит по протоколу SSL.

## Зависимости
Для начала Вам стоит установить все зависимости с помощью
```angular2html
pip install requirements.txt
```

Далее запустить программу с помощью
```angular2html
python imap_client.py
```

## Вход
Вам будет предложено
* ввести сервер imap (imap.mail.ru, например).
* Далее - порт: 993.
* Дальше следует авторизовтаься. Однако обычный пароль здесь не подойдёт. Нужно на сервисе нужной почты создать **пароль для 
внешних приложений** (об этом можно почитать в Интернете, но для mail.ru вот: https://account.mail.ru/user/2-step-auth/passwords?back_url=https%3A%2F%2Fid.mail.ru%2Fsecurity) и ввести именно его.

## Возможности
Далее Вам будет доступно:
* просмотр всех папок,
* чтение всех писем (с загрузкой вложений в эту папку),
* отправка писем другому пользователю данной почты
* удаление писем

## Структура
* imap_client.py - файл для запуска клиента
* registerGUI.py - файл с окном регистрации
* mainClientGUI.py - файл с основным окном почты
* connectedClient.py - файл, описывающий взаимодействия на стороне сервера
* utils.py - файл с полезными утилитами
* coded_folders.pkl - файл для хранения закодированных папок
