import pandas as pd
import matplotlib
matplotlib.use('Agg') # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import io
import base64

def create_visualization(csv_file):
    try:
        df = pd.read_csv(csv_file)
        
        # Clean Price
        if 'Price' not in df.columns:
             return None, "Price column missing in CSV."

        # Handle currency symbols and commas
        df['Price_Clean'] = df['Price'].astype(str).str.replace(',', '', regex=False)
        df['Price_Clean'] = df['Price_Clean'].str.extract(r'(\d+\.?\d*)')[0]
        df['Price_Clean'] = pd.to_numeric(df['Price_Clean'], errors='coerce').fillna(0)
        
        # Filter invalid prices
        if df['Price_Clean'].max() == 0:
             return None, "No valid price data found (all zero or unparseable)."

        df = df.sort_values('Price_Clean')


        # Setup the Dashboard (2 Subplots)
        plt.style.use('dark_background') # Use dark style to match the UI
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        fig.suptitle('Hotel Knowledge Graph & Price Analysis', fontsize=16, color='white')
        
        # --- Plot 1: Price Distribution (Scatter) ---
        prices = df['Price_Clean']
        colors = np.linspace(0, 1, len(prices))
        
        scatter = ax1.scatter(range(len(df)), prices, c=colors, cmap='viridis', s=100, alpha=0.8, edgecolors='w', linewidth=0.5)
        ax1.set_title('Price Distribution Landscape', fontsize=12)
        ax1.set_ylabel('Price (Currency)', fontsize=10)
        ax1.set_xlabel('Hotels (Sorted by Price)', fontsize=10)
        ax1.grid(True, linestyle='--', alpha=0.2)
        
        # Annotate points on Scatter
        for i, (idx, row) in enumerate(df.iterrows()):
            price = row['Price_Clean']
            if len(df) <= 15 or i % (len(df)//10 + 1) == 0: # Sparse labeling
                ax1.annotate(f'{price:.0f}', (i, price), 
                            xytext=(0, 10), textcoords='offset points',
                            ha='center', fontsize=8, color='cyan')

        # --- Plot 2: Top 5 Cheapest Hotels (Bar) ---
        # Get top 5 cheapest (since df is sorted)
        top_n = df.head(5).iloc[::-1] # Reverse to have cheapest at top
        
        bars = ax2.barh(top_n['HotelName'].astype(str).str[:30], top_n['Price_Clean'], color='#4a90e2', alpha=0.8)
        ax2.set_title('Top 5 Best Value Hotels', fontsize=12)
        ax2.set_xlabel('Price', fontsize=10)
        
        # Add value labels to bars
        for bar in bars:
            width = bar.get_width()
            ax2.text(width + (width*0.02), bar.get_y() + bar.get_height()/2, 
                    f'{width:.0f}', 
                    ha='left', va='center', fontsize=9, color='white')

        plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Adjust for suptitle
        
        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, facecolor='#121212') # Dark background for image
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return img_base64, None
        
    except Exception as e:
        return None, str(e)
