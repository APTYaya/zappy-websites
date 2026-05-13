import os

from src.backend.utils.files import (
    load_db as load_file_db,
    save_db as save_file_db,
    UPLOAD_DIR as FILE_UPLOAD_DIR,
)

from src.backend.utils.videos import (
    load_db as load_video_db,
    save_db as save_video_db,
    UPLOAD_DIR as VIDEO_UPLOAD_DIR,
)

from src.backend.utils.pastes import (
    load_db as load_paste_db,
    save_db as save_paste_db,
)


def delete_file(file_id):
    file_db = load_file_db()

    file = file_db.get(file_id)

    if not file:
        return

    file_path = FILE_UPLOAD_DIR / file["stored_file_name"]

    if os.path.exists(file_path):
        os.remove(file_path)

    del file_db[file_id]

    save_file_db(file_db)


def delete_video(video_id):
    video_db = load_video_db()

    video = video_db.get(video_id)

    if not video:
        return

    file_path = VIDEO_UPLOAD_DIR / video["stored_video_name"]

    if os.path.exists(file_path):
        os.remove(file_path)

    del video_db[video_id]

    save_video_db(video_db)


def delete_paste(paste_id):
    paste_db = load_paste_db()

    if paste_id in paste_db:
        del paste_db[paste_id]

        save_paste_db(paste_db)