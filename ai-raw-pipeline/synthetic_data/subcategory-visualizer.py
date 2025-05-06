import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

def visualize_subcategories(data, output_path=None):
    """
    Create a dedicated visualization for subcategories
    
    Parameters:
    - data: List of case dictionaries
    - output_path: Path to save the visualization image (defaults to casedir/subcategories.png)
    """
    if output_path is None:
        output_path = os.getcwd() + "/casedir/subcategories.png"
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(data)
    
    # Check if subcategories are available
    if 'subcateg' not in df.columns or all(df['subcateg'] == "Add Sub Category"):
        print("Error: No meaningful subcategories found in the data.")
        return
    
    # Create a bigger figure for better visibility
    plt.figure(figsize=(14, 10))
    
    # 1. Overall subcategory distribution
    subcateg_counts = df['subcateg'].value_counts()
    
    # Plot horizontal bar chart for better label readability
    plt.subplot(1, 2, 1)
    bars = sns.barplot(y=subcateg_counts.index, x=subcateg_counts.values, orient='h')
    plt.title('Subcategory Distribution')
    plt.xlabel('Count')
    plt.tight_layout()
    
    # 2. Subcategories by main category
    plt.subplot(1, 2, 2)
    
    # Extract subcategory type (before the colon)
    if ':' in df['subcateg'].iloc[0]:
        df['subcateg_type'] = df['subcateg'].apply(lambda x: x.split(':')[0] if ':' in x else x)
        
        # Create cross-tabulation of categories and subcategory types
        ct = pd.crosstab(df['category'], df['subcateg_type'])
        
        # Plot stacked bar chart
        ct.plot(kind='bar', stacked=True)
        plt.title('Subcategory Types by Category')
        plt.xlabel('Category')
        plt.ylabel('Count')
        plt.legend(title='Subcategory Type')
    else:
        # Simple count by category if no subcategory type structure
        sns.countplot(x='category', hue='subcateg', data=df)
        plt.title('Subcategories by Category')
        plt.xlabel('Category')
        plt.ylabel('Count')
        plt.legend(title='Subcategory', loc='upper right')
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    
    print(f"Subcategory visualization saved to {output_path}")
    
    # Create a third, more detailed visualization for specific subcategories
    plt.figure(figsize=(16, 12))
    
    # If we have the category:subtype format, create a heatmap
    if ':' in df['subcateg'].iloc[0]:
        # Extract both parts
        df['subcateg_type'] = df['subcateg'].apply(lambda x: x.split(':')[0] if ':' in x else '')
        df['specific_subcateg'] = df['subcateg'].apply(lambda x: x.split(':')[1] if ':' in x else x)
        
        # Create a crosstab of subcategory types and specific subcategories
        heat_data = pd.crosstab(df['subcateg_type'], df['specific_subcateg'])
        
        # Plot heatmap
        sns.heatmap(heat_data, annot=True, fmt='d', cmap='YlGnBu')
        plt.title('Detailed Subcategory Distribution')
        plt.tight_layout()
        
        # Save the detailed visualization
        detailed_path = os.path.splitext(output_path)[0] + "_detailed.png"
        plt.savefig(detailed_path)
        plt.close()
        
        print(f"Detailed subcategory visualization saved to {detailed_path}")

if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Visualize subcategory distributions.')
    parser.add_argument('--input', type=str, default=os.getcwd() + "/casedir/cases.json",
                       help='Path to the JSON input file (default: casedir/cases.json)')
    parser.add_argument('--output', type=str, default=None,
                       help='Path to save the output image (default: casedir/subcategories.png)')
    
    args = parser.parse_args()
    
    # Check if the input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} not found.")
        exit(1)
    
    # Load the JSON data
    try:
        with open(args.input, 'r') as fp:
            data = json.load(fp)
        print(f"Successfully loaded {len(data)} cases from {args.input}")
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        exit(1)
    
    # Create visualizations
    visualize_subcategories(data, args.output)