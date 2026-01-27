import re
import asyncio
import os
import pandas as pd
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

class BookingScraper:
    def __init__(self, records_dir="app/records"):
        self.records_dir = records_dir
        if not os.path.exists(self.records_dir):
            os.makedirs(self.records_dir)
        self.hotels_data = []

    async def run(self, limit=10):
        # Enforce limits
        limit = max(10, min(100, int(limit)))
        print(f"Starting scrape for {limit} records...")
        
        async with async_playwright() as p:
            # Headless must be True for server hosting (Vercel, Docker, etc.)
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            # Construct URL with dates (Tomorrow -> +1 day) to ensure prices are shown
            tomorrow = datetime.now() + timedelta(days=1)
            next_day = tomorrow + timedelta(days=1)
            checkin = tomorrow.strftime("%Y-%m-%d")
            checkout = next_day.strftime("%Y-%m-%d")
            
            # Base URL for New York search
            url = (
                f"https://www.booking.com/searchresults.en-gb.html?"
                f"ss=New+York&checkin={checkin}&checkout={checkout}"
                f"&group_adults=2&no_rooms=1&group_children=0"
            )
            
            print(f"Navigating to: {url}")
            await page.goto(url, timeout=60000)
            
            # Handle common popups
            try:
                await page.get_by_label("Dismiss sign in information.").click(timeout=2000)
            except: pass
            
            try:
                await page.locator("button#onetrust-accept-btn-handler").click(timeout=2000)
            except: pass

            self.hotels_data = []
            
            while len(self.hotels_data) < limit:
                # Wait for cards to load
                try:
                    await page.wait_for_selector('[data-testid="property-card"]', timeout=10000)
                except:
                    print("No property cards found.")
                    break
                
                cards = await page.locator('[data-testid="property-card"]').all()
                print(f"Found {len(cards)} cards on this page.")
                
                for card in cards:
                    if len(self.hotels_data) >= limit:
                        break
                        
                    # Extract Data from Card
                    try:
                        # Name
                        name = await card.locator('[data-testid="title"]').first.inner_text()
                    except:
                        name = "N/A"
                        
                    try:
                        # Price
                        price = await card.locator('[data-testid="price-and-discounted-price"]').first.inner_text()
                    except:
                        try:
                            # Fallback
                            price = await card.locator('.bui-price-display__value').first.inner_text()
                        except:
                            price = "0"
                            
                    try:
                        # Location / Address
                        address = await card.locator('[data-testid="address"]').first.inner_text()
                    except:
                        address = "New York" # Fallback since we searched for NY
                        
                    try:
                        # Rating
                        rating = await card.locator('[data-testid="review-score"]').first.inner_text()
                        # Clean rating text (e.g., "8.5\nVery Good\n1,200 reviews")
                        rating = rating.replace("\n", " ")
                    except:
                        rating = "N/A"
                        
                    try:
                        # Stars
                        stars_count = await card.locator('[data-testid="rating-stars"] span').count()
                        if stars_count == 0:
                            stars_count = await card.locator('[data-testid="rating-squares"] span').count()
                        stars = f"{stars_count} stars" if stars_count > 0 else "N/A"
                    except:
                        stars = "N/A"

                    self.hotels_data.append({
                        "HotelName": name.strip(),
                        "Location": address.strip(),
                        "Price": price.strip(),
                        "Rating": rating.strip(),
                        "Stars": stars,
                        "City": "New York"
                    })
                    
                print(f"Collected {len(self.hotels_data)}/{limit} hotels...")
                
                if len(self.hotels_data) < limit:
                    # Pagination
                    try:
                        next_button = page.locator('button[aria-label="Next page"]')
                        if await next_button.is_visible():
                            await next_button.click()
                            await page.wait_for_timeout(3000) # Wait for page load
                        else:
                            print("No next page button found.")
                            break
                    except Exception as e:
                        print(f"Pagination error: {e}")
                        break
            
            await browser.close()
            
        # Save to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"hotels_{limit}_{timestamp}.csv"
        filepath = os.path.join(self.records_dir, filename)
        
        df = pd.DataFrame(self.hotels_data)
        
        # Ensure columns exist
        required_cols = ["HotelName", "Location", "Price", "Rating", "Stars", "City"]
        for col in required_cols:
            if col not in df.columns:
                df[col] = "N/A"
                
        df.to_csv(filepath, index=False)
        print(f"Data saved to {filepath}")
        return filepath

if __name__ == "__main__":
    scraper = BookingScraper()
    asyncio.run(scraper.run(limit=10))
