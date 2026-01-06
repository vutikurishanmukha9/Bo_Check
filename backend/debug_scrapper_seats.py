
import asyncio
from playwright.async_api import async_playwright

async def main():
    print("🕵️ Debugging Seat Layout Scraping...")
    
    # We need a URL for a specific movie's booking page involved in the flow
    # or we navigate from a listing.
    # Let's try navigating from the Hyderabad listing to find ANY movie with shows.
    
    city_url = "https://in.bookmyshow.com/explore/movies-hyderabad"
    
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True) # Consistent with working scraper
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
            locale="en-US"
        )
        page = await context.new_page()
        
        try:
            print(f"Navigating to {city_url}")
            await page.goto(city_url, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            await page.mouse.wheel(0, 3000)
            await page.wait_for_timeout(2000)
            
            # Click the first movie card that looks like it's released (not "Coming Soon")
            # We'll just try the first few links
            movie_links = await page.locator("a[href*='/movies/']").all()
            
            target_movie_url = None
            
            for link in movie_links[:5]:
                href = await link.get_attribute("href")
                if "buytickets" in href: # Direct booking link? Rare from listing
                    pass 
                
                # Check if it has a rating (implies released)
                text = await link.inner_text()
                if "%" in text or "/10" in text or "Votes" in text:
                    target_movie_url = href
                    print(f"Found candidate movie: {text.splitlines()[0]}")
                    break
            
            if not target_movie_url:
                print("No obvious released movie found. Pick a specific one if known. Trying first one anyway.")
                if movie_links:
                    target_movie_url = await movie_links[0].get_attribute("href")

            if not target_movie_url:
                print("No movie links found.")
                return

            if target_movie_url.startswith("http"):
                full_url = target_movie_url
            else:
                full_url = f"https://in.bookmyshow.com{target_movie_url}"
                
            print(f"Going to Movie: {full_url}")
            await page.goto(full_url, wait_until="domcontentloaded")
            
            # Click Book Tickets
            try:
                await page.click("text=Book tickets", timeout=5000)
                print("Clicked 'Book tickets'")
            except:
                print("Book tickets button not found. Maybe not released.")
                return

            # Handle Modals
            await page.wait_for_timeout(2000)
            try:
                # Format selection
                if await page.locator("ul#format-list").count() > 0:
                   await page.locator("ul#format-list li").first.click()
            except: pass

            try:
                # Language selection
                 if await page.locator(".lang-select").count() > 0:
                   await page.locator(".lang-select li").first.click()
            except: pass
            
            # Now on booking page. Wait for showtimes.
            try:
                await page.wait_for_selector(".showtime-pill", timeout=10000)
                print("Showtimes loaded.")
            except:
                print("No showtimes found.")
                return
                
            # Click the first available showtime
            # GREEN showtimes usually avail
            showtimes = await page.locator(".showtime-pill").all()
            target_show = None
            for show in showtimes:
                classes = await show.get_attribute("class") or ""
                if "sold" not in classes.lower():
                    target_show = show
                    break
            
            if not target_show:
                print("No available shows found (all sold out?).")
                return
                
            print(f"Clicking showtime: {await target_show.inner_text()}")
            await target_show.click()
            
            # Handle "Accept Terms" / "How many seats" popup
            await page.wait_for_timeout(2000)
            
            # Seat quantity selection popup (1, 2, 3...)
            try:
                qty_selector = page.locator("#qty-selector, ul#pop_qty")
                if await qty_selector.count() > 0:
                    print("Selecting 1 seat...")
                    await page.click("li#pop_1") # Click '1'
                    await page.click("text=Select Seats")
            except: 
                print("No quantity selector found (maybe direct entry?)")

            # Now we should be on SEAT LAYOUT
            print("Waiting for Seat Layout...")
            await page.wait_for_selector(".seat-layout, table.seat-table, .seat-container", timeout=15000)
            
            # CAPTURE SEAT DATA
            print("📸 Taking screenshot of seat layout...")
            await page.screenshot(path="bms_seat_layout_debug.png")
            
            # Analyze DOM for seats
            # Common BMS classes: ._available, ._blocked, ._sold, .seat
            # Or: a.seat
            
            seats = await page.locator(".seat-layout .seat, .seat-layout td div a").all()
            print(f"Found {len(seats)} total seat elements.")
            
            available_count = 0
            blocked_count = 0
            booked_count = 0
            
            for seat in seats:
                classes = await seat.get_attribute("class") or ""
                classes = classes.lower()
                
                if "_available" in classes:
                    available_count += 1
                elif "_blocked" in classes or "_sold" in classes:
                    booked_count += 1
                else:
                    # Maybe "gap" or aisle
                    pass
            
            print(f"📊 Layout Analysis:")
            print(f"   Total Seats Found: {len(seats)}")
            print(f"   Available: {available_count}")
            print(f"   Booked/Sold: {booked_count}")
            print(f"   Approx Booked: {booked_count} / {available_count + booked_count}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="bms_debug_error.png")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
