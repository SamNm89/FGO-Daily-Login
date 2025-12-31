from datetime import datetime
import main
import requests
import user
from typing import Union


def topLogin(data: list) -> None:
    endpoint = main.webhook_discord_url

    rewards: user.Rewards = data[0]
    login: user.Login = data[1]
    bonus: Union[user.Bonus, str] = data[2]

    messageBonus = ''
    nl = '\n'

    if isinstance(bonus, user.Bonus):
        messageBonus += f":gift: __**{bonus.message}**__{nl}```{nl.join(bonus.items)}```"

        if bonus.bonus_name is not None:
            messageBonus += (
                f"{nl}:confetti_ball: __**{bonus.bonus_name}**__\n"
                f"{bonus.bonus_detail}{nl}```{nl.join(bonus.bonus_camp_items)}```"
            )

        messageBonus += "\n"

    jsonData = {
        "content": "<@217003486489870336>",
        "embeds": [
            {
                "title": f":sunrise: FGO Daily Login — {main.fate_region}",
                "description": f":date: **Scheduled Login Report** for Fate/Grand Order\n\n{messageBonus}",
                "color": 0xFDCB58,
                "fields": [
                    {
                        "name": ":1234: Player Info",
                        "value": f":military_medal: **Level**: {rewards.level}\n\n"
                                 f":tickets: **Tickets**: {rewards.ticket}\n\n"
                                 f":gem: **Saint Quartz**: {rewards.stone}",
                        "inline": False
                    },
                    {
                        "name": ":clock3: Login Stats",
                        "value": f":date: **Today**: {login.login_days}\n\n"
                                 f":calendar: **Total**: {login.total_days}",
                        "inline": True
                    },
                    {
                        "name": ":busts_in_silhouette: Friend Points",
                        "value": f":heavy_plus_sign: **+{login.add_fp}** today\n\n"
                                 f":100: **Total**: {login.total_fp}",
                        "inline": True
                    },
                    {
                        "name": ":zap: AP Details",
                        "value": f":battery: **Max AP**: {login.act_max}",
                        "inline": True
                    }
                ],
                "thumbnail": {
                    "url": "https://cdn.discordapp.com/emojis/979017022740516874.webp"
                },
                "image": {
                    "url": "https://cdn.discordapp.com/emojis/977346800111484990.webp"
                },
                "footer": {
                    "text": "I love You",
                    "icon_url": "https://cdn.discordapp.com/emojis/809521848416862218.webp"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        ],
        "attachments": []
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(endpoint, json=jsonData, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to send webhook: {e}")


def Present(name, namegift, object_id_count) -> None:
    endpoint = main.webhook_discord_url
    
    jsonData = {
        "content": None,
        "embeds": [
            {
                "title": f"FGO Shop System - {main.fate_region}",
                "description": "Exchange Successful",
                "color": 8388736,
                "fields": [
                    {
                        "name": f"{name}",
                        "value": f"{namegift} x{object_id_count}",
                        "inline": False
                    }
                ],
                "thumbnail": {
                    "url": "https://www.fate-go.jp/manga_fgo2/images/commnet_chara06.png"
                }
            }
        ],
        "attachments": []
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        requests.post(endpoint, json=jsonData, headers=headers)
    except Exception as e:
        print(f"Webhook error: {e}")


def shop(item: str, quantity: str) -> None:
    endpoint = main.webhook_discord_url
    
    jsonData = {
        "content": None,
        "embeds": [
            {
                "title": f"FGO Shop System - {main.fate_region}",
                "description": "Purchase Successful",
                "color": 5814783,
                "fields": [
                    {
                        "name": f"Shop",
                        "value": f"Spent {40 * int(quantity)} AP to buy {quantity}x {item}",
                        "inline": False
                    }
                ],
                "thumbnail": {
                    "url": "https://www.fate-go.jp/manga_fgo2/images/commnet_chara10.png"
                }
            }
        ],
        "attachments": []
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        requests.post(endpoint, json=jsonData, headers=headers)
    except Exception as e:
        print(f"Webhook error: {e}")
