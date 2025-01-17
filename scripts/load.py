from curl_cffi import requests
import json

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
# last json response is saved in ./test/oetv-rankings.json if the function is run
# last error is saved in ./test/error-last-call.txt


def main():
    all_rankings = []
    start = 0

    try:
        r = requests.get(url, headers=headers, referer=referer, impersonate="chrome")
        # c = requests.Session()
        # print(r.text)

        while start < 8000:
            paginated_url = url.replace("firstResult=0", f"firstResult={start}")
            r = requests.get(
                paginated_url, headers=headers, referer=referer, impersonate="chrome"
            )

            if r.status_code == 200:
                # # temporary file
                # with open("../test/oetv.json", "w") as file:
                #     file.write(r.text)

                # Parse the JSON response
                # iterate into the data objects
                rankings_data = json.loads(r.text)
                d = list(rankings_data.values())[1]
                rankings_data = list(d.values())[3]

                if not rankings_data:
                    break

                all_rankings.extend(rankings_data)
                start += 100

                print(f"Item {start} fetched")
            else:
                handle_error(r.status_code)
                break

    except Exception as e:
        handle_error(e)
    return all_rankings


# run the func to create json file from the response
def jsoncreate(all_rankings):
    try:
        # Save the JSON response to a file
        with open("../test/oetv-rankings.json", "w") as file:

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
