# Importing modules
from playwright.sync_api import sync_playwright
from dataclasses import dataclass, asdict, field
from tqdm import tqdm
import pandas as pd
import argparse 
import re

# Making the main data structure
@dataclass
class Business:
    name: str = None
    address: str = None
    phone: str = None
    website: str = None
    rating: float = None
    link: str = None


# Making save feature
@dataclass
class Businesslist:
    business_list : list[Business] = field(default_factory=list)

    # Convert list of Business dataclass objects into a flat DataFrame for CSV/XLSX export
    def dataframe(self):
        return pd.json_normalize((asdict(business) for business in self.business_list), sep="_")
    
    # Save the data to xlsx file
    def save_to_excel(self, filename):
        self.dataframe().to_excel(f"{filename}.xlsx", index=False)

    # Save the data to csv file
    def save_to_csv(self, filename):
        self.dataframe().to_csv(f"{filename}.csv", index=False)


# Main feature
def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Open the Google map web page
        page.goto("https://maps.app.goo.gl/iFpQVotV9J7ydMGR9", timeout=15000)
        page.wait_for_timeout(5000)

        # Find and fill the search box
        page.locator("//input[@id='searchboxinput']").fill(looking_for)
        page.keyboard.press("Enter")
        page.wait_for_timeout(3000)

        # Find all the avaible data
        listings = page.locator("//div[contains(@class, 'Nv2PK')]").all()
        if len(listings) == 0: # If nothing found, break tghe program
            print("No result are found")
            browser.close()
            return
        
        # Define the made class
        businesslist = Businesslist()
        
        # Looping throught every data found
        for listing in tqdm(listings, desc="Extracting", unit="Data")[:total_data]:
            listing.click() # Click the place from listings and wait for 1.5second before continue
            page.wait_for_timeout(1500)

            # Define the made class
            business = Business()

            # Find and store the place name and address to class business
            business.name = page.locator("//h1[contains(@class, 'DUwDvf')]").inner_text()
            business.address = page.locator(".rogA2c").nth(0).inner_text()

            # Looping throght the line of data to find the phone number
            for idx in [2, 3, 4]:
                phone_num = page.locator(".Io6YTe.fontBodyMedium.kR99db.fdkmkc").nth(idx).inner_text()
                if re.search(r"\+?\d[\d\s\-]+", phone_num):
                    business.phone = phone_num
                    break

            # Find and store the business website and rating to made class
            business.website = page.locator(".rogA2c.ITvuef").inner_text()
            rating_elemen = page.locator(".fontBodyMedium.dmRWX").inner_text().split("\n")
            business.rating = "".join(rating_elemen)
            
            # Find and click share button in Indonesia language or English language
            try:
                page.locator("//button[@data-value='Bagikan']").click()
            except:
                page.locator("//button[@data-value='Share']").click()

            # Get the business link, and store them all into a list 
            business.link = page.locator(".vrsrZe").get_attribute("value")
            page.locator("//button[@jsaction='modal.close']").click()
            businesslist.business_list.append(business)
            page.wait_for_timeout(1500)

        # Call the made save to csv or xlsx function
        if "xlsx" in save_format:
            businesslist.save_to_excel(f"Gmap scrape {looking_for}")
        elif "csv" in save_format:
            businesslist.save_to_csv(f"Gmap scrape {looking_for}")
        else:
            businesslist.save_to_excel(f"Gmap scrape {looking_for}")
            businesslist.save_to_csv(f"Gmap scrape {looking_for}")

        # Close the browser 
        browser.close()


# If the python file run directly
if __name__ == "__main__":
    # An option for user 
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--search", type=str, default="Hospital Engaland", help="Search the desire location and place")
    parser.add_argument("-t", "--total", type=int, default=5, help="Decide how many data that will be extracted")
    parser.add_argument("-f", "--file", type=str, default=["xlsx", "csv"], choices=["xlsx", "csv"], help="Choose output file format. Not choosing any will result with both file as result")
    args = parser.parse_args()

    looking_for = args.search
    total_data = args.total
    save_format = args.file
    
    # Call the main function
    main()