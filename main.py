from playwright.sync_api import sync_playwright
from dataclasses import dataclass, asdict, field
import pandas as pd
import argparse 
import time

@dataclass
class Business:
    name: str = None
    address: str = None
    phone: str = None
    website: str = None
    rating: float = None
    link: str = None

@dataclass
class Businesslist:
    business_list : list[Business] = field(default_factory=list)

    def dataframe(self):
        return pd.json_normalize((asdict(business) for business in self.business_list), sep="_")
    
    def save_to_excel(self, filename):
        self.dataframe().to_excel(f"{filename}.xlsx", index=False)

    def save_to_csv(self, filename):
        self.dataframe().to_csv(f"{filename}.csv", index=False)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://www.google.com/maps", timeout=15000)
        page.wait_for_timeout(5000)

        page.locator("//input[@id='searchboxinput']").fill(looking_for)
        page.keyboard.press("Enter")
        page.wait_for_timeout(3000)

        listings = page.locator("//div[contains(@class, 'Nv2PK')]").all()
        if len(listings) == 0:
            print("No result are found")
            browser.close()
            return

        business_list = Businesslist()
        for listing in listings:
            listing.click()
            page.wait_for_timeout(1500)

            name = page.locator("//h1[contains(@class, 'DUwDvf')]").inner_text()
            address = page.locator(".rogA2c").nth(0).inner_text()
            phone = page.locator(".rogA2c").nth(2).inner_text()
            website = page.locator(".rogA2c.ITvuef").inner_text()

            rating_elemen = page.locator(".fontBodyMedium.dmRWX").inner_text().split("\n")
            rating = "".join(rating_elemen)
            
            page.locator("//button[@data-value='Bagikan']").click()
            link = page.locator(".vrsrZe").get_attribute("value")


        browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--search", type=str)
    parser.add_argument("-l", "--location", type=str)
    args = parser.parse_args()

    if args.location and args.search:
        looking_for = f"{args.search} {args.location}"
    else:
        looking_for = "hospital england"
    
    main()