import sys
import os
import pandas as pd
import json

# Add the directory containing this script to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
import threading
import asyncio
import glob
from scraper import BookingScraper
from visualizer import create_visualization

app = Flask(__name__)

# Global state for simplicity (in a real app, use a DB or Redis)
SCRAPE_STATUS = {
    "is_scraping": False,
    "progress": 0,
    "message": "Idle",
    "last_file": None,
    "error": None
}

def get_records_dir():
    """
    Returns the path to the records directory.
    Uses /tmp/records if the application root is not writable (e.g., Vercel),
    otherwise uses app/records.
    """
    if os.access(app.root_path, os.W_OK):
        base_dir = app.root_path
    else:
        base_dir = "/tmp"
    
    records_path = os.path.join(base_dir, "records")
    if not os.path.exists(records_path):
        try:
            os.makedirs(records_path, exist_ok=True)
        except OSError:
            # Fallback for some very restrictive environments
            return "/tmp"
    return records_path

def run_scraper_background(limit):
    global SCRAPE_STATUS
    SCRAPE_STATUS["is_scraping"] = True
    SCRAPE_STATUS["progress"] = 0
    SCRAPE_STATUS["message"] = "Starting scraper..."
    SCRAPE_STATUS["error"] = None
    
    try:
        records_dir = get_records_dir()
        scraper = BookingScraper(records_dir=records_dir)
        # We need a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        filepath = loop.run_until_complete(scraper.run(limit=limit))
        loop.close()
        
        SCRAPE_STATUS["last_file"] = filepath
        SCRAPE_STATUS["message"] = "Completed"
        SCRAPE_STATUS["progress"] = 100
    except Exception as e:
        SCRAPE_STATUS["error"] = str(e)
        SCRAPE_STATUS["message"] = "Error"
    finally:
        SCRAPE_STATUS["is_scraping"] = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start-scrape', methods=['POST'])
def start_scrape():
    global SCRAPE_STATUS
    if SCRAPE_STATUS["is_scraping"]:
        return jsonify({"status": "error", "message": "Scraping already in progress"}), 400
        
    data = request.json
    limit = int(data.get('limit', 10))

    # Clear previous records to ensure data freshness
    records_dir = get_records_dir()
    try:
        if os.path.exists(records_dir):
            for f in glob.glob(os.path.join(records_dir, "*.csv")):
                os.remove(f)
            # Reset last_file in status
            SCRAPE_STATUS["last_file"] = None
    except Exception as e:
        print(f"Warning: Could not clear old records: {e}")
    
    # Start background thread
    thread = threading.Thread(target=run_scraper_background, args=(limit,))
    thread.start()
    
    return jsonify({"status": "started", "limit": limit})

@app.route('/status')
def status():
    return jsonify(SCRAPE_STATUS)

@app.route('/visualization')
def visualization():
    global SCRAPE_STATUS
    # Find latest file if not in memory
    if not SCRAPE_STATUS["last_file"]:
        # Look in records dir
        records_dir = get_records_dir()
        files = glob.glob(os.path.join(records_dir, "*.csv"))
        if files:
            SCRAPE_STATUS["last_file"] = max(files, key=os.path.getctime)
    
    if not SCRAPE_STATUS["last_file"]:
        return "No data found. Please scrape first."
        
    try:
        # Read and process CSV for Knowledge Graph
        df = pd.read_csv(SCRAPE_STATUS["last_file"])
        
        # Clean Price for logic (create a numeric column)
        # Handle cases like 'PKR 12,345' -> 12345
        df['Price_Clean'] = df['Price'].astype(str).str.replace(',', '', regex=False)
        df['Price_Clean'] = df['Price_Clean'].str.extract(r'(\d+\.?\d*)')[0]
        df['Price_Clean'] = pd.to_numeric(df['Price_Clean'], errors='coerce').fillna(0)
        
        # Handle N/A
        df = df.fillna("N/A")
        
        # Convert to list of dicts for frontend
        hotels_data = df.to_dict(orient='records')
        
        filename = os.path.basename(SCRAPE_STATUS["last_file"])
        return render_template('visualization.html', hotels_data=hotels_data, filename=filename)
        
    except Exception as e:
        return f"Error processing data: {str(e)}"

@app.route('/download/<filename>')
def download_file(filename):
    records_dir = get_records_dir()
    filepath = os.path.join(records_dir, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
