async function fetchData() {
    const response = await fetch("https://www.oetv.at/?oetvappapi=1&apikey=QWXWLwYAtSFvJGmyFtEMlypWS6fH71wk&method=nu-ranking&firstResult=0&ageRange=&subtype=general&region=&gender=male&type=oetv&itnFrom=&rankFrom=&search=", {
        "credentials": "include",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:135.0) Gecko/20100101 Firefox/135.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
            "X-WP-Nonce": "undefined",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache"
        },
        "referrer": "https://www.oetv.at/rangliste",
        "method": "GET",
        "mode": "cors"
    });

    const data = await response.json();
    console.log(data);
}

fetchData();