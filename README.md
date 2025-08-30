# Letterboxd Stats

Generate interactive stats from your Letterboxd data using Python and Plotly. Explore your watch habits, favorite directors, genres, and more.

**Live demo:** [View demo here](http://umerkniazi.dev/letterboxd-stats/)

## ✨ Features

- Interactive charts (bar, pie, line) using Plotly
- Top 10 directors, actors, genres, countries, languages
- Liked percentage
- Time spent watching (hours, days, months, years)
- Fun comparisons (e.g., Breaking Bad binging equivalents)
- Liked ratio by genre
- Works offline once stats are generated

## 🛠 Tech Stack

- Python 3.10+
- Pandas
- Requests
- Plotly
- tqdm

## 🚀 Getting Started

### Option 1: Use pre-generated stats

Open `index.html` in your browser to explore interactive charts immediately.

### Option 2: Generate your own stats

Step 1: Letterboxd export

- Go to [Letterboxd Settings → Data Export](https://letterboxd.com/settings/data-export/)
- Download the ZIP export
- Place it in the project folder and rename to `letterboxd-export.zip`

Step 2: TMDb API key

- Sign up at [TMDb](https://www.themoviedb.org/)
- Create a new API key under your account → API section
- Replace the placeholder key in `fetch_metadata.py` with your API key

Step 3: Run scripts

- Fetch metadata: `python fetch_metadata.py`
- Render stats: `python render_stats.py`
- Open `index.html` in your browser to explore your personalized stats

## 📄 License

This project is licensed under the [MIT License](LICENSE)
