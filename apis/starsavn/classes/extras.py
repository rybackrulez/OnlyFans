import copy
from itertools import chain
import math
from pathlib import Path
from typing import Any, Literal, Optional, Union


class auth_details:
    def __init__(self, options: dict[str, Any] = {}) -> None:
        self.username = options.get("username", "")
        self.cookie = cookie_parser(options.get("cookie", ""))
        self.user_agent = options.get("user_agent", "")
        self.email = options.get("email", "")
        self.password = options.get("password", "")
        self.hashed = options.get("hashed", False)
        self.support_2fa = options.get("support_2fa", True)
        self.active = options.get("active", True)

    def upgrade_legacy(self, options: dict[str, Any]):
        if "cookie" not in options:
            self = legacy_auth_details(options).upgrade(self)
        return self

    def export(self):
        new_dict = copy.copy(self.__dict__)
        cookie = self.cookie.convert()
        new_dict["cookie"] = cookie
        return new_dict


class legacy_auth_details:
    def __init__(self, option: dict[str, Any] = {}):
        self.username = option.get("username", "")
        self.auth_id = option.get("auth_id", "")
        self.sess = option.get("sess", "")
        self.user_agent = option.get("user_agent", "")
        self.auth_hash = option.get("auth_hash", "")
        self.auth_uniq_ = option.get("auth_uniq_", "")
        self.x_bc = option.get("x_bc", "")
        self.email = option.get("email", "")
        self.password = option.get("password", "")
        self.hashed = option.get("hashed", False)
        self.support_2fa = option.get("support_2fa", True)
        self.active = option.get("active", True)

    def upgrade(self, new_auth_details: auth_details):
        new_dict = ""
        for key, value in self.__dict__.items():
            value = value if value != None else ""
            skippable = ["username", "user_agent"]
            if key not in skippable:
                new_dict += f"{key}={value}; "
        new_dict = new_dict.strip()
        new_auth_details.cookie = cookie_parser(new_dict)
        return new_auth_details


class cookie_parser:
    def __init__(self, options: str) -> None:
        new_dict: dict[str, Any] = {}
        for crumble in options.strip().split(";"):
            if crumble:
                key, value = crumble.strip().split("=")
                new_dict[key] = value
        self.auth_id = new_dict.get("auth_id", "")
        self.sess = new_dict.get("sess", "")
        self.auth_hash = new_dict.get("auth_hash", "")
        self.auth_uniq_ = new_dict.get("auth_uniq_", "")
        self.auth_uid_ = new_dict.get("auth_uid_", "")

    def format(self):
        """
        Typically used for adding cookies to requests
        """
        return self.__dict__

    def convert(self):
        new_dict = ""
        for key, value in self.__dict__.items():
            key = key.replace("auth_uniq_", f"auth_uniq_{self.auth_id}")
            key = key.replace("auth_uid_", f"auth_uid_{self.auth_id}")
            new_dict += f"{key}={value}; "
        new_dict = new_dict.strip()
        return new_dict


class content_types:
    def __init__(self, option={}) -> None:
        class archived_types(content_types):
            def __init__(self) -> None:
                self.Posts = []

        self.Stories = []
        self.Posts = []
        self.Products = []
        self.Archived = archived_types()
        self.Chats = []
        self.Messages = []
        self.Highlights = []
        self.MassMessages = []

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value


class endpoint_links(object):
    def __init__(
        self,
        identifier: Optional[int | str] = None,
        identifier2: Optional[int | str] = None,
        identifier3: Optional[int | str] = None,
        text: str = "",
        global_limit: int = 10,
        global_offset: int = 0,
        sort_order: Literal["asc", "desc"] = "desc",
    ):
        domain = "https://stars.avn.com"
        api = "/api2/v2"
        full_url_path = f"{domain}{api}"
        self.full_url_path = full_url_path
        self.customer = f"{full_url_path}/users/me"
        self.users = f"{full_url_path}/users/{identifier}"
        self.subscriptions = f"{full_url_path}/subscriptions/following?limit={global_limit}&offset={global_offset}&type=active"
        self.lists_users = f"https://onlyfans.com/api2/v2/lists/{identifier}/users?limit={global_limit}&offset={global_offset}&query="
        self.list_chats = f"https://onlyfans.com/api2/v2/chats?limit={global_limit}&offset={global_offset}&order=desc"
        self.post_by_id = f"https://onlyfans.com/api2/v2/posts/{identifier}"
        self.message_by_id = f"https://onlyfans.com/api2/v2/chats/{identifier}/messages?limit=10&offset=0&firstId={identifier2}&order=desc&skip_users=all&skip_users_dups=1"
        self.search_chat = f"https://onlyfans.com/api2/v2/chats/{identifier}/messages/search?query={text}"
        self.message_api = f"{full_url_path}/chats/{identifier}/messages?limit={global_limit}&offset={global_offset}&order=desc"
        self.search_messages = f"https://onlyfans.com/api2/v2/chats/{identifier}?limit=10&offset=0&filter=&order=activity&query={text}"
        self.mass_messages_api = f"https://onlyfans.com/api2/v2/messages/queue/stats?limit=100&offset=0&format=infinite"
        self.stories_api = f"https://onlyfans.com/api2/v2/users/{identifier}/stories?limit=100&offset=0&order=desc"
        self.list_highlights = f"https://onlyfans.com/api2/v2/users/{identifier}/stories/highlights?limit=100&offset=0&order=desc"
        self.highlight = f"https://onlyfans.com/api2/v2/stories/highlights/{identifier}"
        self.post_api = f"{full_url_path}/users/{identifier}/posts?limit={global_limit}&offset={global_offset}&order=publish_date_desc&skip_users_dups=0"
        self.media_api = f"{full_url_path}/media/{identifier}?limit={global_limit}&offset={global_offset}"
        self.archived_posts = f"https://onlyfans.com/api2/v2/users/{identifier}/posts/archived?limit={global_limit}&offset={global_offset}&order=publish_date_desc"
        self.archived_stories = f"https://onlyfans.com/api2/v2/stories/archive/?limit=100&offset=0&order=publish_date_desc"
        self.paid_api = (
            f"{full_url_path}/users/purchases?{global_limit}&offset={global_offset}"
        )
        self.pay = f"https://onlyfans.com/api2/v2/payments/pay"
        self.subscribe = f"https://onlyfans.com/api2/v2/users/{identifier}/subscribe"
        self.like = f"https://onlyfans.com/api2/v2/{identifier}/{identifier2}/like"
        self.favorite = f"https://onlyfans.com/api2/v2/{identifier}/{identifier2}/favorites/{identifier3}"
        self.transactions = (
            f"https://onlyfans.com/api2/v2/payments/all/transactions?limit=10&offset=0"
        )
        self.two_factor = f"https://onlyfans.com/api2/v2/users/otp/check"

    def list_posts(
        self,
        content_id: Optional[int | str],
        global_limit: int = 10,
        global_offset: int = 0,
    ):
        return f"{self.full_url_path}/users/{content_id}/posts?limit={global_limit}&offset={global_offset}&order=publish_date_desc&skip_users_dups=0"

    def create_links(self, link: str, api_count: int, limit: int = 10, offset: int = 0):
        """
        This function will create a list of links depending on their content count.

        Example:\n
        create_links(link="base_link", api_count=50) will return a list with 5 links.
        """
        final_links: list[str] = []
        if api_count:
            ceil = math.ceil(api_count / limit)
            numbers = list(range(ceil))
            for num in numbers:
                num = num * limit
                link = link.replace(f"limit={limit}", f"limit={limit}")
                new_link = link.replace(f"offset={offset}", f"offset={num}")
                final_links.append(new_link)
        return final_links


class ErrorDetails:
    def __init__(self, result: dict[str, Any]) -> None:
        error = result["error"] if "error" in result else result
        self.code = error["code"]
        self.message = error["message"]

    async def format(self, extras: dict[str, Any]):
        match self.code:
            case 0:
                match self.message:
                    case "User not found":
                        link = Path(extras["link"])
                        self.message = f"{link.name} not found"
        return self


def create_headers(
    dynamic_rules: dict[str, Any],
    auth_id: Union[str, int],
    user_agent: str = "",
    link: str = "https://onlyfans.com/",
):
    headers: dict[str, Any] = {}
    headers["user-agent"] = user_agent
    headers["referer"] = link
    headers["user-id"] = str(auth_id)
    headers["x-bc"] = ""
    for remove_header in dynamic_rules["remove_headers"]:
        headers.pop(remove_header)
    return headers


def handle_refresh(argument, argument2):
    argument = argument.get(argument2)
    return argument


class media_types:
    def __init__(self, option={}, assign_states=False) -> None:
        self.Images = option.get("Images", [])
        self.Videos = option.get("Videos", [])
        self.Audios = option.get("Audios", [])
        self.Texts = option.get("Texts", [])
        if assign_states:
            for k, v in self:
                setattr(self, k, assign_states())

    def remove_empty(self):
        copied = copy.deepcopy(self)
        for k, v in copied:
            if not v:
                delattr(self, k)
            print
        return self

    def get_status(self) -> list:
        x = []
        for key, item in self:
            for key2, item2 in item:
                new_status = list(chain.from_iterable(item2))
                x.extend(new_status)
        return x

    def extract(self, string: str) -> list:
        a = self.get_status()
        source_list = [getattr(x, string, None) for x in a]
        x = list(set(source_list))
        return x

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value
