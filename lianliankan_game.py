import random
import math
import tkinter as tk
from tkinter import messagebox


class LianLianKanGame:
    def __init__(self, root):
        self.root = root
        self.root.title("水果连连看 - 3关挑战")
        self.root.resizable(False, False)
        self.root.configure(bg="#fff7ed")

        self.levels = [
            {"rows": 6, "cols": 6, "types": 9, "tile": 68},
            {"rows": 8, "cols": 8, "types": 14, "tile": 58},
            {"rows": 10, "cols": 10, "types": 20, "tile": 50},
        ]
        self.symbols = [
            "apple", "orange", "lemon", "watermelon", "grape", "strawberry",
            "cherry", "kiwi", "pineapple", "coconut", "avocado", "peach",
            "pear", "mango", "blueberry", "banana", "carrot", "corn",
            "mushroom", "pretzel",
        ]

        self.level_index = 0
        self.hints_left = 3
        self.selected = None
        self.board = []
        self.tile_items = {}
        self.line_items = []

        self.bg = "#fff7ed"
        self.panel = "#ffffff"
        self.ink = "#1f2937"
        self.muted = "#7c2d12"
        self.accent = "#f97316"
        self.good = "#22c55e"
        self.hint = "#06b6d4"
        self.shadow = "#fed7aa"

        self.make_layout()
        self.start_level()

    def make_layout(self):
        header = tk.Frame(self.root, bg=self.bg)
        header.pack(fill="x", padx=18, pady=(16, 8))

        title = tk.Label(
            header,
            text="水果连连看",
            font=("Microsoft YaHei UI", 22, "bold"),
            fg=self.ink,
            bg=self.bg,
        )
        title.pack(side="left")

        self.info_label = tk.Label(
            header,
            font=("Microsoft YaHei UI", 12, "bold"),
            fg=self.muted,
            bg=self.bg,
            padx=16,
        )
        self.info_label.pack(side="left")

        actions = tk.Frame(header, bg=self.bg)
        actions.pack(side="right")

        self.hint_button = self.make_button(actions, "提示", self.use_hint)
        self.hint_button.pack(side="left", padx=(0, 8))

        self.shuffle_button = self.make_button(actions, "洗牌", self.shuffle_board)
        self.shuffle_button.pack(side="left", padx=(0, 8))

        self.restart_button = self.make_button(actions, "重开", self.restart_level)
        self.restart_button.pack(side="left")

        self.canvas = tk.Canvas(
            self.root,
            bg=self.bg,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(padx=16, pady=(0, 16))
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def make_button(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("Microsoft YaHei UI", 11, "bold"),
            fg="#ffffff",
            bg=self.accent,
            activeforeground="#ffffff",
            activebackground="#ea580c",
            relief="flat",
            bd=0,
            padx=18,
            pady=8,
            cursor="hand2",
        )

    def start_level(self):
        self.selected = None
        self.build_board()
        self.ensure_playable_board()
        self.draw_board()
        self.update_info()

    def restart_level(self):
        self.start_level()

    def build_board(self):
        conf = self.levels[self.level_index]
        rows, cols, type_count = conf["rows"], conf["cols"], conf["types"]
        self.rows = rows
        self.cols = cols
        self.tile = conf["tile"]
        pair_count = rows * cols // 2
        chosen = self.symbols[:type_count]
        values = [random.choice(chosen) for _ in range(pair_count)] * 2
        random.shuffle(values)

        self.board = [[0] * (cols + 2) for _ in range(rows + 2)]
        for i, value in enumerate(values):
            r = i // cols + 1
            c = i % cols + 1
            self.board[r][c] = value

    def ensure_playable_board(self):
        for _ in range(80):
            if self.find_hint_pair():
                return
            self.shuffle_remaining(update=False)

    def draw_board(self):
        conf = self.levels[self.level_index]
        self.rows = conf["rows"]
        self.cols = conf["cols"]
        self.tile = conf["tile"]
        self.gap = 8
        self.step = self.tile + self.gap
        self.outer = self.step + 14

        width = self.outer * 2 + (self.cols - 1) * self.step + self.tile
        height = self.outer * 2 + (self.rows - 1) * self.step + self.tile
        self.canvas.config(width=width, height=height)
        self.canvas.delete("all")
        self.tile_items = {}
        self.line_items = []

        self.round_rect(
            10,
            10,
            width - 10,
            height - 10,
            18,
            fill="#ffedd5",
            outline="",
        )
        self.round_rect(
            22,
            22,
            width - 22,
            height - 22,
            18,
            fill="#fffaf0",
            outline="#fdba74",
            width=2,
        )

        for r in range(1, self.rows + 1):
            for c in range(1, self.cols + 1):
                if self.board[r][c] != 0:
                    self.draw_tile(r, c)

    def draw_tile(self, r, c, state="normal"):
        x1, y1, x2, y2 = self.tile_bounds(r, c)
        icon_name = self.board[r][c]

        colors = {
            "normal": ("#ffffff", "#fed7aa", self.ink),
            "selected": ("#fffbeb", "#f97316", self.accent),
            "hint": ("#ecfeff", "#06b6d4", "#0891b2"),
            "matched": ("#dcfce7", "#22c55e", self.good),
            "blocked": ("#fef2f2", "#ef4444", "#ef4444"),
        }
        fill, outline, text_fill = colors[state]

        old = self.tile_items.get((r, c), [])
        for item in old:
            self.canvas.delete(item)

        shadow = self.round_rect(
            x1 + 3,
            y1 + 4,
            x2 + 3,
            y2 + 4,
            12,
            fill=self.shadow,
            outline="",
        )
        card = self.round_rect(
            x1,
            y1,
            x2,
            y2,
            12,
            fill=fill,
            outline=outline,
            width=3,
        )
        shine = self.round_rect(
            x1 + 8,
            y1 + 7,
            x2 - 8,
            y1 + 15,
            8,
            fill="#fff7ed",
            outline="",
        )
        icon_items = self.draw_icon(icon_name, x1, y1, x2, y2, text_fill)
        self.tile_items[(r, c)] = [shadow, card, shine] + icon_items

    def draw_icon(self, name, x1, y1, x2, y2, outline):
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2 + self.tile * 0.04
        size = self.tile
        items = []

        def oval(rx, ry, fill, dx=0, dy=0, width=2):
            return self.canvas.create_oval(
                cx - rx + dx, cy - ry + dy, cx + rx + dx, cy + ry + dy,
                fill=fill, outline=outline, width=width,
            )

        def leaf(dx, dy, fill="#16a34a"):
            return self.canvas.create_oval(
                cx + dx, cy + dy, cx + dx + size * 0.24, cy + dy + size * 0.13,
                fill=fill, outline=outline, width=2,
            )

        if name == "apple":
            items.append(oval(size * 0.23, size * 0.25, "#ef4444", dx=-size * 0.07))
            items.append(oval(size * 0.23, size * 0.25, "#dc2626", dx=size * 0.07))
            items.append(self.canvas.create_line(cx, cy - size * 0.30, cx + size * 0.05, cy - size * 0.42, fill=outline, width=3))
            items.append(leaf(size * 0.01, -size * 0.43))
        elif name == "orange":
            items.append(oval(size * 0.30, size * 0.30, "#fb923c"))
            items.append(self.canvas.create_arc(cx - size * 0.18, cy - size * 0.12, cx + size * 0.18, cy + size * 0.18, start=20, extent=130, style="arc", outline="#fed7aa", width=3))
            items.append(leaf(size * 0.02, -size * 0.39, "#22c55e"))
        elif name == "lemon":
            items.append(self.canvas.create_oval(cx - size * 0.34, cy - size * 0.22, cx + size * 0.34, cy + size * 0.22, fill="#fde047", outline=outline, width=3))
            items.append(self.canvas.create_oval(cx - size * 0.20, cy - size * 0.11, cx + size * 0.20, cy + size * 0.11, fill="#fef08a", outline="", width=0))
            items.append(leaf(size * 0.06, -size * 0.35))
        elif name == "watermelon":
            items.append(self.canvas.create_arc(cx - size * 0.36, cy - size * 0.28, cx + size * 0.36, cy + size * 0.44, start=200, extent=140, style="pieslice", fill="#22c55e", outline=outline, width=3))
            items.append(self.canvas.create_arc(cx - size * 0.30, cy - size * 0.20, cx + size * 0.30, cy + size * 0.38, start=200, extent=140, style="pieslice", fill="#fb7185", outline="#fef2f2", width=3))
            for dx in (-0.12, 0, 0.12):
                items.append(oval(size * 0.025, size * 0.045, "#111827", dx=size * dx, dy=size * 0.10, width=1))
        elif name == "grape":
            for dx, dy in [(-.12, -.05), (.02, -.06), (.15, .02), (-.02, .09), (-.16, .08), (.10, .16)]:
                items.append(oval(size * 0.105, size * 0.105, "#8b5cf6", dx=size * dx, dy=size * dy))
            items.append(self.canvas.create_line(cx - size * 0.03, cy - size * 0.22, cx + size * 0.09, cy - size * 0.35, fill=outline, width=3))
            items.append(leaf(size * 0.03, -size * 0.39, "#16a34a"))
        elif name == "strawberry":
            points = [
                cx, cy + size * 0.32, cx - size * 0.28, cy - size * 0.05,
                cx - size * 0.18, cy - size * 0.28, cx + size * 0.18, cy - size * 0.28,
                cx + size * 0.28, cy - size * 0.05,
            ]
            items.append(self.canvas.create_polygon(points, smooth=True, fill="#ef4444", outline=outline, width=3))
            for dx, dy in [(-.11, -.07), (.08, -.08), (0, .04), (-.08, .15), (.11, .13)]:
                items.append(oval(size * 0.018, size * 0.032, "#fde68a", dx=size * dx, dy=size * dy, width=1))
            items.append(leaf(-size * 0.11, -size * 0.35))
        elif name == "cherry":
            items.append(oval(size * 0.14, size * 0.14, "#ef4444", dx=-size * 0.15, dy=size * 0.12))
            items.append(oval(size * 0.14, size * 0.14, "#dc2626", dx=size * 0.15, dy=size * 0.10))
            items.append(self.canvas.create_line(cx - size * 0.15, cy, cx - size * 0.02, cy - size * 0.32, cx + size * 0.14, cy - size * 0.02, fill=outline, width=3, smooth=True))
            items.append(leaf(size * 0.00, -size * 0.37))
        elif name == "kiwi":
            items.append(oval(size * 0.30, size * 0.30, "#84cc16"))
            items.append(oval(size * 0.16, size * 0.16, "#fefce8", width=2))
            for angle in range(0, 360, 45):
                dx = size * 0.22 * math.cos(math.radians(angle))
                dy = size * 0.22 * math.sin(math.radians(angle))
                items.append(oval(size * 0.012, size * 0.012, "#111827", dx=dx, dy=dy, width=1))
        elif name == "pineapple":
            items.append(self.canvas.create_oval(cx - size * 0.24, cy - size * 0.18, cx + size * 0.24, cy + size * 0.31, fill="#facc15", outline=outline, width=3))
            for dx in (-.12, 0, .12):
                items.append(self.canvas.create_line(cx + size * dx, cy - size * 0.16, cx + size * (dx + 0.18), cy + size * 0.23, fill="#ca8a04", width=2))
                items.append(self.canvas.create_line(cx + size * dx, cy + size * 0.23, cx + size * (dx + 0.18), cy - size * 0.16, fill="#ca8a04", width=2))
            items.append(leaf(-size * 0.18, -size * 0.40))
            items.append(leaf(-size * 0.02, -size * 0.43))
        elif name == "coconut":
            items.append(oval(size * 0.30, size * 0.28, "#92400e"))
            items.append(oval(size * 0.20, size * 0.18, "#fef3c7", width=2))
            for dx in (-.08, .02, .12):
                items.append(oval(size * 0.022, size * 0.022, "#451a03", dx=size * dx, dy=-size * 0.05, width=1))
        elif name == "avocado":
            items.append(self.canvas.create_oval(cx - size * 0.26, cy - size * 0.33, cx + size * 0.26, cy + size * 0.34, fill="#65a30d", outline=outline, width=3))
            items.append(oval(size * 0.17, size * 0.23, "#fef3c7", dy=size * 0.06, width=2))
            items.append(oval(size * 0.08, size * 0.08, "#92400e", dy=size * 0.14, width=2))
        elif name == "peach":
            items.append(oval(size * 0.22, size * 0.25, "#fb7185", dx=-size * 0.08))
            items.append(oval(size * 0.22, size * 0.25, "#fdba74", dx=size * 0.08))
            items.append(self.canvas.create_line(cx, cy - size * 0.24, cx, cy + size * 0.24, fill="#f97316", width=2))
            items.append(leaf(size * 0.03, -size * 0.39))
        elif name == "pear":
            items.append(self.canvas.create_oval(cx - size * 0.21, cy - size * 0.33, cx + size * 0.21, cy + size * 0.08, fill="#bef264", outline=outline, width=3))
            items.append(oval(size * 0.27, size * 0.25, "#a3e635", dy=size * 0.11))
            items.append(leaf(size * 0.02, -size * 0.42))
        elif name == "mango":
            items.append(self.canvas.create_oval(cx - size * 0.31, cy - size * 0.23, cx + size * 0.31, cy + size * 0.23, fill="#f59e0b", outline=outline, width=3))
            items.append(self.canvas.create_arc(cx - size * 0.24, cy - size * 0.16, cx + size * 0.28, cy + size * 0.20, start=210, extent=120, style="arc", outline="#fde68a", width=3))
            items.append(leaf(size * 0.04, -size * 0.35))
        elif name == "blueberry":
            for dx, dy in [(-.14, .04), (.02, -.08), (.16, .05), (-.01, .14)]:
                items.append(oval(size * 0.13, size * 0.13, "#3b82f6", dx=size * dx, dy=size * dy))
                items.append(oval(size * 0.045, size * 0.045, "#1e3a8a", dx=size * dx, dy=size * dy, width=1))
        elif name == "banana":
            items.append(self.canvas.create_arc(cx - size * 0.36, cy - size * 0.30, cx + size * 0.38, cy + size * 0.33, start=205, extent=125, style="arc", outline="#facc15", width=max(9, int(size * 0.16))))
            items.append(self.canvas.create_arc(cx - size * 0.34, cy - size * 0.27, cx + size * 0.36, cy + size * 0.30, start=205, extent=125, style="arc", outline=outline, width=2))
        elif name == "carrot":
            items.append(self.canvas.create_polygon(cx, cy + size * 0.32, cx - size * 0.20, cy - size * 0.16, cx + size * 0.20, cy - size * 0.16, fill="#f97316", outline=outline, width=3))
            items.append(leaf(-size * 0.16, -size * 0.37))
            items.append(leaf(size * 0.00, -size * 0.39))
        elif name == "corn":
            items.append(self.canvas.create_oval(cx - size * 0.19, cy - size * 0.34, cx + size * 0.19, cy + size * 0.34, fill="#facc15", outline=outline, width=3))
            for dy in (-.18, -.06, .06, .18):
                items.append(self.canvas.create_line(cx - size * 0.15, cy + size * dy, cx + size * 0.15, cy + size * dy, fill="#fde68a", width=2))
            items.append(self.canvas.create_arc(cx - size * 0.38, cy - size * 0.05, cx - size * 0.02, cy + size * 0.42, start=300, extent=115, style="arc", outline="#22c55e", width=5))
            items.append(self.canvas.create_arc(cx + size * 0.02, cy - size * 0.05, cx + size * 0.38, cy + size * 0.42, start=125, extent=115, style="arc", outline="#16a34a", width=5))
        elif name == "mushroom":
            items.append(self.canvas.create_arc(cx - size * 0.34, cy - size * 0.34, cx + size * 0.34, cy + size * 0.20, start=0, extent=180, style="pieslice", fill="#ef4444", outline=outline, width=3))
            items.append(self.canvas.create_rectangle(cx - size * 0.12, cy - size * 0.03, cx + size * 0.12, cy + size * 0.30, fill="#fef3c7", outline=outline, width=3))
            for dx in (-.15, .02, .17):
                items.append(oval(size * 0.04, size * 0.04, "#fee2e2", dx=size * dx, dy=-size * 0.17, width=1))
        elif name == "pretzel":
            items.append(self.canvas.create_oval(cx - size * 0.31, cy - size * 0.10, cx - size * 0.02, cy + size * 0.21, fill="", outline="#b45309", width=7))
            items.append(self.canvas.create_oval(cx + size * 0.02, cy - size * 0.10, cx + size * 0.31, cy + size * 0.21, fill="", outline="#b45309", width=7))
            items.append(self.canvas.create_line(cx - size * 0.25, cy + size * 0.25, cx, cy - size * 0.19, cx + size * 0.25, cy + size * 0.25, fill="#b45309", width=7, smooth=True))
        else:
            items.append(oval(size * 0.28, size * 0.28, "#38bdf8"))

        return items

    def round_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return self.canvas.create_polygon(points, smooth=True, splinesteps=12, **kwargs)

    def tile_bounds(self, r, c):
        x1 = self.outer + (c - 1) * self.step
        y1 = self.outer + (r - 1) * self.step
        return x1, y1, x1 + self.tile, y1 + self.tile

    def cell_center(self, r, c):
        x = self.outer + (c - 1) * self.step + self.tile / 2
        y = self.outer + (r - 1) * self.step + self.tile / 2
        return x, y

    def update_info(self):
        total = self.rows * self.cols
        left = sum(
            1
            for r in range(1, self.rows + 1)
            for c in range(1, self.cols + 1)
            if self.board[r][c] != 0
        )
        self.info_label.config(
            text=f"第 {self.level_index + 1}/3 关  剩余 {left}/{total}  提示 {self.hints_left}"
        )
        state = "normal" if self.hints_left > 0 else "disabled"
        self.hint_button.config(state=state)

    def on_canvas_click(self, event):
        pos = self.point_to_cell(event.x, event.y)
        if not pos:
            return

        r, c = pos
        if self.board[r][c] == 0:
            return

        if self.selected is None:
            self.select_tile(r, c)
            return

        r1, c1 = self.selected
        if (r1, c1) == (r, c):
            self.draw_tile(r, c)
            self.selected = None
            return

        if self.board[r1][c1] != self.board[r][c]:
            self.draw_tile(r1, c1)
            self.select_tile(r, c)
            return

        path = self.find_path((r1, c1), (r, c))
        if path:
            self.show_connection(path)
            self.draw_tile(r1, c1, "matched")
            self.draw_tile(r, c, "matched")
            self.root.after(180, lambda: self.remove_pair((r1, c1), (r, c)))
        else:
            self.draw_tile(r1, c1, "blocked")
            self.draw_tile(r, c, "blocked")
            self.root.after(260, lambda: self.reset_failed_pair((r1, c1), (r, c)))

    def point_to_cell(self, x, y):
        for r in range(1, self.rows + 1):
            for c in range(1, self.cols + 1):
                x1, y1, x2, y2 = self.tile_bounds(r, c)
                if x1 <= x <= x2 and y1 <= y <= y2:
                    return r, c
        return None

    def select_tile(self, r, c):
        self.clear_lines()
        self.selected = (r, c)
        self.draw_tile(r, c, "selected")

    def reset_failed_pair(self, p1, p2):
        for point in (p1, p2):
            if self.board[point[0]][point[1]] != 0:
                self.draw_tile(*point)
        self.selected = None

    def remove_pair(self, p1, p2):
        for r, c in (p1, p2):
            self.board[r][c] = 0
            for item in self.tile_items.get((r, c), []):
                self.canvas.delete(item)
            self.tile_items.pop((r, c), None)

        self.selected = None
        self.update_info()
        if self.check_win():
            self.root.after(260, self.next_level)
        elif not self.find_hint_pair():
            self.root.after(260, self.no_moves_left)

    def show_connection(self, path):
        self.clear_lines()
        points = [self.cell_center(r, c) for r, c in self.compress_path(path)]
        flat = [value for point in points for value in point]
        glow = self.canvas.create_line(
            *flat,
            fill="#fed7aa",
            width=9,
            capstyle="round",
            joinstyle="round",
        )
        line = self.canvas.create_line(
            *flat,
            fill=self.accent,
            width=4,
            capstyle="round",
            joinstyle="round",
        )
        self.line_items = [glow, line]
        self.root.after(280, self.clear_lines)

    def clear_lines(self):
        for item in self.line_items:
            self.canvas.delete(item)
        self.line_items = []

    def compress_path(self, path):
        if len(path) <= 2:
            return path

        compressed = [path[0]]
        last_dir = None
        for i in range(1, len(path)):
            prev = path[i - 1]
            cur = path[i]
            direction = (cur[0] - prev[0], cur[1] - prev[1])
            if last_dir is not None and direction != last_dir:
                compressed.append(prev)
            last_dir = direction
        compressed.append(path[-1])
        return compressed

    def check_win(self):
        return all(
            self.board[r][c] == 0
            for r in range(1, self.rows + 1)
            for c in range(1, self.cols + 1)
        )

    def next_level(self):
        if self.level_index == len(self.levels) - 1:
            messagebox.showinfo("通关", "恭喜你完成全部 3 关！游戏将重新开始。")
            self.level_index = 0
            self.hints_left = 3
        else:
            self.level_index += 1
            messagebox.showinfo("过关", f"进入第 {self.level_index + 1} 关！")
        self.start_level()

    def use_hint(self):
        if self.hints_left <= 0:
            return

        pair = self.find_hint_pair()
        if not pair:
            self.no_moves_left()
            return

        self.hints_left -= 1
        self.update_info()
        p1, p2 = pair
        self.flash_hint(p1, p2)
        path = self.find_path(p1, p2)
        if path:
            self.show_connection(path)

    def flash_hint(self, p1, p2):
        for point in (p1, p2):
            if self.board[point[0]][point[1]] != 0:
                self.draw_tile(*point, state="hint")

        def recover():
            for point in (p1, p2):
                if self.board[point[0]][point[1]] != 0:
                    self.draw_tile(*point)

        self.root.after(900, recover)

    def shuffle_board(self):
        self.selected = None
        self.clear_lines()
        self.shuffle_remaining(update=True)
        self.ensure_playable_board()
        self.draw_board()
        self.update_info()

    def shuffle_remaining(self, update):
        values = []
        cells = []
        for r in range(1, self.rows + 1):
            for c in range(1, self.cols + 1):
                if self.board[r][c] != 0:
                    values.append(self.board[r][c])
                    cells.append((r, c))
        random.shuffle(values)
        for (r, c), value in zip(cells, values):
            self.board[r][c] = value
        if update:
            self.draw_board()

    def no_moves_left(self):
        messagebox.showinfo("没有可消除的组合", "当前棋盘没有可连接的图案，已经帮你洗牌。")
        self.shuffle_board()

    def find_hint_pair(self):
        points = []
        for r in range(1, self.rows + 1):
            for c in range(1, self.cols + 1):
                if self.board[r][c] != 0:
                    points.append((r, c))

        random.shuffle(points)
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                p1, p2 = points[i], points[j]
                if self.board[p1[0]][p1[1]] == self.board[p2[0]][p2[1]]:
                    if self.find_path(p1, p2):
                        return p1, p2
        return None

    def find_path(self, start, target):
        if start == target:
            return None

        rows = len(self.board)
        cols = len(self.board[0])
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        queue = [(start[0], start[1], -1, 0, [start])]
        best = {}

        while queue:
            r, c, direction_index, turns, path = queue.pop(0)
            for next_dir, (dr, dc) in enumerate(directions):
                nr, nc = r + dr, c + dc
                if not (0 <= nr < rows and 0 <= nc < cols):
                    continue

                next_turns = turns
                if direction_index != -1 and next_dir != direction_index:
                    next_turns += 1
                if next_turns > 2:
                    continue

                if (nr, nc) != target and self.board[nr][nc] != 0:
                    continue

                state = (nr, nc, next_dir)
                if best.get(state, 3) <= next_turns:
                    continue
                best[state] = next_turns

                next_path = path + [(nr, nc)]
                if (nr, nc) == target:
                    return next_path
                queue.append((nr, nc, next_dir, next_turns, next_path))

        return None


def main():
    root = tk.Tk()
    LianLianKanGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
