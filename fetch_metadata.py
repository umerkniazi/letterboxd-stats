import os
import zipfile
import pandas as pd
import requests
import time
from tqdm import tqdm

EXPORT_ZIP = "letterboxd-export.zip"
EXPORT_DIR = "lb_export"
CACHE_FILE = "metadata_cache.csv"
TMDB_API_KEY = "YOUR_API_KEY"  # Replace with your TMDb API key

# --- STEP 0: Extract Letterboxd export ---
def ensure_export():
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)

    if os.path.exists(EXPORT_ZIP):
        print(f"📦 Found {EXPORT_ZIP}, extracting...")
        with zipfile.ZipFile(EXPORT_ZIP, "r") as zip_ref:
            zip_ref.extractall(EXPORT_DIR)
        print(f"✅ Extracted to {EXPORT_DIR}/")
    else:
        raise FileNotFoundError(f"{EXPORT_ZIP} not found! Please put your Letterboxd export ZIP in the project folder.")

# --- STEP 1: Query TMDb ---
def fetch_metadata(title, year):
    search_url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": TMDB_API_KEY, "query": title, "year": year}
    r = requests.get(search_url, params=params)
    if r.status_code != 200:
        return None

    results = r.json().get("results", [])
    if not results:
        return None

    movie = results[0]
    movie_id = movie["id"]

    details_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    details_params = {"api_key": TMDB_API_KEY, "append_to_response": "credits,release_dates,keywords"}
    r = requests.get(details_url, params=details_params)
    if r.status_code != 200:
        return None

    d = r.json()

    # Basic
    genres = [g["name"] for g in d.get("genres", [])]
    runtime = d.get("runtime")
    release_date = d.get("release_date", "")
    year = release_date.split("-")[0] if release_date else ""

    # Director & writers
    director = ""
    writers = []
    for crew in d.get("credits", {}).get("crew", []):
        job = crew.get("job")
        if job == "Director":
            director = crew.get("name")
        elif job in ["Writer", "Screenplay", "Author"]:
            writers.append(crew.get("name"))

    # Cast
    cast = [c.get("name") for c in d.get("credits", {}).get("cast", [])[:10]]

    # Production & countries
    production_companies = [c["name"] for c in d.get("production_companies", [])]
    countries = [c["name"] for c in d.get("production_countries", [])]

    # Languages
    languages = [l["english_name"] for l in d.get("spoken_languages", [])]

    # Certification
    certification = ""
    for rd in d.get("release_dates", {}).get("results", []):
        if rd["iso_3166_1"] == "US" and rd.get("release_dates"):
            certification = rd["release_dates"][0].get("certification", "")
            break

    # Ratings & popularity
    vote_average = d.get("vote_average")
    vote_count = d.get("vote_count")
    popularity = d.get("popularity")

    # Content
    overview = d.get("overview", "")
    keywords = [k["name"] for k in d.get("keywords", {}).get("keywords", [])]

    # Media
    poster_path = d.get("poster_path")
    backdrop_path = d.get("backdrop_path")

    return {
        "tmdb_id": movie_id,
        "title": d.get("title"),
        "year": year,
        "runtime": runtime,
        "genres": str(genres),
        "director": director,
        "writers": str(writers),
        "cast": str(cast),
        "production_companies": str(production_companies),
        "countries": str(countries),
        "languages": str(languages),
        "release_date": release_date,
        "certification": certification,
        "vote_average": vote_average,
        "vote_count": vote_count,
        "popularity": popularity,
        "overview": overview,
        "keywords": str(keywords),
        "poster_path": poster_path,
        "backdrop_path": backdrop_path,
    }

# --- STEP 2: Build Cache ---
def build_cache(films):
    cache = []
    for _, row in tqdm(films.iterrows(), total=len(films), desc="Fetching metadata"):
        title, year = row["Name"], row["Year"]
        meta = fetch_metadata(title, year)
        if meta:
            cache.append(meta)
        time.sleep(0.25)
    return pd.DataFrame(cache)

# --- STEP 3: Main ---
def main():
    ensure_export()

    watched = pd.read_csv(os.path.join(EXPORT_DIR, "watched.csv"))
    watchlist = pd.read_csv(os.path.join(EXPORT_DIR, "watchlist.csv"))
    likes = pd.read_csv(os.path.join(EXPORT_DIR, "likes", "films.csv"))

    all_films = pd.concat([
        watched[["Name", "Year"]],
        watchlist[["Name", "Year"]],
        likes[["Name", "Year"]]
    ]).drop_duplicates()

    print(f"📊 Found {len(all_films)} unique films across watched, watchlist, and likes.")

    cache = build_cache(all_films)
    cache.to_csv(CACHE_FILE, index=False)
    print(f"✅ Metadata saved to {CACHE_FILE}")

if __name__ == "__main__":
    main()