import pytest
import pandas as pd
from preprocess import preprocess_data
from path_finder import find_common_paths

@pytest.fixture
def sample_log_data():
    """Fixture to create sample log data for testing."""
    data = {
        'sessionId': [
            'session1', 'session1', 'session1', 'session1', # Successful path
            'session2', 'session2', 'session2', 'session2', # Successful path (same)
            'session3', 'session3', 'session3',             # Different path
            'session4', 'session4',                         # Short session
            'session5', 'session5', 'session5', 'session5'  # Successful but different goal
        ],
        'timestamp': pd.to_datetime([
            '2024-01-01 10:00:00', '2024-01-01 10:00:01', '2024-01-01 10:00:02', '2024-01-01 10:00:03',
            '2024-01-01 10:01:00', '2024-01-01 10:01:01', '2024-01-01 10:01:02', '2024-01-01 10:01:03',
            '2024-01-01 10:02:00', '2024-01-01 10:02:01', '2024-01-01 10:02:02',
            '2024-01-01 10:03:00', '2024-01-01 10:03:01',
            '2024-01-01 10:04:00', '2024-01-01 10:04:01', '2024-01-01 10:04:02', '2024-01-01 10:04:03'
        ]),
        'type': [
            'click', 'input', 'click', 'navigation',
            'click', 'input', 'click', 'navigation',
            'click', 'click', 'navigation',
            'scroll', 'click',
            'click', 'input', 'click', 'navigation'
        ],
        'url': [
            'http://test.com/page1', 'http://test.com/page1', 'http://test.com/page1', 'http://test.com/goal',
            'http://test.com/page1', 'http://test.com/page1', 'http://test.com/page1', 'http://test.com/goal',
            'http://test.com/pageA', 'http://test.com/pageA', 'http://test.com/pageB',
            'http://test.com/start', 'http://test.com/start',
            'http://test.com/other', 'http://test.com/other', 'http://test.com/other', 'http://test.com/other_goal'
        ],
        'details': [
            {'target': {'tagName': 'BUTTON', 'id': 'btn1', 'className': 'primary'}}, {}, {'target': {'tagName': 'A', 'id': 'link1', 'className': 'nav'}}, {},
            {'target': {'tagName': 'BUTTON', 'id': 'btn1', 'className': 'primary'}}, {}, {'target': {'tagName': 'A', 'id': 'link1', 'className': 'nav'}}, {},
            {'target': {'tagName': 'BUTTON', 'id': 'btnA', 'className': 'secondary'}}, {'target': {'tagName': 'A', 'id': 'linkB', 'className': 'nav'}}, {},
            {}, {},
            {'target': {'tagName': 'BUTTON', 'id': 'btnX', 'className': 'primary'}}, {}, {'target': {'tagName': 'A', 'id': 'linkY', 'className': 'nav'}}, {}
        ]
    }
    return pd.DataFrame(data)

# ========== Tests for preprocess.py ==========

def test_preprocess_data_filters_short_sessions(sample_log_data):
    """Test that sessions with less than 3 events are removed."""
    processed_df = preprocess_data(sample_log_data)
    remaining_sessions = processed_df['sessionId'].unique()
    assert 'session4' not in remaining_sessions
    assert 'session1' in remaining_sessions
    assert 'session3' in remaining_sessions

def test_preprocess_data_empty_dataframe():
    """Test preprocessing with an empty DataFrame."""
    empty_df = pd.DataFrame(columns=['sessionId', 'timestamp'])
    processed_df = preprocess_data(empty_df)
    assert processed_df.empty

# ========== Tests for path_finder.py ==========

def test_find_common_paths_identifies_correct_path(sample_log_data):
    """Test that the most common path to a goal is found."""
    goal_url = 'http://test.com/goal'
    
    # Preprocess first to remove short sessions
    processed_df = preprocess_data(sample_log_data)
    
    common_path = find_common_paths(processed_df, goal_url)
    
    expected_path = [
        "BUTTON(id=btn1, class=primary)",
        "A(id=link1, class=nav)"
    ]
    
    assert common_path is not None
    assert common_path == expected_path

def test_find_common_paths_no_successful_sessions(sample_log_data):
    """Test behavior when no sessions reach the goal URL."""
    goal_url = 'http://test.com/non_existent_goal'
    processed_df = preprocess_data(sample_log_data)
    
    common_path = find_common_paths(processed_df, goal_url)
    
    assert common_path is None

def test_find_common_paths_empty_dataframe():
    """Test path finding with an empty DataFrame."""
    empty_df = pd.DataFrame(columns=['sessionId', 'url', 'type', 'details'])
    common_path = find_common_paths(empty_df, 'http://test.com/goal')
    assert common_path is None

