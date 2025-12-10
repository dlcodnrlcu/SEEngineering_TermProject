import pandas as pd
from data_loader import load_data_from_db

def preprocess_data(df):
    """
    Performs preprocessing on the raw log data.
    - Groups logs by session.
    - Removes noise (e.g., short sessions, rapid clicks).
    """
    if df.empty:
        print("DataFrame is empty. No preprocessing to be done.")
        return df

    print("Starting preprocessing...")

    # Sort by session and time
    df = df.sort_values(by=['sessionId', 'timestamp'])

    # Example: Filter out sessions with less than 3 events
    session_counts = df['sessionId'].value_counts()
    valid_sessions = session_counts[session_counts >= 3].index
    df = df[df['sessionId'].isin(valid_sessions)]

    print(f"Preprocessing complete. {len(df)} logs remaining.")
    return df

if __name__ == '__main__':
    df_raw = load_data_from_db()
    if df_raw is not None:
        df_processed = preprocess_data(df_raw.copy())
        print("Processed DataFrame head:")
        print(df_processed.head())
