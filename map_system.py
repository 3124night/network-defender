"""
网络守护者 - 地图系统
处理游戏地图、路径、网格和可视化元素
"""

import pygame
import math
from config import *


class GameMap:
    """游戏地图类"""
    
    def __init__(self, path_type='zigzag'):
        self.grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.path = []  # 敌人路径点列表
        self.towers = []  # 防御塔位置列表
        self.base_pos = None  # 基地位置
        self.spawn_pos = None  # 出生点位置
        self.path_type = path_type
        
        # 动画效果
        self.path_pulse = 0
        self.grid_anim_offset = 0
        
        self._init_map()
        self._generate_path()
    
    def _init_map(self):
        """初始化地图网格"""
        # 0 = 空地, 1 = 路径, 2 = 基地, 3 = 出生点
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                self.grid[row][col] = 0
    
    def _generate_path(self):
        """生成敌人行走路径"""
        if self.path_type == 'zigzag':
            path_points = [
                (0, 3), (3, 3), (3, 8), (7, 8), (7, 2),
                (11, 2), (11, 10), (15, 10), (15, 2),
                (18, 2), (18, 12), (14, 12), (14, 14), (19, 14),
            ]
        elif self.path_type == 'spiral':
            path_points = [
                (0, 7), (2, 7), (2, 2), (17, 2), (17, 7),
                (6, 7), (6, 12), (13, 12), (13, 14), (19, 14),
            ]
        elif self.path_type == 'cross':
            path_points = [
                (0, 3), (4, 3), (4, 9), (10, 9), (10, 2),
                (15, 2), (15, 10), (9, 10), (9, 14), (19, 14),
            ]
        else:
            path_points = [
                (0, 3), (3, 3), (3, 8), (7, 8), (7, 2),
                (11, 2), (11, 10), (15, 10), (15, 2),
                (18, 2), (18, 12), (14, 12), (14, 14), (19, 14),
            ]
        
        self.spawn_pos = (path_points[0][0] * GRID_SIZE + GRID_SIZE // 2,
                         path_points[0][1] * GRID_SIZE + GRID_SIZE // 2)
        self.base_pos = (path_points[-1][0] * GRID_SIZE + GRID_SIZE // 2,
                        path_points[-1][1] * GRID_SIZE + GRID_SIZE // 2)
        
        # 标记路径网格
        for i in range(len(path_points) - 1):
            x1, y1 = path_points[i]
            x2, y2 = path_points[i + 1]
            
            # 水平路径
            if y1 == y2:
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    self.grid[y1][x] = 1
                    self.path.append((x * GRID_SIZE + GRID_SIZE // 2, 
                                    y1 * GRID_SIZE + GRID_SIZE // 2))
            # 垂直路径
            elif x1 == x2:
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    self.grid[y][x1] = 1
                    self.path.append((x1 * GRID_SIZE + GRID_SIZE // 2, 
                                    y * GRID_SIZE + GRID_SIZE // 2))
        
        # 移除重复的路径点
        self.path = list(dict.fromkeys(self.path))
        
        # 标记基地和出生点
        spawn_col, spawn_row = path_points[0]
        base_col, base_row = path_points[-1]
        self.grid[spawn_row][spawn_col] = 3
        self.grid[base_row][base_col] = 2
    
    def is_valid_tower_position(self, grid_x, grid_y):
        """检查是否是有效的防御塔位置"""
        if grid_x < 0 or grid_x >= GRID_COLS or grid_y < 0 or grid_y >= GRID_ROWS:
            return False
        
        # 不能建在路径上
        if self.grid[grid_y][grid_x] == 1:
            return False
        
        # 不能建在基地或出生点上
        if self.grid[grid_y][grid_x] in [2, 3]:
            return False
        
        # 检查是否已有防御塔
        for tower in self.towers:
            if tower['grid_x'] == grid_x and tower['grid_y'] == grid_y:
                return False
        
        return True
    
    def place_tower(self, grid_x, grid_y, tower_type):
        """放置防御塔"""
        if self.is_valid_tower_position(grid_x, grid_y):
            self.towers.append({
                'grid_x': grid_x,
                'grid_y': grid_y,
                'type': tower_type,
                'world_x': grid_x * GRID_SIZE + GRID_SIZE // 2,
                'world_y': grid_y * GRID_SIZE + GRID_SIZE // 2
            })
            return True
        return False
    
    def remove_tower(self, grid_x, grid_y):
        """移除防御塔"""
        for tower in self.towers:
            if tower['grid_x'] == grid_x and tower['grid_y'] == grid_y:
                self.towers.remove(tower)
                return True
        return False
    
    def get_tower_at(self, grid_x, grid_y):
        """获取指定位置的防御塔"""
        for tower in self.towers:
            if tower['grid_x'] == grid_x and tower['grid_y'] == grid_y:
                return tower
        return None
    
    def world_to_grid(self, world_x, world_y):
        """世界坐标转网格坐标"""
        grid_x = int(world_x // GRID_SIZE)
        grid_y = int(world_y // GRID_SIZE)
        return grid_x, grid_y
    
    def grid_to_world(self, grid_x, grid_y):
        """网格坐标转世界坐标（中心点）"""
        world_x = grid_x * GRID_SIZE + GRID_SIZE // 2
        world_y = grid_y * GRID_SIZE + GRID_SIZE // 2
        return world_x, world_y
    
    def get_path_distance(self, pos1, pos2):
        """获取路径上两点之间的距离"""
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        return math.sqrt(dx * dx + dy * dy)
    
    def update(self, dt):
        """更新地图动画"""
        self.path_pulse += dt * 3
        self.grid_anim_offset += dt * 0.5
    
    def draw(self, screen):
        """绘制地图"""
        # 绘制背景渐变
        self._draw_background(screen)
        
        # 绘制网格
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                x = col * GRID_SIZE
                y = row * GRID_SIZE
                
                cell_type = self.grid[row][col]
                
                if cell_type == 0:  # 空地
                    # 动态网格效果
                    alpha = int(30 + 20 * math.sin(self.grid_anim_offset + col * 0.3 + row * 0.2))
                    pygame.draw.rect(screen, (alpha, alpha + 10, alpha + 20), (x, y, GRID_SIZE, GRID_SIZE), 1)
                elif cell_type == 1:  # 路径
                    self._draw_path_cell(screen, x, y)
                elif cell_type == 2:  # 基地
                    self._draw_base(screen, x, y)
                elif cell_type == 3:  # 出生点
                    self._draw_spawn_point(screen, x, y)
        
        # 绘制路径发光效果
        self._draw_path_glow(screen)
        
        # 绘制防御塔位置标记
        for tower in self.towers:
            self._draw_tower_base(screen, tower['world_x'], tower['world_y'])
    
    def _draw_background(self, screen):
        """绘制动态背景"""
        screen.fill(COLOR_BACKGROUND)
        
        # 绘制微妙的背景网格点
        for row in range(0, GRID_ROWS * GRID_SIZE, GRID_SIZE * 2):
            for col in range(0, GRID_COLS * GRID_SIZE, GRID_SIZE * 2):
                offset = int(2 * math.sin(self.grid_anim_offset + col * 0.1))
                alpha = int(20 + 15 * math.sin(self.grid_anim_offset * 2 + row * 0.1))
                pygame.draw.circle(screen, (alpha, alpha + 20, alpha + 40), 
                                 (col + offset, row), 1)
    
    def _draw_path_cell(self, screen, x, y):
        """绘制路径单元格"""
        # 脉冲效果
        pulse = math.sin(self.path_pulse) * 0.15 + 1
        base_color = (70, 85, 110)
        glow_color = (
            int(min(255, base_color[0] * pulse + 20)),
            int(min(255, base_color[1] * pulse + 20)),
            int(min(255, base_color[2] * pulse + 30))
        )
        
        # 绘制路径背景
        pygame.draw.rect(screen, glow_color, (x + 2, y + 2, GRID_SIZE - 4, GRID_SIZE - 4), border_radius=4)
        
        # 绘制路径边框发光
        glow_alpha = int(40 + 20 * math.sin(self.path_pulse * 2))
        glow_surface = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (100, 150, 255, glow_alpha), 
                        (0, 0, GRID_SIZE, GRID_SIZE), 2, border_radius=4)
        screen.blit(glow_surface, (x, y))
    
    def _draw_path_glow(self, screen):
        """绘制路径发光效果"""
        if len(self.path) > 1:
            # 主路径线
            pygame.draw.lines(screen, (120, 160, 200), False, self.path, 3)
            
            # 发光效果
            glow_alpha = int(30 + 15 * math.sin(self.path_pulse))
            glow_surface = pygame.Surface((GAME_AREA_WIDTH, GAME_AREA_HEIGHT), pygame.SRCALPHA)
            pygame.draw.lines(glow_surface, (100, 180, 255, glow_alpha), False, self.path, 8)
            screen.blit(glow_surface, (0, 0))
    
    def _draw_base(self, screen, x, y):
        """绘制基地"""
        center_x = x + GRID_SIZE // 2
        center_y = y + GRID_SIZE // 2
        
        # 外圈发光
        glow_pulse = math.sin(self.path_pulse * 2) * 5
        glow_surface = pygame.Surface((GRID_SIZE + 20, GRID_SIZE + 20), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (80, 255, 120, 60), 
                          (GRID_SIZE // 2 + 10, GRID_SIZE // 2 + 10), 
                          GRID_SIZE // 2 + int(glow_pulse))
        screen.blit(glow_surface, (x - 10, y - 10))
        
        # 外圈
        pygame.draw.circle(screen, (80, 200, 120), (center_x, center_y), GRID_SIZE // 2 - 4)
        # 内圈
        pygame.draw.circle(screen, (120, 255, 160), (center_x, center_y), GRID_SIZE // 2 - 8)
        # 核心
        pygame.draw.circle(screen, (200, 255, 220), (center_x, center_y), 8)
        
        # 绘制服务器图标（简化版）
        pygame.draw.rect(screen, COLOR_BACKGROUND, (center_x - 6, center_y - 10, 12, 20), 2)
        pygame.draw.line(screen, COLOR_BACKGROUND, (center_x - 4, center_y - 6), (center_x + 4, center_y - 6), 1)
        pygame.draw.line(screen, COLOR_BACKGROUND, (center_x - 4, center_y), (center_x + 4, center_y), 1)
        pygame.draw.line(screen, COLOR_BACKGROUND, (center_x - 4, center_y + 6), (center_x + 4, center_y + 6), 1)
    
    def _draw_spawn_point(self, screen, x, y):
        """绘制出生点"""
        center_x = x + GRID_SIZE // 2
        center_y = y + GRID_SIZE // 2
        
        # 危险发光效果
        glow_pulse = math.sin(self.path_pulse * 3) * 3
        glow_surface = pygame.Surface((GRID_SIZE + 16, GRID_SIZE + 16), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (255, 80, 80, 80), 
                          (GRID_SIZE // 2 + 8, GRID_SIZE // 2 + 8), 
                          GRID_SIZE // 2 + int(glow_pulse))
        screen.blit(glow_surface, (x - 8, y - 8))
        
        # 外圈
        pygame.draw.circle(screen, (200, 80, 80), (center_x, center_y), GRID_SIZE // 2 - 4)
        # 内圈
        pygame.draw.circle(screen, (255, 120, 120), (center_x, center_y), GRID_SIZE // 2 - 8)
        # 核心
        pygame.draw.circle(screen, (255, 200, 200), (center_x, center_y), 8)
        
        # 绘制警告图标
        pygame.draw.polygon(screen, COLOR_BACKGROUND, [
            (center_x, center_y - 8),
            (center_x - 7, center_y + 6),
            (center_x + 7, center_y + 6)
        ])
        pygame.draw.line(screen, (200, 80, 80), (center_x, center_y - 4), (center_x, center_y + 2), 2)
    
    def _draw_tower_base(self, screen, x, y):
        """绘制防御塔底座"""
        # 绘制一个淡淡的底座标记
        pygame.draw.circle(screen, (60, 80, 100), (int(x), int(y)), 4)
    
    def draw_highlight(self, screen, grid_x, grid_y, color, alpha=128):
        """绘制高亮区域"""
        if grid_x < 0 or grid_x >= GRID_COLS or grid_y < 0 or grid_y >= GRID_ROWS:
            return
        
        x = grid_x * GRID_SIZE
        y = grid_y * GRID_SIZE
        
        highlight_surface = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
        highlight_surface.fill((*color, alpha))
        screen.blit(highlight_surface, (x, y))
    
    def draw_range_circle(self, screen, x, y, range_radius, color, alpha=64):
        """绘制范围圈"""
        range_surface = pygame.Surface((range_radius * 2, range_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(range_surface, (*color, alpha), (range_radius, range_radius), range_radius)
        pygame.draw.circle(range_surface, (*color, alpha + 64), (range_radius, range_radius), range_radius, 2)
        screen.blit(range_surface, (int(x - range_radius), int(y - range_radius)))
