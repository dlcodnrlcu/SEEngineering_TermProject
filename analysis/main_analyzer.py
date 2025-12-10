from data_loader import load_data_from_db
from preprocess import preprocess_data
from path_finder import find_common_paths
from generate_guide import save_guide_to_db
from datetime import datetime
import os
from dotenv import load_dotenv

def analyze_and_generate_guides(goal_url):
    """
    Orchestrates the full analysis pipeline:
    1. Loads data from DB.
    2. Preprocesses the data.
    3. Finds the most common path to a goal URL.
    4. Generates and saves a guide structure.
    """
    print("Starting full analysis pipeline...")

    # Load data
    df_raw = load_data_from_db()
    if df_raw is None or df_raw.empty:
        print("Pipeline stopped: No data loaded.")
        return

    # Preprocess data
    df_processed = preprocess_data(df_raw.copy())
    if df_processed.empty:
        print("Pipeline stopped: No data after preprocessing.")
        return

    # Find common path
    common_path = find_common_paths(df_processed, goal_url)
    if not common_path:
        print("Pipeline stopped: No common path found.")
        return

    # Generate and save guide
    # This is a simplified transformation. A real implementation would need
    # to map the abstract 'element_identifier' back to a robust CSS selector.
    guide_steps = []
    for i, step_identifier in enumerate(common_path):
        guide_steps.append({
            "selector": step_identifier, # Placeholder: this needs to be a real CSS selector
            "title": f"Step {i+1}",
            "description": f"Click on the element identified by: {step_identifier}"
        })
    
    guide_data = {
        "url": goal_url, # The guide is for the page that leads to the goal
        "steps": guide_steps,
        "analyzed_at": datetime.utcnow()
    }

    save_guide_to_db(guide_data)
    print("Analysis pipeline completed successfully.")

if __name__ == '__main__':
    # Load environment variables (e.g., MONGO_URI)
    dotenv_path = os.path.join(os.path.dirname(__file__), '../server/.env')
    load_dotenv(dotenv_path=dotenv_path)

    # This is the target URL we want to find the path to.
    # In a real system, this would be determined from business goals.
    TARGET_GOAL_URL = "http://127.0.0.1:5500/example/success.html" 

    analyze_and_generate_guides(TARGET_GOAL_URL)
