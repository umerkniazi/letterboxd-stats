import os
import pandas as pd
import plotly.express as px

EXPORT_DIR = "lb_export"
CACHE_FILE = "metadata_cache.csv"
OUTPUT_HTML = "index.html"
TOP_N = 10

def load_data():
    if not os.path.exists(CACHE_FILE):
        raise FileNotFoundError("metadata_cache.csv not found. Run fetch_metadata.py first!")
    cache = pd.read_csv(CACHE_FILE)
    watched = pd.read_csv(os.path.join(EXPORT_DIR, "watched.csv"))
    watchlist = pd.read_csv(os.path.join(EXPORT_DIR, "watchlist.csv"))
    likes = pd.read_csv(os.path.join(EXPORT_DIR, "likes", "films.csv"))
    return cache, watched, watchlist, likes

def plot_bar(df, value_col, label_col, title, horizontal=False):
    df = df.sort_values(value_col, ascending=False)
    if horizontal:
        df = df[::-1]
        fig = px.bar(df, x=value_col, y=label_col, text=value_col, orientation='h',
                     title=title, color=value_col, color_continuous_scale=px.colors.sequential.Teal)
    else:
        fig = px.bar(df, x=label_col, y=value_col, text=value_col,
                     title=title, color=value_col, color_continuous_scale=px.colors.sequential.Viridis)
    fig.update_traces(textposition='outside')
    fig.update_layout(margin=dict(l=40, r=40, t=50, b=50), plot_bgcolor='white', paper_bgcolor='white')
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def plot_pie(series, title, top_n=TOP_N):
    top = series.dropna().value_counts().head(top_n).reset_index()
    top.columns = ['name', 'count']
    fig = px.pie(top, names='name', values='count', title=title,
                 color='name', color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def plot_line(series, title):
    counts = series.value_counts().sort_index()
    fig = px.line(x=counts.index, y=counts.values, markers=True, title=title, line_shape='spline', color_discrete_sequence=['#3498db'])
    fig.update_layout(xaxis_title='Year/Decade', yaxis_title='Number of Films',
                      plot_bgcolor='white', paper_bgcolor='white')
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def prepare_count_df(series, col_name='name', top_n=TOP_N):
    df = series.dropna().value_counts().head(top_n).reset_index()
    df.columns = [col_name, 'count']
    return df

def render_html(cache, watched, watchlist, likes):
    liked_titles = set(likes["Name"])
    watched_titles = set(watched["Name"])
    watchlist_titles = set(watchlist["Name"])
    cache["liked"] = cache["title"].apply(lambda x: x in liked_titles)

    total_watched = len(watched_titles)
    total_watchlist = len(watchlist_titles)
    total_liked = len(liked_titles)
    watched_in_watchlist = watched_titles.intersection(watchlist_titles)
    completion_ratio = len(watched_in_watchlist) / max(total_watchlist, 1) * 100
    like_percentage = len(watched_titles.intersection(liked_titles)) / max(total_watched, 1) * 100

    total_runtime = cache["runtime"].dropna().sum()
    avg_runtime = cache["runtime"].dropna().mean()
    hours = total_runtime / 60
    longest = cache.loc[cache["runtime"].idxmax()]
    shortest = cache.loc[cache["runtime"].idxmin()]

    fun_facts = [
        f"You could have binged <b>Breaking Bad</b> (~62 hours) {hours/62:.1f} times.",
        f"Or watched every <b>Marvel Cinematic Universe</b> movie ({hours/50:.1f} times, ~50 hours total).",
        f"Or completed <b>{hours/40:.1f} playthroughs of Fallout 3</b>.",
        f"Or watched <b>{hours/9:.1f} times Christopher Nolan’s Dark Knight Trilogy</b> in a row.",
        f"Or watched <b>{hours/15:.1f} times the entire Harry Potter film series</b> (~15 hours total)."
    ]

    decade_plot = plot_line((cache["year"] // 10 * 10).dropna().astype(int), "Films Watched per Decade")
    year_plot = plot_line(cache["year"].dropna().astype(int), "Films Watched by Year")

    directors_plot = plot_bar(prepare_count_df(cache["director"], 'director'), 'count', 'director', 'Top Directors', horizontal=True)
    writers_plot = plot_bar(prepare_count_df(pd.Series(sum(cache["writers"].dropna().apply(eval), [])), 'writer'), 'count', 'writer', 'Top Writers', horizontal=True)
    actors_plot = plot_bar(
        prepare_count_df(pd.Series(sum(cache["cast"].dropna().apply(eval), [])), 'actor/actress'),
        'count',
        'actor/actress',
        'Top Actor/Actress',
        horizontal=True
    )
    prod_plot = plot_bar(prepare_count_df(pd.Series(sum(cache["production_companies"].dropna().apply(eval), [])), 'company'), 'count', 'company', 'Top Production Companies', horizontal=True)

    countries_plot = plot_pie(pd.Series(sum(cache["countries"].dropna().apply(eval), [])), "Top Countries")
    languages_plot = plot_pie(pd.Series(sum(cache["languages"].dropna().apply(eval), [])), "Top Languages")
    genres_plot = plot_pie(pd.Series(sum(cache["genres"].dropna().apply(eval), [])), "Top Genres")

    liked_genres = [(g,row["liked"]) for _, row in cache.iterrows() if pd.notna(row["genres"]) for g in eval(row["genres"])]
    df_liked = pd.DataFrame(liked_genres, columns=["genre","liked"])
    genre_like_ratio = df_liked.groupby("genre")["liked"].mean().sort_values(ascending=False).head(TOP_N).reset_index()
    genre_like_plot = plot_bar(genre_like_ratio,'liked','genre','Like Ratio by Genre',horizontal=True)

    wl_genres = [g for _, row in cache.iterrows() if row["title"] in watchlist_titles and pd.notna(row["genres"]) for g in eval(row["genres"])]
    wl_genres_plot = plot_bar(prepare_count_df(pd.Series(wl_genres), 'genre'), 'count','genre','Top Genres in Watchlist',horizontal=True)

    vote_genre_rows = [(g,row["vote_average"]) for _, row in cache.iterrows() if pd.notna(row["genres"]) and pd.notna(row["vote_average"]) for g in eval(row["genres"])]
    df_vote = pd.DataFrame(vote_genre_rows, columns=["genre","vote"])
    genre_avg_vote = df_vote.groupby("genre")["vote"].mean().sort_values(ascending=False).head(TOP_N).reset_index()
    vote_plot = plot_bar(genre_avg_vote,'vote','genre','Average Vote by Genre',horizontal=True)

    top_director = cache["director"].dropna().value_counts().idxmax()
    top_actor = pd.Series(sum(cache["cast"].dropna().apply(eval), [])).value_counts().idxmax()
    top_genre = pd.Series(sum(cache["genres"].dropna().apply(eval), [])).value_counts().idxmax()

    html = f"""
    <html>
    <head>
        <title>Letterboxd Stats</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f6f8; margin: 0; padding: 20px; }}
            h1 {{ color: #2c3e50; margin-bottom: 10px; }}
            h2 {{ color: #34495e; margin-top: 40px; }}
            .overview-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 30px; }}
            .overview-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 15px; }}
            .overview-grid div {{ background: #eaf2f8; padding: 15px; border-radius: 8px; text-align: center; }}
            .overview-grid div b {{ display: block; margin-bottom: 5px; font-weight: 700; }}
            .plot-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 30px; width: 100%; overflow-x: auto; }}
            ul {{ padding-left: 20px; }}
            @media (max-width: 768px) {{
                .overview-grid {{ grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); }}
                .plot-card iframe {{ width: 100% !important; height: auto !important; }}
            }}
        </style>
    </head>
    <body>
        <h1>Letterboxd Stats</h1>
        <div class="overview-card">
            <h2>Overview</h2>
            <div class="overview-grid">
                <div><b>Watched</b>{total_watched}</div>
                <div><b>Liked</b>{total_liked}</div>
                <div><b>Watchlist</b>{total_watchlist}</div>
                <div><b>Watchlist %</b>{completion_ratio:.1f}%</div>
                <div><b>Liked %</b>{like_percentage:.1f}%</div>
                <div><b>Top Director</b>{top_director}</div>
                <div><b>Top Actor/Actress</b>{top_actor}</div>
                <div><b>Top Genre</b>{top_genre}</div>
                <div><b>Total Runtime</b>{total_runtime:.0f} min (~{hours:.0f} hrs)</div>
                <div><b>Avg Runtime</b>{avg_runtime:.1f} min</div>
                <div><b>Shortest Film</b>{shortest['title']} ({shortest['runtime']} min)</div>
                <div><b>Longest Film</b>{longest['title']} ({longest['runtime']} min)</div>
            </div>
        </div>
        <h2>Fun Facts</h2>
        <ul>{''.join(f"<li>{fact}</li>" for fact in fun_facts)}</ul>
        <div class="plot-card">{decade_plot}</div>
        <div class="plot-card">{year_plot}</div>
        <div class="plot-card">{directors_plot}</div>
        <div class="plot-card">{writers_plot}</div>
        <div class="plot-card">{actors_plot}</div>
        <div class="plot-card">{prod_plot}</div>
        <div class="plot-card">{countries_plot}</div>
        <div class="plot-card">{languages_plot}</div>
        <div class="plot-card">{genres_plot}</div>
        <div class="plot-card">{genre_like_plot}</div>
        <div class="plot-card">{wl_genres_plot}</div>
        <div class="plot-card">{vote_plot}</div>
    </body>
    </html>
    """
    return html

def main():
    if os.path.exists(OUTPUT_HTML):
        print(f"✅ Using cached stats: {OUTPUT_HTML}")
        return
    cache, watched, watchlist, likes = load_data()
    html = render_html(cache, watched, watchlist, likes)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Stats generated and saved to {OUTPUT_HTML}")

if __name__ == "__main__":
    main()