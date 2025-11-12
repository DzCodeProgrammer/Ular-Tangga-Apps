import tkinter as tk
import random
import time

# ==== KONFIGURASI DASAR ====
BOARD_SIZE = 10
CELL_SIZE = 60
PLAYER_COLORS = ["#00e5ff", "#ffde59"]
NUM_ITEMS = 6
ITEM_TYPES = ["boost", "prank", "troll"]
ITEM_COLORS = {
    "boost": "#00ff88",
    "prank": "#b39ddb",
    "troll": "#ff6b6b",
}

# Tangga & Ular (start: end)
LADDERS = {
    3: 22,
    5: 8,
    11: 26,
    20: 29,
    17: 38,
    27: 56,
    36: 44,
}
SNAKES = {
    34: 1,
    47: 19,
    65: 52,
    87: 57,
    91: 61,
    99: 78,
}

# ==== FUNGSI KONVERSI ====
def get_coords(position):
    """Konversi posisi (1-100) ke koordinat grid"""
    row = (position - 1) // BOARD_SIZE
    col = (position - 1) % BOARD_SIZE
    if row % 2 == 1:
        col = BOARD_SIZE - 1 - col
    x = col * CELL_SIZE + CELL_SIZE // 2
    y = (BOARD_SIZE - 1 - row) * CELL_SIZE + CELL_SIZE // 2
    return x, y

# ==== KELAS GAME ====
class SnakesAndLadders:
    def __init__(self, root):
        self.root = root
        self.root.title("🎲 Ular Tangga Modern - by Azzikri")
        self.root.geometry(f"{BOARD_SIZE*CELL_SIZE+300}x{BOARD_SIZE*CELL_SIZE+60}")
        self.root.resizable(False, False)
        self.root.configure(bg="#0a192f")

        self.canvas = tk.Canvas(
            root,
            width=BOARD_SIZE * CELL_SIZE,
            height=BOARD_SIZE * CELL_SIZE,
            bg="#1a1a1a",
            highlightthickness=0
        )
        self.canvas.pack(side="left", padx=15, pady=15)

        self.info_frame = tk.Frame(root, bg="#0a192f")
        self.info_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)
        # positions for two players (index 0 and 1)
        self.positions = [1, 1]
        # 0 or 1 - who has the current turn
        self.current_player = 0
        self.create_board()
        self.create_ui()

    def create_board(self):
        """Gambar papan ular tangga"""
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x1 = col * CELL_SIZE
                y1 = row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                color = "#0d47a1" if (row + col) % 2 == 0 else "#1565c0"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#212121")

        # Gambar angka
        num = 1
        for row in range(BOARD_SIZE):
            cols = range(BOARD_SIZE) if row % 2 == 0 else range(BOARD_SIZE - 1, -1, -1)
            for col in cols:
                x = col * CELL_SIZE + 5
                y = (BOARD_SIZE - 1 - row) * CELL_SIZE + 5
                self.canvas.create_text(x + 10, y + 10, text=str(num), fill="#ffffff", anchor="nw", font=("Consolas", 10))
                num += 1

        # Ular & Tangga (visual sederhana)
        for start, end in LADDERS.items():
            x1, y1 = get_coords(start)
            x2, y2 = get_coords(end)
            self.canvas.create_line(x1, y1, x2, y2, fill="#00ff88", width=4, arrow=tk.LAST)
        for start, end in SNAKES.items():
            x1, y1 = get_coords(start)
            x2, y2 = get_coords(end)
            self.canvas.create_line(x1, y1, x2, y2, fill="#ff3b30", width=4, arrow=tk.LAST)

        # Token pemain (dua pemain)
        # slightly smaller so two tokens fit in the same cell
        self.players = [
            self.canvas.create_oval(0, 0, 24, 24, fill=PLAYER_COLORS[0], outline="#00ffff"),
            self.canvas.create_oval(0, 0, 24, 24, fill=PLAYER_COLORS[1], outline="#b36b00")
        ]
        # set both initial positions
        self.update_player_position(0)
        self.update_player_position(1)

        # place random items on the board
        self.items = {}  # pos -> type
        self.item_icons = {}  # pos -> canvas id
        self.place_items()

    def create_ui(self):
        """Buat panel kanan (UI Info dan Tombol)"""
        title = tk.Label(
            self.info_frame,
            text="🐍 Ular Tangga Modern 🧩",
            font=("Poppins", 18, "bold"),
            fg="#00e5ff",
            bg="#0a192f"
        )
        title.pack(pady=(20, 10))

        self.dice_label = tk.Label(
            self.info_frame,
            text="🎲 Lempar dadu untuk mulai!",
            font=("Poppins", 14),
            fg="white",
            bg="#0a192f"
        )
        self.dice_label.pack(pady=20)

        # Turn and positions info for two players
        self.turn_label = tk.Label(
            self.info_frame,
            text=f"Giliran: Pemain {self.current_player+1}",
            font=("Poppins", 12),
            fg="white",
            bg="#0a192f"
        )
        self.turn_label.pack(pady=(5, 5))

        self.positions_label = tk.Label(
            self.info_frame,
            text=f"P1: {self.positions[0]}   P2: {self.positions[1]}",
            font=("Poppins", 12),
            fg="white",
            bg="#0a192f"
        )
        self.positions_label.pack(pady=(0, 15))

        self.roll_button = tk.Button(
            self.info_frame,
            text="🎲 Lempar Dadu",
            font=("Poppins", 16, "bold"),
            bg="#00bcd4",
            fg="#121212",
            relief="flat",
            padx=20,
            pady=10,
            activebackground="#00e5ff",
            activeforeground="black",
            command=self.roll_dice
        )
        self.roll_button.pack(pady=30)

    def place_items(self):
        """Place a small number of items randomly on the board, avoiding start/end and snakes/ladders starts."""
        forbidden = {1, 100} | set(LADDERS.keys()) | set(SNAKES.keys())
        # valid positions: 2..99 excluding forbidden
        candidates = [p for p in range(2, 100) if p not in forbidden]
        random.shuffle(candidates)
        chosen = candidates[:NUM_ITEMS]
        for pos in chosen:
            typ = random.choice(ITEM_TYPES)
            self.items[pos] = typ
            x, y = get_coords(pos)
            # small square marker with first letter
            size = 10
            color = ITEM_COLORS.get(typ, "#ffffff")
            icon = self.canvas.create_oval(x - size, y - size, x + size, y + size, fill=color, outline="#000000")
            # label letter on top
            letter = "B" if typ == "boost" else ("P" if typ == "prank" else "T")
            text_id = self.canvas.create_text(x, y, text=letter, fill="#000000", font=("Consolas", 9, "bold"))
            # group icon and text by storing both ids in a tuple
            self.item_icons[pos] = (icon, text_id)

    def apply_item(self, player_idx, typ, pos):
        """Apply the effect of an item for player index. Effects are removed after use."""
        other = 1 - player_idx
        if typ == "boost":
            # move forward a few steps
            boost_steps = 3
            self.dice_label.config(text=f"✨ Pemain {player_idx+1} mendapat BOOST +{boost_steps}!")
            # animate
            for _ in range(boost_steps):
                if self.positions[player_idx] < 100:
                    self.positions[player_idx] += 1
                    self.update_player_position(player_idx)
                    self.root.update()
                    time.sleep(0.06)
            # after boost, check ladders/snakes
            if self.positions[player_idx] in LADDERS:
                self.positions[player_idx] = LADDERS[self.positions[player_idx]]
            elif self.positions[player_idx] in SNAKES:
                self.positions[player_idx] = SNAKES[self.positions[player_idx]]
            self.update_player_position(player_idx)

        elif typ == "prank":
            # move other player backward
            prank_steps = 3
            self.dice_label.config(text=f"😈 Pemain {player_idx+1} menjahili Pemain {other+1} -{prank_steps}!")
            self.positions[other] = max(1, self.positions[other] - prank_steps)
            self.update_player_position(other)

        elif typ == "troll":
            # move self backward
            troll_steps = 2
            self.dice_label.config(text=f"🤦 Pemain {player_idx+1} kena TROLL -{troll_steps}!")
            self.positions[player_idx] = max(1, self.positions[player_idx] - troll_steps)
            self.update_player_position(player_idx)

        # update positions label after applying
        self.positions_label.config(text=f"P1: {self.positions[0]}   P2: {self.positions[1]}")

    def update_player_position(self):
        # kept for backward-compat, not used
        pass

    def update_player_position(self, player_idx):
        """Update canvas coords for given player index (0 or 1)."""
        pos = self.positions[player_idx]
        x, y = get_coords(pos)
        # offset tokens so both are visible in the same cell
        offset_x = -6 if player_idx == 0 else 6
        size = 12
        self.canvas.coords(self.players[player_idx], x - size + offset_x, y - size, x + size + offset_x, y + size)

    def roll_dice(self):
        dice_value = random.randint(1, 6)
        self.dice_label.config(text=f"🎲 Dadu: {dice_value} (Pemain {self.current_player+1})")
        # move current player
        self.move_player(self.current_player, dice_value)

        # if landed on an item, apply and remove it
        pos = self.positions[self.current_player]
        if pos in self.items:
            typ = self.items.pop(pos)
            icons = self.item_icons.pop(pos, None)
            if icons:
                for i in icons:
                    try:
                        self.canvas.delete(i)
                    except Exception:
                        pass
            # apply effect
            self.apply_item(self.current_player, typ, pos)

        # update positions display
        self.positions_label.config(text=f"P1: {self.positions[0]}   P2: {self.positions[1]}")

        # check for win (movement or item could have finished the game)
        if self.positions[self.current_player] >= 100:
            self.dice_label.config(text=f"🏆 Pemain {self.current_player+1} menang!")
            self.turn_label.config(text=f"Pemenang: Pemain {self.current_player+1}")
            self.roll_button.config(state="disabled")
            return

        # switch turn
        self.current_player = 1 - self.current_player
        self.turn_label.config(text=f"Giliran: Pemain {self.current_player+1}")

    def move_player(self, player_idx, steps):
        """Move given player by steps with simple animation, then handle snakes/ladders."""
        for _ in range(steps):
            if self.positions[player_idx] < 100:
                self.positions[player_idx] += 1
                self.update_player_position(player_idx)
                self.root.update()
                time.sleep(0.08)

        # Cek tangga & ular untuk player
        if self.positions[player_idx] in LADDERS:
            dest = LADDERS[self.positions[player_idx]]
            self.positions[player_idx] = dest
            self.dice_label.config(text=f"🪜 Pemain {player_idx+1} naik tangga ke {dest}!")
        elif self.positions[player_idx] in SNAKES:
            dest = SNAKES[self.positions[player_idx]]
            self.positions[player_idx] = dest
            self.dice_label.config(text=f"🐍 Pemain {player_idx+1} kena ular turun ke {dest}!")
        else:
            self.dice_label.config(text=f"Pemain {player_idx+1} di petak {self.positions[player_idx]}")

        # final update for this player
        self.update_player_position(player_idx)
        self.root.update()

# ==== JALANKAN GAME ====
if __name__ == "__main__":
    root = tk.Tk()
    game = SnakesAndLadders(root)
    root.mainloop()
