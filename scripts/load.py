from curl_cffi import requests
import json
import time
import random
import os
from pathlib import Path

# no additional crawling library needed
# crawling the response (json) directly


def handle_error(status_code):
    print("Error: ", status_code)
    os.makedirs("../test", exist_ok=True)
    with open("../test/error-last-call.txt", "a") as file:
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
    os.makedirs("../test", exist_ok=True)
    return "../test/checkpoint.txt"


def save_checkpoint(start, all_rankings):
    with open(get_checkpoint_file(), "w") as f:
        f.write(str(start))
    
    # Optionally save the current rankings as backup
    if all_rankings:
        temp_path = "../test/rankings_checkpoint.json"
        try:
            with open(temp_path, "w") as file:
                rankings_data_write = str(all_rankings)
                rankings_data_write = rankings_data_write.replace("False", '"False"')
                rankings_data_write = rankings_data_write.replace("True", '"True"')
                rankings_data_write = rankings_data_write.replace("O'Brien", "O Brien")
                rankings_data_write = rankings_data_write.replace("D'ans", "D Ans")
                rankings_data_write = rankings_data_write.replace("'", '"')
                file.write(rankings_data_write)
        except Exception as e:
            print(f"Error saving rankings checkpoint: {e}")


def load_checkpoint():
    if os.path.exists(get_checkpoint_file()):
        with open(get_checkpoint_file(), "r") as f:
            return int(f.read().strip())
    return 0


def main():
    all_rankings = []
    start = load_checkpoint()
    total_results = 0
    max_retries = 5
    request_timeout = 30  # seconds
    
    print(f"Starting from position {start}")

    try:
        # First request to get total results
        retries = 0
        while retries < max_retries:
            try:
                r = requests.get(
                    url, 
                    headers=headers, 
                    referer=referer, 
                    impersonate="chrome",
                    timeout=request_timeout
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
        
        if retries >= max_retries:
            raise Exception("Maximum retries exceeded on initial request")

        # Main pagination loop
        while start <= total_results:
            paginated_url = url.replace("firstResult=0", f"firstResult={start}")
            retries = 0
            success = False
            
            while retries < max_retries and not success:
                try:
                    r = requests.get(
                        paginated_url,
                        headers=headers,
                        referer=referer,
                        impersonate="chrome",
                        timeout=request_timeout
                    )
                    
                    if r.status_code == 200:
                        rankings_data = json.loads(r.text)
                        all_data = list(rankings_data.values())
                        data = all_data[1]
                        rankings_data = list(data.values())[3]
                        all_rankings.extend(rankings_data)
                        
                        start += 100
                        save_checkpoint(start, all_rankings)
                        
                        print(f"Item {start} fetched. Total items so far: {len(all_rankings)}")
                        success = True
                        
                        # Add a random delay between requests to avoid rate limiting
                        time.sleep(random.uniform(0.5, 2.0))
                    else:
                        print(f"Error status code: {r.status_code}, retrying...")
                        retries += 1
                        time.sleep(5 * retries)  # Increasing backoff
                        
                except Exception as e:
                    print(f"Exception during pagination: {e}")
                    retries += 1
                    time.sleep(5 * retries)
            
            if not success:
                print(f"Failed to fetch data at position {start} after {max_retries} retries. Continuing...")
                start += 100  # Skip this batch and continue
                save_checkpoint(start, all_rankings)

    except Exception as e:
        print(f"Fatal error: {e}")
        handle_error(str(e))
        # Still save what we have so far
        save_checkpoint(start, all_rankings)
    
    print(f"Completed fetching {len(all_rankings)} records")
    return all_rankings


# run the func to create json file from the response
def jsoncreate(all_rankings):
    try:
        # Save the JSON response to a file
        os.makedirs("../test", exist_ok=True)
        with open("../test/rankings.json", "w") as file:

            rankings_data_write = str(all_rankings)
            rankings_data_write = rankings_data_write.replace("False", '"False"')
            rankings_data_write = rankings_data_write.replace("True", '"True"')
            rankings_data_write = rankings_data_write.replace("O'Brien", "O Brien")
            rankings_data_write = rankings_data_write.replace("D'ans", "D Ans")
            rankings_data_write = rankings_data_write.replace("'", '"')

            file.write(rankings_data_write)

    except Exception as e:
        handle_error(e)


if __name__ == "__main__":
    jsoncreate(main())
    # print(type(main()))
