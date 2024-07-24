import aiohttp
import asyncio
import logging
import aiofiles
from beautifultable import BeautifulTable
import random
import json

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

api_key = '222222'  # API ключ от 2Captcha
site_key = '6Lf9mRcqAAAAAOklG4xckZVUNdBaWW6sJ5WD5TsP'  # НЕ ТРОГАЕМ
page_url = 'https://eligibility.layer3foundation.org/'  # НЕ ТРОГАЕМ

async def load_proxies(filename):
    proxies = []
    async with aiofiles.open(filename, mode='r') as f:
        async for line in f:
            proxies.append(line.strip())
    return proxies

async def load_wallets(filename):
    wallets = []
    async with aiofiles.open(filename, mode='r') as f:
        async for line in f:
            wallets.append(line.strip())
    return wallets

async def solve_recaptcha(site_key, page_url, api_key):
    async with aiohttp.ClientSession() as client:
        try:
            response = await client.post(
                'http://2captcha.com/in.php',
                params={
                    'key': api_key,
                    'method': 'userrecaptcha',
                    'googlekey': site_key,
                    'pageurl': page_url,
                    'json': 1
                }
            )
            response_json = await response.json()
            request_id = response_json.get('request')
            if request_id is None:
                logging.error(f"Ошибка при отправке запроса к 2Captcha: {response_json}")
                return None

            while True:
                await asyncio.sleep(5)  
                response = await client.get(
                    'http://2captcha.com/res.php',
                    params={
                        'key': api_key,
                        'action': 'get',
                        'id': request_id,
                        'json': 1
                    }
                )
                result = await response.json()
                if result.get('status') == 1:
                    logging.info(f"reCAPTCHA решена")
                    return result['request']
                elif result.get('status') == 0:
                    logging.debug("Решение капчи еще не готово, повторная попытка...")
                else:
                    logging.error(f"Ошибка при решении reCAPTCHA: {result}")
                    return None
        except Exception as e:
            logging.error(f"Ошибка при решении reCAPTCHA: {e}")
            return None

def parse_allocation(allocation):
    if allocation == "0":
        return 0
    return int(allocation) // 10**18

async def perform_get_request(session, wallet_address, proxies, results, max_retries=3):
    recaptcha_token = await solve_recaptcha(site_key, page_url, api_key)
    if recaptcha_token:
        url = f"https://8zr8yl9lzb.execute-api.eu-central-1.amazonaws.com//eligibility"
        params = {
            'address': wallet_address,
            'recaptchaToken': recaptcha_token
        }
        
        retries = 0
        while retries < max_retries:
            proxy = random.choice(proxies) 
            proxy_parts = proxy.split(':')
            proxy_url = f"http://{proxy_parts[2]}:{proxy_parts[3]}@{proxy_parts[0]}:{proxy_parts[1]}"
            
            logging.debug(f"Отправка GET запроса с прокси: {proxy_url}")
            try:
                async with session.get(url, params=params, proxy=proxy_url) as response:
                    text = await response.text()
                    try:
                        data = await response.json()
                        allocation = parse_allocation(data.get('allocation', '0'))
                        results.append({'wallet': wallet_address, 'allocation': allocation})
                        logging.info(f"{wallet_address} - {allocation}")
                        return
                    except aiohttp.ContentTypeError:
                        logging.error(f"Unexpected content type: {response.headers.get('Content-Type', '')}")
                        logging.debug(f"{wallet_address} - {text}")
                        data = json.loads(text)
                        allocation = parse_allocation(data.get('allocation', '0'))
                        results.append({'wallet': wallet_address, 'allocation': allocation})
                        logging.info(f"{wallet_address} - {allocation}")
                        return
            except Exception as e:
                logging.error(f"Ошибка выполнения запроса с прокси {proxy}: {e}")
                retries += 1
        
        logging.error(f"Не удалось выполнить запрос для {wallet_address} после {max_retries} попыток")
    else:
        logging.error("Не удалось получить токен reCAPTCHA")

async def main():
    proxies = await load_proxies('proxy.txt')
    wallets = await load_wallets('wallets.txt')
    results = []

    async with aiohttp.ClientSession() as session:
        tasks = []
        for wallet in wallets:
            tasks.append(perform_get_request(session, wallet, proxies, results))
        await asyncio.gather(*tasks)
    
    table = BeautifulTable()
    table.columns.header = ["Wallet", "Allocation"]
    for result in results:
        table.rows.append([result['wallet'], result['allocation']])
    print(table)

if __name__ == "__main__":
    asyncio.run(main())
