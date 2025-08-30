# Letterboxd Stats

Generate interactive stats from your Letterboxd data using Python and Plotly. Explore your watch habits, favorite directors, genres, and more.

**Live demo:** Open `index.html` in the repo (pre-generated charts).

## ✨ Features

- Interactive charts (bar, pie, line) using Plotly
- Top 10 directors, actors, genres, countries, languages
- Watchlist completion ratio & liked percentage
- Time spent watching (hours, days, months, years)
- Fun comparisons (e.g., Breaking Bad binging equivalents)
- Average vote by genre and liked ratio by genre
- Works offline once stats are generated

## 🛠 Tech Stack

- Python 3.10+
- Pandas
- Requests
- Plotly
- tqdm

## 🚀 Getting Started

### Option 1: Use pre-generated stats

1. Open `index.html` in your browser.
2. Explore interactive charts immediately.

### Option 2: Generate your own stats

#### Step 1: Letterboxd export

1. Go to [Letterboxd Settings → Data Export](https://letterboxd.com/settings/data-export/)
2. Download the ZIP export.
3. Place it in the project folder and rename to `letterboxd-export.zip`.

#### Step 2: TMDb API key

1. Sign up at [TMDb](https://www.themoviedb.org/)
2. Create a new API key under your account → API section
3. Replace the placeholder key in `fetch_metadata.py`:

TMDB_API_KEY = "YOUR_API_KEY"

#### Step 3: Run scripts

1. Fetch metadata:

python fetch_metadata.py

2. Render stats:

python render_stats.py

3. Open `stats.html` in your browser to explore your personalized stats.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
