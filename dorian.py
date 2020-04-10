#!/usr/bin/env python3
import discord
import re
import logging
import asyncio
from os import environ
from random import randint

logging.basicConfig(level=logging.INFO)

client = discord.Client()
discord.opus.load_opus
roll_command = "/croll"

FirstConnect=True
LastPlayingIndex=-1
PlayingQuotes = {
        1: "with dice",
    }

COL_CRIT_SUCCESS=0xFFFFFF
COL_EXTR_SUCCESS=0xf1c40f
COL_HARD_SUCCESS=0x2ecc71
COL_NORM_SUCCESS=0x2e71cc
COL_NORM_FAILURE=0xe74c3c
COL_CRIT_FAILURE=0x992d22

class DiceResult:
    def __init__(self):
        self.title=""
        self.desc=""
        self.colour=COL_NORM_SUCCESS

def RollDie(min=1, max=10):
    result = randint(min,max)
    return result

def ResolveDice(BonusDie, PenaltyDie, Threshold):
  TenResultPool = []
  TenResultPool.append(RollDie(0, 9))

  TenResult = min(TenResultPool)
  OneResult = RollDie()

  if BonusDie > 0 and PenaltyDie > 0:
      return "Can't chain bonus and penalty dice"

  for i in range(BonusDie):
      TenResultPool.append(RollDie(0, 9))
      TenResult = min(TenResultPool)
  
  for i in range(PenaltyDie):
      TenResultPool.append(RollDie(0, 9))
      TenResult = max(TenResultPool)

  CombinedResult = (TenResult*10) + OneResult
  desc = str(TenResult*10) + '(' + '/'.join([str(i*10) for i in TenResultPool]) + ') + ' + str(OneResult) + ' = ' + str(CombinedResult)

  if Threshold:
    ret = DiceResult()
    if CombinedResult == 1:
      ret.title = "Critical Success!"
      ret.colour = COL_CRIT_SUCCESS
    elif CombinedResult == 100:
      ret.title = "Critical Failure!"
      ret.colour = COL_CRIT_FAILURE
    elif CombinedResult <= Threshold/5:
      ret.title = "Extreme Success!"
      ret.colour = COL_EXTR_SUCCESS
    elif CombinedResult <= Threshold/2:
      ret.title = "Hard Success!"
      ret.colour = COL_HARD_SUCCESS
    elif CombinedResult <= Threshold:
      ret.title = "Success"
      ret.colour = COL_NORM_SUCCESS
    else:
      ret.title = "Failure"
      ret.colour = COL_NORM_FAILURE

    ret.desc = desc
    return ret
  else:
    ret = desc
    return ret

def parseRoll(diceString):
    fail="""
Unable to parse dice command. Usage:
```
/croll [[number=1][die type]]...[[score][threshold]]

Die Types:
    b: Bonus dice (can't be chained with Penalty)
    p: Penalty dice (can't be chained with Bonus)
    t: Threshold to determine success/fail. Score is required if a threshold is set.

Examples:
    /croll
    36

    /croll 60t
    Hard Success: 24

    /croll b
    70/30 + 5 = 35

    /croll 2p70t
    Failure: 0/50/70 + 4 = 74
```
"""
    dice=[x for x in re.split('(\d*?[bpt])',diceString) if x]

    if len(dice) > 1 and 'b' in diceString and 'p' in diceString:
        return "Can't chain bonus and penalty dice"
    
    BonusDie=0
    PenaltyDie=0
    Threshold=False

    for die in dice:
        default_num = False
        s=re.search('(\d*?)([bpt])', die)
        if not s:
            default_num = True
            die="1"+die
        s=re.search('(\d*?)([bpt])', die)
        if not s:
            return fail
        g=s.groups()
        if len(g) != 2:
            return fail
        try:
            num=int(g[0])
        except:
            default_num = True
            num=1

        dieCode=g[1]
        
        if len(dieCode) > 1:
            return fail

        if dieCode == 'b':
            BonusDie = num

        if dieCode == 'p':
            PenaltyDie = num

        if  dieCode == 't':
            if default_num:
              return "Threshold requires a value!"
            else:
              Threshold = num
        
    return ResolveDice(BonusDie, PenaltyDie, Threshold)

async def cyclePlaying():
    global LastPlayingIndex
    playing=PlayingQuotes[randint(1,len(PlayingQuotes))]
    while playing == LastPlayingIndex:
        playing=PlayingQuotes[randint(1,len(PlayingQuotes))]
    LastPlayingIndex=playing
    #await client.change_presence(game=discord.Game(name=playing))
    await asyncio.sleep(randint(60,600))

@client.event
async def on_ready():
    global FirstConnect
    print("Dorian connected")
    if FirstConnect:
        FirstConnect = False
        while True:
            await asyncio.ensure_future(cyclePlaying())
        
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(roll_command):
        result = parseRoll(message.content[len(roll_command)+1:])
        if isinstance(result, str):
            await message.channel.send(result)
        else:
            em = discord.Embed(title=result.title, description=result.desc, colour=result.colour)
            em.set_footer(text=result.desc)
            em.description=None
            await message.channel.send(embed=em)
    
token=environ['DORIAN_TOKEN']
client.run(token)
