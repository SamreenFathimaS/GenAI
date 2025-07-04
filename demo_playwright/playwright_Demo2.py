from playwright.sync_api import sync_playwright

# 1️⃣ Launch Playwright and open a browser
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
    page = browser.new_page()
    page.goto("https://www.google.com")

    # Fill the input with ID 'APjFqb'
    page.locator('//*[@id="APjFqb"]').fill("South Africa vs Australia score")
    page.locator('//*[@id="APjFqb"]').press("Enter")

    # 4️⃣ Wait for results
    page.wait_for_selector("text=South Africa")

    # 5️⃣ Scrape score box if exists
    try:
        score_box = page.query_selector("div[jsname='W297wb']")  # Google uses this for live scores
        score_text = score_box.inner_text() if score_box else "Score box not found!"
    except:
        score_text = "Could not find score box!"

    # 6️⃣ Get top news snippets
    news_results = page.query_selector_all("div.BNeawe.s3v9rd.AP7Wnd")  # Google news snippets CSS
    news_snippets = "\n".join([result.inner_text() for result in news_results])

    # 7️⃣ Combine all text
    full_text = f"=== South Africa vs Australia Score ===\n{score_text}\n\n=== Latest News ===\n{news_snippets}"

    # 8️⃣ Write to TXT file
    with open("sa_vs_aus_news.txt", "w", encoding="utf-8") as f:
        f.write(full_text)

    print("✅ Data saved to sa_vs_aus_news.txt")

    # 9️⃣ Done — close browser
    browser.close()
