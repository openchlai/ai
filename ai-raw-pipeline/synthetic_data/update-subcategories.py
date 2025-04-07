import os
import json
import random

def update_categories_in_data(input_file, output_file=None):
    """
    Update the categories and subcategories in the existing JSON data file
    
    Parameters:
    - input_file: Path to the input JSON file
    - output_file: Path to save the updated JSON file (defaults to input_file)
    
    Returns:
    - The updated data
    """
    if output_file is None:
        output_file = input_file
    
    # Define proper categories with subcategories
    categories = {
        'abuse': {
            'physical': ['domestic violence', 'child abuse', 'elder abuse'],
            'emotional': ['bullying', 'verbal abuse', 'isolation'],
            'sexual': ['assault', 'harassment', 'exploitation']
        },
        'violence': {
            'domestic': ['intimate partner', 'family member', 'caregiver'],
            'community': ['school', 'workplace', 'public space'],
            'digital': ['cyberbullying', 'online threats', 'stalking']
        },
        'emergency': {
            'medical': ['injury', 'illness', 'pregnancy'],
            'safety': ['imminent danger', 'shelter needed', 'rescue required'],
            'disaster': ['fire', 'flood', 'displacement']
        }
    }
    
    # Load the existing data
    try:
        with open(input_file, 'r') as fp:
            data = json.load(fp)
        print(f"Successfully loaded {len(data)} cases from {input_file}")
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return None
    
    # Update each case with proper categories and subcategories
    for case in data:
        # Randomly select a main category
        main_category = random.choice(list(categories.keys()))
        case['category'] = main_category
        
        # Randomly select a subcategory type
        subcategory_type = random.choice(list(categories[main_category].keys()))
        
        # Randomly select a specific subcategory
        specific_subcategory = random.choice(categories[main_category][subcategory_type])
        
        # Update the subcategory field with type:specific format
        case['subcateg'] = f"{subcategory_type}:{specific_subcategory}"
    
    # Save the updated data
    try:
        with open(output_file, 'w') as fp:
            json.dump(data, fp, indent=4)
        print(f"Successfully saved updated data to {output_file}")
    except Exception as e:
        print(f"Error saving JSON file: {e}")
        return None
    
    return data

if __name__ == "__main__":
    import argparse
    
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Update categories in case data.')
    parser.add_argument('--input', type=str, default=os.getcwd() + "/casedir/cases.json",
                       help='Path to the JSON input file (default: casedir/cases.json)')
    parser.add_argument('--output', type=str, default=None,
                       help='Path to save the updated JSON file (default: same as input)')
    
    args = parser.parse_args()
    
    # Check if the input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} not found.")
        exit(1)
    
    # Update the categories
    update_categories_in_data(args.input, args.output)