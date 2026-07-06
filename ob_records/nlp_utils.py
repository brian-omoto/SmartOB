import spacy

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("⚠️ spaCy model not found. Downloading...")
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

def extract_entities(text):
    """Extract named entities from a query using spaCy."""
    doc = nlp(text)
    
    entities = {
        "case_type": None,
        "location": None,
        "date": None,
        "persons": [],
        "all_entities": []
    }
    
    # Case type keywords
    case_keywords = ['theft', 'robbery', 'assault', 'burglary', 'traffic', 
                     'domestic', 'fraud', 'murder', 'rape', 'arson', 'forgery', 
                     'kidnapping', 'cybercrime']
    
    # Extract spaCy entities
    for ent in doc.ents:
        entities["all_entities"].append({
            "text": ent.text,
            "label": ent.label_
        })
        
        if ent.label_ == "GPE" or ent.label_ == "LOC":
            entities["location"] = ent.text
        elif ent.label_ == "DATE":
            entities["date"] = ent.text
        elif ent.label_ == "PERSON":
            entities["persons"].append(ent.text)
    
    # Manual case type detection
    text_lower = text.lower()
    for keyword in case_keywords:
        if keyword in text_lower:
            entities["case_type"] = keyword
            break
    
    return entities