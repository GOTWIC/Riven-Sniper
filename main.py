import os
import json
from discord import channel
from discord.message import Message
from requests_html import HTMLSession
import discord
from discord.ext import commands
import asyncio
import pymongo
from pymongo import MongoClient


rawRivenIDs = []
newRivenIDs = []

updateRivens = True

url = "https://api.warframe.market/v1/auctions?type=rivens"
session = HTMLSession()
client = commands.Bot(command_prefix='.')
channel1 = channel


cluster = MongoClient("mongodb+srv://GOTWIC:Swagnik10Caesar12_MED@cluster1.mu094.mongodb.net/test?ssl=true&ssl_cert_reqs=CERT_NONE")
db = cluster["Riven_Sniper_Database"]
collection = db["Old_Riven_Log"]

mongoID = 170204

query = {"_id": mongoID}



@client.event
async def on_ready():
    print('\n\n|/---~---~---~---~---~---~---~---\|')
    print('| ~~ Logged in as ' + client.user.name + ' ~~ |')
    print('|\---~---~---~---~---~---~---~---/|\n\n')
    await info(setChannel1())

# Channel for all rivens
def setChannel1():
    return client.get_channel(868140630491140137)

# Get list of old riven IDs
def queryMongo1():
    if (collection.count_documents(query) == 0):
        collection.insert_one({"_id": mongoID, "Riven_IDs": []})
        
    user = collection.find(query)
    for result in user:
        IDs = result["Riven_IDs"]

    return IDs
    

async def getNewRivens(channel1):
    while updateRivens:
        
        oldRivenIDs = queryMongo1()
        rawDatajson = getRawData()
        auctions = rawDatajson['payload']['auctions']

        rawRivenIDs = []

        for id in auctions: 
           rawRivenIDs.append(id['id'])
        
        newRivenIDs = [x for x in rawRivenIDs if x not in set(oldRivenIDs)]

        field = "Riven_IDs"
  

        
        #collection.delete_one(query)
        #collection.insert_one({"_id": mongoID, "Riven_IDs": rawRivenIDs})

        filter = { 'Riven_IDs': [] }
  
        newvalues = { "$set": { 'Riven_IDs': rawRivenIDs } }
  
        updateMongo(rawRivenIDs, field) 

        numberOfRivens = len(newRivenIDs)


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

                embed = discord.Embed(
                    title = riven['weapon_url_name'].replace("_", " ").title() + " " + riven['name'].title(),
                    description = "Click [here]" + auctionUrl + " to go to auction",
                    color = discord.Color.purple()
                )

                for stat in riven['attributes']:
                    rivenStats[statCount] = stat['url_name'].replace("_", " ").title() + ": " + str(stat['value'])
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
            #await asyncio.sleep(.5)



        await asyncio.sleep(30)

def updateMongo(arr, field):
    collection.update_one(query, { "$set": { field: arr } })

def getRawData():
    rawDatajson = session.get(url).json()
    return rawDatajson


@client.command()
async def info(channel):
    client.loop.create_task(getNewRivens(channel))




client.run('ODY4MTM3NjQyMzA5NTgyODU4.YPrSLw.ewZd22TCBkDTDMN-__QxwjhZ9uM')


# To-Do
# Channeling Damage = Initial Combo
# Base Damage / Melee Damage = Damage
# Critical Chance On Slide Attack = Slide CC
#
#



