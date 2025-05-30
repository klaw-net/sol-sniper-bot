import requests
import time
import telegram
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = telegram.Bot(token=BOT_TOKEN)
seen_tokens = set()

def check_new_tokens():
    url = "https://api.dexscreener.com/latest/dex/pairs/solana"
    try:
        response = requests.get(url)
        data = response.json()
        pairs = data.get("pairs", [])

        for pair in pairs[:10]:
            token_address = pair["baseToken"]["address"]
            if token_address in seen_tokens:
                continue

            seen_tokens.add(token_address)

            solscan_url = f"https://public-api.solscan.io/token/meta?tokenAddress={token_address}"
            meta = requests.get(solscan_url).json()

            mint_auth = meta.get("mintAuthority")
            freeze_auth = meta.get("freezeAuthority")

            burned = '✅' if not mint_auth else '❌'
            renounced = '✅' if not freeze_auth else '❌'

            name = pair["baseToken"]["name"]
            symbol = pair["baseToken"]["symbol"]
            mc = pair.get("fdv", "N/A")
            liq = pair.get("liquidity", {}).get("usd", "N/A")

            msg = f"""🆕 New Token Alert on Solana

Name: {name}
Symbol: ${symbol}
Burned: {burned}
Renounced: {renounced}

💰 Marketcap: ${int(mc):,}
💧 Liquidity: ${int(liq):,}

🔗 [DexScreener]({pair['url']})
🔗 [SolScan](https://solscan.io/token/{token_address})
🔗 [BirdEye](https://birdeye.so/token/{token_address}?chain=solana)
"""
            bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")
            time.sleep(1)

    except Exception as e:
        print(f"Error: {e}")

while True:
    check_new_tokens()
    time.sleep(60)
