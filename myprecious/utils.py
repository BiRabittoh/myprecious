from myprecious.encoding import obj_encode
import myprecious.constants as c

def handle_platform(game, platform):
    try:
        game_cover = "https:" + game["cover"]["url"]
    except KeyError:
        game_cover = c.MISSING_COVER_URL
    temp_obj = {
        "game_id": game["id"],
        "platform_id": platform["id"],
        "cover": game_cover,
        "title": game["name"],
        "platform": platform["name"]
    }
    temp_obj["info"] = obj_encode(temp_obj)
    return temp_obj

def handle_response(response):
    games = [ [ handle_platform(game, platform) for platform in game["platforms"] ] for game in response ]
    return collapse_list_of_lists(games)

def collapse_list_of_lists(l):
    return [ item for sublist in l for item in sublist ]

def parse_remember(form):
    try:
        return bool(form["remember"])
    except KeyError:
        return False
