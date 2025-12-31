<img width="100%" style="border: 1px solid black" src="https://i.imgur.com/bre34Xl.png">

# FGO Daily Login
FGO Daily Login is a mod of the repository [FGODailyBonus](https://github.com/hexstr/FGODailyBonus)

It has the following features:
- Discord Webhook
- Region NA 

# Extract your auth data
You need to extract your authentication data to do this.
It's simple, all you need to do is navigate to the following path and get the following file: 

| Region | Path | File |
| --- | --- | --- | 
| NA | `android/data/com.aniplex.fategrandorder.en/files/data/` | 54cc790bf952ea710ed7e8be08049531 |

# Decript your data
Be careful with this data, you should not pass this data to other person, this is private data.

1. Open the file with notopad or text editor and copy from **ZSv** to end!
2. Go to [Compiler Online](https://dotnetfiddle.net/ug7C0x) and paste the string
3. You will get all necesary data to fill Secrets

# Discord Webhook 
To create webhook discord you need create a server in discord and create a text channel, in settings of that channel search
`integration > webhook > create webhook > copy url webhook`



# Secrets
Add this enviroment variables into `Repository > settings > secrets > actions`
| Secret | Example |
| --- | --- |
| GAME_AUTHKEYS | RaNdOmStRiNg1234:randomAAAAA=,RaNdOmStRiNg1235:randomAAAAA= |
| GAME_SECRETKEYS | RaNdOmStRiNg1234:randomAAAAA=,RaNdOmStRiNg1235:randomAAAAA= |
| GAME_USERIDS | 60951234,60951235 |
| DISCORD_WEBHOOK | https://discord.com/api/webhooks/randomNumber/randomString |
| DISCORD_USERID | (Optional) 217003486489870336 |

# Road Map
- [ ] Perform Daily Friend Point Summons
- [ ] Claim all Saint Quartz and Tickets from gif box
- [x] Buy monthly summon tickets
- [x] Make blue apple automatic

# Acknowledgments 
- [hexstr](https://github.com/hexstr) author of FGO Daily Bonus