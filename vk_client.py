import vk_api


def _upload_album_photo(session, group_id: str, image_path: str) -> str | None:
    """Пробует загрузить фото в обычный фотоальбом сообщества (не через
    заблокированный для community-токенов photos.getWallUploadServer) и
    вернуть attachment-строку вида photo<owner>_<id>. При любой ошибке
    (в том числе если этот путь тоже запрещён для токена сообщества)
    возвращает None."""
    try:
        vk = session.get_api()
        albums = vk.photos.getAlbums(owner_id=-int(group_id), need_system=0)
        if albums.get("count"):
            album_id = albums["items"][0]["id"]
        else:
            album = vk.photos.createAlbum(title="Новости", group_id=int(group_id))
            album_id = album["id"]

        upload = vk_api.VkUpload(session)
        photo = upload.photo(image_path, album_id=album_id, group_id=int(group_id))[0]
        return f"photo{photo['owner_id']}_{photo['id']}"
    except Exception:
        return None


def post_news(
    token: str,
    group_id: str,
    title: str,
    text: str,
    image_path: str | None = None,
    link: str | None = None,
) -> None:
    if not token or not group_id:
        raise RuntimeError("VK_TOKEN / VK_GROUP_ID не заданы в .env")

    session = vk_api.VkApi(token=token)
    vk = session.get_api()

    message = f"{title}\n\n{text}"

    # 1) Пробуем реальное фото через фотоальбом сообщества.
    if image_path:
        photo_attachment = _upload_album_photo(session, group_id, image_path)
        if photo_attachment:
            try:
                vk.wall.post(
                    owner_id=-int(group_id),
                    from_group=1,
                    message=message,
                    attachments=photo_attachment,
                )
                return
            except Exception:
                pass

    # 2) Пробуем карточку-превью по ссылке (работает, только если на
    #    странице simkran.ru есть подходящая og:image).
    if link:
        try:
            vk.wall.post(
                owner_id=-int(group_id), from_group=1, message=message, attachments=link
            )
            return
        except Exception:
            pass

    # 3) Просто текст, чтобы публикация в любом случае состоялась.
    vk.wall.post(owner_id=-int(group_id), from_group=1, message=message)
