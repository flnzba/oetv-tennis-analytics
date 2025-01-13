from curl_cffi import requests # type: ignore
import os

response = requests.get('https://www.oetv.at/rangliste')
print(response.status_code)

if response.status_code == 200:
    print(response.text)

    with open('./test/oetv.html', 'w') as file:
        file.write(response.text)

if __name__ == '__main__':
    pass