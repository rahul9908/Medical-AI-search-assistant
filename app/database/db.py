"""
Database setup for SQLite and ChromaDB
"""
import sqlite3
import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path

# Database paths
DB_PATH = Path("data/medical_records.db")
CHROMA_PATH = Path("data/chroma_db")

# Initialize embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def init_sqlite():
    """Initialize SQLite database with medical records schema"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create medical records table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medical_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            patient_name TEXT NOT NULL,
            date TEXT NOT NULL,
            record_type TEXT NOT NULL,
            description TEXT,
            medication TEXT,
            diagnosis TEXT,
            lab_result TEXT,
            doctor TEXT
        )
    """)
    
    # Create index for faster queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_patient_id ON medical_records(patient_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_date ON medical_records(date)
    """)
    
    conn.commit()
    conn.close()
    print("✅ SQLite database initialized")

def init_chromadb():
    """Initialize ChromaDB for vector search"""
    # Create persistent ChromaDB client
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    
    # Create or get collection
    try:
        collection = client.get_or_create_collection(
            name="medical_records",
            metadata={"description": "Medical records for semantic search"}
        )
        print("✅ ChromaDB initialized")
        return client, collection
    except Exception as e:
        print(f"❌ Error initializing ChromaDB: {e}")
        return None, None

def get_sqlite_connection():
    """Get SQLite database connection"""
    return sqlite3.connect(DB_PATH)

def get_chromadb_client():
    """Get ChromaDB client and collection"""
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    collection = client.get_collection(name="medical_records")
    return client, collection

def search_records_sqlite(query: str, patient_id: str = None):
    """Search records in SQLite using text matching"""
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    
    if patient_id:
        cursor.execute("""
            SELECT * FROM medical_records 
            WHERE patient_id = ? 
            AND (description LIKE ? OR diagnosis LIKE ? OR medication LIKE ?)
            ORDER BY date DESC
        """, (patient_id, f"%{query}%", f"%{query}%", f"%{query}%"))
    else:
        cursor.execute("""
            SELECT * FROM medical_records 
            WHERE description LIKE ? OR diagnosis LIKE ? OR medication LIKE ?
            ORDER BY date DESC
        """, (f"%{query}%", f"%{query}%", f"%{query}%"))
    
    results = cursor.fetchall()
    conn.close()
    return results

def search_records_vector(query: str, top_k: int = 5):
    """Search records using vector similarity in ChromaDB"""
    try:
        client, collection = get_chromadb_client()
        
        # Generate query embedding
        query_embedding = embedding_model.encode(query).tolist()
        
        # Search in ChromaDB
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        return results
    except Exception as e:
        print(f"❌ Error searching ChromaDB: {e}")
        return None

def get_patient_records(patient_id: str):
    """Get all records for a specific patient"""
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM medical_records 
        WHERE patient_id = ? 
        ORDER BY date DESC
    """, (patient_id,))
    
    results = cursor.fetchall()
    conn.close()
    return results

def get_all_patients():
    """Get list of all unique patients"""
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT patient_id, patient_name 
        FROM medical_records 
        ORDER BY patient_name
    """)
    
    results = cursor.fetchall()
    conn.close()
    return results

if __name__ == "__main__":
    # Initialize databases when run directly
    print("Initializing databases...")
    init_sqlite()
    init_chromadb()
    print("✅ All databases ready!")