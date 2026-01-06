"""Debug script to discover booking URL via UI interaction with retry."""

import asyncio
from playwright.async_api import async_playwright

async def main():
    print("Navigating to Movie Detail Page...")
    
    # Target: Shambhala in Hyderabad (try a fresh session)
    url = "https://in.bookmyshow.com/hyderabad/movies/shambhala/ET00454256"
    
    async with async_playwright() as p:
        # Use more human-like args
        browser = await p.firefox.launch(headless=True, args=["--kiosk"])
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
            locale="en-IN",
            timezone_id="Asia/Kolkata"
        )
        page = await context.new_page()
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Click Book Tickets
            try:
                book_btn = page.get_by_text("Book tickets", exact=False).first
                await book_btn.click()
                print("Clicked 'Book tickets'.")
            except:
                print("Button not found.")
                return

            await page.wait_for_timeout(3000)
            
            # Handle "Rated A" / Content Warning modal
            try:
                continue_btn = page.get_by_text("Continue", exact=True)
                if await continue_btn.count() > 0:
                    print("Found 'Continue' button. Clicking...")
                    await continue_btn.click()
                    await page.wait_for_timeout(2000)
            except: pass

            # Handle "Select Language/Format" modal if present
            # Look for 2D or Telugu if popup
            try:
               # Sometimes it's a list items
               format_opts = await page.locator("li:has-text('2D')").all()
               if format_opts:
                   print(f"Found {len(format_opts)} format options. Clicking first...")
                   await format_opts[0].click()
                   await page.wait_for_timeout(2000)
            except: pass

            print(f"URL after interaction: {page.url}")
            
            # If we hit the error page ("Oops! Something went wrong")
            # Try to click "Refresh page" button if it exists
            error_btn = page.get_by_text("Refresh page", exact=False)
            if await error_btn.count() > 0:
                print("Found Error Page. Clicking Refresh...")
                await error_btn.click()
                await page.wait_for_timeout(5000)
            
            # Take screenshot
            await page.screenshot(path="bms_booking_retry.png")
            
            # Check for Showtimes (Time Slots)
            # Usually distinct class names like .time, .showtime-pill
            shows = await page.locator("a[class*='showtime'], div[class*='showtime']").all()
            print(f"Found {len(shows)} showtime elements.")
            
            if shows:
                print("✅ Access to showtimes confirmed!")
            else:
                text = await page.inner_text("body")
                if "Something went wrong" in text:
                    print("❌ Still blocked.")
                else:
                    print("ℹ️ Page loaded but no showtimes found (maybe none for date?).")

        except Exception as e:
            print(f"Error: {e}")
            await page.screenshot(path="bms_error.png")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
