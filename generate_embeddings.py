import os
import django
import psycopg2
from sentence_transformers import SentenceTransformer

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartob.settings')
django.setup()

from ob_records.models import OBRecord

print("Loading sentence transformer model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded successfully!")

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="smartob_db",
    user="postgres",
    password="5434",
    host="localhost",
    port=5432
)
cur = conn.cursor()

# Get records without embeddings
cur.execute("""
    SELECT ob_id, case_summary, complainant_name, suspect_names, location, case_type
    FROM ob_records
    WHERE embedding IS NULL
""")
records = cur.fetchall()

print(f"Found {len(records)} records without embeddings")

if len(records) == 0:
    print("All records already have embeddings!")
    cur.close()
    conn.close()
    exit()

# Generate embeddings for each record
for ob_id, case_summary, complainant, suspect, location, case_type in records:
    # Combine relevant fields for a richer embedding
    text = f"{case_type} {location} {case_summary}"
    if complainant:
        text += f" Complainant: {complainant}"
    if suspect:
        text += f" Suspect: {suspect}"
    
    # Generate embedding
    embedding = model.encode(text).tolist()
    
    # Update database
    cur.execute(
        "UPDATE ob_records SET embedding = %s WHERE ob_id = %s",
        (embedding, ob_id)
    )
    print(f"Updated OB {ob_id}")

# Commit changes
conn.commit()
cur.close()
conn.close()

print(f"\n✅ Successfully generated embeddings for {len(records)} records!")
print("You can now perform semantic search on your OB records.")