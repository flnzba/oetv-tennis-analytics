# ÖTV Tennis Ranking Scraper

Welcome to the ÖTV Tennis Ranking Scraper project! This repository contains a Python script that automates the extraction of tennis player rankings from the ÖTV (Österreichischer Tennisverband) website. The data is then stored in a SQLite database and visualized using matplotlib to show the distribution of players across different rankings.

## Project Overview

This project is designed to demonstrate web scraping using Selenium, data storage with SQLite, and data visualization with matplotlib. It navigates through the dynamic loading mechanism of the ÖTV website, where additional data is fetched by interacting with the web page.

### Features

- **Web Scraping with Selenium:** Automates a web browser to interact with JavaScript-heavy web pages.
- **Data Storage:** Utilizes SQLite to store the scraped data.
- **Data Visualization:** Generates bar plots to analyze the frequency of different tennis rankings.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed if you are not using Docker:
- Python 3.8+
- pip (Python package installer)
- Google Chrome and ChromeDriver if running the script manually

### Installation

#### Using Docker

1. **Build the Docker image**

   Navigate to the directory containing the Dockerfile and run:

   ```bash
   docker build -t tennis-ranking-scraper .
   ```

2. **Run the container**

   After the image is built, you can run the container with:

   ```bash
   docker run -d -p 4000:80 tennis-ranking-scraper
   ```

   This command runs the scraping script and makes the container's port 80 available on local port 4000.

3. **Verify that the Docker container is running**
   
   ```bash
   docker ps
   ```

#### Manual Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/oetv-tennis-ranking-scraper.git
   cd oetv-tennis-ranking-scraper
   ```

2. **Set up a virtual environment (optional but recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the requirements**

   ```bash
   pip install -r requirements.txt
   ```

4. **Download the WebDriver**

   Ensure you have Google Chrome and the ChromeDriver installed that matches your Chrome version. Update the path to ChromeDriver in the script if necessary.

### Configuration

- **Docker users**: The Dockerfile sets environment variables and copies all necessary files.
- **Manual setup**: Edit the `scraper.py` file to include the path to your WebDriver:

   ```python
   chromedriver_path = '/path/to/your/chromedriver'
   ```

## Usage

- **Docker**: The container will automatically run `crawl-data.py` on startup.
- **Manual**: Run the scraper script using the following command:

   ```bash
   python crawl-data.py
   ```

After execution, you'll find the data in a SQLite database named `players.db`, and a plot will be displayed showing the distribution of player rankings.

## Visualization Example

![Bar Chart of Player Rankings](/path/to/bar_chart.png)

This bar chart shows the number of players for each ranking category obtained from the ÖTV website.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have suggestions or improvements.

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Florian Zeba - florian@fzeba.com

Project Link: [https://github.com/flnzba/oetv-tennis-ranking-scraper](https://github.com/flnzba/oetv-tennis-ranking-scraper)

---
