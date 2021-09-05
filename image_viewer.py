from PIL import Image, ImageColor
import json
from blaseball_mike import chronicler
import requests
from os import path

COLORS = [
    ImageColor.getrgb("#000000"),
    ImageColor.getrgb("#996633"),
    ImageColor.getrgb("#FF0000"),
    ImageColor.getrgb("#FF9900"),
    ImageColor.getrgb("#FFFF00"),
    ImageColor.getrgb("#00FF00"),
    ImageColor.getrgb("#0000FF"),
    ImageColor.getrgb("#FF00FF"),
    ImageColor.getrgb("#CCCCCC"),
    ImageColor.getrgb("#FFFFFF"),
]

MOD_COLORS = {
    "": ImageColor.getrgb("#000000"),
    "COFFEE_RALLY": ImageColor.getrgb("#44c97c"),
    "MAGNIFY_2X": ImageColor.getrgb("#041a29"),
    "SUBTRACTOR": ImageColor.getrgb("#420000"),
    "TIRED": ImageColor.getrgb("#511c00"),
    "WIRED": ImageColor.getrgb("#ffffff"),
    "BLASERUNNING": ImageColor.getrgb("#570026"),
    "TRIPLE_THREAT": ImageColor.getrgb("#5dbcd2"),
    "UNDERHANDED": ImageColor.getrgb("#362236"),
}

DIVIDER_COLOR = (255, 0, 0)
BOOLEAN_COLOR = (255, 255, 255)
CELL_WIDTH = 6
CELL_HEIGHT = 8

SEASON = 22  # 1-indexed

max_play_counts = []


def write_square(x, y, packet):
    # Home team color/score
    img.putpixel((x, y), ImageColor.getrgb(team_colors[packet["homeTeam"]]))
    home_score = packet["homeScore"]
    if(home_score < 0):
        img.putpixel((x+1, y), BOOLEAN_COLOR)
        home_score *= -1
    img.putpixel((x+2, y), COLORS[int((home_score / 10) % 10)])
    img.putpixel((x+3, y), COLORS[int((home_score) % 10)])
    img.putpixel((x+4, y), COLORS[int((home_score * 10) % 10)])

    # Away team color/score
    img.putpixel((x, y+1), ImageColor.getrgb(team_colors[packet["awayTeam"]]))
    away_score = packet["awayScore"]
    if(away_score < 0):
        img.putpixel((x+1, y+1), BOOLEAN_COLOR)
        away_score *= -1
    img.putpixel((x+2, y+1), COLORS[int((away_score / 10) % 10)])
    img.putpixel((x+3, y+1), COLORS[int((away_score) % 10)])
    img.putpixel((x+4, y+1), COLORS[int((away_score * 10) % 10)])

    # Inning
    b_inning = [bool(int(i)) for i in list('{0:05b}'.format(packet["inning"] + 1))]
    for i in range(5):
        if(b_inning[i]):
            img.putpixel((x, y+2+i), BOOLEAN_COLOR)
    if(not packet["topOfInning"]):
        img.putpixel((x, y+7), BOOLEAN_COLOR)

    # packet feed type
    b_feed = [bool(int(i)) for i in list('{0:08b}'.format(packet["type"]))]
    for i in range(8):
        if(b_feed[i]):
            img.putpixel((x+5, y+i), BOOLEAN_COLOR)

    # Balls / Strikes / Outs
    for i in range(4):
        if(packet["atBatBalls"] > i):
            img.putpixel((x+(4-i), y+2), BOOLEAN_COLOR)
        if(packet["atBatStrikes"] > i):
            img.putpixel((x+(4-i), y+3), BOOLEAN_COLOR)
        if(packet["halfInningOuts"] > 0):
            img.putpixel((x+(4-i), y+4), BOOLEAN_COLOR)

    # Bases / Mods
    for i in range(len(packet["basesOccupied"])):
        base = packet["basesOccupied"][i]
        img.putpixel((x+4-base, y+5), ImageColor.getrgb("#" + packet["baseRunners"][i][0:6]))
        # if(MOD_COLORS[packet["baseRunnerMods"][i]] != (0, 0, 0)):
        #     print("runner", x+4-base, y+6, MOD_COLORS[packet["baseRunnerMods"][i]])
        img.putpixel((x+4-base, y+6), MOD_COLORS[packet["baseRunnerMods"][i]])

    # Pitcher/Batter/Mods
    if(packet["topOfInning"]):
        pitcher = packet["homePitcher"]
        pitcher_mod = packet["homePitcherMod"]
        batter = packet["awayBatter"]
        batter_mod = packet["awayBatterMod"]
    else:
        pitcher = packet["awayPitcher"]
        pitcher_mod = packet["awayPitcherMod"]
        batter = packet["homeBatter"]
        batter_mod = packet["homeBatterMod"]

    if(pitcher is not None):
        img.putpixel((x+1, y+7), ImageColor.getrgb("#" + pitcher[0:6]))
        img.putpixel((x+2, y+7), MOD_COLORS[pitcher_mod])
    if(batter is not None):
        img.putpixel((x+3, y+7), ImageColor.getrgb("#" + batter[0:6]))
        img.putpixel((x+4, y+7), MOD_COLORS[batter_mod])

    for i in range(CELL_HEIGHT + 1):
        img.putpixel((x+CELL_WIDTH, y+i), DIVIDER_COLOR)

    for i in range(CELL_WIDTH + 1):
        img.putpixel((x+i, y+CELL_HEIGHT), DIVIDER_COLOR)


# get team colors:
r = requests.get(f"https://api.sibr.dev/corsmechanics/time/season/{SEASON-1}/day/1")
start_time = r.json()[0]["startTime"]
teams = list(chronicler.v2.get_entities("team", at=start_time))
team_colors = {}
for team in teams:
    team_colors[team["entityId"]] = team["data"]["mainColor"]

packets = {}

if(path.exists(f"data_{SEASON}.json")):
    with open(f"data_{SEASON}.json", "r") as f:
        packets = json.load(f)

else:
    print("No packets file found for the selected season, generating...")
    print("This may take a few minutes.")
    games = chronicler.get_games(SEASON)
    print(f"There are {len(games)} games to fetch")
    i = 0
    for game in games:
        if(i % 100 == 0):
            print(f"Fetched {i} games.")
        game_id = game["gameId"]
        r = requests.get(f'https://api.sibr.dev/eventually/sachet/packets?id={game_id}')
        packets[game_id] = r.json()
        i += 1

    print("Fetched all games, saving to file.")
    with open(f"data_{SEASON}.json", "w") as f:
        json.dump(packets, f)

for game_id in packets:
    max_play_counts.append(len(packets[game_id]))

# Create the image
width = len(packets)*(CELL_WIDTH + 1)
height = max(max_play_counts)*(CELL_HEIGHT + 1)+50
img = Image.new(mode="RGB", size=(width, height))

x = 0
for game_id in packets:
    y = 0
    for packet in packets[game_id]:
        if(not packet["_sachet_packet_incomplete"]):
            write_square(x, y, packet)
        y += CELL_HEIGHT + 1
    x += CELL_WIDTH + 1

img.show()
