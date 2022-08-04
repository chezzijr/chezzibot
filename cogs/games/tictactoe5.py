# This example requires the 'message_content' privileged intent to function.

from typing import List
import discord

# Defines a custom button that contains the logic of the game.
# The ['TicTacToe'] bit is for type hinting purposes to tell your IDE or linter
# what the type of `self.view` is. It is not required.


class TicTacToe5Button(discord.ui.Button['TicTacToe5']):
    def __init__(self, x: int, y: int):
        # A label is required, but we don't need one so a zero-width space is used
        # The row parameter tells the View which row to place the button under.
        # A View can only contain up to 5 rows -- each row can only have 5 buttons.
        # Since a Tic Tac Toe grid is 3x3 that means we have 3 rows and 3 columns.
        super().__init__(style=discord.ButtonStyle.secondary, label='\u200b', row=y)
        self.x = x
        self.y = y

    # This function is called whenever this particular button is pressed
    # This is part of the "meat" of the game logic
    async def callback(self, interaction: discord.Interaction):
        view: TicTacToe5 = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return

        pl, sb = view.current_player()

        if sb == view.X:
            self.style = discord.ButtonStyle.danger
            self.label = 'X'
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.change_turn()
            pl, _ = view.current_player()
            content = f"It is now `{pl.display_name}`'s turn"
        else:
            self.style = discord.ButtonStyle.success
            self.label = 'O'
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.change_turn()
            pl, _ = view.current_player()
            content = f"It is now `{pl.display_name}`'s turn"

        winner = view.check_board_winner()
        if winner is not None:
            w = view.players[1 - view.turn]
            if winner == view.Tie:
                content = "It's a tie!"
            else:
                content = f'`{w.display_name}` won!'

            for child in view.children:
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)


# This is our actual board View
class TicTacToe5(discord.ui.View):
    # This tells the IDE or linter that all our children will be TicTacToeButtons
    # This is not required
    children: List[TicTacToe5Button]
    X = -1
    O = 1
    Tie = 2

    def __init__(self, first: discord.Member, second: discord.Member):
        super().__init__()
        self.players = (second, first)
        self.symbols = (self.X, self.O)

        self.turn = 0

        self.board = [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]

        # Our board is made up of 3 by 3 TicTacToeButtons
        # The TicTacToeButton maintains the callbacks and helps steer
        # the actual game.
        for x in range(5):
            for y in range(5):
                self.add_item(TicTacToe5Button(x, y))

    def current_player(self) -> tuple[discord.Member, int]:
        return self.players[self.turn], self.symbols[self.turn]

    def change_turn(self):
        self.turn = 1 - self.turn

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.current_player()[0] == interaction.user

    # This method checks for the board winner -- it is used by the TicTacToeButton
    def check_board_winner(self):
        for across in self.board:
            value = sum(across)
            if value >= 4:
                return self.O
            elif value <= -4:
                return self.X

        # Check vertical
        for line in range(5):
            value = self.board[0][line] + self.board[1][line] + \
                self.board[2][line] + self.board[3][line] + self.board[4][line]
            if value >= 4:
                return self.O
            elif value <= -4:
                return self.X

        # Check diagonals
        for i, j in {(0, 0), (0, 1), (1, 0), (1, 1)}:
            s = 0
            for d in range(4):
                s += self.board[i + d][j + d]
            if s == 4:
                return self.O
            elif s == -4:
                return self.X

        for i, j in {(0, 4), (1, 4), (0, 3), (1, 3)}:
            s = 0
            for d in range(4):
                s += self.board[i + d][j - d]
            if s == 4:
                return self.O
            elif s == -4:
                return self.X

        # If we're here, we need to check if a tie was made
        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return None
