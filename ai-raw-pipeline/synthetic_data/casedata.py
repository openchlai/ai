import os
import json
import random
import string
import pandas as pd
from datetime import datetime, timedelta
from time import time, mktime, strftime


def generate_synthetic_data(num_years=1, num_cases=100):
    """
    Generate synthetic case data with realistic time distribution.

    Parameters:
    - num_years: Number of years to spread the data across (backward from today)
    - num_cases: Total number of cases to generate

    Returns:
    - List of case dictionaries
    """
    # Set end date as today
    end_date = datetime.now()

    # Calculate start date based on num_years
    start_date = end_date - timedelta(days=365 * num_years)

    # Convert to timestamps for easier calculations
    end_timestamp = int(end_date.timestamp())
    start_timestamp = int(start_date.timestamp())

    # The categories dictionary - Fixed structure to match our JSON
    categories = {
        "Abuse": {
            "Child Exploitation": [
                "Child Labor - Bonded",
                "Child Labor - Commercial",
                "Child Labor-Domestic",
                "Children Used for Begging",
                "Children Used For Criminal Activity",
                "Commercial Sex Exploitation",
                "General/Multiple",
            ],
            "Child Neglect": [
                "Child Abandonment",
                "Child Maintenance",
                "Child Malnutrition",
                "Denial of Education",
                "Denial of Shelter",
                "General/Multiple",
            ],
            "Economic Violence": [
                "Denial of Asset and Resources",
                "Denial of Food and Medical Care",
                "Denial of Shelter",
                "Family Neglect",
                "General/Multiple",
            ],
            "Emotional & Psychological Abuse": [
                "Bullying",
                "General/Multiple",
                "Humiliation",
                "Infidelity",
                "Labeling /Name calling",
                "Verbal attack",
                "Witness to Violence/Abuse",
            ],
            "Harmful Traditional Practices": [
                "Dowry related Violence",
                "Early/ Child Marriages",
                "Female Genital Mutilation",
                "Forced Marriages",
                "General/Multiple",
            ],
            "Murder": [
                "Abortion",
                "Attempted Murder",
                "Child Sacrifice",
                "Death Due to Abuse",
                "General/Multiple",
                "Mysterious Death",
                "Poisoning",
            ],
            "Online Sexual Abuse & Violence": [
                "Attempted Rape",
                "Exposure of Nudes",
                "Exposure to Online Pornography",
                "Exposure to Online Adult Pornography",
                "General/Multiple",
                "Online Extortion and Blackmail",
                "Online grooming for sexual purpose",
                "Revenge Pornography",
                "Unwanted Sexting",
                "Victim of Online adult Pornography",
            ],
            "Others": ["Threatening Violence and many more"],
            "Physical Violence": [
                "Battering and beating",
                "Beating with an object",
                "Corporal Punishment",
                "Cutting",
                "Electric- shocking",
                "General/Multiple",
                "Suffocating",
                "Burning intentionally",
            ],
            "Sexual Violence": [
                "Attempted Defilement",
                "Attempted Rape",
                "Cross generational sex",
                "Defilement",
                "Exposure to Pornographic Materials",
                "Forced prostitution",
                "General/Multiple",
                "Incest",
                "Indecent assault",
                "Rape",
            ],
        },
        "Counseling": {
            "Addiction": [
                "Alcohol",
                "Drugs/Substance abuse",
                "Food",
                "Gambling",
                "Gaming",
                "Masturbation",
                "Pornography",
                "Smoking",
                "Social Media/Internet",
            ],
            "Bestiality": [],
            "Boy/Girl Relationship": [],
            "Career Guidance": [],
            "Child Custody": [
                "Adoption",
                "Institutionalization",
                "Paternity/Maternity Right",
            ],
            "Child In Conflict with the Law": [
                "Child Imprisonment",
                "Juvenile Deliquency",
            ],
            "Child to Child Sex": [],
            "Denial of conjugal rights": [],
            "Differently Abled Persons": [
                "Deaf",
                "Mental Disability",
                "Physical Disability",
                "Visually Impaired",
            ],
            "Discrimination": [
                "Access to Education",
                "Age",
                "Criminal Record/Ex-Prisoner",
                "Ethnicity",
                "HIV/AIDS",
                "Marginal/Vulnerable Groups",
            ],
        },
        "Distress": {
            "Death": [],
            "Denial of Food": [],
            "Denied Medical Care": [],
            "Detention": [],
            "Imprisonment": [],
            "Lack of PPE": [],
            "Overworking": [],
            "Sexual Harassment/Forced Abortion": [],
            "Torture (Physical and Verbal)": [],
            "Unpaid Salary": [],
        },
        "Fraud/Theft": {
            "Fraud (Charging Exorbitant Fees)": [],
            "Misuse of Monies by Family Members": [],
            "Theft": [],
        },
        "Health": {
            "Mental Health": [],
            "Sickness (Physical Health, Home Sickness)": [],
        },
        "Information Inquiry": {
            "Appreciation": [],
            "Birth Registration": [],
            "Case Update": [],
            "Employment/Job": [],
            "Financial Aid": [],
            "In Need of School Fees": [],
            "Information on Helpline Services": [],
            "Inquiry on Other Services": [],
            "Medical Aid": [
                "Access to health care",
                "Concerns about illnesses",
                "In need of medical assistance",
            ],
            "Pre-trial Briefing": [],
        },
    }
    
    # instantiate empty datasets
    data = []

    # we load the location dataset
    KE = os.getcwd() + "/casedir/kenya.json"
    try:
        with open(KE, "r") as fp:
            locdf = pd.DataFrame(json.load(fp))
    except FileNotFoundError:
        print(f"Error: The file {KE} was not found.")
        print("Creating a dummy location dataframe for testing purposes.")
        # Create dummy location data for testing
        locdf = pd.DataFrame({
            "county": ["County1", "County2", "County3"],
            "district": ["District1", "District2", "District3"],
            "ward": ["Ward1", "Ward2", "Ward3"],
            "station": ["Station1", "Station2", "Station3"],
            "loop": [1, 2, 3],
            "idcounty": [1, 2, 3],
            "iddistrict": [1, 2, 3],
            "idward": [1, 2, 3],
            "streams": ["", "", ""]
        })

    # drop unwanted columns
    DROP = ["loop", "idcounty", "iddistrict", "idward", "streams"]
    locdf = locdf.drop(columns=[col for col in DROP if col in locdf.columns])

    gender = ["female"] * 8 + ["male"] * 2
    perp = ["female"] * 2 + ["male"] * 11

    # Get the main categories
    main_categories = list(categories.keys())

    # Working hours in seconds since midnight (6am to 10pm)
    work_hours_start = 6 * 3600  # 6am in seconds
    work_hours_end = 22 * 3600  # 10pm in seconds
    work_duration = work_hours_end - work_hours_start
    
    # Add tracking for day of week distribution (for validation)
    day_of_week_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}

    # Define time periods with weights favoring evening hours
    # Times are in seconds since midnight
    time_periods = [
        (6 * 3600, 9 * 3600),    # Morning: 6am - 9am
        (9 * 3600, 12 * 3600),   # Late morning: 9am - 12pm
        (12 * 3600, 15 * 3600),  # Afternoon: 12pm - 3pm
        (15 * 3600, 18 * 3600),  # Late afternoon: 3pm - 6pm
        (18 * 3600, 20 * 3600),  # Evening: 6pm - 8pm
        (20 * 3600, 22 * 3600)   # Night: 8pm - 10pm
    ]

    # Weights heavily favoring evening and late afternoon
    time_weights = [10, 15, 20, 30, 40, 25]  # Higher weights for evening hours

    # Define age brackets with weighted probabilities
    reporter_age_brackets = [
        "Child (under 18)",
        "Young Adult (18-24)",
        "Adult (25-40)",
        "Middle-aged (41-60)",
        "Senior (61+)",
        "Unknown"
    ]

    # Weights to make adults and middle-aged more common (higher numbers = more likely)
    reporter_weights = [5, 15, 40, 30, 5, 5]  # Heavily weighted toward adults and middle-aged

    perpetrator_age_brackets = [
        "Child (under 12)",
        "Adolescent (12-17)",
        "Young Adult (18-24)",
        "Adult (25-40)",
        "Middle-aged (41-60)",
        "Senior (61+)",
        "Unknown"
    ]

    # Weights to make 18-50 more common
    perpetrator_weights = [3, 7, 25, 40, 20, 3, 2]  # Heavily weighted toward 18-50 age range
    
    # Define reporter relationship options with weights
    reporter_relationship_options = [
        "Parent",
        "Guardian", 
        "Grandparent",
        "Teacher/School Staff",
        "Neighbor",
        "Relative",
        "Sibling",
        "Social Worker",
        "Medical Professional",
        "Friend of Family",
        "Community Member",
        "Self-reporting",
        "Anonymous"
    ]
    
    # Weights for reporter relationships (higher number = more common)
    reporter_relationship_weights = [30, 15, 10, 12, 7, 8, 5, 10, 8, 6, 5, 2, 8]
    
    # Define perpetrator relationship options with weights
    perpetrator_relationship_options = [
        "Parent",
        "Step-parent",
        "Guardian",
        "Relative",
        "Sibling",
        "Family Friend",
        "Teacher",
        "Caregiver",
        "Neighbor",
        "Stranger",
        "Coach/Instructor",
        "Religious Leader",
        "Peer/Classmate",
        "Employer"
    ]
    
    # Weights for perpetrator relationships (higher number = more common)
    perpetrator_relationship_weights = [25, 15, 10, 12, 8, 10, 5, 7, 6, 5, 3, 2, 8, 4]

    for x in range(num_cases):
        random.shuffle(perp)
        random.shuffle(gender)
        
        try:
            ward = locdf.sample()
            ward = ward.to_json(orient="records")
            ward = json.loads(ward)[0]
        except (ValueError, IndexError):
            # Fallback if sampling fails
            ward = {
                "county": "Default County",
                "district": "Default District",
                "ward": "Default Ward",
                "station": "Default Station"
            }
            
        dat = {}

        # Generate a random date within the specified year range
        random_timestamp = random.randint(start_timestamp, end_timestamp)
        dt = datetime.fromtimestamp(random_timestamp)
        
        # Add day-of-week bias (more cases on weekends)
        # Get the day of the week (0 = Monday, 6 = Sunday)
        day_of_week = dt.weekday()
        
        # Apply weekend bias (retry for a weekend day with some probability)
        # 0-4 are weekdays, 5-6 are weekend days
        if day_of_week < 5:  # If it's a weekday
            # 40% chance to regenerate the date to try to get a weekend
            if random.random() < 0.4:
                # Generate a new date, keeping trying until we get a weekend or exceed retry limit
                retry_limit = 3
                retry_count = 0
                while retry_count < retry_limit and day_of_week < 5:
                    # Generate a new random date
                    random_timestamp = random.randint(start_timestamp, end_timestamp)
                    dt = datetime.fromtimestamp(random_timestamp)
                    day_of_week = dt.weekday()
                    retry_count += 1
        
        # Update day of week counter for validation
        day_of_week_counts[day_of_week] += 1
        
        # Reset the time to midnight
        dt = dt.replace(hour=0, minute=0, second=0)
        midnight_timestamp = int(dt.timestamp())
        
        # Select a time period based on weights
        selected_period = random.choices(time_periods, weights=time_weights, k=1)[0]
        
        # Generate a random time within the selected period
        random_seconds = random.randint(selected_period[0], selected_period[1])
        
        # Create the final timestamp
        random_timestamp = midnight_timestamp + random_seconds

        ctime = str(random_timestamp)
        dat["uniqueid"] = ctime + "." + str(random.randint(1000, 9999))

        dat["transcription"] = {}

        dat["translation"] = {}

        # Format start date and time with seconds
        dt = datetime.fromtimestamp(int(ctime))
        dat["startdate"] = dt.strftime("%d %b %Y")
        dat["starttime"] = dt.strftime("%H:%M:%S")

        # Get seconds since midnight for the selected time
        seconds_since_midnight = dt.hour * 3600 + dt.minute * 60 + dt.second

        # Generate talk time between 10 and 20 minutes with seconds precision
        talk_seconds = random.randint(
            10 * 60, 20 * 60
        )  # Between 10 and 20 minutes in seconds

        # Ensure the call doesn't extend beyond working hours
        end_seconds = seconds_since_midnight + talk_seconds
        if end_seconds > work_hours_end:
            talk_seconds = work_hours_end - seconds_since_midnight

        unixt = int(ctime) + talk_seconds
        dat["stoptime"] = datetime.fromtimestamp(unixt).strftime("%H:%M:%S")

        # Format talk time as minutes:seconds
        minutes = talk_seconds // 60
        seconds = talk_seconds % 60
        dat["talktime"] = f"{minutes}:{seconds:02d}"

        # Select a random main category
        main_category = random.choice(main_categories)
        dat["category"] = main_category

        # Select a random subcategory
        subcategories = list(categories[main_category].keys())
        subcategory = random.choice(subcategories)
        dat["subcateg"] = subcategory

        # Select a random specific issue if there are any
        specific_issues = categories[main_category][subcategory]
        if specific_issues:
            specific_issue = random.choice(specific_issues)
            dat["specific_issue"] = specific_issue
        else:
            dat["specific_issue"] = "General"  # Default value for empty lists

        dat["victim"] = {}
        dat["victim"]["gender"] = random.choice(gender)
        dat["victim"]["age"] = str(random.randint(3, 16))
        dat["victim"]["birthday"] = str(int(strftime("%Y")) - int(dat["victim"]["age"]))
        dat["reporter"] = {}
        dat["reporter"]["age"] = random.choices(
            reporter_age_brackets, 
            weights=reporter_weights, 
            k=1
        )[0]
        dat["reporter"]["gender"] = random.choice(gender)
        dat["reporter"]["relationship"] = random.choices(
            reporter_relationship_options, 
            weights=reporter_relationship_weights, 
            k=1
        )[0]        
        dat["county"] = ward["county"]
        dat["subcounty"] = ward["district"]
        dat["ward"] = ward["ward"]
        dat["landmark"] = ward["station"]
        dat["perpetrator"] = {}
        dat["perpetrator"]["age"] = random.choices(
            perpetrator_age_brackets, 
            weights=perpetrator_weights, 
            k=1
        )[0]
        dat["perpetrator"]["gender"] = random.choice(perp)
        dat["perpetrator"]["relationship"] = random.choices(
            perpetrator_relationship_options, 
            weights=perpetrator_relationship_weights, 
            k=1
        )[0]
        dat["counselor"] = "Counselor Name"
        dat["narrative"] = "Counselor narrative goes here"
        data.append(dat)

    # Print day of week distribution for validation
    print("Day of week distribution:")
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for day_num, count in day_of_week_counts.items():
        print(f"{days[day_num]}: {count} ({count/num_cases*100:.1f}%)")
        
    # Count and print reporter and perpetrator relationship distributions
    reporter_rel_counts = {}
    perpetrator_rel_counts = {}
    
    for case in data:
        # Count reporter relationships
        rep_rel = case["reporter"]["relationship"]
        reporter_rel_counts[rep_rel] = reporter_rel_counts.get(rep_rel, 0) + 1
        
        # Count perpetrator relationships
        perp_rel = case["perpetrator"]["relationship"]
        perpetrator_rel_counts[perp_rel] = perpetrator_rel_counts.get(perp_rel, 0) + 1
    
    print("\nReporter relationship distribution:")
    for rel, count in sorted(reporter_rel_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{rel}: {count} ({count/num_cases*100:.1f}%)")
        
    print("\nPerpetrator relationship distribution:")
    for rel, count in sorted(perpetrator_rel_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{rel}: {count} ({count/num_cases*100:.1f}%)")
    
    return data


# Example usage
if __name__ == "__main__":
    num_years = 2
    num_cases = 100000
    cases_data = generate_synthetic_data(num_years, num_cases)

    # Save to file
    if len(cases_data):
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(os.getcwd() + "/casedir/"), exist_ok=True)
            
            with open(os.getcwd() + "/casedir/cases.json", "w") as fp:
                fp.write(json.dumps(cases_data, indent=4))
            print(f"Successfully generated {len(cases_data)} cases across {num_years} year(s)")
        except Exception as e:
            print(f"Error saving data: {e}")
            # Fallback to save in current directory
            with open("cases.json", "w") as fp:
                fp.write(json.dumps(cases_data, indent=4))
            print(f"Saved {len(cases_data)} cases to current directory as cases.json")