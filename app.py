from curl_cffi import requests  # type: ignore
import os

# no additional crawling library needed
# crawling the response (json) directly


def handle_error(status_code):
    print("Error: ", status_code)
    with open("./test/error-last-call.txt", "w") as file:
        file.write(f"Error: {status_code}")


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

try:
    r = requests.get(url, headers=headers, referer=referer, impersonate="chrome")
    c = requests.Session()

    if r.status_code == 200:
        with open("./test/oetv.json", "w") as file:
            file.write(r.text)
    else:
        handle_error(r.status_code)
except Exception as e:
    handle_error(e)

if __name__ == "__main__":
    pass
