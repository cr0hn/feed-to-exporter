import requests

from feed_to_wordpress.model import AppConfig
from feed_to_wordpress.exceptions import FeedToWordpressException


def check_post_already_exits(slug_title: str, config: AppConfig) -> bool:
    """
    Returns True if post already exits, False otherwise
    """
    response_draft = requests.get(
        f"{config.wordpress_api_url}/posts?slug={slug_title}&status=draft",
        headers=config.token)

    if not response_draft.json():
        response_published = requests.get(
            f"{config.wordpress_api_url}/"
            f"posts?slug={slug_title}&status=publish",
            headers=config.token)

        if not response_published.json():
            return False
        else:
            return True
    else:
        return True


def get_or_create_tag_or_category(tag_or_category: str,
                                  name: str,
                                  config: AppConfig,
                                  description: str = None) -> str:
    """
    Returns tag Id of wordpress
    :param tag_or_category: possible values: tag|category
    :type tag_or_category: str

    """
    if tag_or_category not in ("tag", "category"):
        raise FeedToWordpressException(
            "Invalid value. Allowed values are: tag|category")

    if tag_or_category == "tag":
        endpoint = "tags"
    else:
        endpoint = "categories"

    response = requests.get(
        f"{config.wordpress_api_url}/{endpoint}",
        headers=config.token,
        json={"slug": name}
    )

    if response.json():
        return response.json()[0]['id']
    else:
        json_data = {
            "name": name,
            "slug": name
        }

        if description:
            json_data["description"] = description

        response = requests.post(
            f"{config.wordpress_api_url}/{endpoint}",
            headers=config.token,
            json=json_data
        )

        return response.json()['id']


def publish_post(post_data: dict, config: AppConfig):
    # -------------------------------------------------------------------------
    # Check if already exits this post
    # -------------------------------------------------------------------------
    slug = post_data['slug']
    a = check_post_already_exits(slug, config)

    print(f"    <*> Checking if '{slug}' already exits")
    if not a:
        print(f"    <*> Creating: Post with url '{slug}' doesn't exits")
        response = requests.post(f"{config.wordpress_api_url}/posts",
                                 headers=config.token,
                                 json=post_data)

        if str(response.status_code).startswith("20"):
            print(f"    <*> Created: Post with url '{slug}' created")
        else:
            print(f"    <!> Can't create post with url '{slug}'. "
                  f"Error: {response.json()['message']}")

    else:
        print(f"    <i> Post with url '{slug}' already exits. Skipping...")


__all__ = ("get_or_create_tag_or_category", "publish_post",
           "check_post_already_exits")