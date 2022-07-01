#!/usr/bin/env python3
import discord
import re, logging
from os import environ
from random import randint

logging.basicConfig(level=logging.INFO)

bot = discord.Bot()

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

def ResolveDice(BonusDie, PenaltyDie, Threshold, DiceString) :
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
  desc = f"""
Roll: {DiceString}
Result: {str(TenResult*10)} ({'/'.join([str(i*10) for i in TenResultPool])}) + {str(OneResult)} = {str(CombinedResult)}
"""

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
    help = """
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
    fail="""
Unable to parse dice command. Usage:
""" + help

    if diceString == 'help':
        return help
    
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
        
    return ResolveDice(BonusDie, PenaltyDie, Threshold, diceString)

@bot.slash_command(name="croll")
async def cthulhu_roll(
    ctx: discord.ApplicationContext,
    dice: discord.Option(str, "Dice string. Enter 'help' for more details.", default="")
):
    """
    Call of Cthulhu dice roll.
    """
    result = parseRoll(dice)
    if isinstance(result, str):
        await ctx.respond(result)
    else:
        em = discord.Embed(title=result.title, description=result.desc, colour=result.colour)
        em.set_footer(text=result.desc)
        em.description=None
        await ctx.respond(embed=em)

token=environ['DORIAN_TOKEN']
bot.run(token)
