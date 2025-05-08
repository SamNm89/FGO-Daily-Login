from datetime import datetime
import main
import requests
import user


def topLogin(data: list) -> None:
    endpoint = main.webhook_discord_url

    rewards: user.Rewards = data[0]
    login: user.Login = data[1]
    bonus: user.Bonus or str = data[2]

    messageBonus = ''
    nl = '\n'

    if bonus != "No Bonus":
        messageBonus += f":gift: __**{bonus.message}**__{nl}```{nl.join(bonus.items)}```"

        if bonus.bonus_name is not None:
            messageBonus += (
                f"{nl}:confetti_ball: __**{bonus.bonus_name}**__\n"
                f"{bonus.bonus_detail}{nl}```{nl.join(bonus.bonus_camp_items)}```"
            )

        messageBonus += "\n"

    jsonData = {
        "content": "<@217003486489870336>",  # :white_check_mark: your original mention stays here
        "embeds": [
            {
                "title": f":sunrise: FGO Daily Login — {main.fate_region}",
                "description": f":date: **Scheduled Login Report** for Fate/Grand Order\n\n{messageBonus}",
                "color": 0xFDCB58,
                "fields": [
                    {
                        "name": ":1234: Player Info",
                        "value": f":military_medal: **Level**: {rewards.level}\n"
                                 f":tickets: **Tickets**: {rewards.ticket}\n"
                                 f":gem: **Saint Quartz**: {rewards.stone}",
                        "inline": False
                    },
                    {
                        "name": ":clock3: Login Stats",
                        "value": f":date: **Today**: {login.login_days}\n"
                                 f":calendar: **Total**: {login.total_days}",
                        "inline": True
                    },
                    {
                        "name": ":busts_in_silhouette: Friend Points",
                        "value": f":heavy_plus_sign: **+{login.add_fp}** today\n"
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
                    "url": "https://cdn.discordapp.com/emojis/1000505037967065109.webp"
                },
                "footer": {
                    "text": ":compass: FGO Daily Tracker Bot",
                    "icon_url": "https://i.imgur.com/LJMPpP8.png"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        ],
        "attachments": []
    }

    headers = {
        "Content-Type": "application/json"
    }

    requests.post(endpoint, json=jsonData, headers=headers)
