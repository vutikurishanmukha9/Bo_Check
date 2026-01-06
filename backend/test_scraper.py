"""BookMyShow scraper v2: URL discovery."""

import asyncio
from playwright.async_api import async_playwright

async def run():
    print("=" * 60)
    print("BMS Scraper URL Test")
    print("=" * 60)
    
    cities = ["hyderabad", "mumbai"]
    
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
            viewport={"width": 1920, "height": 1080}
        )
        
        for city in cities:
            page = await context.new_page()
            
            # Try new URL structure
            url = f"https://in.bookmyshow.com/explore/movies-{city}"
            print(f"\n📍 Trying: {url}")
            
            try:
                response = await page.goto(url, wait_until="domcontentloaded")
                print(f"   Status: {response.status}")
                
                if response.status == 200:
                    await page.wait_for_timeout(3000)
                    title = await page.title()
                    print(f"   Title: {title}")
                    
                    # Check for movie cards
                    cards = await page.locator("div[class*='MovieCard']").all()
                    if not cards:
                         cards = await page.locator("a[href*='/movies/']").all()
                    
                    if cards:
                        print(f"   ✅ Found {len(cards)} movie cards!")
                        # Print first few
                        for card in cards[:3]:
                            txt = await card.inner_text()
                            print(f"      - {txt.splitlines()[0]}")
                    else:
                        print("   ⚠️ No cards found (might be dynamic loading)")
                        await page.screenshot(path=f"bms_{city}_debug.png")
                else:
                    print("   ❌ Failed to load")
                    
            except Exception as e:
                print(f"   Error: {e}")
            
            await page.close()
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
