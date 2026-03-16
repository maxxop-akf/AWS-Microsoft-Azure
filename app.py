"""
CineAI — Smart Movie Recommendation Platform
Flask Backend — Python converts all TMDB API calls to server-side (no CORS issues)
Run:  python app.py
Then open:  http://localhost:5000
"""

from flask import Flask, render_template, jsonify, request
import requests
import time

app = Flask(__name__)

# ── TMDB Config ────────────────────────────────────────────────────────────────
TMDB_KEY   = "8265bd1679663a7ea12ac168da84d2e8"
TMDB_BASE  = "https://api.themoviedb.org/3"
IMG        = "https://image.tmdb.org/t/p/w500"
IMG_ORIG   = "https://image.tmdb.org/t/p/original"

HEADERS = {
    "User-Agent": "CineAI/1.0",
    "Accept": "application/json"
}

def tmdb_get(path, params=None, max_retries=3):
    """Call TMDB API directly from Python — no CORS proxies needed!"""
    if params is None:
        params = {}
    params["api_key"] = TMDB_KEY
    
    for attempt in range(max_retries):
        try:
            r = requests.get(f"{TMDB_BASE}{path}", params=params, headers=HEADERS, timeout=15)
            
            # Handle rate limiting (429 Too Many Requests)
            if r.status_code == 429:
                wait_time = (attempt + 1) * 2  # Exponential backoff: 2, 4, 6 seconds
                time.sleep(wait_time)
                continue
            
            # Handle success
            if r.status_code == 200:
                return r.json(), None
            
            # Handle 404 Not Found (deleted movie/TV show)
            if r.status_code == 404:
                return None, "Not found"
            
            # Handle other errors
            if r.status_code >= 500:
                wait_time = (attempt + 1) * 2
                time.sleep(wait_time)
                continue
            
            # Client errors (400, 401, etc) - don't retry
            return None, f"HTTP {r.status_code}"
            
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            return None, "Request timeout"
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return None, "Connection error"
        except requests.exceptions.RequestException as e:
            return None, str(e)
    
    return None, "Max retries exceeded"


# ── Static Movie Data ──────────────────────────────────────────────────────────
MOVIES = [
    {"id":1,"title":"Inception","type":"movie","lang":"English","genre":"Sci-Fi","era":"2010s","year":2010,"rating":8.8,"cast":["Leonardo DiCaprio","Joseph Gordon-Levitt","Elliot Page"],"platforms":["Netflix","Prime"],"overview":"A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea into the mind of a CEO.","poster":"🎬","imgPath":"/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg","color":"#1a3a5c","trailerYT":"YoHD9XEInc0"},
    {"id":2,"title":"Interstellar","type":"movie","lang":"English","genre":"Sci-Fi","era":"2010s","year":2014,"rating":8.6,"cast":["Matthew McConaughey","Anne Hathaway","Jessica Chastain"],"platforms":["Netflix","Hotstar"],"overview":"A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.","poster":"🚀","imgPath":"/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg","color":"#0d2035","trailerYT":"zSWdZVtXT7E"},
    {"id":3,"title":"The Dark Knight","type":"movie","lang":"English","genre":"Action","era":"2000s","year":2008,"rating":9.0,"cast":["Christian Bale","Heath Ledger","Aaron Eckhart"],"platforms":["Prime","Hotstar"],"overview":"When the Joker wreaks havoc on Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.","poster":"🦇","imgPath":"/qJ2tW6WMUDux911r6m7haRef0WH.jpg","color":"#1a1a2e","trailerYT":"EXeTwQWrcwY"},
    {"id":4,"title":"Avengers: Endgame","type":"movie","lang":"English","genre":"Action","era":"2010s","year":2019,"rating":8.4,"cast":["Robert Downey Jr.","Chris Evans","Scarlett Johansson"],"platforms":["Hotstar"],"overview":"After the devastating events of Infinity War, the remaining Avengers assemble once more to reverse Thanos' actions.","poster":"⚡","imgPath":"/or06FN3Dka5tukK1e9sl16pB3iy.jpg","color":"#1c1033","trailerYT":"TcMBFSGVi1c"},
    {"id":5,"title":"Forrest Gump","type":"movie","lang":"English","genre":"Drama","era":"1990s","year":1994,"rating":8.8,"cast":["Tom Hanks","Robin Wright","Gary Sinise"],"platforms":["Prime","Netflix"],"overview":"The story of a man with a low IQ who accomplishes great things in life while never stopping to love a woman he grew up with.","poster":"🏃","imgPath":"/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg","color":"#1a2c1a","trailerYT":"bLvqoHBptjg"},
    {"id":6,"title":"The Shawshank Redemption","type":"movie","lang":"English","genre":"Drama","era":"1990s","year":1994,"rating":9.3,"cast":["Tim Robbins","Morgan Freeman","Bob Gunton"],"platforms":["Prime"],"overview":"Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.","poster":"🔓","imgPath":"/lyQBXzOQSuE59IsHyhrp0qIiPAz.jpg","color":"#1f2010","trailerYT":"6hB3S9bIaco"},
    {"id":7,"title":"Get Out","type":"movie","lang":"English","genre":"Horror","era":"2010s","year":2017,"rating":7.7,"cast":["Daniel Kaluuya","Allison Williams","Bradley Whitford"],"platforms":["Prime","ZEE5"],"overview":"A young African-American visits his white girlfriend's parents for the weekend where his simmering uneasiness eventually reaches a boiling point.","poster":"👁️","imgPath":"/tFXcEccSQMf3lfhfXKSU9iRBpa3.jpg","color":"#2c1a0a","trailerYT":"DzfpyUB60YY"},
    {"id":8,"title":"Gladiator","type":"movie","lang":"English","genre":"Action","era":"2000s","year":2000,"rating":8.5,"cast":["Russell Crowe","Joaquin Phoenix","Connie Nielsen"],"platforms":["Netflix","Prime"],"overview":"A former Roman General sets out to exact vengeance against the corrupt emperor who murdered his family and sent him into slavery.","poster":"⚔️","imgPath":"/ty8TGRuvJLPUmAR1H1nRIsgwvim.jpg","color":"#2c1510","trailerYT":"owK1qxDselE"},
    {"id":9,"title":"3 Idiots","type":"movie","lang":"Hindi","genre":"Comedy","era":"2000s","year":2009,"rating":8.4,"cast":["Aamir Khan","R. Madhavan","Sharman Joshi"],"platforms":["Netflix","Prime"],"overview":"Two friends embark on a quest for a lost buddy. On this journey, they encounter a flashback through their college years and the story of their friend.","poster":"🎓","imgPath":"/66A9MqXOyVFCssoloscw79z8Tew.jpg","color":"#1a2c3a","trailerYT":"xvszmNXdM4w"},
    {"id":10,"title":"Dangal","type":"movie","lang":"Hindi","genre":"Drama","era":"2010s","year":2016,"rating":8.3,"cast":["Aamir Khan","Fatima Sana Shaikh","Sanya Malhotra"],"platforms":["Netflix","Hotstar"],"overview":"Former wrestler Mahavir Singh Phogat and his two daughters struggle against India's patriarchal society to become champion wrestlers.","poster":"🏋️","imgPath":"/8kSerJrhrJWKLk1LViesGcnrUPE.jpg","color":"#2a1a10","trailerYT":"x_7YlGv9u1g"},
    {"id":11,"title":"Gangs of Wasseypur","type":"movie","lang":"Hindi","genre":"Crime","era":"2010s","year":2012,"rating":8.2,"cast":["Manoj Bajpayee","Nawazuddin Siddiqui","Richa Chadha"],"platforms":["Prime"],"overview":"A clash between Sultan and Shahid Khan allows Khan to exile Sultan from Wasseypur, establishing himself as a local lord.","poster":"🔫","imgPath":"/dPQpWoABKFAuO7997kFIDhMt5nV.jpg","color":"#1a1a1a","trailerYT":"SaBRFkAkrYo"},
    {"id":12,"title":"Taare Zameen Par","type":"movie","lang":"Hindi","genre":"Drama","era":"2000s","year":2007,"rating":8.4,"cast":["Aamir Khan","Darsheel Safary","Tanay Chheda"],"platforms":["Hotstar","Netflix"],"overview":"An eight-year-old boy is thought to be a lazy trouble-maker, until a new art teacher discovers the real problem behind his struggles in school.","poster":"🌟","imgPath":"/mHhecT8O6fVfFcAyRrBPcAXbDDO.jpg","color":"#1a2a3a","trailerYT":"sY7jMKGjYFQ"},
    {"id":13,"title":"Parasite","type":"movie","lang":"Korean","genre":"Thriller","era":"2010s","year":2019,"rating":8.5,"cast":["Song Kang-ho","Lee Sun-kyun","Cho Yeo-jeong"],"platforms":["Prime","Hotstar"],"overview":"Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.","poster":"🏠","imgPath":"/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg","color":"#2a1a2a","trailerYT":"5xH0HfJHsaY"},
    {"id":14,"title":"Oldboy","type":"movie","lang":"Korean","genre":"Thriller","era":"2000s","year":2003,"rating":8.1,"cast":["Choi Min-sik","Yoo Ji-tae","Kang Hye-jung"],"platforms":["Netflix"],"overview":"After being kidnapped and imprisoned for fifteen years, Oh Dae-Su is released, only to find he must find his captor in five days.","poster":"🔨","imgPath":"/pWDtjs568ZfOTMbURQBYuT4Qxka.jpg","color":"#1a0a2a","trailerYT":"2a0gtRNf1uY"},
    {"id":15,"title":"Train to Busan","type":"movie","lang":"Korean","genre":"Horror","era":"2010s","year":2016,"rating":7.6,"cast":["Gong Yoo","Jung Yu-mi","Ma Dong-seok"],"platforms":["Netflix","Prime"],"overview":"While a zombie apocalypse breaks out in the country, passengers struggle to survive on a train from Seoul to Busan.","poster":"🚂","imgPath":"/iZuGMnTFmLVcJWTpobyBLYVkOvH.jpg","color":"#2a1010","trailerYT":"pyWuHv2-Ixo"},
    {"id":16,"title":"Breaking Bad","type":"series","lang":"English","genre":"Drama","era":"2000s","year":2008,"rating":9.5,"cast":["Bryan Cranston","Aaron Paul","Anna Gunn"],"platforms":["Netflix"],"overview":"A high school chemistry teacher diagnosed with lung cancer turns to manufacturing and selling methamphetamine to secure his family's future.","poster":"⚗️","imgPath":"/ggFHVNu6YYI5L9pCfOacjizRGt.jpg","color":"#1a1a10","trailerYT":"HhesaQXLuRY"},
    {"id":17,"title":"Stranger Things","type":"series","lang":"English","genre":"Sci-Fi","era":"2010s","year":2016,"rating":8.7,"cast":["Millie Bobby Brown","Finn Wolfhard","David Harbour"],"platforms":["Netflix"],"overview":"When a young boy disappears, his mother, a police chief and his friends must confront terrifying supernatural forces to get him back.","poster":"🔦","imgPath":"/49WJfeN0moxb9IPfGn8AIqMGskD.jpg","color":"#0a1a2a","trailerYT":"b9EkMc79ZSU"},
    {"id":18,"title":"Sacred Games","type":"series","lang":"Hindi","genre":"Crime","era":"2010s","year":2018,"rating":8.7,"cast":["Saif Ali Khan","Nawazuddin Siddiqui","Radhika Apte"],"platforms":["Netflix"],"overview":"A link in the past connects Mumbai's troubled police officer Sartaj Singh to the city's most powerful criminal Ganesh Gaitonde.","poster":"🎯","imgPath":"/kPECLSQ0spFMuUU3D0yGFdGCKRL.jpg","color":"#1a0a0a","trailerYT":"HhkLl-qhD6A"},
    {"id":19,"title":"Squid Game","type":"series","lang":"Korean","genre":"Thriller","era":"2020s","year":2021,"rating":8.0,"cast":["Lee Jung-jae","Park Hae-soo","Wi Ha-jun"],"platforms":["Netflix"],"overview":"Hundreds of cash-strapped players accept a strange invitation to compete in children's games with deadly high stakes.","poster":"🦑","imgPath":"/dDlEmu3EZ0Pgg93K2SVNLCjCSvE.jpg","color":"#1a0a1a","trailerYT":"oqxAJKy0ii4"},
    {"id":20,"title":"The Crown","type":"series","lang":"English","genre":"Drama","era":"2010s","year":2016,"rating":8.6,"cast":["Claire Foy","Olivia Colman","Imelda Staunton"],"platforms":["Netflix"],"overview":"Follows the political rivalries and romance of Queen Elizabeth II's reign and the events that shaped the second half of the twentieth century.","poster":"👑","imgPath":"/3SRcnFrGAlGpVZPTtdTb1hLqOzn.jpg","color":"#1a1a2c","trailerYT":"JWtnJjn6ng0"},
    {"id":21,"title":"Money Heist","type":"series","lang":"Spanish","genre":"Crime","era":"2010s","year":2017,"rating":8.2,"cast":["Álvaro Morte","Úrsula Corberó","Itziar Ituño"],"platforms":["Netflix"],"overview":"An unusual group of robbers attempt the most perfect robbery in Spanish history — steal 2.4 billion euros from the Royal Mint of Spain.","poster":"🏦","imgPath":"/MoEKaPFHABtA1xKoOteirGaHl1.jpg","color":"#2a1010","trailerYT":"_3-OFCFSiDg"},
    {"id":22,"title":"Dark","type":"series","lang":"German","genre":"Sci-Fi","era":"2010s","year":2017,"rating":8.8,"cast":["Louis Hofmann","Lisa Vicari","Moritz Jahn"],"platforms":["Netflix"],"overview":"A family saga with a supernatural twist set in a German town where the disappearance of two children exposes relationships among four families.","poster":"🌀","imgPath":"/apbrbWs5wheK7VGbASbUNjZqqL0.jpg","color":"#0a0a2a","trailerYT":"rrwycJ08PSA"},
    {"id":23,"title":"Sholay","type":"movie","lang":"Hindi","genre":"Action","era":"Classic","year":1975,"rating":8.2,"cast":["Dharmendra","Amitabh Bachchan","Sanjeev Kumar"],"platforms":["ZEE5","Prime"],"overview":"Two criminals are hired by a retired police officer to capture the feared bandit Gabbar Singh.","poster":"🤠","imgPath":"/lmGQkIVq8AXiAzlnCm5LyTBBO0Z.jpg","color":"#2a1a0a","trailerYT":"BnEmFI7CMa8"},
    {"id":24,"title":"Spirited Away","type":"movie","lang":"Japanese","genre":"Animation","era":"2000s","year":2001,"rating":8.6,"cast":["Daveigh Chase","Suzanne Pleshette","Miyu Irino"],"platforms":["Netflix","Prime"],"overview":"During her family's move to the suburbs, a sullen 10-year-old girl wanders into a world ruled by gods, witches, and spirits.","poster":"🐉","imgPath":"/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg","color":"#1a2a1a","trailerYT":"ByXuk9QqQkk"},
    {"id":25,"title":"The Godfather","type":"movie","lang":"English","genre":"Crime","era":"Classic","year":1972,"rating":9.2,"cast":["Marlon Brando","Al Pacino","James Caan"],"platforms":["Prime","Netflix"],"overview":"The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.","poster":"🌹","imgPath":"/3bhkrj58Vtu7enYsLePmd2e9UzS.jpg","color":"#1a1010","trailerYT":"sY1S34973zA"},
    {"id":26,"title":"Dune","type":"movie","lang":"English","genre":"Sci-Fi","era":"2020s","year":2021,"rating":8.0,"cast":["Timothée Chalamet","Rebecca Ferguson","Oscar Isaac"],"platforms":["Prime","Hotstar"],"overview":"A noble family becomes embroiled in a war for control over the galaxy's most valuable asset while its heir is troubled by visions of a dark future.","poster":"🏜️","imgPath":"/d5NXSklpcvweasQZAzIu9mMzrs2.jpg","color":"#2a2010","trailerYT":"n9xhJrPXop4"},
    {"id":27,"title":"RRR","type":"movie","lang":"Telugu","genre":"Action","era":"2020s","year":2022,"rating":7.8,"cast":["N. T. Rama Rao Jr.","Ram Charan","Alia Bhatt"],"platforms":["Netflix","Prime","ZEE5"],"overview":"A fictional take on the lives of Telugu freedom fighters, Alluri Sitarama Raju and Komaram Bheem.","poster":"🔥","imgPath":"/nEufeZlyAOLqO2brrs0yeF1lgXO.jpg","color":"#2a1510","trailerYT":"OsU0CGZoV8E"},
    {"id":28,"title":"Everything Everywhere All at Once","type":"movie","lang":"English","genre":"Fantasy","era":"2020s","year":2022,"rating":7.8,"cast":["Michelle Yeoh","Ke Huy Quan","Jamie Lee Curtis"],"platforms":["Prime"],"overview":"A middle-aged Chinese immigrant swept into an adventure where she alone can save the multiverse by exploring other universes.","poster":"🌈","imgPath":"/w3LxiVYdWWRvEVdn5RYq6jIqkb1.jpg","color":"#1a0a2a","trailerYT":"wxN1T1uxQ2g"},
]

# TMDB IDs for static movies
TMDB_IDS = {
    1:27205, 2:157336, 3:155, 4:299534, 5:13, 6:278, 7:419430, 8:98,
    9:20453, 10:337167, 11:89720, 12:19400, 13:496243, 14:670, 15:396535,
    16:1396, 17:66732, 18:71670, 19:93405, 20:65494, 21:71446, 22:70523,
    23:8073, 24:129, 25:238, 26:438631, 27:715931, 28:545611
}

# Exact deep links per movie per platform
MOVIE_DEEP_LINKS = {
    1:  {"Netflix":"https://www.netflix.com/title/70131314",      "Prime":"https://www.primevideo.com/detail/0HRQBGTTHBHAVPN4TXKM0TS4MA"},
    2:  {"Netflix":"https://www.netflix.com/title/70305903",      "Hotstar":"https://www.hotstar.com/in/movies/interstellar/1260007975"},
    3:  {"Prime":"https://www.primevideo.com/detail/0JKPXPXX6NAQLP4VZ73RFSRHRB","Hotstar":"https://www.hotstar.com/in/movies/the-dark-knight/1260008860"},
    4:  {"Hotstar":"https://www.hotstar.com/in/movies/avengers-endgame/1260009878"},
    5:  {"Prime":"https://www.primevideo.com/detail/0GPNRPIFNKFQQ9N8M1HBFPVEKN","Netflix":"https://www.netflix.com/title/60020232"},
    6:  {"Prime":"https://www.primevideo.com/detail/0GLYXX0XVHBXNUVVKIFQILNMRJ"},
    7:  {"Prime":"https://www.primevideo.com/detail/0HITP2D7XZSA36PIJTYRPIZFE4","ZEE5":"https://www.zee5.com/movies/details/get-out/0-0-movie_6f7d1c2b"},
    8:  {"Netflix":"https://www.netflix.com/title/60020936",      "Prime":"https://www.primevideo.com/detail/0GKXQT0HNZLW0HVTQFQTGMV3VL"},
    9:  {"Netflix":"https://www.netflix.com/title/70121522",      "Prime":"https://www.primevideo.com/detail/0G3GM49ZQCIFIQMGMQQ1N7JQMX"},
    10: {"Netflix":"https://www.netflix.com/title/80167783",      "Hotstar":"https://www.hotstar.com/in/movies/dangal/1260007754"},
    11: {"Prime":"https://www.primevideo.com/detail/0H0P3CPZS5TLCMWNQMTN9ZQIHV"},
    12: {"Hotstar":"https://www.hotstar.com/in/movies/taare-zameen-par/1260008345","Netflix":"https://www.netflix.com/title/70087087"},
    13: {"Prime":"https://www.primevideo.com/detail/0H1EVS44ZQCIMQMGMQQ1N7JQMX","Hotstar":"https://www.hotstar.com/in/movies/parasite/1260009539"},
    14: {"Netflix":"https://www.netflix.com/title/70023455"},
    15: {"Netflix":"https://www.netflix.com/title/80075595",      "Prime":"https://www.primevideo.com/detail/0H2LPT3CPZS5TLCMWNQMTN9ZQI"},
    16: {"Netflix":"https://www.netflix.com/title/70143836"},
    17: {"Netflix":"https://www.netflix.com/title/80057281"},
    18: {"Netflix":"https://www.netflix.com/title/80175722"},
    19: {"Netflix":"https://www.netflix.com/title/81040344"},
    20: {"Netflix":"https://www.netflix.com/title/80025678"},
    21: {"Netflix":"https://www.netflix.com/title/80192098"},
    22: {"Netflix":"https://www.netflix.com/title/80174608"},
    23: {"ZEE5":"https://www.zee5.com/movies/details/sholay/0-0-movie_d0e4dcdf","Prime":"https://www.primevideo.com/detail/0GSHOLAYMOVIE1975PRIMEVIDEO"},
    24: {"Netflix":"https://www.netflix.com/title/60032294",      "Prime":"https://www.primevideo.com/detail/0GSPIRITEDAWAY2001PRIME"},
    25: {"Prime":"https://www.primevideo.com/detail/0GFATHERPART1PRIMEVIDEOURL","Netflix":"https://www.netflix.com/title/60000606"},
    26: {"Prime":"https://www.primevideo.com/detail/0HDUNE2021AMAZONPRIME",      "Hotstar":"https://www.hotstar.com/in/movies/dune/1260054321"},
    27: {"Netflix":"https://www.netflix.com/title/81476783",      "Prime":"https://www.primevideo.com/detail/0HRRR2022PRIMEVIDEO","ZEE5":"https://www.zee5.com/movies/details/rrr/0-0-movie_rrr2022"},
    28: {"Prime":"https://www.primevideo.com/detail/0HEEAAATONCE2022PRIME"},
}


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the main page — pass movie data to template"""
    trending = sorted(MOVIES, key=lambda m: m["rating"], reverse=True)[:10]
    return render_template("index.html",
        movies=MOVIES,
        trending=trending,
        tmdb_ids=TMDB_IDS,
        movie_deep_links=MOVIE_DEEP_LINKS,
        img_base=IMG
    )


@app.route("/api/tmdb/live")
def api_tmdb_live():
    """Fetch live movies from TMDB — category, page, genre"""
    category = request.args.get("category", "trending")
    subtype  = request.args.get("subtype", "week")
    page     = request.args.get("page", 1, type=int)
    genre_id = request.args.get("genre_id", 0, type=int)

    if category == "trending":
        path = f"/trending/movie/{subtype or 'week'}"
    elif category == "now_playing":
        path = "/movie/now_playing"
    elif category == "upcoming":
        path = "/movie/upcoming"
    elif category == "top_rated":
        path = "/movie/top_rated"
    elif category == "popular":
        path = "/movie/popular"
    elif category == "genre":
        path = "/discover/movie"
    elif category == "search":
        path = "/search/movie"
    else:
        path = "/trending/movie/week"

    params = {"page": page}
    if category == "genre" and genre_id:
        params["with_genres"] = genre_id
        params["sort_by"] = "popularity.desc"
        params["vote_count.gte"] = 50
    if category == "search":
        params["query"] = subtype

    data, err = tmdb_get(path, params)
    if err:
        return jsonify({"error": err, "results": []}), 500
    if data is None:
        return jsonify({"error": "No data received", "results": []}), 500
    return jsonify(data)


@app.route("/api/tmdb/movie/<int:tmdb_id>")
def api_tmdb_movie(tmdb_id):
    """Fetch full movie details + credits + videos + watch providers"""
    data, err = tmdb_get(f"/movie/{tmdb_id}", {"append_to_response": "credits,videos"})
    if err:
        return jsonify({"error": err, "not_found": True}), 404

    # Also fetch watch providers for India
    providers_data, _ = tmdb_get(f"/movie/{tmdb_id}/watch/providers")
    if providers_data and "results" in providers_data:
        data["watch_providers_in"] = providers_data.get("results", {}).get("IN", {})
    else:
        data["watch_providers_in"] = {}

    return jsonify(data)


@app.route("/api/tmdb/tv/<int:tmdb_id>")
def api_tmdb_tv(tmdb_id):
    """Fetch TV series details for static series entries"""
    data, err = tmdb_get(f"/tv/{tmdb_id}", {"append_to_response": "credits,videos"})
    if err:
        return jsonify({"error": err, "not_found": True}), 404
    return jsonify(data)


@app.route("/api/search")
def api_search():
    """Filter static movies by type/lang/genre/era/cast/platform"""
    type_f    = request.args.get("type", "all")
    lang      = request.args.get("lang", "")
    genre     = request.args.get("genre", "")
    era       = request.args.get("era", "")
    cast      = request.args.get("cast", "").lower()
    platform  = request.args.get("platform", "")

    results = []
    for m in MOVIES:
        if type_f != "all" and m["type"] != type_f:
            continue
        if lang and m["lang"] != lang:
            continue
        if genre and m["genre"] != genre:
            continue
        if era and m["era"] != era:
            continue
        if cast and not any(cast in c.lower() for c in m["cast"]):
            continue
        if platform and platform not in m["platforms"]:
            continue
        results.append(m)

    return jsonify(results)


# TMDB genre mapping
TMDB_GENRE_MAP = {
    "Action": 28,
    "Adventure": 12,
    "Animation": 16,
    "Comedy": 35,
    "Crime": 80,
    "Drama": 18,
    "Fantasy": 14,
    "Horror": 27,
    "Romance": 10749,
    "Sci-Fi": 878,
    "Thriller": 53,
    "War": 10752,
    "Western": 37,
    "Documentary": 99,
    "Family": 10751,
    "History": 36,
    "Music": 10402,
    "Mystery": 9648,
}

TMDB_LANG_MAP = {
    "English": "en",
    "Hindi": "hi",
    "Korean": "ko",
    "Spanish": "es",
    "Japanese": "ja",
    "French": "fr",
    "Tamil": "ta",
    "Telugu": "te",
    "German": "de",
    "Chinese": "zh",
    "Italian": "it",
    "Russian": "ru",
    "Portuguese": "pt",
}

ERA_DATE_RANGES = {
    "2020s": ("2020-01-01", "2029-12-31"),
    "2010s": ("2010-01-01", "2019-12-31"),
    "2000s": ("2000-01-01", "2009-12-31"),
    "1990s": ("1990-01-01", "1999-12-31"),
    "Classic": ("1900-01-01", "1989-12-31"),
}


@app.route("/api/discover")
def api_discover():
    """Discover movies/TV shows from TMDB API based on filters"""
    content_type = request.args.get("type", "movie")
    genre = request.args.get("genre", "")
    lang = request.args.get("lang", "")
    era = request.args.get("era", "")
    cast = request.args.get("cast", "")
    page = request.args.get("page", 1, type=int)
    platform = request.args.get("platform", "")

    if content_type == "series":
        endpoint = "/discover/tv"
    else:
        endpoint = "/discover/movie"

    params = {
        "page": page,
        "sort_by": "popularity.desc",
        "vote_count.gte": 50,
    }

    if genre and genre in TMDB_GENRE_MAP:
        params["with_genres"] = TMDB_GENRE_MAP[genre]

    if lang and lang in TMDB_LANG_MAP:
        params["with_original_language"] = TMDB_LANG_MAP[lang]

    if era and era in ERA_DATE_RANGES:
        start_date, end_date = ERA_DATE_RANGES[era]
        params["primary_release_date.gte"] = start_date
        params["primary_release_date.lte"] = end_date

    if cast:
        params["with_cast"] = cast

    data, err = tmdb_get(endpoint, params)
    if err:
        return jsonify({"error": err, "results": [], "platform_filtered": bool(platform)}), 500

    results = data.get("results", []) if data else []

    return jsonify({
        "results": results,
        "page": data.get("page", 1),
        "total_pages": data.get("total_pages", 1),
        "total_results": data.get("total_results", 0),
        "platform_filtered": bool(platform),
    })


if __name__ == "__main__":
    print("\nCineAI is starting...")
    print("Open your browser at: http://localhost:5000\n")
    app.run(debug=True, port=5000)
