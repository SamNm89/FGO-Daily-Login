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
        messageBonus += f"__{bonus.message}__{nl}```{nl.join(bonus.items)}```"

        if bonus.bonus_name is not None:
            messageBonus += (
                f"{nl}__{bonus.bonus_name}__{nl}"
                f"{bonus.bonus_detail}{nl}```{nl.join(bonus.bonus_camp_items)}```"
            )

        messageBonus += "\n"

    jsonData = {
        "content": "<@334992555957813249>",
        "embeds": [
            {
                "title": f"🎁 FGO Daily Bonus – {main.fate_region}",
                "description": f"Scheduled Login Rewards:\n\n{messageBonus}",
                "color": 0x7289DA,
                "fields": [
                    {"name": "🎖️ Level", "value": f"**{rewards.level}**", "inline": True},
                    {"name": "🎟️ Tickets", "value": f"**{rewards.ticket}**", "inline": True},
                    {"name": "💎 Saint Quartz", "value": f"**{rewards.stone}**", "inline": True},
                    {"name": "📅 Login Days", "value": f"**{login.login_days}**", "inline": True},
                    {"name": "📆 Total Days", "value": f"**{login.total_days}**", "inline": True},
                    {"name": "👥 Total FP", "value": f"**{login.total_fp}**", "inline": True},
                    {"name": "➕ Friend Points", "value": f"**+{login.add_fp}**", "inline": True},
                    {"name": "🔋 AP Max", "value": f"**{login.act_max}**", "inline": True}
                ],
                "thumbnail": {
                    "url": "https://grandorder.wiki/images/thumb/3/3d/Icon_Item_Saint_Quartz.png/200px-Icon_Item_Saint_Quartz.png"
                },
                "footer": {
                    "text": "FGO Daily Tracker",
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


def drawFP(servants, missions) -> None:
    endpoint = main.webhook_discord_url

    message_mission = ""
    message_servant = ""

    if len(servants) > 0:
        servants_atlas = requests.get(
            f"https://api.atlasacademy.io/export/JP/basic_svt_lang_en.json"
        ).json()

        svt_dict = {svt["id"]: svt for svt in servants_atlas}

        for servant in servants:
            try:
                svt = svt_dict[servant.objectId]
                message_servant += f"`{svt['name']}` "
            except KeyError:
                message_servant += f"`Unknown ID: {servant.objectId}` "

    if len(missions) > 0:
        for mission in missions:
            message_mission += f"__{mission.message}__\n**{mission.progressTo}/{mission.condition}**\n"

    jsonData = {
        "content": "<@334992555957813249>",
        "embeds": [
            {
                "title": f"✨ FGO FP Gacha – {main.fate_region}",
                "description": f"Friend Point Results:\n\n{message_mission or 'No mission updates.'}",
                "color": 0xFF69B4,
                "fields": [
                    {
                        "name": "🎰 Gacha Result",
                        "value": message_servant or "*No servants summoned.*",
                        "inline": False
                    }
                ],
                "thumbnail": {
                    "url": "https://i.imgur.com/LJMPpP8.png"
                },
                "footer": {
                    "text": "FGO Daily Tracker",
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
