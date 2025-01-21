import matplotlib.pyplot as plt
import numpy as np
from utils import execute_query
from adjustText import adjust_text

# Query to get state performance metrics
query = """
WITH customer_purchases AS (
    SELECT 
        c.customer_unique_id,
        c.customer_state,
        o.order_purchase_timestamp::timestamp,
        LAG(o.order_purchase_timestamp::timestamp) OVER (
            PARTITION BY c.customer_unique_id 
            ORDER BY o.order_purchase_timestamp
        ) as previous_purchase
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
),
time_between_purchases AS (
    SELECT 
        customer_state,
        EXTRACT(days FROM (order_purchase_timestamp - previous_purchase)) as days_between_purchases
    FROM customer_purchases
    WHERE previous_purchase IS NOT NULL
)
SELECT 
    customer_state,
    COUNT(*) as number_of_repeat_purchases,
    ROUND(AVG(days_between_purchases))::integer as avg_days_between_purchases
FROM time_between_purchases
GROUP BY customer_state
HAVING COUNT(*) >= 5
ORDER BY number_of_repeat_purchases DESC;
"""

# Get data using utils.py
df = execute_query(query)

if df is not None:
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Calculate means for quadrant lines
    mean_days = df['avg_days_between_purchases'].mean()
    mean_purchases = df['number_of_repeat_purchases'].mean()
    
    # Get axis limits
    x_min, x_max = df['avg_days_between_purchases'].min() - 5, df['avg_days_between_purchases'].max() + 20
    y_min, y_max = 0, df['number_of_repeat_purchases'].max() * 1.1
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)

    # Add light background colors for quadrants
    rect_fast_high = plt.Rectangle((x_min, mean_purchases), mean_days - x_min, y_max - mean_purchases,
                                 facecolor='#e3f2fd', alpha=0.2, zorder=0)
    rect_slow_high = plt.Rectangle((mean_days, mean_purchases), x_max - mean_days, y_max - mean_purchases,
                                 facecolor='#fff3e0', alpha=0.2, zorder=0)
    rect_fast_low = plt.Rectangle((x_min, y_min), mean_days - x_min, mean_purchases - y_min,
                                facecolor='#e8f5e9', alpha=0.2, zorder=0)
    rect_slow_low = plt.Rectangle((mean_days, y_min), x_max - mean_days, mean_purchases - y_min,
                                facecolor='#fafafa', alpha=0.2, zorder=0)
    
    ax.add_patch(rect_fast_high)
    ax.add_patch(rect_slow_high)
    ax.add_patch(rect_fast_low)
    ax.add_patch(rect_slow_low)
    
    # Draw quadrant lines
    plt.axvline(x=mean_days, color='#9e9e9e', linestyle='--', alpha=0.5, zorder=1)
    plt.axhline(y=mean_purchases, color='#9e9e9e', linestyle='--', alpha=0.5, zorder=1)
    
    # Create scatter plot with size based on number of purchases
    sizes = df['number_of_repeat_purchases']
    normalized_sizes = 100 + (sizes - sizes.min()) / (sizes.max() - sizes.min()) * 400
    
    plt.scatter(df['avg_days_between_purchases'], 
                df['number_of_repeat_purchases'],
                alpha=0.7,
                s=normalized_sizes,
                c='#4a90e2',  # Consistent blue color
                edgecolor='white')
    
    # Add state labels with adjust_text
    texts = []
    for idx, row in df.iterrows():
        texts.append(plt.text(row['avg_days_between_purchases'],
                            row['number_of_repeat_purchases'],
                            row['customer_state'],
                            fontsize=9))
    
    # Adjust text positions to avoid overlap
    adjust_text(texts, arrowprops=dict(arrowstyle='-', color='gray', alpha=0.5))
    
    # Add quadrant labels with background boxes
    plt.text(x_min + (mean_days - x_min)/2, y_max * 0.95, 
             'FAST & HIGH\n(Ideal)',
             ha='center', va='top',
             bbox=dict(facecolor='#e3f2fd', edgecolor='none', 
                      alpha=0.5, pad=5),
             fontsize=10)
    
    plt.text(mean_days + (x_max - mean_days)/2, y_max * 0.95,
             'SLOW & HIGH\n(Volume Leaders)',
             ha='center', va='top',
             bbox=dict(facecolor='#fff3e0', edgecolor='none', 
                      alpha=0.5, pad=5),
             fontsize=10)
    
    plt.text(x_min + (mean_days - x_min)/2, y_min + (mean_purchases * 0.15),
             'FAST & LOW\n(Frequency Leaders)',
             ha='center', va='bottom',
             bbox=dict(facecolor='#e8f5e9', edgecolor='none', 
                      alpha=0.5, pad=5),
             fontsize=10)
    
    plt.text(mean_days + (x_max - mean_days)/2, y_min + (mean_purchases * 0.15),
             'SLOW & LOW\n(Need Attention)',
             ha='center', va='bottom',
             bbox=dict(facecolor='#fafafa', edgecolor='none', 
                      alpha=0.5, pad=5),
             fontsize=10)
    
    # Add specific annotations for SP and MS
    sp_row = df[df['customer_state'] == 'SP'].iloc[0]
    ms_row = df[df['customer_state'] == 'MS'].iloc[0]
    
    # SP annotation with more prominent styling
    plt.annotate(
        "SP (São Paulo)\nVolume: 1,455 repeat purchases\nHighest total market value",
        xy=(sp_row['avg_days_between_purchases'], sp_row['number_of_repeat_purchases']),
        xytext=(sp_row['avg_days_between_purchases'] + 10, sp_row['number_of_repeat_purchases'] - 100),
        ha='left',
        va='top',
        bbox=dict(facecolor='#e3f2fd', edgecolor='#4a90e2', alpha=0.9, pad=5),
        arrowprops=dict(arrowstyle='->', color='#4a90e2', lw=2),
        fontsize=10,
        fontweight='bold')
    
    # MS annotation with updated styling
    plt.annotate(
        "MS (Mato Grosso do Sul)\nHighest purchase frequency\nLow volume impact",
        xy=(ms_row['avg_days_between_purchases'], ms_row['number_of_repeat_purchases']),
        xytext=(ms_row['avg_days_between_purchases'] + 5, ms_row['number_of_repeat_purchases'] + 300),
        ha='left',
        va='bottom',
        bbox=dict(facecolor='#e8f5e9', edgecolor='#66bb6a', alpha=0.9, pad=5),
        arrowprops=dict(arrowstyle='->', color='#66bb6a', lw=2),
        fontsize=9)
    
    # Labels and title
    plt.xlabel('Average Days Between Purchases', fontsize=10)
    plt.ylabel('Number of Repeat Purchases', fontsize=10)
    plt.title('State Performance Quadrants', pad=20, fontsize=12, fontweight='bold')
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Add grid with lower opacity
    plt.grid(True, alpha=0.2, zorder=0)
    
    plt.tight_layout()
    plt.show()
    
    # Print quadrant analysis
    print("\nQuadrant Analysis:")
    print("\nFAST & HIGH (Ideal):")
    print(df[(df['avg_days_between_purchases'] < mean_days) & 
            (df['number_of_repeat_purchases'] > mean_purchases)]['customer_state'].tolist())
    
    print("\nSLOW & HIGH (Volume Leaders):")
    print(df[(df['avg_days_between_purchases'] > mean_days) & 
            (df['number_of_repeat_purchases'] > mean_purchases)]['customer_state'].tolist())
    
    print("\nFAST & LOW (Frequency Leaders):")
    print(df[(df['avg_days_between_purchases'] < mean_days) & 
            (df['number_of_repeat_purchases'] < mean_purchases)]['customer_state'].tolist())
    
    print("\nSLOW & LOW (Need Attention):")
    print(df[(df['avg_days_between_purchases'] > mean_days) & 
            (df['number_of_repeat_purchases'] < mean_purchases)]['customer_state'].tolist())
else:
    print("Error: Could not retrieve data from database")