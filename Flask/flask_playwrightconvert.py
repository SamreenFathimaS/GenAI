from flask import Flask, jsonify
import asyncio
from playwright.async_api import async_playwright

app = Flask(__name__)

async def playwright_function():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://www.google.com")
        await page.wait_for_timeout(10000)  # 10 sec
        await browser.close()
        return "✅ Playwright done!"

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "✅ Flask is running. Use /search to run async Playwright."})

@app.route("/search", methods=["GET"])
def run_playwright():
    result = asyncio.run(playwright_function())
    return jsonify({"message": result})

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
