import slugify
import requests

from feed_to_exporter.exceptions import FeedToWordpressException


def check_post_already_exits(slug_title: str, config) -> bool:
    """
    Returns True if post already exits, False otherwise
    """
    response_draft = requests.get(
        f"{config.wordpress_url}/posts?slug={slug_title}&status=draft",
        headers=config.token)

    if not response_draft.json():
        response_published = requests.get(
            f"{config.wordpress_url}/"
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
                                  config,
                                  description: str = None,
                                  parent_id_category: str = None) -> str:
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
        f"{config.wordpress_url}/{endpoint}",
        headers=config.token,
        json={"slug": slugify.slugify(name)}
    )

    if response.json():
        return response.json()[0]['id']
    else:
        json_data = {
            "name": name,
            "slug": slugify.slugify(name)
        }

        if parent_id_category:
            # Parent ID
            json_data["parent"] = parent_id_category

        if description:
            json_data["description"] = description

        response = requests.post(
            f"{config.wordpress_url}/{endpoint}",
            headers=config.token,
            json=json_data
        )

        response_data = response.json()

        if response.status_code == 409:
            return response_data.json()["data"]["term_id"]
        else:
            return response_data.json()['id']


def publish_post(post_data: dict, config):
    # -------------------------------------------------------------------------
    # Check if already exits this post
    # -------------------------------------------------------------------------
    slug = post_data['slug']
    a = check_post_already_exits(slug, config)

    print(f"    <*> Checking if '{slug}' already exits")
    if not a:
        print(f"    <*> Creating: Post with url '{slug}' doesn't exits")
        response = requests.post(f"{config.wordpress_url}/posts",
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