# Layer3 Wallet Checker

Этот скрипт проверяет кошельки на возможность получения дропа от Layer3. Он использует прокси и взаимодействует с API 2Captcha для решения reCAPTCHA.

![image](https://github.com/user-attachments/assets/e3a1d164-bbc3-4f27-9944-85049e9ed14b)

## Установка
```bash
git clone https://github.com/Marcelkoo/layer3-checker
cd layer3-checker
```

## Настройка

1. Заполните файл `wallets.txt` и добавьте евм адреса.
2. Заполните файл `proxies.txt` и добавьте ваши HTTP прокси формата (ip:port:login:password).
3. Откройте файл `main.py` и замените api_key:'222222' на ваш реальный API ключ от 2Captcha. Ключ от 2Captcha можете получить по ссылке: [https://2captcha.com/](https://2captcha.com/?from=6981114)

## Установка зависимостей

1. cd [путь]
2. pip install -r requirements.txt

## Подпишись

https://t.me/marcelkow_crypto
