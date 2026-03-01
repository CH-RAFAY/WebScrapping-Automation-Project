Web-Scraper & Visualizer

A powerful full-stack application that scrapes hotel data from Booking.com and visualizes it as an interactive force-directed graph.

##  Features
- **Automated Scraping**: Uses Playwright to scrape real-time hotel data (prices, ratings, locations).
- **Interactive Visualization**: D3.js force-directed graph to explore hotel relationships.
- **Data Processing**: Automatic cleaning and formatting of scraped data using Pandas.
- **Professional UI**: Modern dark-themed interface with neon accents and guided workflows.

##  Tech Stack
- **Backend**: Python, Flask
- **Scraping**: Playwright (Async)
- **Data**: Pandas
- **Frontend**: HTML5, CSS3 (Bootstrap 5), D3.js v7

##  Deployment Guide

### Option 1: Vercel (Frontend & UI Only)
**Note:** Vercel has a strict 50MB size limit for serverless functions. **Playwright browsers (Chromium) exceed this limit.**
- If you deploy to Vercel, the **UI and Visualization will work**, but the **Scraping feature will likely fail** unless you connect to an external browser service (like Browserless.io).

**Steps:**
1. Push this code to a GitHub repository.
2. Go to [Vercel.com](https://vercel.com) and "Add New Project".
3. Import your GitHub repository.
4. Vercel will automatically detect the `vercel.json` and `requirements.txt`.
5. Click **Deploy**.

### Option 2: Render / Railway (Recommended for Full Functionality)
For the scraper to work fully, you need a platform that supports Docker or larger environments.

**Steps for Render:**
1. Create a `Dockerfile` (already included in this project).
2. Push code to GitHub.
3. Go to [Render.com](https://render.com) -> New -> **Web Service**.
4. Connect your repo.
5. Select **Docker** as the Runtime.
6. Click **Create Web Service**.

##  Local Development
1. Clone the repo.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```
3. Run the app:
   ```bash
   python app/main.py
   ```
4. Open `http://localhost:5000`.
