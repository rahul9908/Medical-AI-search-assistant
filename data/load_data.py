"""
Script to load medical records CSV into SQLite and ChromaDB
"""
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path to import from app
sys.path.append(str(Path(__file__).parent.parent))

from app.database.db import (
    init_sqlite, 
    init_chromadb, 
    get_sqlite_connection,
    embedding_model
)

def load_csv_to_sqlite():
    """Load CSV data into SQLite database"""
    print("Loading CSV into SQLite...")
    
    # Read CSV
    csv_path = Path(__file__).parent / "medical_records.csv"
    df = pd.read_csv(csv_path)
    
    print(f"Found {len(df)} records in CSV")
    
    # Connect to database
    conn = get_sqlite_connection()
    
    # Insert data
    df.to_sql('medical_records', conn, if_exists='replace', index=False)
    
    conn.close()
    print(f"✅ Loaded {len(df)} records into SQLite")
    
    return df

def load_csv_to_chromadb(df):
    """Load CSV data into ChromaDB with embeddings"""
    print("Loading data into ChromaDB...")
    
    client, collection = init_chromadb()
    
    if client is None:
        print("❌ Failed to initialize ChromaDB")
        return
    
    # Prepare documents for embedding
    documents = []
    metadatas = []
    ids = []
    
    for idx, row in df.iterrows():
        # Create rich text representation for embedding
        doc_text = f"""
        Patient: {row['patient_name']} (ID: {row['patient_id']})
        Date: {row['date']}
        Type: {row['record_type']}
        Description: {row['description']}
        Diagnosis: {row['diagnosis']}
        Medication: {row['medication']}
        Lab Results: {row['lab_result']}
        Doctor: {row['doctor']}
        """.strip()
        
        documents.append(doc_text)
        
        # Store metadata
        metadatas.append({
            "patient_id": str(row['patient_id']),
            "patient_name": str(row['patient_name']),
            "date": str(row['date']),
            "record_type": str(row['record_type']),
            "diagnosis": str(row['diagnosis']) if pd.notna(row['diagnosis']) else "",
            "medication": str(row['medication']) if pd.notna(row['medication']) else "",
        })
        
        ids.append(f"record_{idx}")
    
    print("Generating embeddings... (this may take 30-60 seconds)")
    
    # Generate embeddings
    embeddings = embedding_model.encode(documents, show_progress_bar=True)
    
    # Add to ChromaDB in batches
    batch_size = 10
    for i in range(0, len(documents), batch_size):
        batch_end = min(i + batch_size, len(documents))
        
        collection.add(
            documents=documents[i:batch_end],
            embeddings=embeddings[i:batch_end].tolist(),
            metadatas=metadatas[i:batch_end],
            ids=ids[i:batch_end]
        )
        
        print(f"Added batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
    
    print(f"✅ Loaded {len(documents)} records into ChromaDB")

def main():
    """Main loading function"""
    print("=" * 60)
    print("MEDGRAPH AI - DATA LOADING")
    print("=" * 60)
    
    # Initialize databases
    print("\n1. Initializing databases...")
    init_sqlite()
    
    # Load CSV to SQLite
    print("\n2. Loading CSV to SQLite...")
    df = load_csv_to_sqlite()
    
    # Load CSV to ChromaDB
    print("\n3. Loading CSV to ChromaDB...")
    load_csv_to_chromadb(df)
    
    print("\n" + "=" * 60)
    print("✅ DATA LOADING COMPLETE!")
    print("=" * 60)
    print(f"\nTotal records loaded: {len(df)}")
    print(f"Unique patients: {df['patient_id'].nunique()}")
    print(f"\nDatabases created:")
    print(f"  - SQLite: data/medical_records.db")
    print(f"  - ChromaDB: data/chroma_db/")
    print("\n✅ Ready to start the API server!")

if __name__ == "__main__":
    main()