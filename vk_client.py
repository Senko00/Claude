import vk_api


def post_news(token: str, group_id: str, title: str, text: str, link: str | None = None) -> None:
    if not token or not group_id:
        raise RuntimeError("VK_TOKEN / VK_GROUP_ID не заданы в .env")

    session = vk_api.VkApi(token=token)
    vk = session.get_api()

    message = f"{title}\n\n{text}"
    kwargs = dict(owner_id=-int(group_id), from_group=1, message=message)
    if link:
        # VK разворачивает ссылку в карточку с картинкой из og:image страницы.
        kwargs["attachments"] = link
    vk.wall.post(**kwargs)
