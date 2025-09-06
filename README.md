# WhatsApp Auto Reply Bot 🤖💬

A Python project that uses Selenium WebDriver to automate WhatsApp Web.  
The bot detects incoming messages from a specific contact and replies automatically with customizable responses.

## 🚀 Features
- Auto-detects new messages.
- Sends random or custom replies.
- Simulates human-like typing delay.
- Works in headless or normal Chrome mode.
- Avoids repeated replies (tracks processed messages).

## 📦 Requirements
- Python 3.8+
- Google Chrome
- [ChromeDriver](https://chromedriver.chromium.org/downloads) 
- Selenium library (`pip install selenium`)

## ⚙️ Installation
```bash
git clone https://github.com/<your-username>/whatsapp-auto-reply-bot.git
cd whatsapp-auto-reply-bot
pip install -r requirements.txt
