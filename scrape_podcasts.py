"""
Scrape episode URLs from an Apple Podcasts show page.

Opens the public show page, finds and clicks the visible "See All (number)"
control to reach the full episode list, then scrolls until that many episodes
have loaded (or the list stops growing) before saving unique episode links.
"""

import re
import time
from pathlib import Path

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

EPISODE_LINK_SELECTOR = (By.CSS_SELECTOR, 'a[href*="/podcast/"][href*="?i="]')
SEE_ALL_REGEX = re.compile(r"See All\s*\((\d+)\)", re.IGNORECASE)
SCROLL_PAUSE_SEC = 1.2
MAX_SCROLL_WITHOUT_GROWTH = 6


def _unique_episode_hrefs(driver):
    """Return a set of unique episode URLs currently in the DOM."""
    hrefs = set()
    for el in driver.find_elements(*EPISODE_LINK_SELECTOR):
        href = el.get_attribute("href")
        if href and "podcasts.apple.com" in href:
            hrefs.add(href)
    return hrefs


def _locate_see_all(driver):
    """
    Find a visible control whose text looks like 'See All (N)'.
    Returns (element, n) or (None, None).
    """
    candidates = driver.find_elements(
        By.XPATH,
        (
            "//a[contains(., 'See All')]"
            "|//*[@role='link'][contains(., 'See All')]"
            "|//button[contains(., 'See All')]"
        ),
    )
    for el in candidates:
        text = (el.text or el.get_attribute("textContent") or "").strip()
        m = SEE_ALL_REGEX.search(text)
        if m:
            return el, int(m.group(1))
    return None, None


def get_expected_episode_count(driver, wait):
    """Parse the episode count from the visible 'See All (number)' label."""
    try:
        wait.until(lambda d: _locate_see_all(d)[0] is not None)
    except TimeoutException:
        raise RuntimeError(
            "Timed out waiting for a 'See All (number)' control on the show page."
        ) from None
    _, count = _locate_see_all(driver)
    return count


def click_see_all(driver, wait):
    """Click the visible 'See All (number)' element (no manual list URL)."""
    el, _ = _locate_see_all(driver)
    if el is None:
        raise RuntimeError("Could not find a clickable 'See All (number)' control.")

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
    time.sleep(0.3)
    try:
        wait.until(EC.element_to_be_clickable(el))
    except TimeoutException:
        pass
    driver.execute_script("arguments[0].click();", el)


def scroll_until_all_loaded(driver, wait, expected_count):
    """
    Scroll to the bottom repeatedly until we have at least expected_count
    unique episode links, or the count stops growing for several rounds.
    """
    idle_rounds = 0

    while idle_rounds < MAX_SCROLL_WITHOUT_GROWTH:
        current = len(_unique_episode_hrefs(driver))
        if current >= expected_count:
            break

        before = current
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_SEC)
        try:
            wait.until(
                lambda d: len(_unique_episode_hrefs(d)) > before
                or len(_unique_episode_hrefs(d)) >= expected_count
            )
        except TimeoutException:
            pass
        after = len(_unique_episode_hrefs(driver))

        if after <= before:
            idle_rounds += 1
        else:
            idle_rounds = 0


def get_episode_links(driver, wait):
    """Collect deduplicated episode URLs from the current (full list) page."""
    try:
        wait.until(EC.presence_of_element_located(EPISODE_LINK_SELECTOR))
    except TimeoutException:
        return []

    # Stable order for portfolio-friendly diffs / previews.
    return sorted(_unique_episode_hrefs(driver))


def main():
    podcast_url = (
        "https://podcasts.apple.com/us/podcast/more-attention-less-deficit/id312831485"
    )

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)

    try:
        driver.get(podcast_url)

        expected_count = get_expected_episode_count(driver, wait)
        click_see_all(driver, wait)

        # Let the full episode list route render; then ensure at least one row exists.
        time.sleep(1.0)
        try:
            wait.until(EC.presence_of_element_located(EPISODE_LINK_SELECTOR))
        except TimeoutException:
            pass

        scroll_until_all_loaded(driver, wait, expected_count)
        episode_urls = get_episode_links(driver, wait)
    finally:
        driver.quit()

    actual_count = len(episode_urls)
    print(f"Expected episode count (from See All): {expected_count}")
    print(f"Collected unique episode URLs: {actual_count}")
    print("Preview:", episode_urls[:5])

    export_dir = Path("export")
    export_dir.mkdir(parents=True, exist_ok=True)
    output_path = export_dir / "episodes.csv"
    pd.DataFrame({"episode_url": episode_urls}).to_csv(output_path, index=False)
    print(f"Saved: {output_path}")
    return episode_urls


if __name__ == "__main__":
    main()
