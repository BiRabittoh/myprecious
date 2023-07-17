import os
from contextlib import suppress
from werkzeug.utils import secure_filename
import myprecious.constants as c

def get_title_platform(game_id, platform_id):
    # TODO: use IGDB api to validate game_id, platform_id and return title and platform name
    res = { "title": "title", "platform": "platform"}
    if res is None:
        raise Exception
    return res["title"], res["platform"]

def handle_upload(request, user_id):
    f = request.files['file']
    if f.filename is None:
        return "Bad file upload."
    try:
        game_id = int(request.form['game_id'])
        platform_id = int(request.form['platform_id'])
    except ValueError:
        return "Wrong parameter type."
    
    try:
        title, platform = get_title_platform(game_id, platform_id)
    except Exception:
        return "Bad or manipulated game data."
    
    # TODO: save game in DB
    # db.add_platform(platform_id, name)
    # db.add_game(game_id, platform_id, title)
    # db.add_save(user_id, game_id, platform_id, f.filename)

    save_folder = os.path.join(c.BASE_DIRECTORY, c.CONTENT_DIRECTORY, str(user_id), str(game_id), str(platform_id))
    with suppress(FileExistsError):
        os.makedirs(save_folder)
    save_file = os.path.join(save_folder, secure_filename(f.filename))
    f.save(save_file)
    return None
