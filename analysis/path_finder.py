import pandas as pd

def find_common_paths(df, goal_url):
    """
    Analyzes sessions that reached a specific goal URL to find common paths.
    """
    if df.empty:
        print("DataFrame is empty. Cannot find paths.")
        return None

    print(f"Finding common paths to goal: {goal_url}")

    # 1. Filter sessions that successfully reached the goal URL
    successful_sessions = df[df['url'] == goal_url]['sessionId'].unique()
    df_success = df[df['sessionId'].isin(successful_sessions)]
    
    if df_success.empty:
        print("No sessions found that reached the goal URL.")
        return None

    print(f"Found {len(successful_sessions)} successful sessions.")

    # 2. Focus on click events and create a representation of the element
    df_clicks = df_success[df_success['type'] == 'click'].copy()
    df_clicks['element_identifier'] = df_clicks['details'].apply(
        lambda d: f"{d['target']['tagName']}(id={d['target']['id']}, class={d['target']['className']})"
    )

    # 3. For each session, create the sequence of clicks
    path_sequences = df_clicks.groupby('sessionId')['element_identifier'].apply(list)
    
    # 4. Use a simple frequency count to find the most common sequence (as a placeholder)
    # A more advanced approach would use sequence mining algorithms (e.g., Apriori, GSP)
    if path_sequences.empty:
        print("No click sequences found in successful sessions.")
        return None
        
    most_common_sequence = path_sequences.value_counts().idxmax()

    print("Most common path sequence found:")
    print(most_common_sequence)
    
    return most_common_sequence

if __name__ == '__main__':
    # This is a placeholder for testing.
    # In a real scenario, you'd load preprocessed data.
    from preprocess import preprocess_data
    from data_loader import load_data_from_db

    df_raw = load_data_from_db()
    if df_raw is not None:
        df_processed = preprocess_data(df_raw)
        # Define a goal URL for analysis
        # In a real scenario, this would be dynamically determined
        EXAMPLE_GOAL_URL = "http://127.0.0.1:5500/example/page2.html" 
        find_common_paths(df_processed, EXAMPLE_GOAL_URL)
