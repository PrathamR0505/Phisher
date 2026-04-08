import pandas as pd
import os
import glob

def process_datasets():
    dataset_dir = 'backend/dataset'
    output_file = 'backend/mega_dataset.csv'
    
    files = glob.glob(os.path.join(dataset_dir, '*.csv'))
    
    all_data = []
    
    # Common column names for text and label
    text_cols = ['text', 'body', 'text_combined', 'content', 'message', 'Email Text']
    subject_cols = ['subject', 'Subject', 'header']
    label_cols = ['label', 'spam', 'target', 'class', 'Label']

    print(f"Found {len(files)} files to process.")

    for file in files:
        print(f"Processing {os.path.basename(file)}...")
        
        # Try different encodings
        df = None
        for enc in ['utf-8', 'latin-1', 'cp1252']:
            try:
                df = pd.read_csv(file, encoding=enc)
                break
            except Exception:
                continue
        
        if df is None:
            print(f"  Failed to read {file}. Skipping.")
            continue

        # Identify columns
        current_text_col = next((c for c in text_cols if c in df.columns), None)
        current_subject_col = next((c for c in subject_cols if c in df.columns), None)
        current_label_col = next((c for c in label_cols if c in df.columns), None)

        if not current_text_col and not current_subject_col:
            print(f"  No text columns found in {file}. Skipping.")
            continue
        
        if current_label_col is None:
            print(f"  No label column found in {file}. Skipping.")
            continue

        # Prepare normalized dataframe
        df_norm = pd.DataFrame()
        
        # Combine subject and body if both exist
        if current_subject_col and current_text_col:
            df_norm['text'] = "Subject: " + df[current_subject_col].fillna('') + " Body: " + df[current_text_col].fillna('')
        elif current_text_col:
            df_norm['text'] = df[current_text_col].fillna('')
        elif current_subject_col:
            df_norm['text'] = "Subject: " + df[current_subject_col].fillna('')
            
        # Normalize label (assuming 1 is spam/phishing, 0 is safe)
        # Some datasets might use 'spam'/'ham' or 'phishing'/'safe' string labels
        def normalize_label(val):
            if isinstance(val, str):
                val = val.lower().strip()
                if val in ['spam', 'phishing', '1', 'yes', 'fraud']:
                    return 1
                if val in ['ham', 'safe', '0', 'no']:
                    return 0
            try:
                if int(float(val)) >= 1: return 1
                return 0
            except:
                return 0

        df_norm['spam'] = df[current_label_col].apply(normalize_label)
        
        # Drop empty text rows
        df_norm = df_norm[df_norm['text'].str.strip() != '']
        
        all_data.append(df_norm)
        print(f"  Added {len(df_norm)} rows.")

    if not all_data:
        print("No data processed.")
        return

    mega_df = pd.concat(all_data, ignore_index=True)
    print(f"Total rows in mega dataset: {len(mega_df)}")
    print(f"Safe: {len(mega_df[mega_df['spam'] == 0])}, Phishing: {len(mega_df[mega_df['spam'] == 1])}")
    
    # Optional: Shuffle data
    mega_df = mega_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    mega_df.to_csv(output_file, index=False)
    print(f"Saved to {output_file}")

if __name__ == "__main__":
    process_datasets()
