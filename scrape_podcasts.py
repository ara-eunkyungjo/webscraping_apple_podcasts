"""
Scrape episode URLs from an Apple Podcasts show page.
Targets podcasts.apple.com and demonstrates simple dynamic page scraping
by clicking "load more" until all episodes are visible.
"""

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def load_all_episodes(driver, wait):
    """Click the load-more button until it is no longer available."""
    while True:
        try:
            load_more_button = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'div[class^="list-button"] button')
                )
            )
            driver.execute_script("arguments[0].click();", load_more_button)
        except TimeoutException:
            # No more button found (or no longer clickable), so stop.
            break


def get_episode_links(driver, wait):
    """Collect unique episode URLs from the loaded page."""
    try:
        link_elements = wait.until(
            EC.presence_of_all_elements_located(
                (
                    By.CSS_SELECTOR,
                    'a[href*="/podcast/"][href*="?i="]',
                )
            )
        )
    except TimeoutException:
        return []

    episode_urls = []
    seen = set()

    for element in link_elements:
        href = element.get_attribute("href")
        if href and "podcasts.apple.com" in href and href not in seen:
            seen.add(href)
            episode_urls.append(href)

    return episode_urls


def main():
    podcast_url = "https://podcasts.apple.com/us/podcast/more-attention-less-deficit/id312831485"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    try:
        driver.get(podcast_url)
        load_all_episodes(driver, wait)
        episode_urls = get_episode_links(driver, wait)
    finally:
        driver.quit()

    pd.DataFrame({"episode_url": episode_urls}).to_csv("episodes.csv", index=False)
    print(episode_urls)
    return episode_urls


if __name__ == "__main__":
    main()
