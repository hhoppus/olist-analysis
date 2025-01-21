import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from utils import get_db_connection

def get_sp_category_data():
    """Fetch top 10 product categories purchased in SP state"""
    engine = get_db_connection()
    
    query = """
    SELECT 
        p.product_category_name,
        COUNT(*) as purchase_count
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    JOIN orders o ON oi.order_id = o.order_id
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE c.customer_state = 'SP'
        AND p.product_category_name IS NOT NULL
    GROUP BY p.product_category_name
    ORDER BY purchase_count DESC
    LIMIT 10;
    """
    
    df = pd.read_sql_query(query, engine)
    
    # Translate category names
    category_translations = {
        'beleza_saude': 'Health & Beauty',
        'cama_mesa_banho': 'Bed, Bath & Table',
        'esporte_lazer': 'Sports & Leisure',
        'moveis_decoracao': 'Furniture & Decor',
        'informatica_acessorios': 'Computer Accessories',
        'utilidades_domesticas': 'Household Items',
        'relogios_presentes': 'Watches & Gifts',
        'telefonia': 'Mobile Phones & Accessories',
        'automotivo': 'Automotive',
        'brinquedos': 'Toys'
    }
    df['category_english'] = df['product_category_name'].map(category_translations)
    return df

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4))

def get_gradient_color(position, num_bars, start_color='#2E5894', end_color='#94BBD9'):
    """Get color for specific position in gradient"""
    start_rgb = hex_to_rgb(start_color)
    end_rgb = hex_to_rgb(end_color)
    
    fraction = position / (num_bars - 1)
    return tuple(
        start + (end - start) * fraction
        for start, end in zip(start_rgb, end_rgb)
    )

def create_category_plot(df):
    """Create and display a bar plot of the top categories"""
    plt.figure(figsize=(12, 6))
    ax = plt.gca()
    
    # Create bars with gradient colors
    x = range(len(df))
    colors = [get_gradient_color(i, len(df)) for i in range(len(df))]
    plt.bar(x, df['purchase_count'], width=0.8, color=colors)
    
    # Customize the plot
    plt.title('Top 10 Product Categories Purchased in São Paulo', pad=20)
    plt.xlabel('Product Category')
    plt.ylabel('Number of Purchases')
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Set x-axis labels with category names
    plt.xticks(range(len(df)), df['category_english'], rotation=45, ha='right')
    
    # Add value labels on top of each bar
    for i, count in enumerate(df['purchase_count']):
        plt.text(i, count + 50, f'{int(count):,}', ha='center', va='bottom')
    
    # Set y-axis limits to match original
    plt.ylim(0, 5500)
    
    # Add grid lines
    plt.grid(True, axis='y', linestyle='--', alpha=0.3, zorder=0)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Show the plot
    plt.show()

if __name__ == "__main__":
    df = get_sp_category_data()
    create_category_plot(df)