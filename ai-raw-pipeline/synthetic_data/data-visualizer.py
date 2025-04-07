import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
from datetime import datetime


def visualize_distributions(data, output_path=None):
    """
    Create visualizations for the distributions in the synthetic data

    Parameters:
    - data: List of case dictionaries
    - output_path: Path to save the visualization image (defaults to casedir/distributions.png)
    """
    if output_path is None:
        output_path = os.getcwd() + "/casedir/distributions.png"

    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(data)

    # Extract nested data
    df["victim_gender"] = df["victim"].apply(lambda x: x["gender"])
    df["victim_age"] = df["victim"].apply(lambda x: int(x["age"]))
    df["reporter_gender"] = df["reporter"].apply(lambda x: x["gender"])
    df["perpetrator_gender"] = df["perpetrator"].apply(lambda x: x["gender"])

    # Extract hour from starttime for distribution analysis
    df["hour"] = df["starttime"].apply(lambda x: int(x.split(":")[0]))

    # Extract minutes from talktime - ensure we get the proper value
    df["talk_minutes"] = df["talktime"].apply(
        lambda x: (
            float(x.split(":")[0]) + float(x.split(":")[1]) / 60
            if ":" in x
            else float(x)
        )
    )

    # Set a consistent style
    sns.set_style("whitegrid")

    # Create figure with subplots - Use a more modern color palette
    plt.figure(figsize=(20, 15))

    # 1. Gender distributions
    plt.subplot(3, 3, 1)
    gender_data = {
        "Victim": df["victim_gender"].value_counts().to_dict(),
        "Reporter": df["reporter_gender"].value_counts().to_dict(),
        "Perpetrator": df["perpetrator_gender"].value_counts().to_dict(),
    }

    # Prepare data for grouped bar chart
    roles = []
    genders = []
    counts = []

    for role, gender_counts in gender_data.items():
        for gender, count in gender_counts.items():
            roles.append(role)
            genders.append(gender)
            counts.append(count)

    gender_df = pd.DataFrame({"Role": roles, "Gender": genders, "Count": counts})

    # Use custom colors for better visualization
    sns.barplot(x="Role", y="Count", hue="Gender", data=gender_df, palette="viridis")
    plt.title("Gender Distribution by Role", fontsize=14)
    plt.ylabel("Count", fontsize=12)
    plt.legend(title="Gender", fontsize=10)

    # 2. Victim Age Distribution
    plt.subplot(3, 3, 2)
    sns.histplot(df["victim_age"], bins=range(1, 18), kde=True, color="teal")
    plt.title("Victim Age Distribution", fontsize=14)
    plt.xlabel("Age", fontsize=12)
    plt.ylabel("Count", fontsize=12)

    # 3. Start Time Distribution (by hour)
    plt.subplot(3, 3, 3)
    sns.histplot(df["hour"], bins=range(6, 23), kde=True, color="purple")
    plt.title("Call Start Time Distribution", fontsize=14)
    plt.xlabel("Hour of Day", fontsize=12)
    plt.ylabel("Count", fontsize=12)

    # 4. Talk Time Distribution
    plt.subplot(3, 3, 4)
    sns.histplot(df["talk_minutes"], bins=range(10, 21), kde=True, color="darkblue")
    plt.title("Talk Time Distribution", fontsize=14)
    plt.xlabel("Minutes", fontsize=12)
    plt.ylabel("Count", fontsize=12)
    plt.xlim(9.5, 20.5)  # Set x-axis limits to focus on 10-20 minute range

    # 5. County Distribution
    plt.subplot(3, 3, 5)
    county_counts = df["county"].value_counts().head(10)

    sns.barplot(
        x=county_counts.index,
        y=county_counts.values,
        hue=county_counts.index,
        palette="mako",
        legend=False,
    )
    plt.title("Top 10 Counties", fontsize=14)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.ylabel("Count", fontsize=12)

    # Add count labels to the bars
    for i, v in enumerate(county_counts.values):
        plt.text(i, v + 5, str(v), ha="center", fontsize=9)

    # 6. Category Distribution with percentages
    g = plt.subplot(3, 3, 6)

    # Plot main categories and get the count for each category
    category_counts = df["category"].value_counts()
    total_cases = len(df)

    bars = sns.countplot(
        x="category", hue="category", data=df, ax=g, palette="viridis", legend=False
    )
    g.set_title("Category Distribution", fontsize=14)
    g.set_ylabel("Count", fontsize=12)

    # Add percentages and counts above each bar
    for i, v in enumerate(category_counts):
        percentage = (v / total_cases) * 100
        g.text(i, v + 5, f"{v}\n({percentage:.1f}%)", ha="center", fontsize=9)

    # 7. Cases by Month and Year with improved styling
    plt.subplot(3, 3, 7)
    df["date"] = pd.to_datetime(df["startdate"], format="%d %b %Y")
    df["month_year"] = df["date"].dt.strftime("%Y-%m")
    monthly_counts = df["month_year"].value_counts().sort_index()

    # Use a more visually appealing line plot
    plt.plot(
        monthly_counts.index,
        monthly_counts.values,
        marker="o",
        linestyle="-",
        color="darkblue",
        markersize=6,
    )
    plt.title("Cases by Month", fontsize=14)
    # Improve x-axis readability
    plt.xticks(rotation=90, fontsize=9)  # Rotate labels to vertical
    if len(monthly_counts) > 12:
        # Show only every other month if there are many months
        plt.xticks(ticks=plt.xticks()[0][::2], labels=monthly_counts.index[::2])
    plt.ylabel("Count", fontsize=12)

    # Add a trend line
    z = np.polyfit(range(len(monthly_counts)), monthly_counts.values, 1)
    p = np.poly1d(z)
    plt.plot(
        range(len(monthly_counts)),
        p(range(len(monthly_counts))),
        "r--",
        alpha=0.7,
        label=f"Trend: {z[0]:.1f}x{z[1]:+.1f}",
    )
    plt.legend(fontsize=10)

    # 8. Day of Week Distribution with added percentages
    plt.subplot(3, 3, 8)
    df["day_of_week"] = df["date"].dt.day_name()
    day_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    day_counts = df["day_of_week"].value_counts().reindex(day_order)

    bars = sns.barplot(
        x=day_counts.index,
        y=day_counts.values,
        hue=day_counts.index,
        palette="mako",
        legend=False,
    )
    plt.title("Cases by Day of Week", fontsize=14)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.ylabel("Count", fontsize=12)

    # Add count and percentage labels to bars
    for i, v in enumerate(day_counts.values):
        percentage = (v / total_cases) * 100
        plt.text(i, v + 5, f"{v}\n({percentage:.1f}%)", ha="center", fontsize=9)

    # 9. Ward Distribution (Top 10)
    plt.subplot(3, 3, 9)
    ward_counts = df["ward"].value_counts().head(10)
    sns.barplot(x=ward_counts.index, y=ward_counts.values, hue=ward_counts.index, palette="mako", legend=False)
    plt.title("Top 10 Wards", fontsize=14)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.ylabel("Count", fontsize=12)

    # Add count labels to the bars
    for i, v in enumerate(ward_counts.values):
        plt.text(i, v + 5, str(v), ha="center", fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"Visualization saved to {output_path}")

    # Generate summary statistics
    print("\n=== Summary Statistics ===")
    print(f"Total number of cases: {len(df)}")
    print(
        f"Date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}"
    )
    print(
        f"Gender distribution (victims): {df['victim_gender'].value_counts(normalize=True).to_dict()}"
    )
    print(
        f"Gender distribution (perpetrators): {df['perpetrator_gender'].value_counts(normalize=True).to_dict()}"
    )
    print(f"Average victim age: {df['victim_age'].mean():.2f} years")
    print(f"Average talk time: {df['talk_minutes'].mean():.2f} minutes")
    print(f"Number of unique counties: {df['county'].nunique()}")
    print(
        f"Most common county: {df['county'].value_counts().index[0]} ({df['county'].value_counts().values[0]} cases)"
    )

    # Category statistics with percentages
    cat_stats = df["category"].value_counts(normalize=True) * 100
    print("\n=== Category Distribution ===")
    for cat, pct in cat_stats.items():
        count = df["category"].value_counts()[cat]
        print(f"{cat}: {count} cases ({pct:.1f}%)")

    # Subcategory statistics with percentages
    print("\n=== Subcategory Distribution ===")
    subcat_stats = df["subcateg"].value_counts(normalize=True) * 100
    for subcat, pct in subcat_stats.head(5).items():
        count = df["subcateg"].value_counts()[subcat]
        print(f"{subcat}: {count} cases ({pct:.1f}%)")

    # Include specific issues if available
    if "specific_issue" in df.columns:
        print("\n=== Top 5 Specific Issues ===")
        issue_stats = df["specific_issue"].value_counts(normalize=True) * 100
        for issue, pct in issue_stats.head(5).items():
            count = df["specific_issue"].value_counts()[issue]
            print(f"{issue}: {count} cases ({pct:.1f}%)")

    return df


# Fix the issue with the invalid path character '/' in filenames
# The error occurs in the for-loop at the end of the visualize_category_hierarchy function

def visualize_category_hierarchy(data, output_path=None):
    """
    Create visualizations for the new category hierarchy structure

    Parameters:
    - data: List of case dictionaries or DataFrame
    - output_path: Path to save the visualization image
    """
    if output_path is None:
        output_path = os.getcwd() + "/casedir/category_hierarchy.png"

    # Convert to DataFrame if it's a list
    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = data.copy()

    # Check if the new category structure is available
    if "subcateg" not in df.columns or "specific_issue" not in df.columns:
        print("Error: New category hierarchy structure not found in the data.")
        return

    # Set the style for better visualizations
    sns.set_style("whitegrid")

    # Create a figure with subplots - separate into multiple figures for better clarity
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))  # Change to a 1x2 layout with specific axes

    # 1. Main categories distribution
    sns.countplot(y="category", data=df, order=df["category"].value_counts().index, 
                hue="category", palette="viridis", legend=False, ax=axes[0])
    axes[0].set_title("Main Categories Distribution")
    axes[0].set_xlabel("Count")
    axes[0].set_ylabel("Category")

    # 2. Subcategories by main category
    # Create cross-tabulation of categories and subcategories
    ct = pd.crosstab(df["category"], df["subcateg"])
    # Convert to percentage for better visualization
    ct_pct = ct.div(ct.sum(axis=1), axis=0) * 100
    # Plot stacked bar chart with improved colors
    ct_pct.plot(kind="barh", stacked=True, colormap="viridis", ax=axes[1])
    axes[1].set_title("Subcategories by Main Category (%)", fontsize=14)
    axes[1].set_xlabel("Percentage", fontsize=12)
    axes[1].set_ylabel("Main Category", fontsize=12)

    # Improve legend
    axes[1].legend(title="Subcategory", bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=10)

    # Add percentage labels to each segment
    for i, (category, row) in enumerate(ct_pct.iterrows()):
        cumulative = 0
        for subcategory, value in row.items():
            if value > 5:  # Only show labels for segments larger than 5%
                axes[1].text(
                    cumulative + value / 2,
                    i,
                    f"{value:.1f}%",
                    ha="center",
                    va="center",
                    fontsize=10,
                    fontweight="bold",
                )
            cumulative += value

    # IMPORTANT: Save the main figure with tight layout
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    print(f"Category hierarchy visualization saved to {output_path}")
    
    # 3. Specific issues heatmap - with improved readability
    plt.subplot(2, 1, 2)
    # Create a pivot table to count occurrences of each specific issue by subcategory
    pivot = pd.crosstab(df["subcateg"], df["specific_issue"])

    # Create a larger figure for the heatmap
    plt.figure(figsize=(24, 14))

    # Plot heatmap with adjusted parameters for better readability
    sns.heatmap(
        pivot,
        annot=True,
        fmt="d",
        cmap="YlGnBu",
        linewidths=0.5,
        annot_kws={"size": 10},
        cbar_kws={"shrink": 0.7},
    )
    plt.title("Specific Issues by Subcategory", fontsize=16)
    plt.ylabel("Subcategory", fontsize=14)
    plt.xlabel("Specific Issue", fontsize=14)

    # Improve x-axis label readability
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.yticks(fontsize=12)

    # Save this as a separate figure
    specific_heatmap_path = os.path.splitext(output_path)[0] + "_specific_heatmap.png"
    plt.tight_layout()
    plt.savefig(specific_heatmap_path, bbox_inches="tight", dpi=150)
    plt.close()

    print(f"Specific issues heatmap saved to {specific_heatmap_path}")

    # Return to the main figure
    plt.figure(figsize=(18, 12))

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()

    print(f"Category hierarchy visualization saved to {output_path}")

    # Create an additional visualization showing the distribution of specific issues
    plt.figure(figsize=(14, 10))

    # Plot specific issues
    specific_issue_counts = df["specific_issue"].value_counts()

    # Use a horizontal bar chart for better readability with many categories
    bars = sns.barplot(
        y=specific_issue_counts.index,
        x=specific_issue_counts.values,
        hue=specific_issue_counts.index,
        palette="viridis",
        orient="h",
        legend=False,
    )

    # Add count labels to the bars
    for i, v in enumerate(specific_issue_counts.values):
        bars.text(v + 0.1, i, str(v), color="black", va="center")

    plt.title("Distribution of Specific Issues", fontsize=16)
    plt.xlabel("Count", fontsize=14)
    plt.ylabel("Specific Issue", fontsize=14)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)

    # Save the specific issues visualization
    specific_path = os.path.splitext(output_path)[0] + "_specific_issues.png"
    plt.tight_layout()
    plt.savefig(specific_path, bbox_inches="tight", dpi=150)
    plt.close()

    print(f"Specific issues visualization saved to {specific_path}")

    # Create a relationship diagram between categories and subcategories
    plt.figure(figsize=(20, 10))  # Make the figure wider to accommodate the legend

    # Create a summary table of relationships
    cat_subcat_counts = (
        df.groupby(["category", "subcateg"]).size().reset_index(name="count")
    )

    # Sort by count for better visibility
    cat_subcat_counts = cat_subcat_counts.sort_values("count", ascending=False)

    # Plot the relationship
    g = sns.barplot(x="category", y="count", hue="subcateg", data=cat_subcat_counts)
    
    # FIX: Move the legend to the right side of the graph, outside the plot area
    plt.legend(title="Subcategory", title_fontsize=12, fontsize=10, 
               loc='center left', bbox_to_anchor=(1.0, 0.5))
    
    plt.title("Relationship Between Categories and Subcategories", fontsize=16)
    plt.xlabel("Main Category", fontsize=14)
    plt.ylabel("Count", fontsize=14)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)

    # Save the relationship visualization
    relationship_path = os.path.splitext(output_path)[0] + "_category_relationships.png"
    plt.tight_layout()
    plt.savefig(relationship_path, bbox_inches="tight", dpi=150)
    plt.close()

    print(f"Category relationship visualization saved to {relationship_path}")

    # Create a chord diagram visualization for the hierarchical structure
    try:
        plt.figure(figsize=(12, 12))

        # Create hierarchical data structure for visualization
        hierarchy_data = []
        for i, row in df.sample(
            min(1000, len(df))
        ).iterrows():  # Limit to 1000 samples for better visualization
            hierarchy_data.append(
                {
                    "category": row["category"],
                    "subcategory": row["subcateg"],
                    "specific": row["specific_issue"],
                }
            )

        # Convert to DataFrame for easier manipulation
        hierarchy_df = pd.DataFrame(hierarchy_data)

        # Create a matrix of relationships for visualization
        # First between categories and subcategories
        cat_subcat_matrix = pd.crosstab(
            hierarchy_df["category"], hierarchy_df["subcategory"]
        )

        # Then between subcategories and specific issues
        subcat_specific_matrix = pd.crosstab(
            hierarchy_df["subcategory"], hierarchy_df["specific"]
        )

        # Plot heatmap of category to subcategory relationships
        plt.figure(figsize=(14, 8))
        sns.heatmap(
            cat_subcat_matrix, annot=True, fmt="d", cmap="viridis", linewidths=0.5
        )

        plt.title("Category to Subcategory Relationships", fontsize=16)
        plt.ylabel("Category", fontsize=14)
        plt.xlabel("Subcategory", fontsize=14)

        # Save the hierarchy visualization
        hierarchy_path = os.path.splitext(output_path)[0] + "_hierarchy.png"
        plt.tight_layout()
        plt.savefig(hierarchy_path, bbox_inches="tight", dpi=150)
        plt.close()

        print(f"Hierarchy visualization saved to {hierarchy_path}")
    except Exception as e:
        print(f"Could not create hierarchy visualization: {e}")

    # Create a separate visualization for each category showing its subcategories and specific issues
    # FIX: Handle file names with invalid characters like '/'
    for category in df["category"].unique():
        category_df = df[df["category"] == category]

        # Create a figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

        # First subplot: Subcategory distribution within this category
        subcategory_counts = category_df["subcateg"].value_counts()

        sns.barplot(
            y=subcategory_counts.index,
            x=subcategory_counts.values,
            hue=subcategory_counts.index,
            ax=ax1,
            palette="viridis",
            legend=False,
        )
        ax1.set_title(f"Subcategories in {category.capitalize()}", fontsize=16)
        ax1.set_xlabel("Count", fontsize=14)
        ax1.set_ylabel("Subcategory", fontsize=14)

        # Add count labels to the bars
        for i, v in enumerate(subcategory_counts.values):
            ax1.text(v + 0.1, i, str(v), color="black", va="center")

        # Second subplot: Top specific issues for this category
        specific_issue_counts = category_df["specific_issue"].value_counts().head(10)

        sns.barplot(
            y=specific_issue_counts.index,
            x=specific_issue_counts.values,
            hue=specific_issue_counts.index,
            ax=ax2,
            palette="mako",
            legend=False,
        )
        ax2.set_title(f"Top Specific Issues in {category.capitalize()}", fontsize=16)
        ax2.set_xlabel("Count", fontsize=14)
        ax2.set_ylabel("Specific Issue", fontsize=14)

        # Add count labels to the bars
        for i, v in enumerate(specific_issue_counts.values):
            ax2.text(v + 0.1, i, str(v), color="black", va="center")

        plt.tight_layout()

        # FIX: Replace invalid characters in category name for the filename
        safe_category = category.replace('/', '_').replace('\\', '_').replace(':', '_')
        
        # Save the category-specific visualization
        category_specific_path = (
            os.path.splitext(output_path)[0] + f"_{safe_category}_analysis.png"
        )
        
        # Create any necessary directories
        os.makedirs(os.path.dirname(category_specific_path), exist_ok=True)
        
        plt.savefig(category_specific_path, bbox_inches="tight", dpi=150)
        plt.close()

        print(
            f"{category.capitalize()} analysis visualization saved to {category_specific_path}"
        )

if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Visualize case data distributions.")
    parser.add_argument(
        "--input",
        type=str,
        default=os.getcwd() + "/casedir/cases.json",
        help="Path to the JSON input file (default: casedir/cases.json)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=os.getcwd() + "/casedir/distributions.png",
        help="Path to save the output image (default: casedir/distributions.png)",
    )
    parser.add_argument(
        "--categories",
        action="store_true",
        help="Generate additional category hierarchy visualizations",
    )

    args = parser.parse_args()

    # Check if the input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} not found.")
        exit(1)

    # Load the JSON data
    try:
        with open(args.input, "r") as fp:
            data = json.load(fp)
        print(f"Successfully loaded {len(data)} cases from {args.input}")
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        exit(1)

    # Create main visualizations
    df = visualize_distributions(data, args.output)

    # Create category hierarchy visualizations if requested
    if args.categories:
        category_output = os.path.splitext(args.output)[0] + "_categories.png"
        visualize_category_hierarchy(df, category_output)
