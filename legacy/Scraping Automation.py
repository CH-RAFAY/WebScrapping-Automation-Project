import re
from playwright.sync_api import Playwright, sync_playwright, expect
import pandas as pd
from playwright.async_api import async_playwright
import asyncio

hotels = []


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto(
        "https://www.booking.com/index.en-gb.html?label=gen173nr-1BCAEoggI46AdIM1gEaLUBiAEBmAEJuAEXyAEM2AEB6AEBiAIBqAIDuAKDqs25BsACAdICJGNhMDdkNTU5LTkwMTMtNGY3MS1hMTAxLWFmNmEwYTgzMTAyONgCBeACAQ&sid=d8abac8261e5e67d7f378be94403a5d0&keep_landing=1&sb_price_type=total&")
    page.wait_for_timeout(3000)

    try:
        signin_message = page.get_by_label("Dismiss sign in information.")
        signin_message.click()
    except:
        pass
    page.wait_for_timeout(1000)
    page.get_by_test_id("header-language-picker-trigger").click()
    page.wait_for_timeout(3000)
    select_language = page.get_by_test_id("All languages").get_by_role("button", name="English (US)")
    select_language.click()
    page.wait_for_timeout(3000)

    select_city = page.get_by_placeholder("Where are you going?")
    select_city.click()
    page.get_by_placeholder("Where are you going?").fill("NewYork")
    page.wait_for_timeout(1500)
    try:
        countryname = page.get_by_role("button", name="Central New York City New")
        countryname.click()
    except:
        page.get_by_role("button", name="New York New York, United").click()
        pass
    page.get_by_label("27 November").click()
    page.get_by_label("27 December 2024", exact=True).click()
    page.wait_for_timeout(2000)

    # Simplified occupancy configuration for faster execution
    page.get_by_test_id("occupancy-config").click()
    page.locator("div").filter(has_text=re.compile(r"^2$")).locator("button").nth(1).click()
    page.get_by_role("button", name="Done").click()
    page.wait_for_timeout(3000)
    page.get_by_role("button", name="Search").click()
    page.wait_for_timeout(5000)

    # Simplified map search
    page.get_by_placeholder("Search on map").click()
    page.get_by_placeholder("Search on map").fill("New York")
    page.get_by_placeholder("Search on map").press("Enter")
    page.wait_for_timeout(5000)

    # Show available properties
    show_property = page.query_selector(
        "xpath=//html/body/div[12]/div[2]/div/div[1]/div/div/div[2]/fieldset/div[4]/label/span[3]/div/div/div")
    if show_property:
        show_property.click()
    page.wait_for_timeout(5000)

    # Minimal scrolling
    page.press("body", "PageDown")
    page.wait_for_timeout(1000)

    # Get only 10 URLs
    def getHotelsUrl():
        urls = page.query_selector_all("xpath=//html/body/div[12]/div[2]/div/div[2]/div/div/ul/li[.]")
        # Limit to first 10 URLs
        for i, urls_links in enumerate(urls[:10]):
            hotels_url = urls_links.query_selector('a')
            if hotels_url and len(hotels) < 10:
                hotels.append(hotels_url.get_attribute("href"))
                print(f"Added hotel URL {i + 1}/10")

    getHotelsUrl()
    page.wait_for_timeout(2000)
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)

# ======================================================================================================================
hotels_info = []


async def scrape_data(links):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(links)
        await page.wait_for_timeout(3000)
        await page.reload()
        await page.wait_for_timeout(5000)

        try:
            location = await page.wait_for_selector('span.hp_address_subtitle.js-hp_address_subtitle.jq_tooltip')
            location_text = await location.inner_text()
        except:
            location_text = "N/A"

        try:
            hotel_name = await page.query_selector('h2.d2fee87262.pp-header__title')
            hotel_name_text = await hotel_name.inner_text()
        except:
            hotel_name_text = "N/A"

        try:
            rating = await page.query_selector('div.a3b8729ab1.d86cee9b25')
            rating_text = await rating.inner_text()
        except:
            rating_text = "N/A"

        try:
            rating_star = await page.query_selector_all('span.fcd9eec8fb.d31eda6efc.c25361c37f')
            rat_star = f"{len(rating_star)} star"
        except:
            rat_star = "N/A"

        try:
            price = await page.query_selector(
                'div.bui-price-display__value.prco-text-nowrap-helper.prco-inline-block-maker-helper')
            price_text = await price.inner_text()
        except:
            price_text = "N/A"

        booking_info = {
            "HotelName": hotel_name_text,
            "Location": location_text,
            "Price": price_text,
            "Rating": rating_text,
            "Stars": rat_star,
            "City": "New York"  # Added City column with fixed value
        }
        hotels_info.append(booking_info)
        print(f"Scraped data for: {hotel_name_text}")
        await context.close()
        await browser.close()


async def info():
    for i, links in enumerate(hotels):
        print(f"\nScraping hotel {i + 1}/10")
        await scrape_data(links)


asyncio.run(info())

df = pd.DataFrame(hotels_info)
print("\nFinal Dataset:")
print(df)
df.to_csv('hotels_top10.csv', index=False)