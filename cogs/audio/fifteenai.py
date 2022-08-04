import json
import aiohttp
import discord
from typing import Iterable, Optional
from aiohttp.web import HTTPException
from io import BytesIO

MAX_TEXT_LEN = 200

TTS_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "access-control-allow-origin": "*",
    "content-type": "application/json;charset=UTF-8",
    "origin": "https://fifteen.ai",
    "referer": "https://fifteen.ai/app",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "python-requests 15.ai-Python-API(https://github.com/wafflecomposite/15.ai-Python-API)"
}

TTS_URL = "https://api.15.ai/app/getAudioFile5"
AUDIO_URL = "https://cdn.15.ai/audio/"

# dictionary of oringinality and characters
CHARACTERS: dict[str, list[str]] = {
    "Portal": [
        "GLaDOS",
        "Wheatley",
        "Sentry Turret",
        "Chell"
    ],
    "My Little Pony: Friendship is Magic 1": [
        "Twilight Sparkle",
        "Fluttershy",
        "Rarity",
        "Rainbow Dash",
        "Pinkie Pie",
        "Applejack",
        "Princess Celestia",
        "Princess Luna",
        "Spike",
        "Starlight Glimmer",
        "Trixie",
        "Apple Bloom",
        "Sweetie Belle",
        "Scootaloo",
        "Zecora",
        "Derpy Hooves",
        "Lyra",
        "Bon Bon",
        "Princess Cadance",
        "Cozy Glow",
        "Queen Chrysalis",
        "Spitfire",
        "Big Mac",
        "Sunburst",
        "Minuette"
    ],
    "My Little Pony: Friendship is Magic 2": [
        "Cheerilee",
        "Coco Pommel",
        "Maud Pie",
        "Shining Armor",
        "Sugar Belle",
        "Vapor Trail",
        "Moondancer",
        "Lightning Dust",
        "Discord",
        "Soarin'",
        "Diamond Tiara",
        "Silver Spoon",
        "Octavia",
        "Gilda",
        "Gabby",
        "Limestone Pie",
        "Braeburn",
        "Daring Do",
        "Snips",
        "Snails",
    ],
    "SpongeBob SquarePants": [
        "SpongeBob SquarePants"
    ],
    "HuniePop": [
        "Kyu Sugardust"
    ],
    "Daria": [
        "Daria Morgendorffer",
        "Jane Lane",
    ],
    "Aqua Teen Hunger Force": [
        "Carl Brutananadilewski"
    ],
    "Team Fortress 2": [
        "Miss Pauling",
        "Scout",
        "Soldier",
        "Demoman",
        "Heavy",
        "Engineer",
        "Medic",
        "Sniper",
        "Spy"
    ],
    "Persona 4": [
        "Rise Kujikawa"
    ],
    "Steven Universe": [
        "Steven Universe"
    ],
    "Dan Vs.": [
        "Dan"
    ],
    "The Stanley Parable": [
        "The Narrator",
        "Stanley"
    ],
    "2001: A Space Odyssey": [
        "HAL 9000"
    ],
    "Equestria Girls": [
        "Sunset Shimmer",
        "Adagio Dazzle",
        "Aria Blaze",
        "Sonata Dusk",
    ],
    "Doctor Who": [
        "Tenth Doctor"
    ],
    "Undertale": [
        "Sans",
        "Papyrus",
        "Flowey",
        "Toriel",
        "Asgore",
        "Asriel",
        "Alphys",
        "Undyne",
        "Mettaton",
        "Temmie",
        "Susie",
        "Noelle",
        "Berdy",
        "Rudolph",
        "Ralsei",
        "Lancer",
        "King",
        "Queen",
        "Jevil",
        "Spamton",
        "Gaster",
    ],
}


async def get_tts_raw(http: aiohttp.ClientSession, character: str, text: str):

    resp = {"status": "NOT SET", "data": None}

    text_len = len(text)
    if text_len > MAX_TEXT_LEN:
        text = text[:MAX_TEXT_LEN - 1]

    if not text.endswith(".") and not text.endswith("!") and not text.endswith("?"):
        if len(text) < 140:
            text += '.'
        else:
            text = text[:-1] + '.'

    data = json.dumps(
        {"text": text, "character": character, "emotion": "Contextual"})

    try:
        response = await http.post(TTS_URL, data=data, headers=TTS_HEADERS)
    except HTTPException as e:
        resp["status"] = f"ConnectionError ({e})"
        return resp

    if response.status == 200:
        resp["response"] = json.loads(await response.read())
        resp["audio_uri"] = resp["response"]["wavNames"][0]

        try:
            async with http.get(f"{AUDIO_URL}{resp['audio_uri']}", headers=TTS_HEADERS) as responseAudio:
                resp["status"] = "OK"
                resp["data"] = await responseAudio.read()
                return resp
        except HTTPException as e:
            resp["status"] = f"ConnectionError ({e})"
            return resp
    else:
        content = await response.read()
        resp["status"] = f'15.ai API request error, Status code: {response.status}, ({str(content)})'

    return resp


async def save_to_bytesio(http: aiohttp.ClientSession, character: str, text: str, fileobj: BytesIO):
    tts = await get_tts_raw(http, character, text)
    if tts["status"] == "OK" and tts["data"] is not None:
        fileobj.write(tts["data"])
        fileobj.seek(0)
        return {"status": tts["status"], "filename": tts["audio_uri"]}
    else:
        return {"status": tts["status"], "filename": None}


class Dropdown(discord.ui.Select['FifteenAIView']):
    def __init__(self, options: Iterable[str], placeholder: str):
        options = list(map(lambda o: discord.SelectOption(label=o), options))

        super().__init__(placeholder=placeholder,
                         min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.view.stage == 2:
            self.view.character = self.values[0]
            self.view.stop()
            await interaction.response.edit_message(content=f"Selected {self.values[0]}", view=None)
        else:
            self.view.children.clear()
            self.view.add_item(
                Dropdown(CHARACTERS[self.values[0]], "Select a character"))
            self.view.stage += 1
            await interaction.response.edit_message(view=self.view)


class FifteenAIView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Dropdown(CHARACTERS.keys(), "Select a source"))
        self.character: Optional[str] = None
        self.stage = 1
