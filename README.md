# Apple Podcasts Episode Scraper

Simple Selenium-based scraper for collecting episode URLs from an Apple Podcasts show page.
The goal is to collect all episodes shown in `See All (N)`.

## What it does

- Opens a show page
- Clicks `See All (number)`
- Scrolls the episode list
- Extracts unique episode URLs
- Saves results to CSV

## Files

- `scrape_podcasts.py`: main script
- `podcast_scrap.ipynb`: exploration notebook
- `episodes.csv` / `episodes_all.csv`: output examples

