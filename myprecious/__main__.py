from flask import Flask, request, render_template, url_for
from werkzeug.utils import secure_filename
from contextlib import suppress
import os
app = Flask(__name__)

content_folder = "content"
user = "birabittoh"

def handle_upload(game_id, file):
    save_folder = os.path.join(content_folder, user, game_id)
    with suppress(FileExistsError):
        os.makedirs(save_folder)
    save_file = os.path.join(save_folder, secure_filename(f.filename))
    f.save(save_file)
    return 'file uploaded successfully'

@app.route('/')
def route_main():
    return render_template("index.html")

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        return 'Please, use POST.'
    f = request.files['file']
    game_id = request.form['game_id']
    return handle_upload(game_id, f)

if __name__ == "__main__":
    app.run(port=1111)
