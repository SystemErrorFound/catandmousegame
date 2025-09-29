import random
import heapq
import pygame
from constants import MOVES, DIRS

class CatAI:
    def __init__(self, game):
        self.game = game
        
    def update_cat_memory(self):
        mouse_pos_tuple = (self.game.mouse_pos['x'], self.game.mouse_pos['y'])
        self.game.cat_memory.append(mouse_pos_tuple)
        if len(self.game.cat_memory) > self.game.memory_size:
            self.game.cat_memory.pop(0)
        
        if self.game.last_cat_pos:
            if self.game.cat_pos['x'] == self.game.last_cat_pos['x'] and self.game.cat_pos['y'] == self.game.last_cat_pos['y']:
                self.game.cat_stuck_counter += 1
            else:
                self.game.cat_stuck_counter = 0
        
        self.game.last_cat_pos = {'x': self.game.cat_pos['x'], 'y': self.game.cat_pos['y']}

    def should_cat_move(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.game.cat_move_timer >= self.game.cat_move_delay:
            self.game.cat_move_timer = current_time
            return True
        return False

    def cat_ai_move(self):
        if self.game.game_state != 'PLAYING': 
            return
            
        self.update_cat_memory()
        
        if self.game.is_king_mouse: 
            move = self.improved_flee_move(self.game.cat_pos, self.game.mouse_pos)
        else:
            if self.game.cat_difficulty == 'easy': 
                move = self.improved_random_move(self.game.cat_pos)
            elif self.game.cat_difficulty == 'medium': 
                move = self.improved_greedy_move(self.game.cat_pos, self.game.mouse_pos)
            else: 
                move = self.improved_a_star_move(self.game.cat_pos, self.game.mouse_pos)
        
        if move: 
            self.game.move_character(self.game.cat_pos, move['dx'], move['dy'])
        
        self.game.check_collisions_and_state()

    def improved_random_move(self, pos):
        valid_moves = []
        
        for move in MOVES:
            new_x, new_y = pos['x'] + move['dx'], pos['y'] + move['dy']
            if (0 <= new_x < self.game.board_size and 0 <= new_y < self.game.board_size and 
                self.game.board[new_y][new_x] != 1):
                valid_moves.append(move)
        
        if not valid_moves:
            return None
            
        if self.game.cat_stuck_counter > 2:
            unexplored_moves = []
            for move in valid_moves:
                new_pos = (pos['x'] + move['dx'], pos['y'] + move['dy'])
                if new_pos not in self.game.cat_memory[-3:]:
                    unexplored_moves.append(move)
            if unexplored_moves:
                valid_moves = unexplored_moves
        
        best_move = None
        min_dist = float('inf')
        
        for move in valid_moves:
            new_x, new_y = pos['x'] + move['dx'], pos['y'] + move['dy']
            
            dist = abs(new_x - self.game.mouse_pos['x']) + abs(new_y - self.game.mouse_pos['y'])
            
            penalty = 0
            if (new_x, new_y) in self.game.cat_memory[-2:]:
                penalty += 2
            
            adjacent_walls = sum(1 for dx, dy in DIRS
                               if (new_x + dx >= self.game.board_size or new_y + dy >= self.game.board_size or
                                   new_x + dx < 0 or new_y + dy < 0 or
                                   self.game.board[new_y + dy][new_x + dx] == 1))
            if adjacent_walls >= 3:
                penalty += 1
            
            adjusted_dist = dist + penalty
            
            if adjusted_dist < min_dist:
                min_dist = adjusted_dist
                best_move = move
        
        return best_move if best_move else valid_moves[0]
    
    def improved_greedy_move(self, from_pos, to_pos):
        target_pos = self.predict_mouse_position(to_pos)
        
        best_move, min_dist = None, float('inf')
        valid_moves = []
        
        for move in MOVES:
            new_x, new_y = from_pos['x'] + move['dx'], from_pos['y'] + move['dy']
            if (0 <= new_x < self.game.board_size and 0 <= new_y < self.game.board_size and 
                self.game.board[new_y][new_x] != 1):
                
                dist = abs(new_x - target_pos['x']) + abs(new_y - target_pos['y'])
                
                penalty = 0
                if (new_x, new_y) in self.game.cat_memory[-2:]:
                    penalty += 3
                
                adjacent_walls = sum(1 for dx, dy in DIRS
                                   if (new_x + dx >= self.game.board_size or new_y + dy >= self.game.board_size or
                                       new_x + dx < 0 or new_y + dy < 0 or
                                       self.game.board[new_y + dy][new_x + dx] == 1))
                if adjacent_walls >= 3:
                    penalty += 2
                
                adjusted_dist = dist + penalty
                valid_moves.append((move, adjusted_dist))
                
                if adjusted_dist < min_dist:
                    min_dist = adjusted_dist
                    best_move = move
        
        if self.game.cat_stuck_counter > 3:
            valid_moves.sort(key=lambda x: x[1])
            if len(valid_moves) > 1:
                return valid_moves[1][0]
        
        return best_move if best_move else self.improved_random_move(from_pos)

    def predict_mouse_position(self, current_pos):
        if len(self.game.cat_memory) < 2:
            return current_pos
        
        recent_positions = self.game.cat_memory[-2:]
        if len(recent_positions) >= 2:
            dx = recent_positions[-1][0] - recent_positions[-2][0]
            dy = recent_positions[-1][1] - recent_positions[-2][1]
            
            predicted_x = current_pos['x'] + dx
            predicted_y = current_pos['y'] + dy
            
            if (0 <= predicted_x < self.game.board_size and 0 <= predicted_y < self.game.board_size and
                self.game.board[predicted_y][predicted_x] != 1):
                return {'x': predicted_x, 'y': predicted_y}
        
        return current_pos

    def improved_a_star_move(self, from_pos, to_pos):
        target_pos = self.predict_mouse_position(to_pos)
        
        strategies = [
            target_pos,
            to_pos,
            self.get_intercept_position(from_pos, to_pos)
        ]
        
        best_path = None
        for strategy_target in strategies:
            if strategy_target:
                path = self.find_path_with_memory(from_pos, strategy_target)
                if path and len(path) > 1:
                    next_pos = (path[1]['x'], path[1]['y'])
                    if next_pos not in self.game.cat_memory[-2:]:
                        best_path = path
                        break
                    elif not best_path:
                        best_path = path
        
        if best_path and len(best_path) > 1:
            return {'dx': best_path[1]['x'] - from_pos['x'], 'dy': best_path[1]['y'] - from_pos['y']}
        
        return self.improved_greedy_move(from_pos, to_pos)

    def get_intercept_position(self, cat_pos, mouse_pos):
        if len(self.game.cat_memory) < 2:
            return mouse_pos
        
        recent_positions = self.game.cat_memory[-2:]
        if len(recent_positions) >= 2:
            mouse_dx = recent_positions[-1][0] - recent_positions[-2][0]
            mouse_dy = recent_positions[-1][1] - recent_positions[-2][1]
            
            for i in range(1, 5):
                intercept_x = mouse_pos['x'] + mouse_dx * i
                intercept_y = mouse_pos['y'] + mouse_dy * i
                
                if (0 <= intercept_x < self.game.board_size and 0 <= intercept_y < self.game.board_size and
                    self.game.board[intercept_y][intercept_x] != 1):
                    
                    cat_dist = abs(cat_pos['x'] - intercept_x) + abs(cat_pos['y'] - intercept_y)
                    if cat_dist <= i + 2:
                        return {'x': intercept_x, 'y': intercept_y}
        
        return mouse_pos

    def improved_flee_move(self, from_pos, away_from_pos):
        def distance(p1, p2): 
            return abs(p1['x'] - p2['x']) + abs(p1['y'] - p2['y'])
        
        current_dist = distance(from_pos, away_from_pos)
        
        if current_dist > 8:
            strategic_pos = self.find_strategic_position(from_pos, away_from_pos, 'maintain_distance')
            if strategic_pos != from_pos:
                path_to_strategic = self.find_path(from_pos, strategic_pos)
                if path_to_strategic and len(path_to_strategic) > 1:
                    return {'dx': path_to_strategic[1]['x'] - from_pos['x'], 
                           'dy': path_to_strategic[1]['y'] - from_pos['y']}
        
        if not self.game.flee_target or distance(from_pos, self.game.flee_target) < 2:
            safe_spots = []
            
            corners = [
                {'x': 1, 'y': 1}, {'x': self.game.board_size - 2, 'y': 1}, 
                {'x': 1, 'y': self.game.board_size - 2}, {'x': self.game.board_size - 2, 'y': self.game.board_size - 2}
            ]
            
            edges = []
            for i in range(3, self.game.board_size - 3, 2):
                edges.extend([
                    {'x': 1, 'y': i}, {'x': self.game.board_size - 2, 'y': i},
                    {'x': i, 'y': 1}, {'x': i, 'y': self.game.board_size - 2}
                ])
            
            for pos in corners + edges:
                if self.game.board[pos['y']][pos['x']] == 0:
                    pos_dist = distance(pos, away_from_pos)
                    path_to_pos = self.find_path(from_pos, pos)
                    if path_to_pos and pos_dist > current_dist:
                        safe_spots.append((pos, pos_dist, len(path_to_pos)))
            
            if safe_spots:
                safe_spots.sort(key=lambda x: (-x[1], x[2]))
                self.game.flee_target = safe_spots[0][0]
        
        if self.game.flee_target:
            path_to_safety = self.find_path(from_pos, self.game.flee_target)
            if path_to_safety and len(path_to_safety) > 1:
                return {'dx': path_to_safety[1]['x'] - from_pos['x'], 
                       'dy': path_to_safety[1]['y'] - from_pos['y']}
        
        best_move, max_dist = None, -1
        
        for move in MOVES:
            new_x, new_y = from_pos['x'] + move['dx'], from_pos['y'] + move['dy']
            if (0 <= new_x < self.game.board_size and 0 <= new_y < self.game.board_size and 
                self.game.board[new_y][new_x] != 1):
                
                new_dist = distance({'x': new_x, 'y': new_y}, away_from_pos)
                
                penalty = 0
                if (new_x, new_y) in self.game.cat_memory[-2:]:
                    penalty = 1
                
                adjusted_dist = new_dist - penalty
                if adjusted_dist > max_dist:
                    max_dist = adjusted_dist
                    best_move = move
        
        return best_move
    
    def find_path_with_memory(self, start, goal):
        def heuristic(a, b): 
            return abs(a['x'] - b['x']) + abs(a['y'] - b['y'])
        
        def get_path_cost(current, neighbor):
            base_cost = 1
            memory_penalty = 0
            
            neighbor_pos = (neighbor['x'], neighbor['y'])
            if neighbor_pos in self.game.cat_memory:
                for i, pos in enumerate(reversed(self.game.cat_memory)):
                    if pos == neighbor_pos:
                        memory_penalty = (len(self.game.cat_memory) - i) * 0.5
                        break
            
            return base_cost + memory_penalty
        
        open_set = []
        came_from = {}
        g_score = {(start['x'], start['y']): 0}
        f_score = {(start['x'], start['y']): heuristic(start, goal)}
        
        heapq.heappush(open_set, (f_score[(start['x'], start['y'])], start['x'], start['y']))
        
        while open_set:
            current_f, current_x, current_y = heapq.heappop(open_set)
            current = {'x': current_x, 'y': current_y}
            
            if current['x'] == goal['x'] and current['y'] == goal['y']:
                path = [current]
                while (current['x'], current['y']) in came_from:
                    current = came_from[(current['x'], current['y'])]
                    path.append(current)
                return path[::-1]
            
            for dx, dy in DIRS:
                neighbor = {'x': current['x'] + dx, 'y': current['y'] + dy}
                
                if not (0 <= neighbor['x'] < self.game.board_size and 
                       0 <= neighbor['y'] < self.game.board_size and 
                       self.game.board[neighbor['y']][neighbor['x']] != 1):
                    continue
                
                tentative_g_score = g_score.get((current['x'], current['y']), float('inf'))
                tentative_g_score += get_path_cost(current, neighbor)
                
                neighbor_key = (neighbor['x'], neighbor['y'])
                if tentative_g_score < g_score.get(neighbor_key, float('inf')):
                    came_from[neighbor_key] = current
                    g_score[neighbor_key] = tentative_g_score
                    f_score[neighbor_key] = tentative_g_score + heuristic(neighbor, goal)
                    
                    if not any(item[1] == neighbor['x'] and item[2] == neighbor['y'] for item in open_set):
                        heapq.heappush(open_set, (f_score[neighbor_key], neighbor['x'], neighbor['y']))
        
        return None

    def find_path(self, start, goal):
        def heuristic(a, b): 
            dx = abs(a['x'] - b['x'])
            dy = abs(a['y'] - b['y'])
            return dx + dy + min(dx, dy) * 0.001
        
        open_set = []
        came_from = {}
        g_score = {(start['x'], start['y']): 0}
        
        heapq.heappush(open_set, (heuristic(start, goal), start['x'], start['y']))
        
        while open_set:
            _, current_x, current_y = heapq.heappop(open_set)
            current = {'x': current_x, 'y': current_y}
            
            if current['x'] == goal['x'] and current['y'] == goal['y']:
                path = [current]
                while (current['x'], current['y']) in came_from:
                    current = came_from[(current['x'], current['y'])]
                    path.append(current)
                return path[::-1]
            
            for dx, dy in DIRS:
                neighbor = {'x': current['x'] + dx, 'y': current['y'] + dy}
                
                if not (0 <= neighbor['x'] < self.game.board_size and 
                       0 <= neighbor['y'] < self.game.board_size and 
                       self.game.board[neighbor['y']][neighbor['x']] != 1):
                    continue
                
                tentative_g_score = g_score.get((current['x'], current['y']), float('inf')) + 1
                neighbor_key = (neighbor['x'], neighbor['y'])
                
                if tentative_g_score < g_score.get(neighbor_key, float('inf')):
                    came_from[neighbor_key] = current
                    g_score[neighbor_key] = tentative_g_score
                    f = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f, neighbor['x'], neighbor['y']))
        
        return None

    def find_strategic_position(self, from_pos, target_pos, strategy='intercept'):
        candidates = []
        
        if strategy == 'intercept':
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    if dx == 0 and dy == 0:
                        continue
                    
                    candidate_x = target_pos['x'] + dx
                    candidate_y = target_pos['y'] + dy
                    
                    if (0 <= candidate_x < self.game.board_size and 
                        0 <= candidate_y < self.game.board_size and 
                        self.game.board[candidate_y][candidate_x] != 1):
                        
                        candidate = {'x': candidate_x, 'y': candidate_y}
                        dist_to_target = abs(candidate_x - target_pos['x']) + abs(candidate_y - target_pos['y'])
                        dist_from_cat = abs(candidate_x - from_pos['x']) + abs(candidate_y - from_pos['y'])
                        if dist_to_target <= 3 and dist_from_cat <= 6:
                            strategic_value = 10 - dist_to_target - (dist_from_cat * 0.1)
                            candidates.append((candidate, strategic_value))
        
        elif strategy == 'surround':
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                candidate_x = target_pos['x'] + dx
                candidate_y = target_pos['y'] + dy
                
                if (0 <= candidate_x < self.game.board_size and 
                    0 <= candidate_y < self.game.board_size and 
                    self.game.board[candidate_y][candidate_x] != 1):
                    
                    candidate = {'x': candidate_x, 'y': candidate_y}
                    dist_from_cat = abs(candidate_x - from_pos['x']) + abs(candidate_y - from_pos['y'])
                    
                    if dist_from_cat <= 8:
                        strategic_value = 10 - (dist_from_cat * 0.2)
                        candidates.append((candidate, strategic_value))
        
        elif strategy == 'maintain_distance':
            optimal_distance = 6
            
            for dx in range(-4, 5):
                for dy in range(-4, 5):
                    if dx == 0 and dy == 0:
                        continue
                    
                    candidate_x = from_pos['x'] + dx
                    candidate_y = from_pos['y'] + dy
                    
                    if (0 <= candidate_x < self.game.board_size and 
                        0 <= candidate_y < self.game.board_size and 
                        self.game.board[candidate_y][candidate_x] != 1):
                        
                        candidate = {'x': candidate_x, 'y': candidate_y}
                        
                        dist_to_target = abs(candidate_x - target_pos['x']) + abs(candidate_y - target_pos['y'])
                        
                        distance_score = abs(optimal_distance - dist_to_target)
                        strategic_value = 10 - distance_score
                        
                        if (candidate_x, candidate_y) not in self.game.cat_memory[-3:]:
                            strategic_value += 2
                        
                        candidates.append((candidate, strategic_value))
        
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]
        
        return target_pos