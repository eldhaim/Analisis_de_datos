import re

TAG_PATTERN = re.compile(r"\[([^]]+)\s+\"([^\"]+)\"\]")
TO_SQUARE = ('r', 'n', 'b', 'q')
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/91.0.4472.124 Safari/537.3",
    "Referer": "https://www.chess.com/",
}
PLAYER_GAMES_URL = "https://api.chess.com/pub/player/{}/games/{}/{}"
WHITE = "white"
BLACK = "black"
USERNAME = "username"
RATING = "rating"
RESULT = "result"
ID = "@id"
ACCURACIES = "accuracies"
URL = "url"
FEN = "fen"
PGN = "pgn"
START_TIME = "start_time"
END_TIME = "end_time"
TIME_CONTROL = "time_control"
RULES = "rules"
ECO = "eco"
TOURNAMENT = "tournament"
MATCH = "match"
GAMES = "games"
GENERAL = "general"
WHITE_USERNAME = "white_username"
WHITE_RATING = "white_rating"
WHITE_RESULT = "white_result"
WHITE_ID = "white_id"
BLACK_USERNAME = "black_username"
BLACK_RATING = "black_rating"
BLACK_RESULT = "black_result"
BLACK_ID = "black_id"
ACCURACIES_WHITE = "accuracies_white"
ACCURACIES_BLACK = "accuracies_black"
FROM = "from"
PIECE = "piece"
TO = "to"
CAPTURED = "captured"
