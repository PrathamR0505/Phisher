import os
import pandas as pd

dataset_dir = 'backend/dataset'
files = [f for f in os.listdir(dataset_dir) if f.endswith('.csv')]

for file in files:
    path = os.path.join(dataset_dir, file)
    print(f"--- {file} ---")
    try:
        # Try a few encodings
        for enc in ['utf-8', 'latin-1', 'cp1252']:
            try:
                df = pd.read_csv(path, nrows=1, encoding=enc)
                print(f"Columns: {df.columns.tolist()}")
                print(f"Sample:\n{df.head(1).to_string()}")
                break
            except:
                continue
    except Exception as e:
        print(f"Error {e}")
