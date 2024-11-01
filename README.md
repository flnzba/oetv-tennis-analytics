# Data Visualization App with Streamlit

This application is designed to scrape ranking data from the ÖTV website, store it locally in a SQLite database, and display the data through a bar chart on a Streamlit web app. This setup provides an easy-to-use interface for analyzing and visualizing the data, all containerized with Docker for easy deployment and scalability.

## Features

- **Web Scraping**: Automatically scrapes data from the specified ÖTV rankings webpage.
- **Data Storage**: Uses SQLite for efficient local data storage.
- **Data Visualization**: Visualizes the data in a bar chart format using Matplotlib.
- **Web Application**: Streamlit framework provides a user-friendly web interface.
- **Docker Support**: Everything is dockerized for easy setup and portability.

## Prerequisites

Before you begin, ensure you have the following installed on your system:
- Python 3.8+
- Docker (optional, for containerized deployment)

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

4. **Run the Application**
   ```bash
   streamlit run app.py
   ```
   Access the app at `http://localhost:8501`.

### Option 2: Docker Installation

1. **Build the Docker Image**
   ```bash
   docker build -t oetv-tennis-streamlit .
   ```

2. **Run the Container**
   ```bash
   docker run -p 8501:8501 oetv-tennis-streamlit
   ```
   Access the app at `http://localhost:8501`.

## Usage

After launching the app, the interface will allow you to view the bar chart representing the frequency of rankings from the ÖTV website. Data is refreshed each time the application is restarted, ensuring you always have the latest rankings displayed.

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

...

## Contact

Florian Zeba - florian@fzeba.com

Project Link: [https://github.com/flnzba/oetv-tennis-ranking-scraper](https://github.com/flnzba/oetv-tennis-ranking-scraper)

---
