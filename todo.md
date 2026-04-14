# TODO

## 1. Features

- Find why only part of episodes are collected after scrolling and clicking `See All (number)`
- Verify real list-page entry after `click_see_all()` using URL/DOM checks
- Tune wait time after each scroll

## 2. Structure

- Replace hardcoded `podcast_url`/timeout/scroll params with CLI args (`argparse`)
- Replace `print` with `logging` for step-by-step logs
- Unify CSV naming between script (`episodes.csv`) and notebook (`episodes_all.csv`)
- Modularize scraping logic and keep `main()` for orchestration only

## 3. Documentation

- Write `README.md`
- Document environment (Chrome/Chromedriver/Selenium versions) and organize `requirements.txt`

