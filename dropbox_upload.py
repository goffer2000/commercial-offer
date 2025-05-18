import dropbox
import os

DROPBOX_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")

def upload_to_dropbox(local_path, dropbox_filename):
    if not DROPBOX_TOKEN:
        raise Exception("Переменная DROPBOX_ACCESS_TOKEN не установлена!")

    dbx = dropbox.Dropbox(DROPBOX_TOKEN)

    with open(local_path, "rb") as f:
        dbx.files_upload(f.read(), f"/CommercialOffers/{dropbox_filename}", mode=dropbox.files.WriteMode.overwrite)

    shared_link = dbx.sharing_create_shared_link_with_settings(f"/CommercialOffers/{dropbox_filename}")
    return shared_link.url.replace("?dl=0", "?raw=1")
