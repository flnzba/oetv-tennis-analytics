# Data Visualization App with Streamlit

This application is designed to scrape ranking data from the ÖTV website, store it locally in a SQLite database, and display the data through a bar chart on a Streamlit web app. This setup provides an easy-to-use interface for analyzing and visualizing the data, all containerized with Docker for easy deployment and scalability.

![cover-oetv-analytics](https://github.com/user-attachments/assets/26f4b010-3ff7-49b2-994d-816a6e5f63d2)

## Features

- **Web Scraping**: Automatically scrapes data from the specified ÖTV rankings webpage.
- **Data Storage**: Uses SQLite for efficient local data storage.
- **Data Visualization**: Visualizes the data in a bar chart format using Matplotlib.
- **Web Application**: Streamlit framework provides a user-friendly web interface.
- **Docker Support**: Everything is dockerized for easy setup and portability.

## Analytics

1. Normalized Ranking
2. If I have an ITN of X then I am better then Y% of players
3. If I have an ITN of X then I am better then Y% of players in my age group
4. If I have an ITN of X then I am better then Y% of players in my region
5. Change of number of players since last Date X

## Prerequisites

Before you begin, ensure you have the following installed on your system:
- Python 3.12.7+
Optional:
- Docker (for containerized deployment)
- node (if you want to test the fetch directly via js -> app.js)

## Side Info
- app.js is a testing script to fetch directly via js to make sure the response is correct
- app.py is the main script to fetch the data and store it in a sqlite database

## Structure
The application is built on a somewhat 3-layer architecture:
- **Data Layer**: This layer is responsible for fetching the data from the ÖTV website and storing it as backup in a json.
- **Business Layer**: This layer is responsible for processing the data and performing any necessary calculations. We also load and transform the data from json to a SQLite database in this layer.
- **Presentation Layer**: This layer is responsible for displaying the data in a user-friendly format using Streamlit.

The 3-layer structure was chosen to separate concerns and make the application more modular and maintainable. It was applied by creating different folders for each layer and placing the relevant scripts in their respective folders. Now the 3-layer architecture is just the scripts in the scripts folder (without the folder structure). This was done because there were path problems with the imports.

## Installation

### Option 1: Manual Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/flnzba/oetv-tennis-analytics
   cd yourrepository
   ```

2. **Set Up a Virtual Environment** (optional, but recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Cd into the presentation-layer folder**
   ```bash
   cd scripts
   ```

5. **Run the Application**
   ```bash
   streamlit run app.py
   ```
   Access the app at `http://localhost:8501`.

### Option 2: Docker Installation

1. **Build the Docker Image** (from the root directory)
   ```bash
   docker build -t oetv-tennis-analytics .
   ```
   You can name the docker image how you want (after `-t`). The `.` at the end is important.

2. **Run the Container**
   ```bash
   docker run -p 8501:8501 oetv-tennis-analytics
   ```
   Access the app at `http://localhost:8501`.

![Images Example](https://github.com/user-attachments/assets/349203b8-7a70-4278-b0e1-c9378799fa1d)

![Container Example](https://github.com/user-attachments/assets/5b2574e6-57ab-4ce5-a8d2-78988ebf012d)

## Usage

After launching the app, the interface will allow you to view the bar chart representing the frequency of rankings from the ÖTV website. Data is refreshed each time the application is restarted, ensuring you always have the latest rankings displayed.

- load.py -> Load the data from the source into a json file
- transform.py -> Transform the data from the json file into a SQLite database
- app.py -> Main application to display the data in a Streamlit web app

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

Florian Zeba - florian@fzeba.com

Project Link: [https://github.com/flnzba/oetv-tennis-ranking-scraper](https://github.com/flnzba/oetv-tennis-ranking-scraper)

---

# Links
- curl_cffi: https://curl-cffi.readthedocs.io/en/latest/api.html#headers
- requests: https://docs.python-requests.org/en/master/user/quickstart/
- streamlit: https://docs.streamlit.io/
- sqlite: https://docs.python.org/3/library/sqlite3.html
- sqlite JSON Functions: https://www.sqlite.org/json1.html
- pydantic: https://docs.pydantic.dev/2.10/
- matplotlib: https://matplotlib.org/stable/contents.html

## TODOs
- [x] Create a Streamlit App
- [x] Create a SQLite Database
- [ ] Scrape all data from the ÖTV Website approx 93k players - currently break at 62k
- [x] Find a way to design nice dashboard (streamlit and py libraries are not that beautiful)
- [x] Dockerize the application
- [ ] Add more analytics
- [ ] Deploy on VPS with custom domain
- [ ] Pydantic -> Load Data directly to DB -> JSON Formatting problems
   - [x] Load Data from Db instead of JSON
   - [x] "O'Brien" is destroying the json file
   - [x] "D'ans" is destroying the json file
- [x] Optimize Main Loop to crawl dynamically more than 8000 items
- [x] Add more visualizations
