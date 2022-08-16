from __future__ import annotations
import json
from enum import IntEnum
import numpy as np
import discord
from discord.ext import commands


class Tiles(IntEnum):
    Space = 0
    Wall = 1
    Player = 2
    Target = 3
    Box = 4
    BoxOnTarget = 5

    def __eq__(self, __o: int | Tiles) -> bool:
        if isinstance(__o, int):
            return self.value == __o
        if isinstance(__o, Tiles):
            return self.value == __o.value
        raise TypeError(f"Cannot compare Tiles to {type(__o)}")

    def __repr__(self) -> str:
        match self:
            case Tiles.Space:
                return '⬛'
            case Tiles.Wall:
                return '🟫'
            case Tiles.Player:
                return '😳'
            case Tiles.Target:
                return '🟥'
            case Tiles.Box:
                return '❎'
            case Tiles.BoxOnTarget:
                return '☑'


class Result(IntEnum):
    Pending = 0
    Win = 1

    def __eq__(self, __o: object) -> bool:
        return self.value == __o.value


# Self explainatory
BUTTONS = (
    (0, '↖', discord.ButtonStyle.blurple, False),    # UpLeft
    (0, '⬆', discord.ButtonStyle.blurple, False),    # Up
    (0, '↗', discord.ButtonStyle.blurple, False),    # UpRight
    (2, '↙', discord.ButtonStyle.blurple, False),    # DownLeft
    (2, '⬇', discord.ButtonStyle.blurple, False),    # Down
    (2, '↘', discord.ButtonStyle.blurple, False),    # DownRight
    (1, '⬅', discord.ButtonStyle.blurple, False),    # Left
    (1, '​', discord.ButtonStyle.gray, True),         # Useless button
    (1, '➡', discord.ButtonStyle.blurple, False),    # Right
    (3, '⛔', discord.ButtonStyle.red, False),       # Stop
    (3, '🔄', discord.ButtonStyle.gray, False),      # Restart
    (3, '⏩', discord.ButtonStyle.green, True),       # Next level
)


class SokobanButton(discord.ui.Button['Sokoban']):
    def __init__(self, button):
        row, emoji, style, disabled = button
        super().__init__(label=emoji, style=style, row=row, disabled=disabled)

    async def callback(self, interaction: discord.Interaction):
        board = self.view.board
        match self.label:
            case '↖':
                self.view.move_diag(-1, -1)
            case '⬆':
                self.view.move_vertical(-1)
            case '↗':
                self.view.move_diag(-1, 1)
            case '↙':
                self.view.move_diag(1, -1)
            case '⬇':
                self.view.move_vertical(1)
            case '↘':
                self.view.move_diag(1, 1)
            case '⬅':
                self.view.move_horizontal(-1)
            case '➡':
                self.view.move_horizontal(1)
            case '⛔':
                self.view.children = []
                self.view.stop()
            case '🔄':
                self.view.load_level()
            case '⏩':
                self.view.level += 1
                if self.view.level == len(self.view.Levels):
                    self.view.result = Result.Win
                    self.view.children = []
                    self.view.stop()
                else:
                    self.view.load_level()
                    self.view.children[-1].disabled = True

        targetAll = True
        for pos in self.view.targetsPos:
            if Tiles(board[pos]) not in (Tiles.Player, Tiles.BoxOnTarget):
                targetAll = False
                board[pos] = Tiles.Target.value

        if targetAll:
            self.view.children[-1].disabled = False

        await interaction.response.edit_message(content=self.view.render_board(), view=self.view)


def InitSokoban() -> dict:
    with open('./assets/jsons/sokoban.json', 'r') as f:
        data = json.load(f)

    return data


class Sokoban(discord.ui.View):

    Levels = InitSokoban()

    def __init__(self, player: discord.Member):
        super().__init__()

        self.player = player
        self.level = 0
        self.result = Result.Pending
        self.load_level()

        for button in BUTTONS:
            self.add_item(SokobanButton(button))

    def load_level(self):
        board = np.array(
            self.Levels[self.level]["board"], dtype='i')
        self.rows, self.cols = board.shape
        self.board = board.flatten()

        playerPos = self.Levels[self.level]["playerPos"]
        self.playerPos: int = playerPos[0] * self.cols + playerPos[1]

        self.targetsPos: set[int] = set(
            map(lambda x: x[0] * self.cols + x[1], self.Levels[self.level]["targetsPos"]))

    def render_board(self) -> str:
        match self.result:
            case Result.Pending:
                rows = []
                for i in range(self.rows):
                    r = self.cols * i
                    rows.append(
                        "".join(map(lambda x: repr(Tiles(x)), self.board[r: r + self.cols])))

                return "\n".join(rows)
            case Result.Win:
                return "VICTORY"

    def swap(self, pos1: int, pos2: int):
        self.board[pos1], self.board[pos2] = self.board[pos2], self.board[pos1]

    def move_diag(self, dx: int, dy: int) -> bool:
        dx *= self.cols
        if (self.board[self.playerPos + dx] == Tiles.Space
                or self.board[self.playerPos + dy] == Tiles.Space) \
                and self.board[self.playerPos + dx + dy] == Tiles.Space:
            self.swap(self.playerPos + dx + dy, self.playerPos)
            self.playerPos += dx + dy
            return True
        return False

    def move_horizontal(self, dy: int) -> bool:
        newPos = self.playerPos + dy
        moved = False
        match self.board[newPos]:
            case Tiles.Space:
                self.swap(newPos, self.playerPos)
                self.playerPos = newPos
                moved = True
            case Tiles.Box | Tiles.BoxOnTarget:
                if self.board[newPos + dy] == Tiles.Space:
                    self.swap(newPos + dy, newPos)
                    self.swap(self.playerPos, newPos)
                    self.playerPos = newPos
                    moved = True
                if self.board[newPos + dy] == Tiles.Target:
                    self.board[newPos + dy] = Tiles.BoxOnTarget.value
                    self.board[newPos] = Tiles.Player.value
                    self.board[self.playerPos] = Tiles.Space.value
                    self.playerPos = newPos
                    moved = True
            case Tiles.Target:
                self.board[newPos] = Tiles.Player.value
                self.board[self.playerPos] = Tiles.Space.value
                self.playerPos = newPos

        return moved

    def move_vertical(self, dx: int) -> bool:
        dx *= self.cols
        newPos = self.playerPos + dx
        moved = False
        match self.board[newPos]:
            case Tiles.Space:
                self.swap(newPos, self.playerPos)
                self.playerPos = newPos
                moved = True
            case Tiles.Box | Tiles.BoxOnTarget:
                if self.board[newPos + dx] == Tiles.Space:
                    self.swap(newPos + dx, newPos)
                    self.swap(self.playerPos, newPos)
                    self.playerPos = newPos
                    moved = True
                if self.board[newPos + dx] == Tiles.Target:
                    self.board[newPos + dx] = Tiles.BoxOnTarget.value
                    self.board[newPos] = Tiles.Player.value
                    self.board[self.playerPos] = Tiles.Space.value
                    self.playerPos = newPos
                    moved = True
            case Tiles.Target:
                self.board[newPos] = Tiles.Player.value
                self.board[self.playerPos] = Tiles.Space.value
                self.playerPos = newPos
        return moved

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.player == interaction.user
