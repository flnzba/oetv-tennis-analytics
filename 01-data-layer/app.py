from curl_cffi import requests  # type: ignore
import json
import os

# no additional crawling library needed
# crawling the response (json) directly


def handle_error(status_code):
    print("Error: ", status_code)
    with open("../test/error-last-call.txt", "a") as file:
        file.write(f"Error: {status_code} \n")


url = "https://www.oetv.at/?oetvappapi=1&apikey=QWXWLwYAtSFvJGmyFtEMlypWS6fH71wk&method=nu-ranking&firstResult=0&ageRange=&subtype=general&region=&gender=male&type=oetv&itnFrom=&rankFrom=&search="

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

# error handling -> for better print of error
# last json response is saved in ./test/oetv.json
# last error is saved in ./test/error-last-call.txt
# when error occurs last response is preserved in the output folder and error is written to a file


def main():
    try:
        r = requests.get(url, headers=headers, referer=referer, impersonate="chrome")
        # c = requests.Session()
        # print(r.text)

        if r.status_code == 200:
            with open("../test/oetv.json", "w") as file:
                file.write(r.text)

            # Parse the JSON response
            rankings_data = json.loads(r.text)
            # iterate into the second object to get the data object
            d = list(rankings_data.values())[1]
            # print(d)
            # iterate into the "ranking" object to get the players
            rankings_data = list(d.values())[3]

            # Save the JSON response to a file
            with open("../test/oetv-rankings.json", "w") as file:
                rankings_data_write = str(rankings_data).replace("'", '"')
                rankings_data_write = rankings_data_write.replace("False", '"False"')
                file.write(str(rankings_data_write))

        else:
            handle_error(r.status_code)

    except Exception as e:
        handle_error(e)

    return rankings_data


def parse():
    try:
        # load data from json so api call to oetv is not needed every time
        with open("../test/oetv-rankings.json", "r") as file:
            data = json.load(file)

        for i in data:
            print(i)

    except Exception as e:
        handle_error(e)


if __name__ == "__main__":
    parse()
