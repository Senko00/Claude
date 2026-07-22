import vk_api


def post_news(token: str, group_id: str, title: str, text: str, image_path: str) -> None:
    if not token or not group_id:
        raise RuntimeError("VK_TOKEN / VK_GROUP_ID не заданы в .env")

    session = vk_api.VkApi(token=token)
    vk = session.get_api()
    upload = vk_api.VkUpload(session)

    photo = upload.photo_wall(image_path, group_id=int(group_id))[0]
    attachment = f"photo{photo['owner_id']}_{photo['id']}"

    message = f"{title}\n\n{text}"
    vk.wall.post(
        owner_id=-int(group_id),
        from_group=1,
        message=message,
        attachments=attachment,
    )
