import pygame, random, heapq
from collections import deque

class CatAI:
    def __init__(self, game):
        self.game = game
        self.cat_pos_history = []
        self.cat_memory = []
        self.memory_size = 6
        self.stuck_loop_counter = 0
        self.last_cat_pos = None
        self.cat_stuck_counter = 0
        self.last_cat_move_time = 0
        self.cat_move_delay = 300

    def update_memory_and_check_stuck(self):
        cat_pos = (self.game.cat_pos['x'], self.game.cat_pos['y'])
        mouse_pos = (self.game.mouse_pos['x'], self.game.mouse_pos['y'])

        self.cat_memory.append(mouse_pos)
        if len(self.cat_memory) > self.memory_size:
            self.cat_memory.pop(0)

        self.cat_pos_history.append(cat_pos)
        if len(self.cat_pos_history) > 5:
            self.cat_pos_history.pop(0)
        if len(self.cat_pos_history) >= 3:
            if (self.cat_pos_history[-1] == self.cat_pos_history[-3]
                and self.cat_pos_history[-1] != self.cat_pos_history[-2]):
                self.stuck_loop_counter += 1
            else:
                self.stuck_loop_counter = 0

        if self.last_cat_pos == cat_pos:
            self.cat_stuck_counter += 1
        else:
            self.cat_stuck_counter = 0
        self.last_cat_pos = cat_pos

    def should_cat_move(self):
        now = pygame.time.get_ticks()
        delay = {'easy': 450, 'medium': 350, 'hard': 250}[self.game.cat_difficulty]
        if now - self.last_cat_move_time >= delay:
            self.last_cat_move_time = now
            return True
        return False

    def find_path(self, start, goal, mode="bfs"):
        if start == goal:
            return []

        dirs = [(1,0), (-1,0), (0,1), (0,-1)]
        valid = lambda p: (0 <= p[0] < self.game.board_size and 0 <= p[1] < self.game.board_size
                           and self.game.board[p[1]][p[0]] != 1)

        if mode == "bfs":
            queue = deque([start])
            came_from = {start: None}
            while queue:
                cur = queue.popleft()
                if cur == goal:
                    break
                for dx, dy in dirs:
                    nxt = (cur[0]+dx, cur[1]+dy)
                    if valid(nxt) and nxt not in came_from:
                        came_from[nxt] = cur
                        queue.append(nxt)

        else:
            open_set = []
            came_from = {}
            g_score = {start: 0}
            heapq.heappush(open_set, (0, start))
            while open_set:
                _, cur = heapq.heappop(open_set)
                if cur == goal:
                    break
                for dx, dy in dirs:
                    nxt = (cur[0]+dx, cur[1]+dy)
                    if not valid(nxt):
                        continue

                    h = abs(nxt[0]-goal[0]) + abs(nxt[1]-goal[1])
                    new_g = g_score[cur] + 1

                    if mode == "a_star_memory" and nxt in self.cat_memory:
                        new_g += 5

                    if mode == "gbfs":
                        f = h
                    else:
                        f = new_g + h

                    if nxt not in g_score or new_g < g_score[nxt]:
                        g_score[nxt] = new_g
                        came_from[nxt] = cur
                        heapq.heappush(open_set, (f, nxt))

        if goal not in came_from:
            return None
        path = []
        cur = goal
        while cur:
            path.append(cur)
            cur = came_from.get(cur)
        path.reverse()
        return path

    def choose_next_move(self, from_pos, to_pos):
        difficulty = self.game.cat_difficulty.lower()
        is_king = self.game.is_king_mouse

        if is_king:
            return self.get_flee_move(from_pos, to_pos)

        if difficulty == "easy":
            path = self.find_path(from_pos, to_pos, "bfs")
        elif difficulty == "medium":
            path = self.find_path(from_pos, to_pos, "gbfs")
        else:
            path = self.find_path(from_pos, to_pos, "a_star_memory")

        if path and len(path) > 1:
            return path[1]

        return self.random_move(from_pos)

    def random_move(self, pos):
        dirs = [(1,0), (-1,0), (0,1), (0,-1)]
        valid = [(pos[0]+dx, pos[1]+dy) for dx, dy in dirs
                 if 0 <= pos[0]+dx < self.game.board_size and 0 <= pos[1]+dy < self.game.board_size
                 and self.game.board[pos[1]+dy][pos[0]+dx] != 1]
        return random.choice(valid) if valid else pos

    def get_flee_move(self, from_pos, away_from):
        dirs = [(1,0), (-1,0), (0,1), (0,-1)]
        valid = [(from_pos[0]+dx, from_pos[1]+dy) for dx, dy in dirs
                 if 0 <= from_pos[0]+dx < self.game.board_size and 0 <= from_pos[1]+dy < self.game.board_size
                 and self.game.board[from_pos[1]+dy][from_pos[0]+dx] != 1]
        if not valid:
            return from_pos
        return max(valid, key=lambda p: abs(p[0]-away_from[0]) + abs(p[1]-away_from[1]))

    def cat_ai_move(self):
        if self.game.game_state != "PLAYING":
            return

        self.update_memory_and_check_stuck()
        cat_pos = (self.game.cat_pos['x'], self.game.cat_pos['y'])
        mouse_pos = (self.game.mouse_pos['x'], self.game.mouse_pos['y'])

        if self.stuck_loop_counter > 2 or self.cat_stuck_counter > 3:
            new_pos = self.random_move(cat_pos)
        else:
            new_pos = self.choose_next_move(cat_pos, mouse_pos)

        dx = new_pos[0] - cat_pos[0]
        dy = new_pos[1] - cat_pos[1]
        self.game.move_character(self.game.cat_pos, dx, dy)
        self.game.check_collisions_and_state()
