import discord
from discord.ext import commands 

import requests

import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('token')
RAPID_API_KEY = os.getenv('rapid_api_key')

coles_api_url = "https://coles-product-price-api.p.rapidapi.com/coles/product-search/?query="
coles_api_host = "coles-product-price-api.p.rapidapi.com"

woolies_api_url = "https://woolworths-products-api.p.rapidapi.com/woolworths/product-search/?query="
woolies_api_host = "woolworths-products-api.p.rapidapi.com"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='boo ', intents=intents)
bot.remove_command("help")

def parse_response_coles(res) -> float:
    """
    Iterates through the API response to grab the product with the correct name.
    This serves as a sort of safeguard to ensure the price comparision is accurate.
    However mileage may vary lol.
    Returns the price of the white monster.
    """
    json = res.json()
    results = json['results']
    for r in results:
        if r['product_name'] == "Zero Sugar Energy Drink Multipack Cans 4x500mL":
            print("found at coles:",r)
            return float(r['current_price'])


def parse_response_woolies(res):
    """
    Same as parse_response_coles() but unfortunately the APIs give the data with slightly different key names
    (pain)
    """
    json = res.json()
    results = json['results']
    for r in results:
        if r['product_name'] == "Monster Energy Zero Sugar Cans":
            print("found at woolies:",r)
            return float(r['current_price'])
        


def call_apis(product_name) :
    """
    Makes calls to Coles & Woolworths APIs. 
    Returns the supermarket name and price
    """
    try:
        res1 = requests.get(url=coles_api_url+product_name, headers={"x-rapidapi-host":coles_api_host, "x-rapidapi-key":RAPID_API_KEY})
        res2 = requests.get(url=woolies_api_url+product_name, headers={"x-rapidapi-host":woolies_api_host, "x-rapidapi-key":RAPID_API_KEY})
        if res1.status_code != 200 or res2.status_code != 200:
            print(f"API call failed. Coles returned {res1.status_code} and Woolies returned {res2.status_code}")
            return None            
        else:
            coles_price = parse_response_coles(res1)
            woolies_price = parse_response_woolies(res2)

            if coles_price == woolies_price:
                return "same", str(coles_price)
            elif coles_price < woolies_price:
                return "coles", str(coles_price)
            else:
                return "woolies", str(woolies_price)
            
    except Exception as e:
        print("Other error:",e)


@bot.event
async def on_ready():
    print(f'successful login as {bot.user}')

@bot.command()
async def help(ctx):
    """
    Prints a list of available commands.
    """
    await ctx.send("boo help: lists available commands.\n"
                   "boo monster: cheapest monster energy atm.")

@bot.command()
async def monster(ctx):
    try:
        supermarket,price = call_apis("Monster%20Drink%20Zero%20Sugar%204%20pack")
    except:
        await ctx.send("internal server error. try again later.")
        return
    if supermarket == "same":
        await ctx.send(f"white monster is the same price at both: ${price}")
        return
    else:
        await ctx.send(f"white monster is cheaper at {supermarket}: ${price}")
        return

bot.run(TOKEN)
