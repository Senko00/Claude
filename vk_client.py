import vk_api


def post_news(token: str, group_id: str, title: str, text: str) -> None:
    if not token or not group_id:
        raise RuntimeError("VK_TOKEN / VK_GROUP_ID не заданы в .env")

    session = vk_api.VkApi(token=token)
    vk = session.get_api()

    message = f"{title}\n\n{text}"
    vk.wall.post(
        owner_id=-int(group_id),
        from_group=1,
        message=message,
    )
