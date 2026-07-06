import os
import django
import psycopg2
from faker import Faker
import random
from datetime import datetime, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartob.settings')
django.setup()

from ob_records.models import OBRecord

# Initialize Faker with Kenyan locale
fake = Faker('en_KE')

# Kenyan police station locations
KENYAN_LOCATIONS = [
    'Langata', 'Kilimani', 'Central', 'Embakasi', 'Kasarani', 'Westlands',
    'Dagoretti', 'Kamukunji', 'Makadara', 'Starehe', 'Roysambu', 'Ruaraka',
    'Kibra', 'Mathare', 'Njiru', 'Karen', 'Kileleshwa', 'Parklands',
    'Ngara', 'Buruburu', 'Umoja', 'Donholm', 'Tena', 'Ruiru', 'Thika Road',
    'Mombasa Road', 'Jogoo Road', 'Kenyatta Avenue', 'Moi Avenue', 'Kimathi Street',
    'Nairobi West', 'South B', 'South C', 'Eastleigh', 'Kariokor', 'Pangani',
    'Kawangware', 'Kangemi', 'Kabete', 'Uthiru', 'Kikuyu', 'Limuru', 'Rongai'
]

# Kenyan case types
CASE_TYPES = [
    'theft', 'robbery', 'assault', 'burglary', 'traffic', 'domestic_violence', 
    'fraud', 'murder', 'rape', 'defilement', 'arson', 'forgery', 'drug_trafficking',
    'kidnapping', 'cybercrime', 'grievous_bodily_harm', 'corruption', 'embezzlement'
]

# Kenyan first names 
KENYAN_FIRST_NAMES = [
    'John', 'James', 'David', 'Peter', 'Michael', 'Stephen', 'Joseph', 'Samuel',
    'Kenneth', 'Francis', 'Paul', 'William', 'George', 'Charles', 'Anthony', 'Mark',
    'Mary', 'Susan', 'Jane', 'Margaret', 'Elizabeth', 'Grace', 'Ruth', 'Esther',
    'Joyce', 'Judith', 'Alice', 'Rose', 'Ann', 'Lucy', 'Catherine', 'Mercy',
    'Faith', 'Hope', 'Charity', 'Patience', 'Sylvia', 'Caroline', 'Dorothy', 'Helen',
    'James', 'Patrick', 'Robert', 'Daniel', 'Matthew', 'Luke', 'Simon', 'Andrew',
    'Josephine', 'Monica', 'Brenda', 'Rachel', 'Sarah', 'Rebecca', 'Naomi', 'Deborah'
]

# Kenyan last names 
KENYAN_LAST_NAMES = [
    'Odhiambo', 'Ochieng', 'Otieno', 'Omondi', 'Ouma', 'Oduor', 'Onyango', 'Oloo',
    'Owino', 'Okoth', 'Opiyo', 'Omolo', 'Odeke', 'Odera', 'Olouch', 'Owuor',
    'Mwangi', 'Njoroge', 'Kamau', 'Kariuki', 'Wanjiru', 'Ngugi', 'Kibunja', 'Ndirangu',
    'Waweru', 'Maina', 'Ndegwa', 'Muthoni', 'Nyambura', 'Wambui', 'Njuguna', 'Wangari',
    'Kioko', 'Mutua', 'Mutuku', 'Mulei', 'Muendo', 'Kimeu', 'Kilonzi', 'Ndeti',
    'Hassan', 'Mohamed', 'Ali', 'Ahmed', 'Abdi', 'Hassan', 'Omar', 'Yusuf',
    'Singh', 'Patel', 'Kaur', 'Sharma', 'Gill', 'Verma', 'Shah', 'Bhatia',
    'Mukhwana', 'Musalia', 'Wanyonyi', 'Nabwera', 'Webale', 'Khangati', 'Wamalwa',
    'Lekolool', 'Lekishon', 'Ntaiyia', 'Kiprotich', 'Kipchoge', 'Kemboi', 'Koech'
]

# Items commonly stolen in Kenya
ITEMS = [
    'mobile phone', 'laptop', 'wallet', 'cash', 'television', 'jewelry', 
    'bicycle', 'car', 'motorcycle', 'handbag', 'shoes', 'groceries',
    'cattle', 'goats', 'sheep', 'chicken', 'matatu fare', 'street light battery',
    'tablet', 'smart watch', 'power bank', 'headphones', 'luggage'
]

# Common break-in points in Kenyan homes/businesses
ENTRY_POINTS = [
    'door', 'window', 'back gate', 'unlocked door', 'broken window', 'skylight',
    'garage door', 'balcony', 'roof', 'barred window', 'side door', 'living room window',
    'kitchen door', 'bedroom window', 'main gate'
]

# Generate OB number in Kenyan format
def generate_ob_number():
    year = datetime.now().year
    days = random.randint(1, 365)
    return f"OB {random.randint(1, 999)}/{days:02d}/{year}"

# Generate realistic case summary
def generate_case_summary(case_type, location, complainant, suspect_names):
    time_period = random.choice(['morning', 'afternoon', 'evening', 'night', 'dawn'])
    time_hour = random.randint(1, 12)
    time_minute = random.randint(0, 59)
    item = random.choice(ITEMS)
    entry = random.choice(ENTRY_POINTS)
    
    summary_templates = {
        'theft': [
            f"Complainant reported theft of {item} from {location} premises at {time_hour}:{time_minute:02d} {time_period}. The {item} was last seen at {time_hour-1}:{time_minute:02d} {time_period}. Suspect is believed to have accessed through the {entry}.",
            f"{complainant} reported {item} stolen from {location} at approximately {time_hour}:{time_minute:02d} {time_period}. The item was placed at the {entry} and found missing. No signs of forced entry.",
            f"Theft of {item} reported by {complainant} of {location}. Incident occurred at about {time_hour}:{time_minute:02d} {time_period}. Suspect left evidence at the {entry}.",
            f"Report of theft at {location}. {complainant} claims {item} taken between {time_hour}:{time_minute:02d} and {time_hour+1}:{time_minute:02d} {time_period}. Suspect escaped through the {entry}."
        ],
        'robbery': [
            f"{complainant} was robbed at {location} at {time_hour}:{time_minute:02d} {time_period}. The suspect(s) demanded {item} and cash from the victim and fled on foot.",
            f"Armed robbery reported at {location}. {complainant} was approached by unknown persons at {time_hour}:{time_minute:02d} {time_period} and relieved of {item} and personal effects.",
            f"Robbery incident at {location}. {complainant} was attacked at {time_hour}:{time_minute:02d} {time_period} and robbed of {item}. Suspects escaped the scene."
        ],
        'assault': [
            f"{complainant} reported assault at {location} at {time_hour}:{time_minute:02d} {time_period}. Victim sustained injuries to the {random.choice(['face', 'head', 'arms', 'legs', 'back'])}.",
            f"Assault incident at {location}. {complainant} was attacked by unknown person(s) at {time_hour}:{time_minute:02d} {time_period}. Victim treated and discharged.",
            f"{complainant} of {location} reported being assaulted at {time_hour}:{time_minute:02d} {time_period}. Suspect is believed to be known to the victim."
        ],
        'burglary': [
            f"{complainant} reported a break-in at their {location} residence at {time_hour}:{time_minute:02d} {time_period}. The suspects entered through the {entry} and stole {item}.",
            f"Burglary at {location} premises. {complainant} discovered forced entry through the {entry} and items including {item} missing.",
            f"Break-in reported at {location}. The suspects used the {entry} to gain access and stole {item} at {time_hour}:{time_minute:02d} {time_period}."
        ],
        'traffic': [
            f"Traffic accident reported at {location} at {time_hour}:{time_minute:02d} {time_period}. Vehicle involved sustained damage to the {random.choice(['front', 'rear', 'side', 'bumper'])}.",
            f"Road traffic incident at {location}. {complainant} reported minor collision at {time_hour}:{time_minute:02d} {time_period}. No injuries reported.",
            f"{complainant} reported traffic offense at {location} involving {item}. Incident occurred at {time_hour}:{time_minute:02d} {time_period}."
        ],
        'domestic_violence': [
            f"{complainant} reported domestic incident at {location} at {time_hour}:{time_minute:02d} {time_period}. Physical altercation between family members.",
            f"Domestic disturbance reported at {location}. {complainant} alleges assault by {random.choice(['spouse', 'parent', 'child', 'relative'])} at {time_hour}:{time_minute:02d} {time_period}.",
            f"Report of domestic violence at {location}. Victim {complainant} sustained injuries and suspects a known family member."
        ],
        'fraud': [
            f"{complainant} reported fraud at {location}. Victim was conned of {item} worth KES {random.randint(5000, 500000)} at {time_hour}:{time_minute:02d} {time_period}.",
            f"Fraud complaint from {complainant} of {location}. Suspect used fake documents to obtain {item} worth KES {random.randint(10000, 1000000)}.",
            f"{complainant} reported being defrauded at {location}. Incident occurred at {time_hour}:{time_minute:02d} {time_period}."
        ]
    }
    
    templates = summary_templates.get(case_type, summary_templates['theft'])
    return random.choice(templates)

# Generate realistic Kenyan names
def generate_kenyan_name():
    first_name = random.choice(KENYAN_FIRST_NAMES)
    last_name = random.choice(KENYAN_LAST_NAMES)
    titles = ['Mr ', 'Mrs ', 'Ms ', 'Miss ', 'Dr ', 'Prof ', 'Rev ', 'Chief ', '']
    title = random.choice(titles)
    return f"{title}{first_name} {last_name}".strip()

# Generate suspect names (0-3 suspects)
def generate_suspects():
    suspect_count = random.randint(0, 3)
    suspects = []
    for _ in range(suspect_count):
        suspects.append(generate_kenyan_name())
    return ', '.join(suspects) if suspects else ''

# Generate single location
def generate_location():
    return random.choice(KENYAN_LOCATIONS)

# Generate investigating officer
def generate_officer():
    name = generate_kenyan_name()
    for title in ['Mr ', 'Mrs ', 'Ms ', 'Miss ', 'Dr ', 'Prof ', 'Rev ', 'Chief ']:
        name = name.replace(title, '')
    return f"IP. {name}"

def generate_mock_data(num_records=200):
    print(f"Generating {num_records} mock OB records...")
    
    conn = psycopg2.connect(
        dbname="smartob_db",
        user="postgres",
        password="5434",
        host="localhost",
        port=5432
    )
    cur = conn.cursor()
    
    # Check if records already exist
    cur.execute("SELECT COUNT(*) FROM ob_records")
    count = cur.fetchone()[0]
    
    if count > 0:
        print(f"Records already exist ({count} records).")
        choice = input("Do you want to delete existing records and generate new ones? (y/n): ")
        if choice.lower() == 'y':
            cur.execute("DELETE FROM ob_records")
            print("Existing records deleted.")
        else:
            print("Keeping existing records. Exiting...")
            cur.close()
            conn.close()
            return
    
    generated = 0
    for i in range(num_records):
        date_reported = fake.date_between(start_date='-2y', end_date='today')
        ob_number = f"OB {random.randint(1, 999)}/{date_reported.strftime('%d')}/{date_reported.strftime('%m')}/{date_reported.strftime('%Y')}"
        
        case_type = random.choice(CASE_TYPES)
        location = generate_location()
        complainant = generate_kenyan_name()
        suspect_names = generate_suspects()
        investigating_officer = generate_officer()
        case_summary = generate_case_summary(case_type, location, complainant, suspect_names)
        
        # Insert into database
        cur.execute("""
            INSERT INTO ob_records 
            (ob_number, date_reported, case_type, location, complainant_name, suspect_names, case_summary, investigating_officer, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """, (ob_number, date_reported, case_type, location, complainant, suspect_names, case_summary, investigating_officer))
        
        generated += 1
        if generated % 10 == 0:
            print(f"Generated {generated} records...")
    
    conn.commit()
    cur.close()
    conn.close()
    
    print(f"\n✅ Successfully generated {generated} mock OB records!")
    print(f"   - {len(CASE_TYPES)} case types")
    print(f"   - {len(KENYAN_LOCATIONS)} locations")
    print("   - Kenyan-style names and realistic OB entries")

if __name__ == "__main__":
    generate_mock_data(200)  