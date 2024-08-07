[<img src="https://img.shields.io/badge/python-3.10%20%7C%203.11-blue">](https://www.python.org/downloads/)

![img1](.github/images/Preview.png)

## ⚙ [Настройки](https://github.com/OxFF00FF/Hamsters_mayhem/blob/master/.env.example)
| Настройка                    | Описание                                                                                      |
|------------------------------|-----------------------------------------------------------------------------------------------|
| **HAMSTER_TOKEN**            | Ваш Bearer токен из браузерной версии игры                                                    |
| **BOT_TOKEN**                | Токен вашего телеграм бота (необязательно). Нужен для того чтобы отправлять промокоды в вашу группу |
| **GROUP_ID**                 | Id вашей группы (необязательно). Можно узнать добавив бота `(t.me/GetMy1D_bot)` или аналог    |
| **GROUP_URL**                | Url вашей группы (необязательно). находится в `Управление группой -> пригласительные ссылки`  |

## Предварительные условия
Прежде чем начать, убедитесь, что у вас установлен Python версии 3.10 или 3.11:
- [Python 3.10](https://www.python.org/downloads/release/python-3100/)
- [Python 3.11](https://www.python.org/downloads/release/python-3110/)


## Быстрый старт windows
1. Скачайте zip архив и распакуйте в удобное место
2. либо если у вас установлен `git` откройте удобную для вас папку, нажмите `CTRL + L`, напишите `cmd` и нажмите `enter`
    у вас откроется консоль, встввьте туда команду `git clone https://github.com/OxFF00FF/Hamsters_mayhem.git` и нажмите enter.
    в эту папку скачается репозиторий.
3. Чтобы установить библиотеки, запустите `INSTALL.bat`.
4. Для запуска используйте `START.bat` (или в консоли: `python main.py`).





Как получить hamster Bearer token

1. зайдите в свой аккаунт через браузер по номеру или по коду.
![1](https://github.com/user-attachments/assets/0f307b70-b5fa-4479-9ffa-fe0cad537a9e)

2. зайдите в бота hamster kombat (https://t.me/hamster_kombat_bot).
   Нажмите старт и кнопку `играть в 1 клик` или `play`.
   у вас попросят разрешение открыть сайт, соглашаемся нажав на `congirm`
![2](https://github.com/user-attachments/assets/b95141ed-c44e-4853-ad2e-de47e463c18e)
![3](https://github.com/user-attachments/assets/5975d491-2b28-4b70-bf8f-1558ab3c8683)

4. у вас откроется игра с предложением открыть ее на телефоне.
   но нас это не нужно. Открываем инструменты разработчика. Для Chrome нажимаем `F12` или `CTRL + SHIFT + I` либо нажмите на `три точки -> дополнительные инструменты -> инструменты разработчика`
![4](https://github.com/user-attachments/assets/610bf810-6d66-4a35-ad08-a558275bf939)

5. В инструментах разработчика открываем вкладку `Elements` и нажимаем на кнопку справа со стрелочкой, наводим на qr код и нажимаем лкм
![123123123](https://github.com/user-attachments/assets/b01121d8-11f5-42a5-9ffd-2596bc855d2e)

6. У вас выберутся элементы и справа нужно найти элемент `iframe` 
![5](https://github.com/user-attachments/assets/b99f849a-568d-42c0-8de8-edf28adb4fa1)

7. Нажмите 2 раза лкм, и ссылка станет доступной для редактирования. Примерно в середине нужно найти `tgWebAppPlatform=weba`
![6](https://github.com/user-attachments/assets/7536093e-b1cf-4183-93e3-e31cba21e73b)

8. Нужно именить `tgWebAppPlatform=weba` на `tgWebAppPlatform=android` и нажать emter. 
   У вас откроется игра в браузере
![7](https://github.com/user-attachments/assets/c463489e-bd83-4ea9-8daa-6a81e960514e)

9. Длаее нажимаем на вкладку `Network` и в нем `All` и нажимаем на значек с перечерунутым кругом
![8](https://github.com/user-attachments/assets/320d8eb3-f3c2-4589-ad47-1445a6a4b50c)

10. У вас все очистится. и нужно сделать 1 тап в хомяке.
![9](https://github.com/user-attachments/assets/3592748b-5629-4e64-83e4-7cf88ef5d5b1)

11. через пару секунд у вас появится запрос. Нажимаем на него. у вас появится дополнительные сведения о запросе.
   Нужно нажать на `Headers` и внизу найти `Request headers`
![11](https://github.com/user-attachments/assets/aceb418e-87c5-4746-b515-29cfa0bff660)

13. Прокручиваем вниз и тут слева есть `Authorization` а справа нужное нам значение. Это и есть токен.
    Нужно скопировать его полностью от Bearer до последней цифры
![12](https://github.com/user-attachments/assets/a68c821c-ebe1-4829-8897-29ca5908fdff)

14. этот токен нужно будет поставить в .env файле в HAMSTER_TOKEN между кавычек
    
   `HAMSTER_TOKEN="ваш токен из 13 пункта"`
