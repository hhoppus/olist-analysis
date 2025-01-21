import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from utils import execute_query

# Query to get segment distribution by state
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
            (SELECT max_date FROM last_date) - 
            MAX(o.order_purchase_timestamp::timestamp)
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
    SELECT 
        *,
        NTILE(5) OVER (ORDER BY recency DESC) as R,
        NTILE(5) OVER (ORDER BY frequency) as F,
        NTILE(5) OVER (ORDER BY monetary) as M
    FROM customer_rfm
),
customer_segments AS (
    SELECT 
        *,
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
    customer_state,
    customer_segment,
    COUNT(*) as customer_count
FROM customer_segments
GROUP BY customer_state, customer_segment
ORDER BY customer_state, customer_segment;
"""

def create_state_segment_distribution():
    # Get data
    df = execute_query(query)
    if df is None:
        print("Error: Could not retrieve data from database")
        return
        
    # Define segment order
    segment_order = ['Champions', 'Loyal Customers', 'At Risk', 'Lost', 'Others']
    
    # Pivot the data for easier plotting
    df_pivot = df.pivot(index='customer_state', 
                       columns='customer_segment', 
                       values='customer_count').fillna(0)
    
    # Reorder columns
    df_pivot = df_pivot[segment_order]
    
    # Calculate percentages
    df_pct = df_pivot.div(df_pivot.sum(axis=1), axis=0) * 100
    
    # Sort states by total customer count
    total_customers = df_pivot.sum(axis=1)
    df_pivot = df_pivot.loc[total_customers.sort_values(ascending=True).index]
    df_pct = df_pct.loc[total_customers.sort_values(ascending=True).index]
    
    # Create figure and axis with adjusted size
    fig, ax = plt.subplots(figsize=(13, 10))
    
    # Base colors in muted Knaflic style
    base_colors = {
        'Champions': '#c6dbef',      # Light blue
        'Loyal Customers': '#bcbddc', # Muted purple
        'At Risk': '#d9f0d3',        # Light green
        'Lost': '#ccccc6',           # Muted gray
        'Others': '#efedf5'          # Very light purple
    }
    
    # Define states and segments to highlight
    highlights = {
        'SP': ['Champions', 'Loyal Customers', 'At Risk', 'Lost', 'Others'],  # All segments for SP
        'PB': ['Lost'],  # Low lost percentage
        'PI': ['Lost'],  # Low lost percentage
        'AC': ['At Risk'],  # High at risk percentage
        'AP': ['Loyal Customers']  # High loyal customers percentage
    }
    
    # Plot stacked bars
    left = np.zeros(len(df_pivot))
    for segment in segment_order:
        # Create color array with varying opacity
        colors = []
        for state in df_pivot.index:
            base_color = base_colors[segment]
            # Convert to RGB and adjust alpha
            if state in highlights and segment in highlights[state]:
                # Highlighted segments get full opacity
                colors.append(base_color)
            else:
                # Other segments get slightly reduced opacity
                rgb = plt.matplotlib.colors.to_rgb(base_color)
                colors.append((*rgb, 0.7))  # 70% opacity
                
        ax.barh(df_pivot.index, df_pct[segment], left=left, 
                label=segment, color=colors)
        
        # Add percentage labels in the middle of each segment
        for i, (state, value) in enumerate(df_pct[segment].items()):
            if value >= 5:  # Only show label if segment is at least 5%
                x = left[i] + value/2
                # Make text darker and larger for highlighted segments
                if state in highlights and segment in highlights[state]:
                    weight = 'bold'
                    color = '#000000'
                    fontsize = 9
                else:
                    weight = 'normal'
                    color = '#666666'
                    fontsize = 8
                ax.text(x, i, f'{value:.1f}%', 
                       ha='center', va='center',
                       color=color,
                       fontsize=fontsize,
                       fontweight=weight)
        left += df_pct[segment]
    
    # Add annotations for key insights
    ax.annotate('Largest customer base (39,156)\nwith lowest champions and at risk % \nand highest others %',
                xy=(95, df_pivot.index.get_loc('SP')),
                xytext=(101, df_pivot.index.get_loc('SP')),
                ha='left', va='center',
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.7),
                arrowprops=dict(arrowstyle='->'))
                
    ax.annotate('Exceptionally low lost customer %',
                xy=(85, df_pivot.index.get_loc('PB')),
                xytext=(101, df_pivot.index.get_loc('PB')),
                ha='left', va='center',
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.7),
                arrowprops=dict(arrowstyle='->'))
                
    ax.annotate('Highest at-risk %',
            xy=(60, df_pivot.index.get_loc('AC')),
            xytext=(101, df_pivot.index.get_loc('AC')),
            ha='left', va='center',
            bbox=dict(facecolor='white', edgecolor='none', alpha=1.0),  # Make fully opaque
            arrowprops=dict(arrowstyle='->'),
            zorder=5)  # Add zorder to ensure it's above the grid
                
    ax.annotate('Highest loyal customer %',  # Change to one line
            xy=(40, df_pivot.index.get_loc('AP') - 0.1), 
            xytext=(101, df_pivot.index.get_loc('AP') - 0.2),  # Shift down by adjusting the y-position
            ha='left', va='center',
            bbox=dict(facecolor='white', edgecolor='none', alpha=1.0),
            arrowprops=dict(arrowstyle='->'))
    
    # Customize the plot
    ax.set_title('Customer Segment Distribution by State', pad=20, fontsize=12)
    ax.set_xlabel('Percentage of Customers', fontsize=10)
    ax.grid(axis='x', alpha=0.3)
    
    # Add total customer count to y-axis labels
    states_with_totals = [f'{state} ({int(total_customers[state]):,})' 
                         for state in df_pivot.index]
    ax.set_yticklabels(states_with_totals, fontsize=9)
    
    # Stretch bars to fill height
    ax.margins(y=0)  # Remove vertical margins
    
    # Customize legend
    ax.legend(title='Segments', bbox_to_anchor=(1.0, 0.65), 
             loc='lower left', borderaxespad=0., 
             fontsize=9, title_fontsize=10)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Adjust layout to fit everything
    plt.subplots_adjust(right=0.85)  # Make room for annotations
    plt.show()
    
    # Print summary statistics
    print("\nKey Insights:")
    print("\n1. São Paulo (SP)")
    print(f"   - Largest customer base: {int(total_customers['SP']):,} customers")
    print(f"   - Balanced distribution across segments")
    
    print("\n2. Low Lost Customer Percentage")
    print(f"   - Paraíba (PB): {df_pct.loc['PB', 'Lost']:.1f}%")
    print(f"   - Piauí (PI): {df_pct.loc['PI', 'Lost']:.1f}%")
    
    print("\n3. High Risk Areas")
    print(f"   - Acre (AC): {df_pct.loc['AC', 'At Risk']:.1f}% at risk")
    
    print("\n4. Customer Loyalty Leader")
    print(f"   - Amapá (AP): {df_pct.loc['AP', 'Loyal Customers']:.1f}% loyal customers")

if __name__ == "__main__":
    create_state_segment_distribution()