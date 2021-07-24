import os
import json
from discord import channel
from discord.message import Message
from requests_html import HTMLSession
import discord
from discord.ext import commands
import asyncio

rawRivenIDs = []
newRivenIDs = []

updateRivens = True

url = "https://api.warframe.market/v1/auctions?type=rivens"
session = HTMLSession()

client = commands.Bot(command_prefix='.')

channel1 = channel




@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await info(client.get_channel(868140630491140137))

async def setChannel1():
    channel1 = client.get_channel(868140630491140137)
    return channel1



async def my_task(channel1):
    while updateRivens:
        
        rawDatajson = session.get(url).json()
        auctions = rawDatajson['payload']['auctions']
        for id in auctions: 
           rawRivenIDs.append(id['id'])
        newRivenIDs = [x for x in rawRivenIDs if x not in set(json.load(open('oldRivenIDs.json')))]
        with open('oldRivenIDs.json', 'w') as json_file:
          json.dump(rawRivenIDs, json_file)

        numberOfRivens = len(newRivenIDs)


        #if(numberOfRivens == 0):
        #    embed = discord.Embed(
        #        title = 'No new rivens have been created!',
        #        #description = 'This is a description',
        #        color = discord.Color.purple()
        #    )
        #    await channel1.send(embed=embed)

        for item in range(numberOfRivens):
            index = numberOfRivens - (item + 1)
            auction = auctions[index]
            riven = auction['item']
            seller = auction['owner']
            rivenStats = ["", "", "", ""]
            statCount = 0

            if(auctions[index]['item']['type'] == "sister" or auctions[index]['item']['type'] == "lich"):
                continue


    
            embed = discord.Embed(
                title = riven['weapon_url_name'].replace("_", " ").title() + " " + riven['name'].title(),
                #description = 'This is a description',
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

            await channel1.send(embed=embed)
            await asyncio.sleep(1)




        await asyncio.sleep(30)


@client.command()
async def info(channel):
    client.loop.create_task(my_task(channel))




client.run('ODY4MTM3NjQyMzA5NTgyODU4.YPrSLw.ewZd22TCBkDTDMN-__QxwjhZ9uM')



