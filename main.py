import os
import json
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


rawRivenIDs = []
newRivenIDs = []
fullListOfWeapons = []
fullListOfCategories = []

updateRivens = True
mongoID = 170204
query = {"_id": mongoID}

url = "https://api.warframe.market/v1/auctions?type=rivens"
session = HTMLSession()
client = commands.Bot(command_prefix='.')
channel1 = channel
rawItemjson = session.get("https://api.warframe.market/v1/riven/items").json()
items = rawItemjson['payload']['items']


cluster = MongoClient("mongodb+srv://GOTWIC:Swagnik10Caesar12_MED@cluster1.mu094.mongodb.net/test?ssl=true&ssl_cert_reqs=CERT_NONE")
db = cluster["Riven_Sniper_Database"]
collection1 = db["Old_Riven_Log"]
collection2 = db["Riven_Notification_List_Primaries"]
collection3 = db["Riven_Notification_List_Secondaries"]
collection4 = db["Riven_Notification_List_Melees"]
collection5 = db["Riven_Notification_List_Miscellaneous"]

@client.event
async def on_ready():
    print('\n\n|/---~---~---~---~---~---~---~---\|')
    print('| ~~ Logged in as ' + client.user.name + ' ~~ |')
    print('|\---~---~---~---~---~---~---~---/|\n\n')
    await info(getALLChannel())

async def getNewRivens(channel1):
    while updateRivens:
        
        oldRivenIDs = queryMongoForOldRivens()
        rawDatajson = getRawData()
        auctions = rawDatajson['payload']['auctions']

        rawRivenIDs = []

        for id in auctions: 
           rawRivenIDs.append(id['id'])
        
        newRivenIDs = [x for x in rawRivenIDs if x not in set(oldRivenIDs)]

        field = "Riven_IDs"
  
        updateMongo(rawRivenIDs, field, collection1) 

        numberOfRivens = getArrSize(newRivenIDs)


        if(numberOfRivens == 0):
            embed = discord.Embed(
                title = 'No new rivens have been created!',
                #description = 'This is a description',
                color = discord.Color.purple()
            )
            await channel1.send(embed=embed)

        else:
            for item in range(numberOfRivens):

                index = numberOfRivens - (item + 1)
                auction = auctions[index]
                riven = auction['item']
                seller = auction['owner']
                rivenStats = ["", "", "", ""]
                statCount = 0

                auctionUrl = "(https://warframe.market/auction/" + auction['id'] + ")"

                if(auctions[index]['item']['type'] == "sister" or auctions[index]['item']['type'] == "lich"):
                    continue

                slot = getItemAttribute(riven['weapon_url_name'], 'group')
                icon = getItemAttribute(riven['weapon_url_name'], 'icon')

                embed = discord.Embed(
                    title = riven['weapon_url_name'].replace("_", " ").title() + " " + riven['name'].title(),
                    description = "Click [here]" + auctionUrl + " to go to auction",
                    color = discord.Color.purple()
                )

                embed.set_thumbnail(url="https://warframe.market/static/assets/" + icon)

                for stat in riven['attributes']:
                    rawStat = stat['url_name'].replace("_", " ").title()
                    result = abbreviateStat(rawStat, slot)  + ": " + str(stat['value'])
                    rivenStats[statCount] = result
                    statCount += 1
                embed.add_field(name='Stats', value= rivenStats[0] + '\n' + rivenStats[1] + '\n' + rivenStats[2] + '\n' + rivenStats[3], inline=True)
            
                buyout = str(auction['buyout_price'])
                topBid = str(auction['top_bid'])
                if(buyout == "None"):
                    buyout = "∞"
                if(topBid == "None"):
                    topBid = "0"
                if(auction['is_direct_sell'] == True):
                    embed.add_field(name='Offer', value='Sell Price: ' + str(auction['starting_price']), inline=True)
                else:
                    embed.add_field(name='Offer', value='Starting Price: ' + str(auction['starting_price']) + "\n Buyout Price: " + buyout + "\n Top Bid: " + topBid, inline=True)
            
                embed.add_field(name='Seller', value=seller['ingame_name'] + '\n' + seller['status'].title(), inline=True)

                #embed.add_field(name='Auction Link', value="Click [here]" + auctionUrl + " to go to auction", inline=True)


                await channel1.send(embed=embed)

        await asyncio.sleep(30)


@client.command(name="add")
async def _command(ctx):
    global times_used
    await ctx.send(f"What weapon would you like to add to your watch list?")

    notificationSetup()

    #def check(msg):
    #    return msg.author == ctx.author and msg.channel == ctx.channel and \
    #    msg.content.lower() in ["y", "n"]

    msg = await client.wait_for("message")#, check=check)
    
    weaponExists(msg.content.lower())


    #await ctx.send("You said no!")
        


#║╔═════════════════════════════════════════════════════════════════════════╗║#
#║║ ███████╗██╗░░░██╗███╗░░██╗░█████╗░████████╗██╗░█████╗░███╗░░██╗░██████╗ ║║#
#║║ ██╔════╝██║░░░██║████╗░██║██╔══██╗╚══██╔══╝██║██╔══██╗████╗░██║██╔════╝ ║║#
#║║ █████╗░░██║░░░██║██╔██╗██║██║░░╚═╝░░░██║░░░██║██║░░██║██╔██╗██║╚█████╗░ ║║#
#║║ ██╔══╝░░██║░░░██║██║╚████║██║░░██╗░░░██║░░░██║██║░░██║██║╚████║░╚═══██╗ ║║#
#║║ ██║░░░░░╚██████╔╝██║░╚███║╚█████╔╝░░░██║░░░██║╚█████╔╝██║░╚███║██████╔╝ ║║#
#║║ ╚═╝░░░░░░╚═════╝░╚═╝░░╚══╝░╚════╝░░░░╚═╝░░░╚═╝░╚════╝░╚═╝░░╚══╝╚═════╝░ ║║#
#║╚═════════════════════════════════════════════════════════════════════════╝║#


def getALLChannel():
    return client.get_channel(868140630491140137)

def queryMongoForOldRivens():
    if (collection1.count_documents(query) == 0):
        collection1.insert_one({"_id": mongoID, "Riven_IDs": []})
             
    user = collection1.find(query)
    for result in user:
        IDs = result["Riven_IDs"]

    return IDs

def notificationSetup():

    for item in items:
        fullListOfWeapons.append(item['url_name'])
        fullListOfCategories.append(item['group'])

    if (collection2.count_documents(query) == 0):
        PrimaryWeaponNames = []
        SecondaryWeaponNames = []
        MeleeWeaponName = []
        MiscWeaponNames = []

        field = 'init'

        createNotifCollection(0, field, collection2, "primary", PrimaryWeaponNames, items)
        createNotifCollection(0, field, collection3, "secondary", SecondaryWeaponNames, items)
        createNotifCollection(0, field, collection4, "melee", MeleeWeaponName, items)
        createNotifCollection(0, field, collection5, "misc", MiscWeaponNames, items)
        
def weaponExists(weaponName):

    print(type(weaponName))

    search1 = []
    user = collection2.find(query)
    for result in user:
        search1 = result[weaponName]
    updateMongo(["1", "2"], search1, collection2)
    print(search1)
    
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
    rawDatajson = session.get(url).json()
    return rawDatajson

@client.command()
async def info(channel):
    client.loop.create_task(getNewRivens(channel))
    #print("h")





client.run('ODY4MTM3NjQyMzA5NTgyODU4.YPrSLw.ewZd22TCBkDTDMN-__QxwjhZ9uM')




# Try to get values from Mongo - Doesn't Work
    #if (collection1.count_documents(query) == 1):
        #updateMongo(rawItemjson, "Item_Data")
    
    #weaponInfo = collection1.find_one({ "_id": mongoID, "Item_Data.payload.items.item_name" : "Kulstar" },
    #{ "Item_Data.payload.items.$": 1 })['Item_Data']['payload']
