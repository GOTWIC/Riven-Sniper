import os
import json
from re import sub
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


@client.event
async def on_ready():
    print('\n\n|/---~---~---~---~---~---~---~---\|')
    print('| ~~ Logged in as ' + client.user.name + ' ~~ |')
    print('|\---~---~---~---~---~---~---~---/|\n\n')
    await info()
    buildNotificationCollections()

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
                statCount = 0
                auctionInfo = ""

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
                    statCount += 1

                rivenEmbed = createRivenEmbed(weaponName, rivenName, auctionURL, seller, icon, auctionInfo, rivenStats)

                await sendRivenEmbed(rivenEmbed, rolls, weaponName)

        # Riven Market
                

        await asyncio.sleep(30)

@client.command(name="add")
async def _add(ctx, *, args):

    if(args == None):
        await sendSimpleEmbed("You need to Input a Weapon Name!", "", ctx)
    else:
        weaponMongoFormat = args.lower().replace(" ","_")    
        if(weaponExists(weaponMongoFormat)):
            if(addUserToWeaponList(getWeaponCollection(weaponMongoFormat), weaponMongoFormat, ctx.author.id)):
                if(userExists(ctx.author.id) == False):
                    await sendSimpleEmbed("Looks like this is the first time you are adding a riven to your watch list! Where you like to be notified of new rivens?", " - Direct Messages \n - This Channel \n - Both", ctx.channel)  
                    def is_correct(m):
                        return m.author == ctx.author and m.content.lower() == "both" or m.content.lower() == "direct messages" or m.content.lower() == "this channel"#m.content.isdigit()
                    notifPref = await client.wait_for('message', check=is_correct, timeout=60.0)
                    addToUserList(ctx.author.id, ctx.channel.id, notifPref.content)
                    if(notifPref.content != "both"):
                        await sendSimpleEmbed("You will be notified via " + str(notifPref.content), "You can change this setting at anytime using [UNDER DEVELOPMENT]", ctx.channel)
                    else:
                        await sendSimpleEmbed("You will now be notified via DMs and this channel", "You can change this setting at anytime using [UNDER DEVELOPMENT]", ctx.channel)
                await sendSimpleEmbed(args.title() + " has been added your watch list!", "", ctx)
            else:
                await sendSimpleEmbed(args.title() + " is already on your watch list!", "", ctx)
        else:
            await sendSimpleEmbed("That weapon does not exist!", "", ctx)

@client.command(name="remove")
async def _remove(ctx, *, args):
    if(args == None):
        await sendSimpleEmbed("You need to Input a Weapon Name!", "", ctx)
    else:
        weaponMongoFormat = args.lower().replace(" ","_")    
        if(weaponExists(weaponMongoFormat)):
            if(removeUserFromWeaponList(getWeaponCollection(weaponMongoFormat), weaponMongoFormat, ctx.author.id)):
                await sendSimpleEmbed(args.title() + " has been removed your watch list!", "", ctx)
            else:
                await sendSimpleEmbed(args.title() + " is not on your watch list!", "", ctx)
        else:
            await sendSimpleEmbed("That weapon does not exist!", "", ctx)
        

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
   
async def sendRivenEmbed(embed, rolls, weaponName):
    await client.get_channel(channels[0]).send(embed=embed)
    if(rolls == 0):
        await client.get_channel(channels[1]).send(embed=embed)
    weapons = getWeaponCollection(weaponName).find(query)
    for weapon in weapons:
        notifList = weapon[weaponName]
    if(len(notifList)!=0):
        for userID in notifList:
            user = await client.fetch_user(userID)      
            await user.send(embed=embed)

def createRivenEmbed(weaponName, rivenName, auctionURL, seller, thumbnail, auctionInfo, rivenStats):
    embed = discord.Embed(
        title = weaponName.replace("_", " ").title() + " " + rivenName.title(),
        description = "Click [here]" + auctionURL + " to go to auction",
        color = discord.Color.purple()
        )
    embed.add_field(name='Stats', value= rivenStats[0] + '\n' + rivenStats[1] + '\n' + rivenStats[2] + '\n' + rivenStats[3], inline=True)
    embed.add_field(name='Offer', value=auctionInfo, inline=True)
    embed.add_field(name='Seller', value=seller['ingame_name'] + '\n' + seller['status'].title(), inline=True)
    embed.set_thumbnail(url="https://warframe.market/static/assets/" + thumbnail)

    return embed

def queryMongoForOldRivens():
    if (collection1.count_documents(query) == 0):
        collection1.insert_one({"_id": mongoID, "Riven_IDs": []})
    if (collection1.count_documents(query) == 0):
        #collection1.insert_one({"_id": mongoID, "Item_Data": rawItemjson})
        updateMongo(rawItemjson, "Item_Data", collection1)
        #for item in items:
        #    updateMongo(item, item['url_name'], collection1)
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

def addUserToWeaponList(collection, weaponName, authorID):
    mongoWeaponList = collection.find(query)
    for weapon in mongoWeaponList:
        sublist = weapon[weaponName]
    if(authorID in sublist):
        return False
    else:
        sublist.append(authorID)
        updateMongo(sublist, weaponName, collection)
        return True  

def removeUserFromWeaponList(collection, weaponName, authorID):
    mongoWeaponList = collection.find(query)
    for weapon in mongoWeaponList:
        sublist = weapon[weaponName]
    if(authorID in sublist):
        sublist.remove(authorID)
        updateMongo(sublist, weaponName, collection)
        return True
    else:
        return False
 
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

    #result = string
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
        result = "Finsher"
    if(string == "Critical Chance On Slide Attack"):
        result = "Slide CC"
    if(string == "Chance To Gain Extra Combo Count"):
        result = "Combo Count Chance"
    if(string == "Channeling Damage"):
        result = "Initial Combo"
    if(string == "Channeling Efficiency"):
        result = "Combo Efficiency"
    if(string == "Damage Vs Grineed"):
        result = "Grineer"
    if(string == "Damage Vs Corpus"):
        result = "Corpus"
    if(string == "Damage Vs Corrupted"):
        result = "Corrupted"
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
    print(channelID)
    print(type(channelID))



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


