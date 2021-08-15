import os
import json
from re import sub
from discord.abc import User
from discord.guild import Guild
import pymongo
from discord import channel
from discord.client import Client
from discord.message import Message
from pymongo import collection
from pymongo.message import update
from pymongo.read_preferences import Primary
from requests_html import HTMLSession
import discord
from discord.ext import commands
import asyncio
from pymongo import MongoClient
import re
from bs4 import BeautifulSoup
import itertools


intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents = discord.Intents(messages=True, guilds=True)


WFM_rawRivenIDs = []
newRivenIDs = []
fullListOfWeapons = []
fullListOfCategories = []

updateRivens = True
mongoID = 170204
query = {"_id": mongoID}

WFM_url = "https://api.warframe.market/v1/auctions?type=rivens"
RM_url = ""
WFM_session = HTMLSession()
RM_session = HTMLSession()
client = commands.Bot(command_prefix='.', intents=intents)
# Universal Item Info
rawItemjson = WFM_session.get("https://api.warframe.market/v1/riven/items").json()
items = rawItemjson['payload']['items']

# Indexes: All Rivens, Unrolled Rivens
channels = [868140630491140137, 870140373723394058]

# Mongo
cluster = MongoClient("mongodb+srv://GOTWIC:Swagnik10Caesar12_MED@cluster1.mu094.mongodb.net/test?ssl=true&ssl_cert_reqs=CERT_NONE")
db = cluster["Riven_Sniper_Database"]
collection1 = db["Old_Riven_Log"]
collection2 = db["Riven_Notification_List_Primaries"]
collection3 = db["Riven_Notification_List_Secondaries"]
collection4 = db["Riven_Notification_List_Melees"]
collection5 = db["Riven_Notification_List_Miscellaneous"]
collection6 = db["Notification_Settings"]
collection7 = db["Encoding Lookup Table"]

# Lists
listOfStats = ['Ammo Max', 'Attack Speed', 'Cold', 'Combo Count Chance', 'Combo Duration', 'Combo Efficiency', 'Corpus', 'Critical Chance', 'Critical Damage', 'Damage', 'Electric', 'Finisher', 'Fire Rate', 'Grineer', 'Heat', 'Impact', 'Infested', 'Initial Combo', 'Magazine Capacity', 'Multishot', 'Projectile Speed', 'Punch Through', 'Puncture', 'Range', 'Recoil', 'Reload Speed', 'Slash', 'Slide CC', 'Status Chance', 'Status Duration', 'Toxin', 'Zoom']
primeNumbers = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997, 1009, 1013, 1019, 1021, 1031, 1033, 1039, 1049, 1051, 1061, 1063, 1069, 1087, 1091, 1093, 1097, 1103, 1109, 1117, 1123, 1129, 1151, 1153, 1163, 1171, 1181, 1187, 1193, 1201, 1213, 1217, 1223, 1229, 1231, 1237, 1249, 1259, 1277, 1279, 1283, 1289, 1291, 1297, 1301, 1303, 1307, 1319, 1321, 1327, 1361, 1367, 1373, 1381, 1399, 1409, 1423, 1427, 1429, 1433, 1439, 1447, 1451, 1453, 1459, 1471, 1481, 1483, 1487, 1489, 1493, 1499, 1511, 1523, 1531, 1543, 1549, 1553, 1559, 1567, 1571, 1579, 1583, 1597, 1601, 1607, 1609, 1613, 1619, 1621, 1627, 1637, 1657, 1663, 1667, 1669, 1693, 1697, 1699, 1709, 1721, 1723, 1733, 1741, 1747, 1753, 1759, 1777, 1783, 1787, 1789, 1801, 1811, 1823, 1831, 1847, 1861, 1867, 1871, 1873, 1877, 1879, 1889, 1901, 1907, 1913, 1931, 1933, 1949, 1951, 1973, 1979, 1987, 1993, 1997, 1999, 2003, 2011, 2017, 2027, 2029, 2039, 2053, 2063, 2069, 2081, 2083, 2087, 2089, 2099, 2111, 2113, 2129, 2131, 2137, 2141, 2143, 2153, 2161, 2179, 2203, 2207, 2213, 2221, 2237, 2239, 2243, 2251, 2267, 2269, 2273, 2281, 2287, 2293, 2297, 2309, 2311, 2333, 2339, 2341, 2347, 2351, 2357, 2371, 2377, 2381, 2383, 2389, 2393, 2399, 2411, 2417, 2423, 2437, 2441, 2447, 2459, 2467, 2473, 2477, 2503, 2521, 2531, 2539, 2543, 2549, 2551, 2557, 2579, 2591, 2593, 2609, 2617, 2621, 2633, 2647, 2657, 2659, 2663, 2671, 2677, 2683, 2687, 2689, 2693, 2699, 2707, 2711, 2713, 2719, 2729, 2731, 2741, 2749, 2753, 2767, 2777, 2789, 2791, 2797, 2801, 2803, 2819, 2833, 2837, 2843, 2851, 2857, 2861, 2879, 2887, 2897, 2903, 2909, 2917, 2927, 2939, 2953, 2957, 2963, 2969, 2971, 2999, 3001, 3011, 3019, 3023, 3037, 3041, 3049, 3061, 3067, 3079, 3083, 3089, 3109, 3119, 3121, 3137, 3163, 3167, 3169, 3181, 3187, 3191, 3203, 3209, 3217, 3221, 3229, 3251, 3253, 3257, 3259, 3271, 3299, 3301, 3307, 3313, 3319, 3323, 3329, 3331, 3343, 3347, 3359, 3361, 3371, 3373, 3389, 3391, 3407, 3413, 3433, 3449, 3457, 3461, 3463, 3467, 3469, 3491, 3499, 3511, 3517, 3527, 3529, 3533, 3539, 3541, 3547, 3557, 3559, 3571, 3581, 3583, 3593, 3607, 3613, 3617, 3623, 3631, 3637, 3643, 3659, 3671, 3673, 3677, 3691, 3697, 3701, 3709, 3719, 3727, 3733, 3739, 3761, 3767, 3769, 3779, 3793, 3797, 3803, 3821, 3823, 3833, 3847, 3851, 3853, 3863, 3877, 3881, 3889, 3907, 3911, 3917, 3919, 3923, 3929, 3931, 3943, 3947, 3967, 3989, 4001, 4003, 4007, 4013, 4019, 4021, 4027, 4049, 4051, 4057, 4073, 4079, 4091, 4093, 4099, 4111, 4127, 4129, 4133, 4139, 4153, 4157, 4159, 4177, 4201, 4211, 4217, 4219, 4229, 4231, 4241, 4243, 4253, 4259, 4261, 4271, 4273, 4283, 4289, 4297, 4327, 4337, 4339, 4349, 4357, 4363, 4373, 4391, 4397, 4409, 4421, 4423, 4441, 4447, 4451, 4457, 4463, 4481, 4483, 4493, 4507, 4513, 4517, 4519, 4523, 4547, 4549, 4561, 4567, 4583, 4591, 4597, 4603, 4621, 4637, 4639, 4643, 4649, 4651, 4657, 4663, 4673, 4679, 4691, 4703, 4721, 4723, 4729, 4733, 4751, 4759, 4783, 4787, 4789, 4793, 4799, 4801, 4813, 4817, 4831, 4861, 4871, 4877, 4889, 4903, 4909, 4919, 4931, 4933, 4937, 4943, 4951, 4957, 4967, 4969, 4973, 4987, 4993, 4999, 5003, 5009, 5011, 5021, 5023, 5039, 5051, 5059, 5077, 5081, 5087, 5099, 5101, 5107, 5113, 5119, 5147, 5153, 5167, 5171, 5179, 5189, 5197, 5209, 5227, 5231, 5233, 5237, 5261, 5273, 5279, 5281, 5297, 5303, 5309, 5323, 5333, 5347, 5351, 5381, 5387, 5393, 5399, 5407, 5413, 5417, 5419, 5431, 5437, 5441, 5443, 5449, 5471, 5477, 5479, 5483, 5501, 5503, 5507, 5519, 5521, 5527, 5531, 5557, 5563, 5569, 5573, 5581, 5591, 5623, 5639, 5641, 5647, 5651, 5653, 5657, 5659, 5669, 5683, 5689, 5693, 5701, 5711, 5717, 5737, 5741, 5743, 5749, 5779, 5783, 5791, 5801, 5807, 5813, 5821, 5827, 5839, 5843, 5849, 5851, 5857, 5861, 5867, 5869, 5879, 5881, 5897, 5903, 5923, 5927, 5939, 5953, 5981, 5987, 6007, 6011, 6029, 6037, 6043, 6047, 6053, 6067, 6073, 6079, 6089, 6091, 6101, 6113, 6121, 6131, 6133, 6143, 6151, 6163, 6173, 6197, 6199, 6203, 6211, 6217, 6221, 6229, 6247, 6257, 6263, 6269, 6271, 6277, 6287, 6299, 6301, 6311, 6317, 6323, 6329, 6337, 6343, 6353, 6359, 6361, 6367, 6373, 6379, 6389, 6397, 6421, 6427, 6449, 6451, 6469, 6473, 6481, 6491, 6521, 6529, 6547, 6551, 6553, 6563, 6569, 6571, 6577, 6581, 6599, 6607, 6619, 6637, 6653, 6659, 6661, 6673, 6679, 6689, 6691, 6701, 6703, 6709, 6719, 6733, 6737, 6761, 6763, 6779, 6781, 6791, 6793, 6803, 6823, 6827, 6829, 6833, 6841, 6857, 6863, 6869, 6871, 6883, 6899, 6907, 6911, 6917, 6947, 6949, 6959, 6961, 6967, 6971, 6977, 6983, 6991, 6997, 7001, 7013, 7019, 7027, 7039, 7043, 7057, 7069, 7079, 7103, 7109, 7121, 7127, 7129, 7151, 7159, 7177, 7187, 7193, 7207, 7211, 7213, 7219, 7229, 7237, 7243, 7247, 7253, 7283, 7297, 7307, 7309, 7321, 7331, 7333, 7349, 7351, 7369, 7393, 7411, 7417, 7433, 7451, 7457, 7459, 7477, 7481, 7487, 7489, 7499, 7507, 7517, 7523, 7529, 7537, 7541, 7547, 7549, 7559, 7561, 7573, 7577, 7583, 7589, 7591, 7603, 7607, 7621, 7639, 7643, 7649, 7669, 7673, 7681, 7687, 7691, 7699, 7703, 7717, 7723, 7727, 7741, 7753, 7757, 7759, 7789, 7793, 7817, 7823, 7829, 7841, 7853, 7867, 7873, 7877, 7879, 7883, 7901, 7907, 7919]


@client.event
async def on_ready():
    print('\n\n|/---~---~---~---~---~---~---~---\|')
    print('| ~~ Logged in as ' + client.user.name + ' ~~ |')
    print('|\---~---~---~---~---~---~---~---/|\n\n')
    buildNotificationCollections()
    await info()

async def mainCycle():
    while updateRivens:
        
        #auctins, numberofrivs = getNewRivensFromWFM()


        WFM_oldRivenIDs = queryMongoForOldRivens()
        WFM_rawDatajson = getRawData()
        auctions = WFM_rawDatajson['payload']['auctions']
        WFM_rawRivenIDs = []
        for id in auctions: 
           WFM_rawRivenIDs.append(id['id'])
        newRivenIDs = [x for x in WFM_rawRivenIDs if x not in set(WFM_oldRivenIDs)]
        field = "Riven_IDs"
        updateMongo(WFM_rawRivenIDs, field, collection1) 
        numberOfRivens = getArrSize(newRivenIDs)

        # Warframe Market
        if(numberOfRivens != 0):
            for item in range(numberOfRivens):

                index = numberOfRivens - (item + 1)
                auction = auctions[index]
                rivenStats = ["", "", "", ""]
                rivenAttributeList = []
                statCount = 0
                auctionInfo = ""
                negative = False

                if(auction['item']['type'] == "sister" or auction['item']['type'] == "lich"):
                    continue

                riven = auction['item']
                seller = auction['owner']
                weaponName = riven['weapon_url_name']
                rivenName = riven['name']
                auctionURL = "(https://warframe.market/auction/" + auction['id'] + ")"
                icon = getItemAttribute(riven['weapon_url_name'], 'icon')
                slot = getItemAttribute(riven['weapon_url_name'], 'group')
                isDirectSell = auction['is_direct_sell']
                buyout = str(auction['buyout_price'])
                topBid = str(auction['top_bid'])
                rolls = riven['re_rolls']

                if(buyout == "None"):
                    buyout = "∞"
                if(topBid == "None"):
                    topBid = "0"
                if(isDirectSell == True):
                    auctionInfo = 'Sell Price: ' + str(auction['starting_price'])
                else:
                    auctionInfo = 'Starting Price: ' + str(auction['starting_price']) + "\n Buyout Price: " + buyout + "\n Top Bid: " + topBid
                for stat in riven['attributes']:
                    rawStat = stat['url_name'].replace("_", " ").title()
                    rivenStats[statCount] = abbreviateStat(rawStat, slot)  + ": " + str(stat['value'])
                    rivenAttributeList.append(abbreviateStat(rawStat, slot))
                    if(stat['positive'] == False):
                        negative = True
                    statCount += 1 
                encodedID = encodeRiven(weaponName, rivenAttributeList, negative, 0)
                rivenEmbed = createRivenEmbed(weaponName, rivenName, auctionURL, seller, icon, auctionInfo, rivenStats, encodedID)
                await sendRivenEmbed(rivenEmbed, rolls, weaponName, encodedID)

        # Riven Market
                

        await asyncio.sleep(30)

@client.command(name="add")
async def _add(ctx, *, arg):

    if(userExists(ctx.author.id) == False):
        await sendSimpleEmbed("You first need to setup your notifications using the <.setup notifications> command!", "", ctx.channel)
    else:
        if "|" in arg:
            args = arg.split(" | ", 1)
            weapon = args[0]
            stat = args[1]
            weaponMongoFormat = weapon.lower().replace(" ","_")    
            if(weaponExists(weaponMongoFormat) or weapon == "#"):
                if(weapon == "#"):
                    weaponMongoFormat = ""
                stats = stat.split(" , ")
                flag = False
                negative = False
                for item in range(len(stats)):
                    stats[item] = stats[item].title()
                    if("-" in stats[item]):
                        stats[item] = stats[item].replace("-", "")
                        negative = True
                    if(stats[item] not in listOfStats):
                        flag = True
                        print(stats[item])
                if(flag == False):
                    encodedID = encodeRiven(weaponMongoFormat, stats, negative, 0)
                    print(hex(encodedID))
            else:
                await sendSimpleEmbed("That weapon does not exist!", "", ctx.channel)
            
        # Temporary
        else:
            weaponMongoFormat = arg.lower().replace(" ","_")    
            if(weaponExists(weaponMongoFormat)):
                if(addUserToWeaponList(getWeaponCollection(weaponMongoFormat), weaponMongoFormat, ctx.author.id)):
                    await sendSimpleEmbed(arg.title() + " has been added your watch list!", "", ctx.channel)
                else:
                    await sendSimpleEmbed(arg.title() + " is already on your watch list!", "", ctx.channel)
            else:
                await sendSimpleEmbed("That weapon does not exist!", "", ctx.channel)

@client.command(name="remove")
async def _remove(ctx, *, args):
    if(args == None):
        await sendSimpleEmbed("You need to Input a Weapon Name!", "", ctx.channel)
    else:
        weaponMongoFormat = args.lower().replace(" ","_")    
        if(weaponExists(weaponMongoFormat)):
            if(removeUserFromWeaponList(getWeaponCollection(weaponMongoFormat), weaponMongoFormat, ctx.author.id)):
                await sendSimpleEmbed(args.title() + " has been removed your watch list!", "", ctx.channel)
            else:
                await sendSimpleEmbed(args.title() + " is not on your watch list!", "", ctx.channel)
        else:
            await sendSimpleEmbed("That weapon does not exist!", "", ctx.channel)

@client.command(name="update")
async def _update(ctx, *, args):

    if(userExists(ctx.author.id) == False):
        await sendSimpleEmbed("You first need to setup your notifications using the <.setup notifications> command!", "", ctx.channel)
    else:
        if(args.lower() == "channel"):
            if(getUserInfo(ctx.author.id, 0) != ctx.channel.id):
                oldChannel = getUserInfo(ctx.author.id, 0)
                collection6.update_one({"_id": ctx.author.id, "UserInfo": oldChannel}, { "$set": { "UserInfo.$": ctx.channel.id } })
                await sendSimpleEmbed("Updated Channel!", "", ctx.channel)
            else:
                await sendSimpleEmbed("This channel is already your default channel!", "", ctx.channel)
        if(args.lower() == "notifications"):
            await changeUserInfo(ctx, 1)

@client.command(name="setup")
async def _setup(ctx, *, args):
    if(args.lower() == "notifications"):
        if(userExists(ctx.author.id) == False):
            await changeUserInfo(ctx, 0)
        
@client.command(name="try")
async def _try(ctx):
    negatives = []
    for stat in range(len(listOfStats)):
        negatives.append("Negative " + listOfStats[stat])
    master = list(itertools.chain(listOfStats, negatives, fullListOfWeapons))
    insertMongo(2, "Unrolled", collection7)
    for entry in range(len(master)):
        updateMongo(primeNumbers[entry],master[entry], collection7)

@client.command(name="admin")
async def _admin(ctx, *, args):
    if(ctx.author.id == 473517971529138201):
        if(args == "start"):
            updateRivens = True
        elif(args == "stop"):
            updateRivens = False



#║╔═════════════════════════════════════════════════════════════════════════╗║#
#║║ ███████╗██╗░░░██╗███╗░░██╗░█████╗░████████╗██╗░█████╗░███╗░░██╗░██████╗ ║║#
#║║ ██╔════╝██║░░░██║████╗░██║██╔══██╗╚══██╔══╝██║██╔══██╗████╗░██║██╔════╝ ║║#
#║║ █████╗░░██║░░░██║██╔██╗██║██║░░╚═╝░░░██║░░░██║██║░░██║██╔██╗██║╚█████╗░ ║║#
#║║ ██╔══╝░░██║░░░██║██║╚████║██║░░██╗░░░██║░░░██║██║░░██║██║╚████║░╚═══██╗ ║║#
#║║ ██║░░░░░╚██████╔╝██║░╚███║╚█████╔╝░░░██║░░░██║╚█████╔╝██║░╚███║██████╔╝ ║║#
#║║ ╚═╝░░░░░░╚═════╝░╚═╝░░╚══╝░╚════╝░░░░╚═╝░░░╚═╝░╚════╝░╚═╝░░╚══╝╚═════╝░ ║║#
#║╚═════════════════════════════════════════════════════════════════════════╝║#

async def sendSimpleEmbed(title1, description1, channel):
    embed = discord.Embed(
                title = title1,
                description = description1,
                color = discord.Color.purple()
            )
    await channel.send(embed=embed)
   
async def sendRivenEmbed(embed, rolls, weaponName, encodedID):
    await client.get_channel(channels[0]).send(embed=embed)
    if(rolls == 0):
        await client.get_channel(channels[1]).send(embed=embed)
    weapons = getWeaponCollection(weaponName).find(query)
    for weapon in weapons:
        notifList = weapon[weaponName]
    if(len(notifList)!=0):
        for userID in notifList:
            if(getUserInfo(userID, 1) == "direct messages"):
                user = await client.fetch_user(userID)      
                await user.send(embed=embed)
            elif(getUserInfo(userID, 1) == "this channel"):
                await client.get_channel(getUserInfo(userID, 0)).send(embed=embed)
            elif(getUserInfo(userID, 1) == "both"):
                user = await client.fetch_user(userID)      
                await user.send(embed=embed)
                await client.get_channel(getUserInfo(userID, 0)).send(embed=embed)

def createRivenEmbed(weaponName, rivenName, auctionURL, seller, thumbnail, auctionInfo, rivenStats, encodedID):
    embed = discord.Embed(
        title = weaponName.replace("_", " ").title() + " " + rivenName.title(),
        description = "Click [here]" + auctionURL + " to go to auction",
        color = discord.Color.purple()
        )
    embed.add_field(name='Stats', value= rivenStats[0] + '\n' + rivenStats[1] + '\n' + rivenStats[2] + '\n' + rivenStats[3], inline=True)
    embed.add_field(name='Offer', value=auctionInfo, inline=True)
    embed.add_field(name='Seller', value=seller['ingame_name'] + '\n' + seller['status'].title(), inline=True)
    embed.set_thumbnail(url="https://warframe.market/static/assets/" + thumbnail)
    embed.set_footer(text = "Encoded ID: " + hex(encodedID)[2:])

    return embed

def queryMongoForOldRivens():
    if (collection1.count_documents(query) == 0):
        collection1.insert_one({"_id": mongoID, "Riven_IDs": []})
    user = collection1.find(query)
    for result in user:
        IDs = result["Riven_IDs"]
    return IDs

def buildNotificationCollections():
    field = 'init'
    for item in items:
        fullListOfWeapons.append(item['url_name'])
        fullListOfCategories.append(item['group'])
    if (collection2.count_documents(query) == 0):
        PrimaryWeaponNames = []
        createNotifCollection(0, field, collection2, "primary", PrimaryWeaponNames, items)
    if (collection3.count_documents(query) == 0):
        SecondaryWeaponNames = []
        createNotifCollection(0, field, collection3, "secondary", SecondaryWeaponNames, items)
    if (collection4.count_documents(query) == 0):
        MeleeWeaponName = []
        createNotifCollection(0, field, collection4, "melee", MeleeWeaponName, items)
    if (collection5.count_documents(query) == 0):
        MiscWeaponNames = []
        createNotifCollection(0, field, collection5, "misc", MiscWeaponNames, items)
        
def weaponExists(weaponName):  
    if(weaponName in fullListOfWeapons):
        return True
    else:
        return False

def getWeaponCollection(weaponName):  

    weaponSlot = fullListOfCategories[fullListOfWeapons.index(weaponName)]

    if(weaponSlot == "primary"):
        return collection2
    elif(weaponSlot == "secondary"):
        return collection3
    elif(weaponSlot == "melee"):
        return collection4
    else:
        return collection5

def addUserToWeaponList(collection, weaponName, userID):
    mongoWeaponList = collection.find(query)
    for weapon in mongoWeaponList:
        sublist = weapon[weaponName]
    if(userID in sublist):
        return False
    else:
        sublist.append(userID)
        updateMongo(sublist, weaponName, collection)
        addWeaponToUserInfo(userID, weaponName)
        return True  

def addWeaponToUserInfo(userID, weaponName):
    listOfWeapons = getUserInfo(userID, 2)
    listOfWeapons.append(weaponName)
    collection6.update_one({"_id": userID, "UserInfo": getUserInfo(userID, 2)}, { "$set": { "UserInfo.$": listOfWeapons} })

def removeUserFromWeaponList(collection, weaponName, userID):
    mongoWeaponList = collection.find(query)
    for weapon in mongoWeaponList:
        sublist = weapon[weaponName]
    if(userID in sublist):
        sublist.remove(userID)
        updateMongo(sublist, weaponName, collection)
        removeWeaponFromUserInfo(userID, weaponName)
        return True
    else:
        return False
 
def removeWeaponFromUserInfo(userID, weaponName):
    listOfWeapons = getUserInfo(userID, 2)
    listOfWeapons.remove(weaponName)
    collection6.update_one({"_id": userID, "UserInfo": getUserInfo(userID, 2)}, { "$set": { "UserInfo.$": listOfWeapons} })

def getItemAttribute(string, type):
    for item in items:
        if(item['url_name'] == string):
            return item[type]

def createNotifCollection(value, field, collection, type, arr, theItems):
    insertMongo(value, field, collection)
    for item in theItems:
        if(type == "misc"):
            if(item['group'] == "zaw" or item['group'] == "sentinel" or item['group'] == "archgun" or item['group'] == "kitgun"):
                arr.append(item['url_name'])
        else:
            if(item['group'] == type):
                arr.append(item['url_name'])
    for weapon in arr:
            updateMongo([], weapon, collection)

def abbreviateStat(string, slot):
    result = string

    if(string == 'Base Damage / Melee Damage'):
        result = 'Damage'
    if(string == "Fire Rate / Attack Speed"):
        if(slot == "melee"):
            result = "Attack Speed"
        else:
            result = "Fire Rate"
    if(string == "Ammo Maximum"):
        result = "Ammo Max"
    if(string == "Toxin Damage"):
        result = "Toxin"
    if(string == "Cold Damage"):
        result = "Cold"
    if(string == "Heat Damage"):
        result = "Heat"
    if(string == "Electric Damage"):
        result = "Electric"
    if(string == "Impact Damage"):
        result = "Impact"
    if(string == "Slash Damage"):
        result = "Slash"
    if(string == "Puncture Damage"):
        result = "Puncture"
    if(string == "Finisher Damage"):
        result = "Finisher"
    if(string == "Critical Chance On Slide Attack"):
        result = "Slide CC"
    if(string == "Chance To Gain Extra Combo Count" or string == "Chance To Gain Combo Count"):
        result = "Combo Count Chance"
    if(string == "Channeling Damage"):
        result = "Initial Combo"
    if(string == "Channeling Efficiency"):
        result = "Combo Efficiency"
    if(string == "Damage Vs Grineer"):
        result = "Grineer"
    if(string == "Damage Vs Corpus"):
        result = "Corpus"
    if(string == "Damage Vs Infested"):
        result = "Infested"
    
    return result

def getArrSize(arr):
    num = len(arr)
    return num

def updateMongo(value, field, collection):
    collection.update_one(query, { "$set": { field: value } })

def insertMongo(value, field, collection):
    collection.insert_one({"_id": mongoID, field: value})

def getRawData():
    WFM_rawDatajson = WFM_session.get(WFM_url).json()
    return WFM_rawDatajson

def userExists(userID):
    if collection6.count_documents({ '_id': userID }, limit = 1) == 0:
        return False
    return True

def addToUserList(userID, channelID, preference):
    collection6.insert_one({"_id": userID, "UserInfo": [channelID, preference, [], []]})

def getUserInfo(userID, selectionNumber):
    user = collection6.find({"_id": userID})
    for result in user:
        return result["UserInfo"][selectionNumber]

async def changeUserInfo(ctx, num):
    await sendSimpleEmbed("Where you like to be notified of new rivens?", " - Direct Messages \n - This Channel \n - Both", ctx.channel)  
    def is_correct(m):
        return m.author == ctx.author and m.content.lower() == "both" or m.content.lower() == "direct messages" or m.content.lower() == "this channel"#m.content.isdigit()
    notifPref = await client.wait_for('message', check=is_correct, timeout=60.0)
    if(num == 0):
        addToUserList(ctx.author.id, ctx.channel.id, notifPref.content)
    elif(num == 1):
        collection6.update_one({"_id": ctx.author.id, "UserInfo": getUserInfo(ctx.author.id, 1)}, { "$set": { "UserInfo.$": notifPref.content.lower() } })
    if(notifPref.content != "both"):
        await sendSimpleEmbed("You will be notified via " + str(notifPref.content), "You can change this setting at anytime using the <.update notifications> command \n This channel has been designated as your private channel. You can make another channel your private channel using the <.update channel> command.", ctx.channel)
    else:
        await sendSimpleEmbed("You will now be notified via DMs and this channel", "You can change this setting at anytime using the <.update notifications> command \n This channel has been designated as your private channel. You can make another channel your private channel using the <.update channel> command.", ctx.channel)        

def encodeRiven(weaponName, attributes, negative, rolls):
    user = collection7.find(query)
    encodedID = 1   
    for result in user:
            for stat in range(len(attributes)):
                if(stat == len(attributes)-1):
                    if(negative == True):
                        encodedID *= result["Negative " + attributes[stat]]
                        continue
                encodedID *= result[attributes[stat]]
            if(weaponName != ""):
                encodedID *= result[weaponName.replace(" ", "_").lower()]
    return(encodedID)


@client.command()
async def info():
    client.loop.create_task(mainCycle())




client.run('ODY4MTM3NjQyMzA5NTgyODU4.YPrSLw.ewZd22TCBkDTDMN-__QxwjhZ9uM')


# collection6 Structure - 
#    User Info: 
#       [
#           channel number,
#           "Notification Preference (dms, channel, both)",,
#           [List of subscribed weapons], 
#           [List of subscribed stats]
#       ]



# Try to get values from Mongo - Kind of works, can directly search test instead of aggregating
#   test = collection1.find_one({ "_id": mongoID, "Item_Data.payload.items.item_name" : "Kulstar" },
#    { "Item_Data.payload.items.$": 1 })['Item_Data']['payload']['items']
#
#    test1 = str(list(collection1.aggregate([{"$match": {"Item_Data.payload.items.item_name": "Kulstar"},},{"$unwind": "$Item_Data.payload.items"},{"$match": {"Item_Data.payload.items.item_name": "Kulstar"},},{"$project": {"url_name": "$Item_Data.payload.items.url_name"}}])))
#    test2 = re.search("'url_name': '(.*?)'", test1).group(1)
#    print(test1)
#    print(test2)

#    test3 = str(list(collection1.aggregate([{"$match": {"Item_Data.payload.items.item_name": "Kulstar"},},{"$unwind": "$Item_Data.payload.items"},{"$match": {"Item_Data.payload.items.item_name": "Kulstar"},},{"$group": { "_id": "$_id", "testField": { "$addToSet": "$Item_Data.payload.items.testField" } }, }])))
#    test4 = re.search("'testField': [['(.*?)'", str(list(test))).group(1) # Does not work for some reason
#    print(test3)
#    print(test4)


