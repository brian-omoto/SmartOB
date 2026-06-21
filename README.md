# SmartOB: AI-Assisted Search for Digitised Police Occurrence Books

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0-green.svg)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-blue.svg)](https://www.postgresql.org/)
[![pgvector](https://img.shields.io/badge/pgvector-0.5-orange.svg)](https://github.com/pgvector/pgvector)
[![spaCy](https://img.shields.io/badge/spaCy-3.8-purple.svg)](https://spacy.io/)

## 📋 Problem Statement

Kenyan police officers currently spend **15–30 minutes** searching for a single OB record in handwritten or basic digital logs. Manipulated records allow criminals to evade capture, prolong suspect detention, and erode public trust in the justice system.

## 💡 Solution

SmartOB adds an intelligent natural language search layer to existing digital OBs. Officers simply type a plain English query and receive **ranked, relevant results in under 5 seconds**.

### Key Features

- 🔍 **Natural Language Search** – Type plain English queries like *"theft in Langata"*
- 🧠 **Semantic Similarity** – Uses pgvector to find meaning, not just keyword matches
- 📊 **Ranked Results** – Returns top matches with similarity scores
- 👨‍💼 **Admin Dashboard** – Full CRUD operations, user management, logs, CSV export
- 📦 **Offline Ready** – Runs completely inside a Docker container

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Django | Web framework |
| PostgreSQL + pgvector | Database & vector search |
| spaCy | Named entity extraction |
| Sentence Transformers | Generating embeddings |
| Docker | Containerization & offline demo |
| Faker | Generating mock data |

## 📂 Project Structure

SmartOB/
├── .venv/ # Virtual environment
├── ob_records/ # Django app
│ ├── models.py # User, OBRecord, AuditLog, QueryLog
│ ├── views.py # Search views
│ ├── admin.py # Admin interface
│ └── migrations/ # Database migrations
├── smartob/ # Django project
│ └── settings.py # Configuration
├── templates/ # HTML templates
├── static/ # CSS/JS files
├── generate_mock_data.py # Generate 200 Kenyan OB records
├── generate_embeddings.py # Generate vector embeddings
├── requirements.txt # Python dependencies
├── Dockerfile # Docker configuration
├── docker-compose.yml # Multi-container setup
└── README.md # This file

Section 6: Quick Start (Setup)
markdown
## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 17+ with pgvector
- Docker (optional)

### Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/brian-omoto/SmartOB.git
   cd SmartOB

2. Create and activate virtual environment:

--bash--
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

3. Install dependencies:

--bash--
pip install -r requirements.txt
python -m spacy download en_core_web_sm

4. Set up PostgreSQL database:

--sql--
CREATE DATABASE smartob_db;
CREATE EXTENSION IF NOT EXISTS vector;

5. Configure settings.py:

--python--
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'smartob_db',
        'USER': 'postgres',
        'PASSWORD': '5434',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

6. Run migrations:

--bash--
python manage.py makemigrations ob_records
python manage.py migrate

7. Generate mock data:

--bash--
python generate_mock_data.py

8. Generate embeddings:

--bash--
python generate_embeddings.py

9. Create superuser:

--bash--
python manage.py createsuperuser

10. Run the server:

--bash--
python manage.py runserver

11. Access the application: 

Admin: http://localhost:8000/admin

Search: http://localhost:8000



---

### Section 7: Docker Setup

```markdown
### Docker Setup (Offline Demo)

```bash
docker-compose up --build


---

### Section 8: Testing Semantic Search

```markdown
## 🧪 Testing Semantic Search

```python
from sentence_transformers import SentenceTransformer
import psycopg2

model = SentenceTransformer('all-MiniLM-L6-v2')
query = "theft in Langata"
query_embedding = model.encode(query).tolist()

conn = psycopg2.connect(
    dbname="smartob_db",
    user="postgres",
    password="5434",
    host="localhost",
    port=5432
)
cur = conn.cursor()

cur.execute("""
    SELECT ob_number, case_summary, 1 - (embedding <=> %s::vector) AS similarity
    FROM ob_records
    WHERE embedding IS NOT NULL
    ORDER BY embedding <=> %s::vector
    LIMIT 5
""", (query_embedding, query_embedding))

for row in cur.fetchall():
    print(f"{row[0]} - Similarity: {row[2]:.4f}")
    print(f"  {row[1][:100]}...")


---

### Section 9: Database Schema

```markdown
## Database Schema

| Table | Purpose |
|-------|---------|
| `users` | Unified user accounts (officer/admin) |
| `ob_records` | Main OB entries with 384-dim embedding |
| `audit_logs` | Admin action logs (CRUD, login, export) |
| `query_logs` | Officer search history |

Section 10: Sample Results

## Sample Query Results
OB 485/23/11/2024 - Similarity: 0.6123
Report of theft at Langata. Miss Faith Hassan claims headphones taken...

OB 159/23/06/2024 - Similarity: 0.6101
James Njoroge reported power bank stolen from Langata...

OB 617/02/04/2025 - Similarity: 0.5945
Theft of television reported by Chief Stephen Musalia of Langata...


Section 11: Future Improvements

## Future Improvements

- Integration with real NPS databases
- Mobile application
- Advanced analytics dashboard
- Real-time crime mapping

Section 12: Contributors and License

## Contributors

- Omoto Brian (192885)
- Kwikiriza Abraham (191866)

## License

MIT

---

**SmartOB: Making Kenyan police work smarter, faster, and fairer 🇰🇪**