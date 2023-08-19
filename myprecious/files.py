import os
from contextlib import suppress
from werkzeug.utils import secure_filename
import myprecious.constants as c
from myprecious.db import add_save

def get_save_folder(platform_id, game_id, user_id):
    return os.path.join(c.BASE_DIRECTORY, c.CONTENT_DIRECTORY, str(platform_id), str(game_id), str(user_id))

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
    filename = secure_filename(f.filename)
    if filename == "":
        return "Bad filename."
    try:
        game_id = int(request.form['game_id'])
        platform_id = int(request.form['platform_id'])
    except ValueError:
        return "Wrong parameter type."
    
    try:
        title, platform = get_title_platform(game_id, platform_id)
    except Exception:
        return "Bad or manipulated game data."
    
    old_filename = add_save(game_id, title, platform_id, platform, user_id, filename)
    save_folder = get_save_folder(platform_id, game_id, user_id)
    with suppress(FileExistsError):
        os.makedirs(save_folder)
    if old_filename is not None:
        os.remove(os.path.join(save_folder, old_filename))
    save_file = os.path.join(save_folder, filename)
    f.save(save_file)
    return None
