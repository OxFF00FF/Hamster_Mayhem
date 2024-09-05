[<img src="https://img.shields.io/badge/python-3.10%20%7C%203.11-blue">](https://www.python.org/downloads/)
[<img src="https://img.shields.io/badge/Telegram-@me-blue">](https://t.me/OxFF00FF)
[<img src="https://img.shields.io/badge/Group-Hamster_Mayhem-blue">](https://t.me/+SUekzTWJlq8yNzIy)


![1](https://github.com/user-attachments/assets/bc847b2b-721c-42f4-b78d-dd6872c5b865)
> 🇷🇺 README на русском доступен [здесь](https://github.com/OxFF00FF/Hamster_Mayhem/blob/master/README_ru.md)
 
The project was created to help people pass promotional games in the [Hamster Kombat](https://t.me/hamsTer_kombat_bot/start?startapp=kentId1476571560).

🔔  For those wishing to support the project, payment methods are available:  🔔

- 💎  USDT TON (TON): `UQCjwbMX96YhA4POYlbE3v0M7Xx9TlvjX7bqnJIj0KFVfYlR`

- 💎  USDT TRC20 (Tron): `TK7v5F2HFEErUCFVmy4z53bwdwvZWNNzkz`

- 💎  Toncoin (TON): `UQCjwbMX96YhA4POYlbE3v0M7Xx9TlvjX7bqnJIj0KFVfYlR`

- 💎  Bitcoin (BTC): `188BPS54Pkjaa8uZ8CDdZegBwWP1iwxdrG`

- 💎  Notcoin (NOT): `UQCjwbMX96YhA4POYlbE3v0M7Xx9TlvjX7bqnJIj0KFVfYlR`

- 💎  [Boosty](https://boosty.to/oxff00ff)

- 💎  [Donationalerts](https://www.donationalerts.com/r/oxff00ff)

- 💎 [Paypal]()


## Updates
 -  (03.09) Added interface translation into English. To change the language you need to select item 4 in the settings and restart

 -  (01.09) В главном меню теперь есть настройки (s)
   
 - To make sure you won't be so bored waiting for promo codes to be generated, the ability to change the loading indicator has been added 😉

    The `spinner_<num>` command selects an indicator (example `spinner_1`)

   The `list` command, shows all available name options and the number to be specified in `spinner_<num>`.

   The `default` command, will set the default indicator


 - We made a telegram bot to generate keys:

   🌐  https://t.me/Hamster_Mayhem_bot

   In the future, the plan is to make activating promo codes and using all available activities in hamster from the bot.
   Now only generation of promo codes and information about combos and cipher is available.

## Features
- Switching between multiple accounts
- All games added
- Can be launched from your Android smartphone
- Generate promo codes for all available games
- Generate for all games at once (1-2 at a time recommended)
- Send generated promo codes to your group or any chat via bot
- Ability to automatically apply promo codes in your account after generation
- The list of the most profitable cards to buy, which is updated as the cards improve (only those you can buy will be on the list).
- Passing the minigame with candles
- Performing combos and buying individual cards
- Completing the daily cipher
- Completing tasks (watching videos and daily tasks)
- Performing clicks and using boosts
- Displaying the remaining time for all activities

To use multiple accounts you need to specify multiple tokens in the `.env` file.
The format is `HAMSTER_TOKEN_x`. For example `HAMSTER_TOKEN_1`, `HAMSTER_TOKEN_2`, etc.
The default is `HAMSTER_TOKEN_1` if no others are specified.
To switch to another account, select `a` in the menu and the account number.

## ⚙ [Settings](https://github.com/OxFF00FF/Hamsters_mayhem/blob/master/.env.example)
| Настройка                    | Описание                                                                                      |
|------------------------------|-----------------------------------------------------------------------------------------------
| **HAMSTER_TOKEN**            | Your `Bearer` token from the browser version of the game                                                  
| **TELEGRAM_BOT_TOKEN**       | Token of your Telegram bot (optional). You need it to send promo codes to your group or any other chat room
| **GROUP_ID**                 | ID of your group, channel or user (optional). You can find out by adding a bot `(t.me/GetMy1D_bot)` or analog in chat. To allow the bot to send messages you need to add it to a group or channel, if in private messages you need to send the command `/start`.
| **GROUP_URL**                | Url of your group (optional). It can be found in `Group management -> Invitation links`. If specified, the console will be notified to which group he sent the message to

## Prerequisites
Make sure you have Python version 3.10 or 3.11 installed (be sure to check the `add python to PATH` box when installing):
- [Python 3.10](https://www.python.org/downloads/release/python-3100/)
- [Python 3.11](https://www.python.org/downloads/release/python-3110/)


## Windows Quick Start
1. Download the zip archive and unzip to a convenient location
2. If you have `git` installed, open a convenient folder, press `CTRL + L`, type `cmd` and press `enter`.
    a console will open, type the command and press enter. The project will be downloaded to this folder.
>`git clone https://github.com/OxFF00FF/Hamster_Mayhem.git`

3. To install dependencies, run the `INSTALL.bat` file.
4. Use the `1. START.bat` file to start. If **Windows Terminal** is installed, then `2. START_WT.bat`.
5. Customize the `.env` file. Specify your `HAMSTER_TOKEN` and other values if necessary.
6. Use the `UPDATE.bat` file to upgrade (if [git](https://git-scm.com/downloads) is installed)

In a regular windows cmd terminal you most likely won't have colors in the console and emoji working.
For a beautiful display, install 
[windows terminal](https://apps.microsoft.com/detail/9n0dx20hk701?hl=en-US&gl=US) или из папки `Windows Terminal setup`



## How to get the hamster Bearer token

>1. Access your account through your browser by number or code.

![1](https://github.com/user-attachments/assets/0f307b70-b5fa-4479-9ffa-fe0cad537a9e)

>2. Go to [hamster kombat bot](https://t.me/hamsTer_kombat_bot/start?startapp=kentId1476571560).
    Click start and the `play in 1 click` or `play` button.
    You will be asked for permission to open the site, agree by clicking on `confirm`

![2](https://github.com/user-attachments/assets/b95141ed-c44e-4853-ad2e-de47e463c18e)
![3](https://github.com/user-attachments/assets/5975d491-2b28-4b70-bf8f-1558ab3c8683)

>4. You'll be prompted to open the game on your phone.
    but we don't need that. Let's open the developer tools.
    For Chrome, press `F12` or `CTRL + SHIFT + I`.
    or click on `three dots -> advanced tools -> developer tools`.

![4](https://github.com/user-attachments/assets/610bf810-6d66-4a35-ad08-a558275bf939)

>5. In the developer tools, open the `Elements` tab.
    and click on the button on the right with the arrow, point to the qr code and press the left mouse button.

![123123123](https://github.com/user-attachments/assets/b01121d8-11f5-42a5-9ffd-2596bc855d2e)

>6. You will have the elements open and on the right side you need to find the `iframe` element 

![5](https://github.com/user-attachments/assets/b99f849a-568d-42c0-8de8-edf28adb4fa1)

>7. Click 2 times on the lcm and the link will become editable.
    About in the middle you need to find `tgWebAppPlatform=weba`.

![6](https://github.com/user-attachments/assets/7536093e-b1cf-4183-93e3-e31cba21e73b)

>8. You need to change `tgWebAppPlatform=weba` to `tgWebAppPlatform=android` and hit emter. 
    This will open the game in your browser

![7](https://github.com/user-attachments/assets/c463489e-bd83-4ea9-8daa-6a81e960514e)

>9. Click on the `Network` tab and in it `All` and click on the icon with a crossed-out circle.

![8](https://github.com/user-attachments/assets/320d8eb3-f3c2-4589-ad47-1445a6a4b50c)

>10. You'll have everything cleared out. and you need to do 1 tap in the hamster.

![9](https://github.com/user-attachments/assets/3592748b-5629-4e64-83e4-7cf88ef5d5b1)

>11. After a couple seconds, you will be prompted. Click on it. 
    Additional information about the request will appear.
    Click on `Headers` and at the bottom find `Request headers` (make sure that the **Request Method** of the request is **POST**).

![11](https://github.com/user-attachments/assets/aceb418e-87c5-4746-b515-29cfa0bff660)

12. Scroll down and there is `Authorization` on the left and the value we need on the right. 
    This is the token. We need to copy it all the way from Bearer to the last digit

![12](https://github.com/user-attachments/assets/a68c821c-ebe1-4829-8897-29ca5908fdff)

>13. This token will need to be put in the `.env` file in `HAMSTER_TOKEN` between the quotes, in **one line without line break**.


Example:
>`HAMSTER_TOKEN_1="Bearer 2367343478565fuiGOLjkhegyWEkjeruGFjEkjueowhefiwehggergerUTquvnmpoifehkFwugnjle6732593756"`


# How to run code on android

1. Download [Termux](https://trashbox.ru/files30/1963775/termux-app_v0.118.1github-debug_universal.apk/) and enter the commands
2. `pkg update && pkg install git` Accept the installation (y)
3. `pkg install python` Accept the installation (y)
4. `git clone https://github.com/OxFF00FF/Hamster_Mayhem.git`
5. `cd Hamster_mayhem`
6. `cp .env.example .env`
7. `nano .env`. Specify your token in HAMSTER_TOKEN and other values if necessary
8. Press the `CTRL` button and on the keyboard the English `X` then `Y` and `enter` to save the file
9. Check that the data has been written `cat .env` (outputs the contents of the .env file)
10. Dependency installation `pip install -r requirements.txt` 
11. If there are any errors during installation `pip install python-dotenv requests beautifulsoup4 fuzzywuzzy fake-useragent spinners`
12. Or individually:
- `pip install python-dotenv`
- `pip install requests`
- `pip install beautifulsoup4`
- `pip install fuzzywuzzy`
- `pip install fake-useragent`
- `pip install spinners`
13. Run `python main.py`
14. To update the code use the commands `git pull` and `python main.py`
15. If you have the root folder open when you open Termux `~ $`.
You will need to go to the `cd Hamsters_mayhem` project folder and run `python main.py`

### Video instruction
https://github.com/user-attachments/assets/cadbd13e-e932-4e30-9cec-e7a231d4a748


