# coding: utf-8
import uuid
import hashlib
import base64
import fgourl
import mytime
import gacha
import webhook
import main
import requests

from urllib.parse import quote_plus
from libs.GetSubGachaId import GetGachaSubIdFP

import msgpack

class ParameterBuilder:
    def __init__(self, uid: str, auth_key: str, secret_key: str):
        self.uid_ = uid
        self.auth_key_ = auth_key
        self.secret_key_ = secret_key
        self.content_ = ''
        self.parameter_list_ = [
            ('appVer', fgourl.app_ver_),
            ('authKey', self.auth_key_),
            ('dataVer', str(fgourl.data_ver_)),
            ('dateVer', str(fgourl.date_ver_)),
            ('idempotencyKey', str(uuid.uuid4())),
            ('lastAccessTime', str(mytime.GetTimeStamp())),
            ('userId', self.uid_),
            ('verCode', fgourl.ver_code_),
            ('deviceInfo', 'INFINIX Infinix X6817 / Android OS 12 / API-31 (SP1A.210812.016/230215V1740)'),
            ('country', '702'),
        ]

    def AddParameter(self, key: str, value: str):
        self.parameter_list_.append((key, value))

    def Build(self) -> str:
        self.parameter_list_.sort(key=lambda tup: tup[0])
        temp = ''
        for first, second in self.parameter_list_:
            if temp:
                temp += '&'
                self.content_ += '&'
            escaped_key = quote_plus(first)
            if not second:
                temp += first + '='
                self.content_ += escaped_key + '='
            else:
                escaped_value = quote_plus(second)
                temp += first + '=' + second
                self.content_ += escaped_key + '=' + escaped_value

        temp += ':' + self.secret_key_
        self.content_ += '&authCode=' + \
            quote_plus(base64.b64encode(
                hashlib.sha1(temp.encode('utf-8')).digest()))

        return self.content_

    def Clean(self):
        self.content_ = ''
        self.parameter_list_ = [
            ('appVer', fgourl.app_ver_),
            ('authKey', self.auth_key_),
            ('dataVer', str(fgourl.data_ver_)),
            ('dateVer', str(fgourl.date_ver_)),
            ('idempotencyKey', str(uuid.uuid4())),
            ('lastAccessTime', str(mytime.GetTimeStamp())),
            ('userId', self.uid_),
            ('verCode', fgourl.ver_code_),
        ]


class Rewards:
    def __init__(self, stone, level, ticket):
        self.stone = stone
        self.level = level
        self.ticket = ticket


class Login:
    def __init__(self, name, login_days, total_days, act_max, act_recover_at, now_act, add_fp, total_fp):
        self.name = name
        self.login_days = login_days
        self.total_days = total_days
        self.act_max = act_max
        self.act_recover_at = act_recover_at
        self.now_act = now_act
        self.add_fp = add_fp
        self.total_fp = total_fp


class Bonus:
    def __init__(self, message, items, bonus_name, bonus_detail, bonus_camp_items):
        self.message = message
        self.items = items
        self.bonus_name = bonus_name
        self.bonus_detail = bonus_detail
        self.bonus_camp_items = bonus_camp_items


class user:
    def __init__(self, user_id: str, auth_key: str, secret_key: str):
        self.name_ = ''
        self.user_id_ = (int)(user_id)
        self.s_ = fgourl.NewSession()
        self.builder_ = ParameterBuilder(user_id, auth_key, secret_key)
        self.login_data = None

    def Post(self, url):
        res = fgourl.PostReq(self.s_, url, self.builder_.Build())
        self.builder_.Clean()
        return res

    def topLogin(self):
        DataWebhook = []  # This data will be use in discord webhook!

        lastAccessTime = self.builder_.parameter_list_[5][1]
        userState = (-int(lastAccessTime) >>
                     2) ^ self.user_id_ & fgourl.data_server_folder_crc_

        self.builder_.AddParameter(
            'assetbundleFolder', fgourl.asset_bundle_folder_)
        self.builder_.AddParameter('isTerminalLogin', '1')
        self.builder_.AddParameter('userState', str(userState))

        data = self.Post(
            f'{fgourl.server_addr_}/login/top?_userId={self.user_id_}')
        self.login_data = data

        self.name_ = hashlib.md5(
            data['cache']['replaced']['userGame'][0]['name'].encode('utf-8')).hexdigest()
        stone = data['cache']['replaced']['userGame'][0]['stone']
        lv = data['cache']['replaced']['userGame'][0]['lv']
        ticket = 0

        for item in data['cache']['replaced']['userItem']:
            if item['itemId'] == 4001:
                ticket = item['num']
                break

        rewards = Rewards(stone, lv, ticket)

        DataWebhook.append(rewards)

        login_days = data['cache']['updated']['userLogin'][0]['seqLoginCount']
        total_days = data['cache']['updated']['userLogin'][0]['totalLoginCount']

        act_max = data['cache']['replaced']['userGame'][0]['actMax']
        act_recover_at = data['cache']['replaced']['userGame'][0]['actRecoverAt']
        now_act = (act_max - (act_recover_at - mytime.GetTimeStamp()) / 300)

        add_fp = data['response'][0]['success']['addFriendPoint']
        total_fp = data['cache']['replaced']['tblUserGame'][0]['friendPoint']

        login = Login(
            self.name_,
            login_days,
            total_days,
            act_max, act_recover_at,
            now_act,
            add_fp,
            total_fp
        )

        DataWebhook.append(login)

        if 'seqLoginBonus' in data['response'][0]['success']:
            bonus_message = data['response'][0]['success']['seqLoginBonus'][0]['message']

            items = []
            items_camp_bonus = []

            for i in data['response'][0]['success']['seqLoginBonus'][0]['items']:
                items.append(f'{i["name"]} x{i["num"]}')

            if 'campaignbonus' in data['response'][0]['success']:
                bonus_name = data['response'][0]['success']['campaignbonus'][0]['name']
                bonus_detail = data['response'][0]['success']['campaignbonus'][0]['detail']

                for i in data['response'][0]['success']['campaignbonus'][0]['items']:
                    items_camp_bonus.append(f'{i["name"]} x{i["num"]}')
            else:
                bonus_name = None
                bonus_detail = None

            bonus = Bonus(bonus_message, items, bonus_name,
                          bonus_detail, items_camp_bonus)
            DataWebhook.append(bonus)
        else:
            DataWebhook.append("No Bonus")

        webhook.topLogin(DataWebhook)

    def drawFP(self):
        self.builder_.AddParameter('storyAdjustIds', '[]')
        self.builder_.AddParameter('gachaId', '1')
        self.builder_.AddParameter('num', '10')
        self.builder_.AddParameter('ticketItemId', '0')
        self.builder_.AddParameter('shopIdIndex', '1')

        if main.fate_region == "NA":
            gachaSubId = GetGachaSubIdFP("NA")
            if gachaSubId is None:
                gachaSubId = "0"  # or any other default value as a string
            self.builder_.AddParameter('gachaSubId', gachaSubId)
            main.logger.info(f"Friend Point Gacha Sub Id " + gachaSubId)
        else:
            gachaSubId = GetGachaSubIdFP("JP")
            if gachaSubId is None:
                gachaSubId = "0"  # or any other default value as a string
            self.builder_.AddParameter('gachaSubId', gachaSubId)
            main.logger.info(f"Friend Point Gacha Sub Id " + gachaSubId)

        data = self.Post(
            f'{fgourl.server_addr_}/gacha/draw?_userId={self.user_id_}')

        responses = data['response']

        servantArray = []
        missionArray = []

        for response in responses:
            resCode = response['resCode']
            resSuccess = response['success']

            if (resCode != "00"):
                continue

            if "gachaInfos" in resSuccess:
                for info in resSuccess['gachaInfos']:
                    servantArray.append(
                        gacha.gachaInfoServant(
                            info['isNew'], info['objectId'], info['sellMana'], info['sellQp']
                        )
                    )

            if "eventMissionAnnounce" in resSuccess:
                for mission in resSuccess["eventMissionAnnounce"]:
                    missionArray.append(
                        gacha.EventMission(
                            mission['message'], mission['progressFrom'], mission['progressTo'], mission['condition']
                        )
                    )

        webhook.drawFP(servantArray, missionArray)

    def topHome(self):
        self.Post(f'{fgourl.server_addr_}/home/top?_userId={self.user_id_}')

    def get_shop_data(self):
        if hasattr(self, 'shop_data') and self.shop_data:
            return self.shop_data
            
        url = 'https://git.atlasacademy.io/atlasacademy/fgo-game-data/raw/branch/NA/master/mstShop.json'
        try:
            response = requests.get(url)
            response.raise_for_status()
            self.shop_data = response.json()
            return self.shop_data
        except Exception as e:
            main.logger.error(f"Failed to fetch shop data: {e}")
            return None

    def buyMonthlyTickets(self):
        shop_data = self.get_shop_data()
        if not shop_data:
            return

        # Find the monthly summon ticket shop item
        # Target ID 4001 (Summon Ticket), Flag 4096 (Monthly Shop?)
        target_shop_id = None
        limit_num = 0
        price = 0
        shop_name = "Summon Ticket (Monthly)"
        
        current_time = mytime.GetTimeStamp()

        for item in shop_data:
            if 4001 in item.get('targetIds', []) and item.get('flag') == 4096:
                # Check for active shop item based on time
                opened_at = item.get('openedAt', 0)
                closed_at = item.get('closedAt', 0)
                
                if opened_at <= current_time <= closed_at:
                    target_shop_id = item.get('baseShopId')
                    limit_num = item.get('limitNum')
                    price = item.get('prices')[0]
                    main.logger.info(f"Found active monthly ticket shop ID: {target_shop_id}")
                    break

        if target_shop_id is None:
            main.logger.info("Could not find active monthly ticket shop item.")
            return

        if not self.login_data:
            main.logger.error("Login data not found. Cannot proceed with purchase.")
            return

        # Check user's current purchase status
        current_num = 0
        user_shop = self.login_data.get('cache', {}).get('updated', {}).get('userShop', [])
        # Also check replaced just in case
        if not user_shop:
             user_shop = self.login_data.get('cache', {}).get('replaced', {}).get('userShop', [])

        for item in user_shop:
            if item.get('shopId') == target_shop_id:
                current_num = item.get('num')
                break
        
        purchasable_num = limit_num - current_num
        if purchasable_num <= 0:
            main.logger.info("Monthly tickets already purchased.")
            return

        # Check Mana Prisms
        user_game = self.login_data['cache']['replaced']['userGame'][0]
        mana = user_game.get('mana', 0)
        
        max_affordable = mana // price
        if max_affordable == 0:
            main.logger.info("Not enough Mana Prisms.")
            return

        to_buy = min(purchasable_num, max_affordable)

        main.logger.info(f"Attempting to buy {to_buy} tickets...")

        self.builder_.AddParameter('id', str(target_shop_id))
        self.builder_.AddParameter('num', str(to_buy))
        
        try:
            data = self.Post(f'{fgourl.server_addr_}/shop/purchase?_userId={self.user_id_}')
            responses = data['response']
            
            # Check for success
            success = False
            for resp in responses:
                if resp.get('resCode') == '00' and resp.get('nid') == 'purchase':
                    success = True
                    break
            
            if success:
                main.logger.info(f"Successfully bought {to_buy} tickets.")
                webhook.Present("Summon Ticket", "Summon Ticket (Monthly)", to_buy)
            else:
                main.logger.error("Purchase failed (API response).")

        except Exception as e:
            main.logger.error(f"Purchase failed: {e}")

    def buyBlueApple(self):
        if not self.login_data:
            main.logger.error("Login data not found. Cannot proceed with Blue Apple purchase.")
            return

        # Extract AP info
        user_game = self.login_data['cache']['replaced']['userGame'][0]
        act_recover_at = user_game['actRecoverAt']
        act_max = user_game['actMax']
        carry_over_act_point = user_game['carryOverActPoint']
        server_time = self.login_data['cache']['serverTime']

        # Extract Blue Bronze Sapling count (ItemId 103)
        blue_bronze_sapling = 0
        user_item = self.login_data['cache']['replaced']['userItem']
        for item in user_item:
            if item['itemId'] == 103:
                blue_bronze_sapling = item['num']
                break
        
        # Calculate current AP
        ap_points = act_recover_at - server_time
        remaining_ap = 0

        if ap_points > 0:
            lost_ap_point = (ap_points + 299) // 300
            if act_max >= lost_ap_point:
                remaining_ap = act_max - lost_ap_point
        else:
            remaining_ap = act_max + carry_over_act_point
        
        remaining_ap = int(remaining_ap)

        if blue_bronze_sapling > 0:
            quantity = remaining_ap // 40
            if quantity == 0:
                main.logger.info("Not enough AP to buy Blue Apple (Need 40 AP).")
                return
            
            num_to_purchase = min(blue_bronze_sapling, quantity)

            # Dynamic lookup for Blue Apple Shop ID
            shop_id = '13000000' # Default fallback
            shop_data = self.get_shop_data()
            if shop_data:
                found_id = None
                for item in shop_data:
                    # Look for shop item that gives Blue Bronze Fruit (104)
                    if 104 in item.get('targetIds', []):
                        # We prefer the one that matches the known system ID if present, or the latest one
                        found_id = item.get('baseShopId')
                        if str(found_id) == '13000000':
                            break
                
                if found_id:
                    shop_id = str(found_id)
                    main.logger.info(f"Found Blue Apple Shop ID: {shop_id}")
                else:
                    main.logger.warning("Could not find Blue Apple shop in NA data. Using default ID.")

            self.builder_.AddParameter('id', shop_id)
            self.builder_.AddParameter('num', str(num_to_purchase))

            main.logger.info(f"Attempting to convert AP to {num_to_purchase} Blue Apples...")

            try:
                data = self.Post(f'{fgourl.server_addr_}/shop/purchase?_userId={self.user_id_}')
                responses = data['response']

                for response in responses:
                    res_code = response['resCode']
                    res_success = response['success']
                    nid = response.get("nid")

                    if res_code != "00":
                        continue

                    if nid == "purchase":
                        if "purchaseName" in res_success and "purchaseNum" in res_success:
                            purchase_name = res_success['purchaseName']
                            purchase_num = res_success['purchaseNum']

                            main.logger.info(f"Successfully bought {purchase_name} x{purchase_num}")
                            webhook.shop(purchase_name, purchase_num)
            except Exception as e:
                main.logger.error(f"Blue Apple purchase failed: {e}")

        else:
            main.logger.info("No Blue Bronze Saplings available.")

    def get_presents(self):
        self.builder_.AddParameter('limit', '0')
        self.builder_.AddParameter('start', '0')
        data = self.Post(f'{fgourl.server_addr_}/present/list?_userId={self.user_id_}')
        return data

    def receive_presents(self):
        # Item IDs to claim: 1 = Saint Quartz, 4001 = Summon Ticket
        target_mapping = {
            1: "Saint Quartz",
            4001: "Summon Ticket"
        }
        
        try:
            data = self.get_presents()
            if not data or 'cache' not in data or 'updated' not in data['cache']:
                 main.logger.warning("Failed to fetch present list.")
                 return

            present_box = data['cache']['updated'].get('userPresentBox', [])
            if not present_box:
                 present_box = data['cache']['replaced'].get('userPresentBox', [])

            presents_to_receive = []
            claimed_items_report = []

            for present in present_box:
                obj_id = present.get('objectId')
                if obj_id in target_mapping:
                    presents_to_receive.append(str(present['presentId']))
                    
                    # Prepare report
                    name = target_mapping[obj_id]
                    num = present.get('num', 1)
                    claimed_items_report.append(f"{name} x{num}")

            if not presents_to_receive:
                main.logger.info("No Saint Quartz or Tickets found in Present Box.")
                return

            main.logger.info(f"Found {len(presents_to_receive)} items to claim. Claiming...")

            presents_to_receive = [str(pid) for pid in presents_to_receive] # Ensure strings
            msgpack_data = msgpack.packb(presents_to_receive)
            base64_encoded_data = base64.b64encode(msgpack_data).decode()
            
            self.builder_.AddParameter('presentIds', base64_encoded_data)
            self.builder_.AddParameter('itemSelectIdx', '0')
            self.builder_.AddParameter('itemSelectNum', '0')
            self.builder_.AddParameter('shopIdIndex', '1')
            
            data = self.Post(f'{fgourl.server_addr_}/present/receive?_userId={self.user_id_}')
            
            responses = data['response']
            success_count = 0
            
            for resp in responses:
                if resp.get('resCode') == '00' and resp.get('nid') == 'presentReceive':
                     success_count += 1
            
            if success_count > 0:
                main.logger.info(f"Successfully claimed {len(presents_to_receive)} items.")
                # Send webhook
                if claimed_items_report:
                    webhook.presents(claimed_items_report)
            else:
                 main.logger.info("Claim request sent, but no confirmation in primary response.")

        except Exception as e:
            main.logger.error(f"Failed to claim presents: {e}")
