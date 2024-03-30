# NFTSolana-Notification
This bot will give you notification every transaction NFT on your Solana network

### Requirements
1. Python 3.5xx
2. requests
3. json
4. mysql-connector
5. flask
6. Token API Telegram Bot
7. Token API Helius

### Installation
1. Download manually <a href="https://github.com/setiaone-tech/NFTSolana-Notification/archive/refs/heads/main.zip">here</a> or clone this repository
2. Upload all files on your hosting.
   <br>**note : hosting must be support python**
3. Install all requirements
   <br>=> pip install requirements.txt
4. Edit configuration on main.py
   <br>**note : token api telegram bot, token api helius, database configuration, domain website**
5. Running set_webhook.py for configure your bot to receive all commands from webhook
   <br>=> python set_webhook.py or python3 set_webhook.py
6. Running main program.
   <br>=>python main.py or python3 main.py

### How to Use
1. After complete all installation u type on your telegram bot.
   <br>=> /start
2. Telegram bot will give u option to add, edit, delete Solana Wallet
3. If you're done, telegram bot will give you notification every all transcation NFT on your Solana Wallet.
