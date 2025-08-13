from curl_cffi import requests
import json
import time
import random
import os
from datetime import datetime

# no additional crawling library needed
# crawling the response (json) directly


def handle_error(status_code):
    print("Error: ", status_code)
    # Get the base directory from environment or use a default
    DATA_DIR = os.environ.get('DATA_DIR', os.path.dirname(os.path.abspath(__file__)))
    log_dir = os.path.join(DATA_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)
    with open(os.path.join(log_dir, "error-last-call.txt"), "a") as file:
        file.write(f"Error: {status_code} \n")


url = "https://www.oetv.at/?oetvappapi=1&apikey=QWXWLwYAtSFvJGmyFtEMlypWS6fH71wk&method=nu-ranking&firstResult=0&ageRange=&subtype=general&region=&gender=male&type=itn&itnFrom=&rankFrom=&search="


# change headers to your liking
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
    "X-WP-Nonce": "undefined",
    "X-Requested-With": "XMLHttpRequest",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
}

referer = "https://www.oetv.at/rangliste/"


def get_checkpoint_file():
    # Get the base directory from environment or use a default
    # This allows configuration in Docker environments
    DATA_DIR = os.environ.get('DATA_DIR', os.path.dirname(os.path.abspath(__file__)))
    checkpoint_dir = os.path.join(DATA_DIR, "checkpoints")
    os.makedirs(checkpoint_dir, exist_ok=True)
    return os.path.join(checkpoint_dir, "checkpoint.txt")


def save_checkpoint(start, all_rankings=None):
    with open(get_checkpoint_file(), "w") as f:
        f.write(str(start))
    
    # Optionally save the current rankings as backup
    if all_rankings:
        # Get the base directory from environment or use a default
        DATA_DIR = os.environ.get('DATA_DIR', os.path.dirname(os.path.abspath(__file__)))
        checkpoint_dir = os.path.join(DATA_DIR, "checkpoints")
        os.makedirs(checkpoint_dir, exist_ok=True)
        temp_path = os.path.join(checkpoint_dir, "rankings_checkpoint.json")
        try:
            with open(temp_path, "w") as file:
                json.dump(all_rankings, file)
        except Exception as e:
            print(f"Error saving rankings checkpoint: {e}")


def load_checkpoint():
    if os.path.exists(get_checkpoint_file()):
        with open(get_checkpoint_file(), "r") as f:
            return int(f.read().strip())
    return 0


def setup_api_client():
    """Set up and return client configuration for API requests"""
    return {
        'url': url,
        'headers': headers,
        'referer': referer,
        'timeout': 30,  # seconds
        'max_retries': 5,
        'base_delay': 1.0
    }


def get_data_batches(client):
    """Generator function that yields batches of player data as they're fetched.
    
    Parameters:
    - client: Dictionary containing API client configuration
    
    Yields:
    - Batch of player records (list of dictionaries)
    """
    start = load_checkpoint()
    total_results = 0
    consecutive_errors = 0
    max_consecutive_errors = 3
    
    print(f"Starting batch fetching from position {start} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # First request to get total results
        retries = 0
        while retries < client['max_retries']:
            try:
                r = requests.get(
                    client['url'], 
                    headers=client['headers'], 
                    referer=client['referer'], 
                    impersonate="chrome",
                    timeout=client['timeout']
                )
                if r.status_code == 200:
                    rankings_data = json.loads(r.text)
                    all_data = list(rankings_data.values())
                    all_data = list(all_data[1].values())
                    total_results = all_data[0]
                    print(f"Total results to fetch: {total_results}")
                    break
                else:
                    print(f"Error status code: {r.status_code}, retrying...")
                    retries += 1
                    time.sleep(5 * retries)  # Increasing backoff
            except Exception as e:
                print(f"Exception during initial request: {e}")
                retries += 1
                time.sleep(5 * retries)
        
        if retries >= client['max_retries']:
            raise Exception("Maximum retries exceeded on initial request")

        # Main pagination loop
        base_delay = client['base_delay']
        while start <= total_results:
            paginated_url = client['url'].replace("firstResult=0", f"firstResult={start}")
            retries = 0
            success = False
            
            while retries < client['max_retries'] and not success:
                try:
                    r = requests.get(
                        paginated_url,
                        headers=client['headers'],
                        referer=client['referer'],
                        impersonate="chrome",
                        timeout=client['timeout']
                    )
                    
                    if r.status_code == 200:
                        try:
                            # Debug: save raw response for analysis if needed
                            if start > 90000 and start < 95000:
                                # Get the base directory from environment or use a default
                                DATA_DIR = os.environ.get('DATA_DIR', os.path.dirname(os.path.abspath(__file__)))
                                debug_dir = os.path.join(DATA_DIR, "debug")
                                os.makedirs(debug_dir, exist_ok=True)
                                with open(os.path.join(debug_dir, f"debug_response_{start}.json"), "w") as f:
                                    f.write(r.text)
                            
                            rankings_data = json.loads(r.text)
                            
                            # Validate structure and adapt to different response formats
                            if isinstance(rankings_data, dict):
                                all_data = list(rankings_data.values())
                                
                                # Check if structure matches expected format
                                if len(all_data) > 1 and isinstance(all_data[1], dict):
                                    data = all_data[1]
                                    values_list = list(data.values())
                                    
                                    if len(values_list) > 3 and isinstance(values_list[3], list):
                                        rankings_data = values_list[3]
                                    else:
                                        # Try to find a list in the values that contains player data
                                        for item in values_list:
                                            if isinstance(item, list) and len(item) > 0 and isinstance(item[0], dict) and "playerId" in item[0]:
                                                rankings_data = item
                                                break
                                else:
                                    # Try alternative parsing: find any list with player data
                                    for key, value in rankings_data.items():
                                        if isinstance(value, dict):
                                            for subkey, subvalue in value.items():
                                                if isinstance(subvalue, list) and len(subvalue) > 0 and isinstance(subvalue[0], dict) and "playerId" in subvalue[0]:
                                                    rankings_data = subvalue
                                                    break
                            elif isinstance(rankings_data, list):
                                # The response might already be a list of players
                                # Check if it looks like player data
                                if len(rankings_data) > 0 and isinstance(rankings_data[0], dict) and "playerId" in rankings_data[0]:
                                    # It's already in the format we need
                                    pass
                                else:
                                    # Not recognized format
                                    raise ValueError(f"Unrecognized list format in response at position {start}")
                            else:
                                raise ValueError(f"Unexpected response type: {type(rankings_data)}")
                            
                            # Final validation - ensure we have a list of player dictionaries
                            if not isinstance(rankings_data, list):
                                raise ValueError(f"Failed to extract player list from response at position {start}")
                            
                            # Validate that the extracted data has the expected structure
                            if len(rankings_data) > 0 and isinstance(rankings_data[0], dict) and "playerId" in rankings_data[0]:
                                # Yield this batch of players
                                print(f"Yielding batch of {len(rankings_data)} records from position {start}")
                                yield rankings_data
                            else:
                                raise ValueError(f"Extracted data doesn't match expected player format at position {start}")
                            
                            # Update position for next batch
                            start += 100
                            save_checkpoint(start)
                            
                            print(f"Batch at position {start} fetched")
                            success = True
                            
                            # Dynamically adjust delay based on success pattern
                            if consecutive_errors > 0:
                                consecutive_errors = 0
                                # Increase delay slightly after recovering from errors
                                base_delay = min(base_delay * 1.2, 5.0)
                            else:
                                # Gradually decrease delay on consistent success
                                base_delay = max(base_delay * 0.9, 0.5)
                                
                            # Add some randomness to the delay
                            time.sleep(base_delay + random.uniform(0.1, 1.0))
                        except Exception as parse_error:
                            consecutive_errors += 1
                            
                            # Save the problematic response for debugging
                            # Get the base directory from environment or use a default
                            DATA_DIR = os.environ.get('DATA_DIR', os.path.dirname(os.path.abspath(__file__)))
                            debug_dir = os.path.join(DATA_DIR, "debug")
                            os.makedirs(debug_dir, exist_ok=True)
                            error_path = os.path.join(debug_dir, f"error_response_{start}.json")
                            with open(error_path, "w") as f:
                                f.write(r.text)
                            print(f"Error parsing data at position {start}: {parse_error}")
                            print(f"Saved problematic response to {error_path}")
                            handle_error(f"Parse error at position {start}: {parse_error}")
                            
                            # Exponentially increase delay on consecutive errors
                            retry_delay = base_delay * (2 ** retries)
                            print(f"Backing off for {retry_delay:.2f} seconds before retry {retries+1}/{client['max_retries']}")
                            time.sleep(retry_delay)
                            
                            # Try to continue with the next batch instead of completely failing
                            retries += 1
                            if retries >= client['max_retries']:
                                # Skip this batch after max retries
                                print(f"Skipping batch at position {start} after {client['max_retries']} failed attempts")
                                start += 100
                                save_checkpoint(start)
                                success = True
                                
                                # Check if we're having too many consecutive errors
                                if consecutive_errors >= max_consecutive_errors:
                                    print(f"Too many consecutive errors ({consecutive_errors}). Taking a long break...")
                                    time.sleep(60)  # Take a 1-minute break
                    else:
                        consecutive_errors += 1
                        print(f"Error status code: {r.status_code}, retrying...")
                        
                        # Exponential backoff on HTTP errors
                        retry_delay = 5 * (2 ** retries)
                        print(f"Backing off for {retry_delay} seconds")
                        time.sleep(retry_delay)
                        retries += 1
                        
                except Exception as e:
                    consecutive_errors += 1
                    print(f"Exception during pagination: {e}")
                    # Exponential backoff on exceptions
                    retry_delay = 5 * (2 ** retries)
                    print(f"Backing off for {retry_delay} seconds")
                    time.sleep(retry_delay)
                    retries += 1
            
            if not success:
                print(f"Failed to fetch data at position {start} after {client['max_retries']} retries. Continuing...")
                start += 100  # Skip this batch and continue
                save_checkpoint(start)

    except Exception as e:
        print(f"Fatal error: {e}")
        handle_error(str(e))
        # Still save the checkpoint
        save_checkpoint(start)
        raise
    
    print(f"Completed fetching all records at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """Legacy function for backward compatibility - fetches all data at once"""
    all_rankings = []
    client = setup_api_client()
    
    # Use the batch generator but collect all results
    for batch in get_data_batches(client):
        all_rankings.extend(batch)
    
    return all_rankings


# run the func to create json file from the response
def jsoncreate(all_rankings):
    try:
        # Save the JSON response to a file
        # Get the base directory from environment or use a default
        DATA_DIR = os.environ.get('DATA_DIR', os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(DATA_DIR, "data")
        os.makedirs(data_dir, exist_ok=True)
        with open(os.path.join(data_dir, "rankings.json"), "w") as file:
            json.dump(all_rankings, file)
    except Exception as e:
        handle_error(e)


if __name__ == "__main__":
    jsoncreate(main())
    # print(type(main()))
