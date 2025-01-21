import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils import execute_query

# Query to get metrics

query = """
WITH last_date AS (
    SELECT MAX(order_purchase_timestamp::timestamp) as max_date 
    FROM orders
), 
customer_rfm AS (
    SELECT 
        c.customer_unique_id,
        c.customer_state,
        EXTRACT(DAYS FROM (
            (SELECT max_date FROM last_date) - MAX(o.order_purchase_timestamp::timestamp)
        )) as recency,
        COUNT(DISTINCT o.order_id) as frequency,
        SUM(CAST(oi.price AS DECIMAL) + CAST(oi.freight_value AS DECIMAL))::DECIMAL(10,2) as monetary
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id, c.customer_state
),
rfm_scores AS (
    SELECT *,
        NTILE(5) OVER (ORDER BY recency DESC) as R,
        NTILE(5) OVER (ORDER BY frequency) as F,
        NTILE(5) OVER (ORDER BY monetary) as M
    FROM customer_rfm
),
customer_segments AS (
    SELECT *,
        CASE 
            WHEN (R >= 4 AND F >= 4 AND M >= 4) THEN 'Champions'
            WHEN (R >= 3 AND F >= 3 AND M >= 3) THEN 'Loyal Customers'
            WHEN (R <= 2 AND F >= 3 AND M >= 3) THEN 'At Risk'
            WHEN (R <= 2 AND F <= 2 AND M <= 2) THEN 'Lost'
            ELSE 'Others'
        END as customer_segment
    FROM rfm_scores
)
SELECT 
    cs.customer_segment,
    ROUND(AVG(CAST(NULLIF(op.payment_installments, '') AS DECIMAL)), 2) as avg_installments,
    COUNT(DISTINCT cs.customer_unique_id) as customer_count,
    ROUND(AVG(cs.monetary), 2) as avg_total_spend,
    ROUND(AVG(CAST(NULLIF(op.payment_value, '') AS DECIMAL)), 2) as avg_payment_value,
    STRING_AGG(DISTINCT op.payment_type, ', ') as payment_types
FROM customer_segments cs
JOIN customers c ON cs.customer_unique_id = c.customer_unique_id
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_payments op ON o.order_id = op.order_id
GROUP BY cs.customer_segment
ORDER BY avg_total_spend DESC;
"""

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4))

def get_gradient_color(position, num_bars, start_color, end_color):
    """Get color for specific position in gradient"""
    start_rgb = hex_to_rgb(start_color)
    end_rgb = hex_to_rgb(end_color)
    
    fraction = position / (num_bars - 1) if num_bars > 1 else 0
    return tuple(
        start + (end - start) * fraction
        for start, end in zip(start_rgb, end_rgb)
    )

def create_segment_analysis():
    try:
        # Execute query
        df = execute_query(query)
        
        if df is None or df.empty:
            print("No data retrieved from the database!")
            return
            
        # Create figure and axis objects with subplots()
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
        
        # Generate colors for plots
        num_segments = len(df)
        blue_colors = [get_gradient_color(i, num_segments, '#2E5894', '#94BBD9') 
                      for i in range(num_segments)]
        
        # Plot 1: Bar chart for average installments with blue gradient
        bar_width = 0.6
        x = range(len(df['customer_segment']))
        bars1 = ax1.bar(x, df['avg_installments'], bar_width, color=blue_colors)
        ax1.set_ylabel('Average Installments')
        ax1.set_title('Average Installments by Customer Segment', pad=-23, y=1.02)
        ax1.set_xticks(x)
        ax1.set_xticklabels(df['customer_segment'], rotation=0)
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}',
                    ha='center', va='bottom')
        
        # Add padding to y-axis limits
        y_max = df['avg_installments'].max()
        ax1.set_ylim(0, y_max * 1.2)
        
        # Plot 2: Bar chart for average spend with light gray
        bars2 = ax2.bar(x, df['avg_total_spend'], bar_width, color='#CACACA')
        
        # Add customer count as text on top of bars
        for i, bar in enumerate(bars2):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'R${height:,.2f}\n(n={df["customer_count"].iloc[i]:,})',
                    ha='center', va='bottom')
        
        ax2.set_ylabel('Average Total Spend (R$)')
        ax2.set_title('Average Spend by Customer Segment (with customer count)', pad=-23, y=1.02)
        ax2.set_xticks(x)
        ax2.set_xticklabels(df['customer_segment'], rotation=0)
        
        # Add padding to second plot y-axis
        y_max2 = df['avg_total_spend'].max()
        ax2.set_ylim(0, y_max2 * 1.2)
        
        # Remove top and right spines
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        
        # Add grid lines
        ax1.grid(True, axis='y', linestyle='--', alpha=0.3, zorder=0)
        ax2.grid(True, axis='y', linestyle='--', alpha=0.3, zorder=0)
        
        # Adjust layout
        plt.tight_layout()
        plt.show()
        
        # Print detailed analysis
        print("\nDetailed Segment Analysis:")
        print("-" * 80)
        for _, row in df.iterrows():
            print(f"\nSegment: {row['customer_segment']}")
            print(f"Number of Customers: {row['customer_count']:,}")
            print(f"Average Installments: {row['avg_installments']:.1f}")
            print(f"Average Total Spend: R${row['avg_total_spend']:,.2f}")
            print(f"Average Payment Value: R${row['avg_payment_value']:,.2f}")
            print(f"Payment Types Used: {row['payment_types']}")
            print("-" * 40)
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Error details:", e.__class__.__name__)
        raise

if __name__ == "__main__":
    create_segment_analysis()