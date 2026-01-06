"""Run scrapers to populate data."""

import asyncio
from app.scrapers.bookmyshow import BookMyShowScraper

async def main():
    print("=" * 60)
    print("🎬 Bo_Check: Live Data Scraper")
    print("=" * 60)
    
    scraper = BookMyShowScraper()
    
    cities = ["HYD"]
    
    try:
        for city in cities:
            print(f"\n📍 Fetching movies for {city}...")
            print("-" * 40)
            
            movies = await scraper.get_movies(city)
            
            if movies:
                print(f"✅ Successfully scraped {len(movies)} movies!\n")
                
                # Use default popularity order (likely better for finding running movies)
                sorted_movies = movies
                
                # Loop through top 5 movies to fetch shows
                print("\n🎟️ Fetching shows for top 5 movies (this involves navigating to booking pages)...")
                print("=" * 60)
                
                for i, movie in enumerate(sorted_movies[:5], 1):
                    print(f"\n[{i}/5] Fetching shows for: {movie.name} ({movie.external_id})")
                    shows = await scraper.get_shows(city, movie.external_id)
                    
                    if shows:
                        total_shows = len(shows)
                        theaters = set(s.theater_name for s in shows)
                        available_shows = sum(1 for s in shows if s.seat_categories and s.seat_categories[0].available_seats > 0)
                        
                        print(f"   ✅ Found {total_shows} shows in {len(theaters)} theaters")
                        print(f"   🎫 Available: {available_shows} | Sold Out: {total_shows - available_shows}")
                        
                        # Sample theater
                        if theaters:
                            print(f"   📍 Example Theater: {list(theaters)[0]}")
                    else:
                        print("   ⚠️ No shows found or booking button not accessible.")
                        
                if len(movies) > 10:
                    print(f"\n... and {len(movies) - 10} more movies in list.")
            else:
                print("⚠️  No movies found (check network/blocking).")
                
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
    
    finally:
        await scraper.close()
    
    print("\n" + "=" * 60)
    print("Scraping Job Complete")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
