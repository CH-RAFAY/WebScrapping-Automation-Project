import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def create_dot_visualization(csv_file):
    # Read CSV and clean data in one go
    df = pd.read_csv(csv_file)
    df['Price'] = pd.to_numeric(df['Price'].str.replace(r'[PKR\s,]+', '', regex=True), errors='coerce')
    df = df[df['Price'] > 0].sort_values('Price')
    
    # Create simple figure
    plt.figure(figsize=(12, 5))
    
    # Create color groups (every 5K)
    colors = np.digitize(df['Price'], bins=np.arange(0, df['Price'].max() + 5000, 5000))
    
    # Single scatter plot with minimal styling
    plt.scatter(range(len(df)), df['Price'], c=colors, cmap='viridis', s=100, alpha=0.7)
    
    # Add price labels
    for i, price in enumerate(df['Price']):
        plt.annotate(f'{price/1000:.1f}K', (i, price), 
                    xytext=(0, 5), textcoords='offset points',
                    ha='center', fontsize=8, rotation=45)
    
    # Basic styling
    plt.xticks([])
    plt.grid(axis='y', linestyle='--', alpha=0.2)
    plt.title('Hotel Price Distribution', pad=15)
    plt.ylabel('Price (K)')
    
    # Remove unnecessary spines
    for spine in ['top', 'right', 'left']:
        plt.gca().spines[spine].set_visible(False)
    
    plt.tight_layout()
    return plt

if __name__ == "__main__":
    try:
        create_dot_visualization('hotels_top10.csv').show()
    except Exception as e:
        print(f"Error: {e}")