"""
网络守护者 - UI系统
处理游戏界面、按钮、信息面板和菜单
"""

import pygame
from config import *


class Button:
    """按钮类"""
    
    def __init__(self, x, y, width, height, text, color=COLOR_BUTTON, 
                 hover_color=COLOR_BUTTON_HOVER, text_color=COLOR_TEXT,
                 font_size=20, border_radius=8):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_radius = border_radius
        self.hovered = False
        self.enabled = True
        
        self.font = pygame.font.SysFont('simhei', font_size)
    
    def update(self, mouse_pos):
        """更新按钮状态"""
        self.hovered = self.rect.collidepoint(mouse_pos) and self.enabled
    
    def draw(self, screen):
        """绘制按钮"""
        color = self.hover_color if self.hovered else self.color
        if not self.enabled:
            color = (color[0] // 2, color[1] // 2, color[2] // 2)
        
        # 绘制按钮背景
        pygame.draw.rect(screen, color, self.rect, border_radius=self.border_radius)
        
        # 绘制边框
        border_color = COLOR_UI_BORDER if self.hovered else (color[0] + 20, color[1] + 20, color[2] + 20)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=self.border_radius)
        
        # 绘制文字
        text_surface = self.font.render(self.text, True, self.text_color if self.enabled else (150, 150, 150))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_clicked(self, mouse_pos, mouse_pressed):
        """检查按钮是否被点击"""
        return (self.enabled and self.rect.collidepoint(mouse_pos) and 
                mouse_pressed[0])


class TowerButton:
    """防御塔选择按钮"""
    
    def __init__(self, x, y, tower_type, key_number):
        self.tower_type = tower_type
        self.key_number = key_number
        self.rect = pygame.Rect(x, y, 280, 70)
        
        config = TOWER_TYPES[tower_type]
        self.name = config['name']
        self.cost = config['cost']
        self.color = config['color']
        self.description = config['description']
        self.symbol = config['symbol']
        
        self.hovered = False
        self.selected = False
        
        self.font = pygame.font.SysFont('simhei', 18)
        self.small_font = pygame.font.SysFont('simhei', 14)
        self.symbol_font = pygame.font.SysFont('simhei', 24)
    
    def update(self, mouse_pos):
        """更新按钮状态"""
        self.hovered = self.rect.collidepoint(mouse_pos)
    
    def draw(self, screen, can_afford):
        """绘制防御塔按钮"""
        # 背景
        if self.selected:
            bg_color = (self.color[0] // 3, self.color[1] // 3, self.color[2] // 3)
            border_color = self.color
        elif self.hovered:
            bg_color = (self.color[0] // 4, self.color[1] // 4, self.color[2] // 4)
            border_color = (self.color[0] // 2, self.color[1] // 2, self.color[2] // 2)
        else:
            bg_color = COLOR_UI_BG
            border_color = (60, 70, 90)
        
        if not can_afford:
            bg_color = (bg_color[0] // 2, bg_color[1] // 2, bg_color[2] // 2)
            border_color = (80, 80, 80)
        
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=8)
        
        # 绘制颜色标识
        color_rect = pygame.Rect(self.rect.x + 8, self.rect.y + 10, 50, 50)
        pygame.draw.rect(screen, self.color, color_rect, border_radius=6)
        
        # 绘制符号
        symbol_text = self.symbol_font.render(self.symbol, True, COLOR_TEXT)
        symbol_rect = symbol_text.get_rect(center=color_rect.center)
        screen.blit(symbol_text, symbol_rect)
        
        # 绘制名称
        name_text = self.font.render(f"{self.name}", True, 
                                    COLOR_TEXT if can_afford else (150, 150, 150))
        screen.blit(name_text, (self.rect.x + 68, self.rect.y + 8))
        
        # 绘制花费
        cost_text = self.small_font.render(f"💰 {self.cost}", True, 
                                          COLOR_MONEY if can_afford else (150, 150, 150))
        screen.blit(cost_text, (self.rect.x + 68, self.rect.y + 30))
        
        # 绘制描述
        desc_text = self.small_font.render(self.description, True, 
                                          (180, 180, 180) if can_afford else (120, 120, 120))
        screen.blit(desc_text, (self.rect.x + 68, self.rect.y + 48))
        
        # 绘制快捷键
        key_text = self.small_font.render(f"[{self.key_number}]", True, (150, 150, 150))
        screen.blit(key_text, (self.rect.right - 35, self.rect.y + 5))


class UI:
    """游戏UI主类"""
    
    def __init__(self):
        # 面板位置（必须在按钮初始化之前）
        self.panel_x = UI_PANEL_X
        self.panel_width = UI_PANEL_WIDTH
        
        self.font_large = pygame.font.SysFont('simhei', 36)
        self.font_medium = pygame.font.SysFont('simhei', 24)
        self.font_small = pygame.font.SysFont('simhei', 16)
        
        # 游戏状态
        self.money = INITIAL_MONEY
        self.health = INITIAL_HEALTH
        self.wave = 0
        self.score = 0
        self.level = 1
        
        # 选中的防御塔类型
        self.selected_tower_type = None
        
        # 选中的防御塔（用于升级/出售）
        self.selected_tower = None
        
        # 按钮
        self.tower_buttons = []
        self._init_tower_buttons()
        
        # 控制按钮
        self.start_wave_button = None
        self._init_control_buttons()
        
        # 消息系统
        self.messages = []
    
    def _init_tower_buttons(self):
        """初始化防御塔按钮"""
        tower_types = list(TOWER_TYPES.keys())
        for i, tower_type in enumerate(tower_types):
            button = TowerButton(
                self.panel_x + 20,
                140 + i * 75,
                tower_type,
                i + 1
            )
            self.tower_buttons.append(button)
    
    def _init_control_buttons(self):
        """初始化控制按钮"""
        self.start_wave_button = Button(
            self.panel_x + 20, 525, 280, 45,
            "开始下一波", (80, 150, 80), (100, 200, 100)
        )
        
        self.upgrade_button = Button(
            self.panel_x + 20, 580, 135, 40,
            "升级", (80, 120, 200), (100, 150, 255)
        )
        
        self.sell_button = Button(
            self.panel_x + 165, 580, 135, 40,
            "出售", (200, 100, 100), (255, 120, 120)
        )
    
    def update(self, mouse_pos, money, health, wave, score, wave_ready, level=1):
        """更新UI状态"""
        self.money = money
        self.health = health
        self.wave = wave
        self.score = score
        self.level = level
        
        # 更新防御塔按钮
        for button in self.tower_buttons:
            button.update(mouse_pos)
        
        # 更新控制按钮
        self.start_wave_button.update(mouse_pos)
        self.start_wave_button.enabled = wave_ready
        
        if self.selected_tower:
            self.upgrade_button.update(mouse_pos)
            self.sell_button.update(mouse_pos)
            
            # 检查是否可以升级
            tower_info = self.selected_tower.get_info()
            self.upgrade_button.enabled = (tower_info['upgrade_cost'] is not None and 
                                          money >= tower_info['upgrade_cost'])
    
    def draw(self, screen):
        """绘制UI"""
        # 绘制右侧面板背景
        panel_rect = pygame.Rect(self.panel_x, 0, self.panel_width, SCREEN_HEIGHT)
        pygame.draw.rect(screen, COLOR_UI_BG, panel_rect)
        pygame.draw.line(screen, COLOR_UI_BORDER, (self.panel_x, 0), 
                        (self.panel_x, SCREEN_HEIGHT), 3)
        
        # 绘制标题
        title_text = self.font_large.render("网络守护者", True, COLOR_TEXT_HIGHLIGHT)
        screen.blit(title_text, (self.panel_x + 20, 15))
        
        # 绘制状态信息
        self._draw_status(screen)
        
        # 绘制防御塔选择区
        self._draw_tower_selection(screen)
        
        # 绘制控制按钮
        self._draw_controls(screen)
        
        # 绘制选中防御塔信息
        if self.selected_tower:
            self._draw_tower_info(screen)
        
        # 绘制底部提示
        self._draw_tips(screen)
        
        # 绘制消息
        self._draw_messages(screen)
    
    def _draw_status(self, screen):
        """绘制状态信息"""
        y_offset = 55
        
        # 关卡信息
        level_config = LEVELS.get(self.level, LEVELS[1])
        level_text = self.font_small.render(f"关卡 {self.level}: {level_config['name']}", True, COLOR_TEXT_HIGHLIGHT)
        screen.blit(level_text, (self.panel_x + 20, y_offset))
        
        y_offset += 25
        
        # 金币和生命值
        money_text = self.font_medium.render(f"💰 {self.money}", True, COLOR_MONEY)
        screen.blit(money_text, (self.panel_x + 20, y_offset))
        
        health_text = self.font_medium.render(f"❤️ {self.health}", True, COLOR_HEALTH)
        screen.blit(health_text, (self.panel_x + 160, y_offset))
        
        # 波次和分数
        y_offset += 32
        total_waves = len(level_config['waves'])
        wave_text = self.font_small.render(f"波次: {self.wave + 1}/{total_waves}", True, COLOR_WAVE)
        screen.blit(wave_text, (self.panel_x + 20, y_offset))
        score_text = self.font_small.render(f"分数: {self.score}", True, COLOR_TEXT)
        screen.blit(score_text, (self.panel_x + 150, y_offset))
    
    def _draw_tower_selection(self, screen):
        """绘制防御塔选择区"""
        # 分隔线
        pygame.draw.line(screen, (60, 70, 90),
                        (self.panel_x + 20, 130),
                        (self.panel_x + self.panel_width - 20, 130), 1)

        # 绘制防御塔按钮
        for button in self.tower_buttons:
            can_afford = self.money >= button.cost
            button.draw(screen, can_afford)
    
    def _draw_controls(self, screen):
        """绘制控制按钮"""
        # 分隔线
        pygame.draw.line(screen, (60, 70, 90), 
                        (self.panel_x + 20, 518), 
                        (self.panel_x + self.panel_width - 20, 518), 1)
        
        self.start_wave_button.draw(screen)
        
        if self.selected_tower:
            self.upgrade_button.draw(screen)
            self.sell_button.draw(screen)
    
    def _draw_tower_info(self, screen):
        """绘制选中防御塔的信息"""
        if not self.selected_tower:
            return
        
        info = self.selected_tower.get_info()
        
        # 信息背景
        info_y = 640
        info_rect = pygame.Rect(self.panel_x + 10, info_y, self.panel_width - 20, 70)
        pygame.draw.rect(screen, (35, 40, 55), info_rect, border_radius=8)
        pygame.draw.rect(screen, (60, 70, 90), info_rect, 1, border_radius=8)
        
        # 名称和等级
        name_text = self.font_small.render(f"{info['name']} Lv.{info['level']}", True, COLOR_TEXT)
        screen.blit(name_text, (self.panel_x + 20, info_y + 5))
        
        # 属性
        stats_text = self.font_small.render(
            f"伤害:{info['damage']} 射程:{info['range']}", True, (180, 180, 180))
        screen.blit(stats_text, (self.panel_x + 20, info_y + 25))
        
        # 升级费用
        if info['upgrade_cost']:
            upgrade_text = self.font_small.render(f"升级费用: {info['upgrade_cost']}", True, COLOR_MONEY)
            screen.blit(upgrade_text, (self.panel_x + 20, info_y + 45))
        else:
            max_text = self.font_small.render("已满级", True, (100, 255, 100))
            screen.blit(max_text, (self.panel_x + 20, info_y + 45))
        
        # 出售价值
        sell_text = self.font_small.render(f"出售: {info['sell_value']}", True, (255, 150, 150))
        screen.blit(sell_text, (self.panel_x + 160, info_y + 45))
    
    def _draw_tips(self, screen):
        """绘制底部操作提示"""
        tips = [
            "左键: 放置/选中  右键: 取消",
            "数字键1-5: 选塔  空格: 暂停",
            "敌人受击4次会激怒加速!"
        ]
        y_start = 640
        for i, tip in enumerate(tips):
            tip_text = self.font_small.render(tip, True, (100, 110, 130))
            screen.blit(tip_text, (self.panel_x + 20, y_start + i * 22))
    
    def _draw_messages(self, screen):
        """绘制消息提示"""
        current_time = pygame.time.get_ticks()
        y_offset = SCREEN_HEIGHT - 30
        
        for msg in self.messages[:]:
            if current_time - msg['time'] > 3000:  # 3秒后消失
                self.messages.remove(msg)
                continue
            
            alpha = max(0, 255 - (current_time - msg['time']) // 12)
            text_surface = self.font_small.render(msg['text'], True, msg['color'])
            text_surface.set_alpha(alpha)
            screen.blit(text_surface, (self.panel_x + 20, y_offset))
            y_offset -= 25
    
    def add_message(self, text, color=COLOR_TEXT):
        """添加消息"""
        self.messages.append({
            'text': text,
            'color': color,
            'time': pygame.time.get_ticks()
        })
    
    def handle_click(self, mouse_pos, mouse_pressed):
        """处理点击事件"""
        # 检查防御塔按钮点击
        for button in self.tower_buttons:
            if button.hovered and mouse_pressed[0]:
                if self.money >= button.cost:
                    self.selected_tower_type = button.tower_type
                    self.selected_tower = None
                    # 更新按钮选中状态
                    for btn in self.tower_buttons:
                        btn.selected = (btn.tower_type == button.tower_type)
                    return 'select_tower', button.tower_type
                else:
                    self.add_message("金币不足!", (255, 100, 100))
                    return None, None
        
        # 检查开始波次按钮
        if self.start_wave_button.is_clicked(mouse_pos, mouse_pressed):
            return 'start_wave', None
        
        # 检查升级按钮
        if self.selected_tower and self.upgrade_button.is_clicked(mouse_pos, mouse_pressed):
            return 'upgrade_tower', self.selected_tower
        
        # 检查出售按钮
        if self.selected_tower and self.sell_button.is_clicked(mouse_pos, mouse_pressed):
            return 'sell_tower', self.selected_tower
        
        return None, None
    
    def select_tower(self, tower):
        """选中防御塔"""
        self.selected_tower = tower
        self.selected_tower_type = None
        for btn in self.tower_buttons:
            btn.selected = False
    
    def deselect_all(self):
        """取消所有选择"""
        self.selected_tower_type = None
        self.selected_tower = None
        for btn in self.tower_buttons:
            btn.selected = False
    
    def draw_tower_preview(self, screen, grid_x, grid_y, valid):
        """绘制防御塔放置预览"""
        if not self.selected_tower_type:
            return
        
        x = grid_x * GRID_SIZE + GRID_SIZE // 2
        y = grid_y * GRID_SIZE + GRID_SIZE // 2
        
        config = TOWER_TYPES[self.selected_tower_type]
        color = config['color'] if valid else (255, 50, 50)
        
        # 绘制范围预览
        range_surface = pygame.Surface((config['range'] * 2, config['range'] * 2), pygame.SRCALPHA)
        range_alpha = 80 if valid else 40
        pygame.draw.circle(range_surface, (*color, range_alpha), 
                          (config['range'], config['range']), config['range'])
        pygame.draw.circle(range_surface, (*color, range_alpha + 60), 
                          (config['range'], config['range']), config['range'], 2)
        screen.blit(range_surface, (int(x - config['range']), int(y - config['range'])))
        
        # 绘制防御塔预览
        base_size = GRID_SIZE // 2 - 6
        pygame.draw.circle(screen, (color[0] // 2, color[1] // 2, color[2] // 2), (int(x), int(y)), base_size)
        pygame.draw.circle(screen, (*color, 180), (int(x), int(y)), base_size - 2)
        
        # 绘制符号
        symbol_font = pygame.font.SysFont('simhei', 20)
        symbol_text = symbol_font.render(config['symbol'], True, COLOR_TEXT)
        symbol_rect = symbol_text.get_rect(center=(int(x), int(y)))
        screen.blit(symbol_text, symbol_rect)


class MenuScreen:
    """菜单界面"""
    
    def __init__(self):
        self.font_title = pygame.font.SysFont('simhei', 64)
        self.font_subtitle = pygame.font.SysFont('simhei', 28)
        self.font_button = pygame.font.SysFont('simhei', 32)
        self.font_level = pygame.font.SysFont('simhei', 20)
        
        # 动画
        self.anim_time = 0
        
        # 按钮
        self.start_button = Button(
            SCREEN_WIDTH // 2 - 150, 250, 300, 50,
            "开始游戏 (第1关)", (50, 120, 200), (70, 150, 255), font_size=24
        )
        
        # 关卡选择按钮（紧凑布局）
        self.level_buttons = []
        for i, (level_id, level_config) in enumerate(LEVELS.items()):
            btn = Button(
                SCREEN_WIDTH // 2 - 150, 310 + i * 50, 300, 42,
                f"第{level_id}关: {level_config['name']}", 
                (60, 100, 160), (80, 140, 200), font_size=18
            )
            self.level_buttons.append((level_id, btn))
        
        self.help_button = Button(
            SCREEN_WIDTH // 2 - 150, 620, 145, 45,
            "游戏说明", (80, 150, 80), (100, 200, 100), font_size=20
        )
        
        self.quit_button = Button(
            SCREEN_WIDTH // 2 + 5, 620, 145, 45,
            "退出游戏", (200, 80, 80), (255, 100, 100), font_size=20
        )
        
        self.show_help = False
    
    def update(self, mouse_pos):
        """更新菜单状态"""
        self.anim_time += 0.016
        self.start_button.update(mouse_pos)
        for _, btn in self.level_buttons:
            btn.update(mouse_pos)
        self.help_button.update(mouse_pos)
        self.quit_button.update(mouse_pos)
    
    def draw(self, screen):
        """绘制菜单"""
        # 动态背景
        screen.fill(COLOR_BACKGROUND)
        
        # 绘制动态网格装饰
        import math
        for i in range(0, SCREEN_WIDTH, GRID_SIZE):
            offset = int(3 * math.sin(self.anim_time * 2 + i * 0.01))
            alpha = int(25 + 15 * math.sin(self.anim_time + i * 0.02))
            pygame.draw.line(screen, (alpha, alpha + 10, alpha + 20), 
                           (i, 0), (i, SCREEN_HEIGHT))
        for i in range(0, SCREEN_HEIGHT, GRID_SIZE):
            offset = int(3 * math.sin(self.anim_time * 2 + i * 0.01))
            alpha = int(25 + 15 * math.sin(self.anim_time + i * 0.02))
            pygame.draw.line(screen, (alpha, alpha + 10, alpha + 20), 
                           (0, i), (SCREEN_WIDTH, i))
        
        # 背景粒子效果
        for i in range(20):
            x = (i * 67 + int(self.anim_time * 30)) % SCREEN_WIDTH
            y = (i * 53 + int(self.anim_time * 20)) % SCREEN_HEIGHT
            alpha = int(30 + 20 * math.sin(self.anim_time * 3 + i))
            pygame.draw.circle(screen, (alpha, alpha + 30, alpha + 60), (x, y), 2)
        
        # 标题发光效果
        glow_intensity = int(10 * math.sin(self.anim_time * 3))
        title_color = (
            min(255, 100 + glow_intensity),
            min(255, 200 + glow_intensity),
            min(255, 255)
        )
        title_text = self.font_title.render("网络守护者", True, title_color)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 120))
        screen.blit(title_text, title_rect)
        
        # 副标题
        subtitle_text = self.font_subtitle.render("Network Defender", True, (150, 180, 220))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 180))
        screen.blit(subtitle_text, subtitle_rect)
        
        # 装饰线
        pygame.draw.line(screen, COLOR_UI_BORDER, 
                        (SCREEN_WIDTH // 2 - 200, 210), 
                        (SCREEN_WIDTH // 2 + 200, 210), 2)
        
        if self.show_help:
            self._draw_help(screen)
        else:
            # 绘制按钮
            self.start_button.draw(screen)
            
            # 绘制关卡选择按钮
            for level_id, btn in self.level_buttons:
                btn.draw(screen)
                # 在按钮右侧绘制关卡描述
                level_config = LEVELS[level_id]
                desc_text = self.font_level.render(level_config['description'], True, (150, 170, 200))
                screen.blit(desc_text, (btn.rect.right + 15, btn.rect.centery - desc_text.get_height() // 2))
            
            self.help_button.draw(screen)
            self.quit_button.draw(screen)
        
        # 版本信息
        version_text = self.font_subtitle.render("v2.0 - Python网络自动化课设", True, (100, 120, 150))
        version_rect = version_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        screen.blit(version_text, version_rect)
    
    def _draw_help(self, screen):
        """绘制帮助信息"""
        # 帮助背景
        help_rect = pygame.Rect(80, 60, SCREEN_WIDTH - 160, SCREEN_HEIGHT - 120)
        pygame.draw.rect(screen, (30, 40, 60), help_rect, border_radius=15)
        pygame.draw.rect(screen, COLOR_UI_BORDER, help_rect, 3, border_radius=15)
        
        # 帮助标题
        title_text = self.font_subtitle.render("游戏说明", True, COLOR_TEXT_HIGHLIGHT)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 75))
        
        # 帮助内容（分两列显示）
        font_help = pygame.font.SysFont('simhei', 18)
        
        left_texts = [
            ("操作说明:", True),
            ("鼠标左键: 选择并放置防御塔", False),
            ("鼠标右键: 取消选择", False),
            ("数字键 1-5: 快速选择防御塔", False),
            ("空格键: 暂停/继续游戏", False),
            ("ESC键: 返回菜单", False),
            ("", False),
            ("防御塔类型:", True),
            ("防火墙: 基础防御，平衡属性", False),
            ("杀毒软件: 高伤害，攻击较慢", False),
            ("加密节点: 减速敌人", False),
            ("入侵检测: 超远射程，穿透攻击", False),
            ("蜜罐陷阱: 范围爆炸伤害", False),
        ]
        
        right_texts = [
            ("敌人类型:", True),
            ("病毒: 普通敌人，数量多", False),
            ("蠕虫: 速度快但血量低", False),
            ("木马: 血量高，速度较慢", False),
            ("勒索软件: 高血量，需集中火力", False),
            ("DDoS: Boss级，超厚血量", False),
            ("黑客: 会闪避部分攻击", False),
            ("", False),
            ("游戏提示:", True),
            ("击败敌人获得金币奖励", False),
            ("波次间可自由布置防御塔", False),
            ("合理搭配不同防御塔", False),
            ("优先升级高性价比防御塔", False),
        ]
        
        y_offset = 110
        for text, is_title in left_texts:
            if text:
                color = COLOR_TEXT_HIGHLIGHT if is_title else COLOR_TEXT
                text_surface = font_help.render(text, True, color)
                screen.blit(text_surface, (110, y_offset))
            y_offset += 26
        
        y_offset = 110
        for text, is_title in right_texts:
            if text:
                color = COLOR_TEXT_HIGHLIGHT if is_title else COLOR_TEXT
                text_surface = font_help.render(text, True, color)
                screen.blit(text_surface, (SCREEN_WIDTH // 2 + 20, y_offset))
            y_offset += 26
        
        # 底部提示
        hint_text = font_help.render("点击任意处返回菜单", True, (150, 170, 200))
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
        screen.blit(hint_text, hint_rect)
    
    def handle_click(self, mouse_pos, mouse_pressed):
        """处理点击事件"""
        if self.show_help:
            if mouse_pressed[0]:
                self.show_help = False
            return None
        
        if self.start_button.is_clicked(mouse_pos, mouse_pressed):
            return 'start'
        
        # 检查关卡按钮点击
        for level_id, btn in self.level_buttons:
            if btn.is_clicked(mouse_pos, mouse_pressed):
                return f'level_{level_id}'
        
        if self.help_button.is_clicked(mouse_pos, mouse_pressed):
            self.show_help = True
            return None
        if self.quit_button.is_clicked(mouse_pos, mouse_pressed):
            return 'quit'
        
        return None


class GameOverScreen:
    """游戏结束界面"""
    
    def __init__(self):
        self.font_title = pygame.font.SysFont('simhei', 56)
        self.font_score = pygame.font.SysFont('simhei', 32)
        self.font_button = pygame.font.SysFont('simhei', 28)
        self.font_stat = pygame.font.SysFont('simhei', 22)
        
        self.restart_button = Button(
            SCREEN_WIDTH // 2 - 150, 500, 300, 55,
            "重新开始", (50, 120, 200), (70, 150, 255), font_size=26
        )
        
        self.menu_button = Button(
            SCREEN_WIDTH // 2 - 150, 570, 300, 55,
            "返回菜单", (80, 150, 80), (100, 200, 100), font_size=26
        )
        
        self.victory = False
        self.score = 0
        self.wave = 0
        self.total_waves = 0
        
        # 动画
        self.anim_time = 0
        self.particles = []
    
    def update(self, mouse_pos):
        """更新结束界面状态"""
        self.anim_time += 0.016
        self.restart_button.update(mouse_pos)
        self.menu_button.update(mouse_pos)
        
        # 更新粒子
        import random
        if self.victory and random.random() < 0.3:
            self.particles.append({
                'x': random.randint(100, SCREEN_WIDTH - 100),
                'y': SCREEN_HEIGHT + 10,
                'vx': random.uniform(-1, 1),
                'vy': random.uniform(-3, -1),
                'life': random.uniform(1.5, 3.0),
                'color': random.choice([
                    (100, 255, 150), (255, 215, 0), (100, 200, 255),
                    (255, 100, 255), (255, 150, 50)
                ]),
                'size': random.randint(2, 5)
            })
        
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 0.016
            if p['life'] <= 0:
                self.particles.remove(p)
    
    def draw(self, screen):
        """绘制结束界面"""
        import math
        
        # 半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # 绘制粒子
        for p in self.particles:
            alpha = min(255, int(p['life'] * 200))
            particle_surface = pygame.Surface((p['size'] * 2, p['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (*p['color'], alpha), 
                             (p['size'], p['size']), p['size'])
            screen.blit(particle_surface, (int(p['x'] - p['size']), int(p['y'] - p['size'])))
        
        # 中央面板背景
        panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, 100, 500, 540)
        panel_surface = pygame.Surface((500, 540), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (20, 25, 40, 220), (0, 0, 500, 540), border_radius=20)
        screen.blit(panel_surface, (SCREEN_WIDTH // 2 - 250, 100))
        
        # 面板边框发光
        if self.victory:
            glow_color = (100, 255, 150, int(60 + 30 * math.sin(self.anim_time * 3)))
        else:
            glow_color = (255, 80, 80, int(60 + 30 * math.sin(self.anim_time * 3)))
        glow_surface = pygame.Surface((504, 544), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, glow_color, (0, 0, 504, 544), 3, border_radius=20)
        screen.blit(glow_surface, (SCREEN_WIDTH // 2 - 252, 98))
        
        # 标题（带脉冲效果）
        if self.victory:
            pulse = int(10 * math.sin(self.anim_time * 4))
            title_color = (
                min(255, 100 + pulse),
                min(255, 255),
                min(255, 150 + pulse)
            )
            title_text = self.font_title.render("胜 利 !", True, title_color)
            subtitle_text = self.font_score.render("你成功守护了网络安全!", True, (200, 230, 255))
        else:
            pulse = int(10 * math.sin(self.anim_time * 4))
            title_color = (255, min(255, 100 + pulse), min(255, 100 + pulse))
            title_text = self.font_title.render("游 戏 结 束", True, title_color)
            subtitle_text = self.font_score.render("网络已被攻破...", True, (200, 180, 180))
        
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 160))
        screen.blit(title_text, title_rect)
        
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 220))
        screen.blit(subtitle_text, subtitle_rect)
        
        # 分隔线
        pygame.draw.line(screen, (80, 100, 140), 
                        (SCREEN_WIDTH // 2 - 180, 260), 
                        (SCREEN_WIDTH // 2 + 180, 260), 1)
        
        # 统计数据
        total = self.total_waves if self.total_waves > 0 else 1
        
        # 分数（大号高亮）
        score_label = self.font_stat.render("最终分数", True, (150, 160, 180))
        screen.blit(score_label, (SCREEN_WIDTH // 2 - score_label.get_width() // 2, 280))
        
        score_pulse = int(20 * math.sin(self.anim_time * 2))
        score_color = (min(255, 255 + score_pulse), min(255, 215 + score_pulse), 0)
        score_text = self.font_title.render(f"{self.score}", True, score_color)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 330))
        screen.blit(score_text, score_rect)
        
        # 波次和评级
        wave_text = self.font_stat.render(f"通过波次: {self.wave}/{total}", True, COLOR_WAVE)
        wave_rect = wave_text.get_rect(center=(SCREEN_WIDTH // 2, 390))
        screen.blit(wave_text, wave_rect)
        
        # 评级系统
        if self.victory:
            if self.score >= 2000:
                rating = "S"
                rating_color = (255, 215, 0)
            elif self.score >= 1000:
                rating = "A"
                rating_color = (100, 255, 150)
            elif self.score >= 500:
                rating = "B"
                rating_color = (100, 200, 255)
            else:
                rating = "C"
                rating_color = (200, 200, 200)
            
            rating_label = self.font_stat.render("评级:", True, (150, 160, 180))
            screen.blit(rating_label, (SCREEN_WIDTH // 2 - 60, 430))
            
            font_rating = pygame.font.SysFont('simhei', 48)
            rating_text = font_rating.render(rating, True, rating_color)
            rating_rect = rating_text.get_rect(center=(SCREEN_WIDTH // 2 + 40, 445))
            screen.blit(rating_text, rating_rect)
            
            # 评级边框
            pygame.draw.circle(screen, rating_color, (SCREEN_WIDTH // 2 + 40, 445), 30, 2)
        
        # 按钮
        self.restart_button.draw(screen)
        self.menu_button.draw(screen)
    
    def handle_click(self, mouse_pos, mouse_pressed):
        """处理点击事件"""
        if self.restart_button.is_clicked(mouse_pos, mouse_pressed):
            return 'restart'
        elif self.menu_button.is_clicked(mouse_pos, mouse_pressed):
            return 'menu'
        return None
