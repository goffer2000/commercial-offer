import dropbox
import os

DROPBOX_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")

def upload_to_dropbox_and_get_shared_link(local_path, dropbox_filename):
    if not DROPBOX_TOKEN:
        raise Exception("DROPBOX_ACCESS_TOKEN is not set")

    dbx = dropbox.Dropbox(DROPBOX_TOKEN)
    dropbox_path = f"/CommercialOffers/{dropbox_filename}"

    # Загружаем файл
    with open(local_path, "rb") as f:
        dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)

    # Получаем существующую ссылку (если есть)
    links = dbx.sharing_list_shared_links(path=dropbox_path).links
    if links:
        return links[0].url.replace("?dl=0", "?raw=1")

    # Создаём новую ссылку
    shared_link = dbx.sharing_create_shared_link_with_settings(dropbox_path)
    return shared_link.url.replace("?dl=0", "?raw=1")

def delete_from_dropbox(filename):
    if not DROPBOX_TOKEN:
        raise Exception("DROPBOX_ACCESS_TOKEN is not set")
    dbx = dropbox.Dropbox(DROPBOX_TOKEN)
    dropbox_path = f"/CommercialOffers/{filename}"
    dbx.files_delete_v2(dropbox_path)
