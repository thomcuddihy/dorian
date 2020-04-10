# Dorian

## Call of Cthulhu 7E dice roller bot for Discord

[Discord Bot entry.](https://top.gg/bot/698078321472176200)

## Usage

A Call of Cthulhu dice roller bot for Discord.

Created for simplicity. Rolls a d100 with optional bonus or penalty dice, and optional threshold for determining levels of success or failure.

```text
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

## Notes

Needs environmental variable DORIAN_TOKEN to be set if you want to run this yourself. See `set_env.sh.example` for a Linux/OSX method.

Please open an issue for any bugs or feature requests.
