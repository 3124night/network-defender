"""
网络守护者 - 游戏引擎
处理游戏主循环、状态管理和游戏逻辑
"""

import pygame
import sys
from config import *
from map_system import GameMap
from tower_system import TowerManager
from enemy_system import WaveManager
from effect_system import EffectManager
from ui_system import UI, MenuScreen, GameOverScreen
from sound_system import SoundSystem


class Game:
    """游戏主类"""
    
    def __init__(self):
        """初始化游戏"""
        pygame.init()
        pygame.display.set_caption(GAME_TITLE)
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        
        # 游戏状态
        self.game_state = 'menu'  # menu, playing, paused, game_over
        
        # 游戏数据
        self.money = INITIAL_MONEY
        self.health = INITIAL_HEALTH
        self.score = 0
        
        # 游戏系统
        self.game_map = None
        self.tower_manager = None
        self.wave_manager = None
        self.effect_manager = None
        self.ui = None
        
        # 界面
        self.menu_screen = MenuScreen()
        self.game_over_screen = GameOverScreen()
        
        # 音效系统
        self.sound = SoundSystem()
        
        # 鼠标状态
        self.mouse_pos = (0, 0)
        self.mouse_pressed = (False, False, False)
        self.mouse_grid_pos = (0, 0)
        
        # 暂停状态
        self.paused = False
    
    def init_game(self, level=1):
        """初始化游戏数据"""
        self.current_level = level
        level_config = LEVELS.get(level, LEVELS[1])
        
        self.money = level_config['initial_money']
        self.health = level_config['initial_health']
        self.score = 0
        self.gold_multiplier = level_config.get('gold_multiplier', 1.0)
        # 计算金币掉落概率：基础概率 - (关卡-1) * 每关降低值
        from config import COIN_DROP_CHANCE, COIN_DROP_BONUS
        self.drop_chance = max(0.2, COIN_DROP_CHANCE - (level - 1) * COIN_DROP_BONUS)
        
        # 初始化游戏系统
        self.game_map = GameMap(path_type=level_config['path_type'])
        self.tower_manager = TowerManager()
        self.wave_manager = WaveManager()
        self.wave_manager.set_path(self.game_map.path)
        self.wave_manager.waves = level_config['waves']
        self.effect_manager = EffectManager()
        self.ui = UI()
        
        self.paused = False
    
    def run(self):
        """游戏主循环"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # 转换为秒
            
            self._handle_events()
            self._update(dt)
            self._draw()
        
        pygame.quit()
        sys.exit()
    
    def _handle_events(self):
        """处理输入事件"""
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_pressed = pygame.mouse.get_pressed()
        self.mouse_grid_pos = self.game_map.world_to_grid(self.mouse_pos[0], self.mouse_pos[1]) if self.game_map else (0, 0)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_click(event.button)
    
    def _handle_keydown(self, key):
        """处理键盘按键"""
        if self.game_state == 'playing':
            # 数字键选择防御塔
            if pygame.K_1 <= key <= pygame.K_5:
                tower_index = key - pygame.K_1
                tower_types = list(TOWER_TYPES.keys())
                if tower_index < len(tower_types):
                    tower_type = tower_types[tower_index]
                    cost = TOWER_TYPES[tower_type]['cost']
                    if self.money >= cost:
                        self.ui.selected_tower_type = tower_type
                        self.ui.selected_tower = None
                        for btn in self.ui.tower_buttons:
                            btn.selected = (btn.tower_type == tower_type)
                    else:
                        self.ui.add_message("金币不足!", (255, 100, 100))
                    self.sound.play('error')
            
            # 空格键暂停
            elif key == pygame.K_SPACE:
                self.paused = not self.paused
                if self.paused:
                    self.ui.add_message("游戏暂停", (255, 255, 100))
                else:
                    self.ui.add_message("游戏继续", (100, 255, 100))
            
            # ESC键返回菜单
            elif key == pygame.K_ESCAPE:
                self.game_state = 'menu'
    
    def _handle_mouse_click(self, button):
        """处理鼠标点击"""
        if self.game_state == 'menu':
            result = self.menu_screen.handle_click(self.mouse_pos, (True, False, False))
            if result is None:
                return
            elif result == 'start':
                self.init_game(level=1)
                self.game_state = 'playing'
            elif result.startswith('level_'):
                level = int(result.split('_')[1])
                self.init_game(level=level)
                self.game_state = 'playing'
            elif result == 'quit':
                self.running = False
        
        elif self.game_state == 'playing':
            # 左键点击
            if button == 1:
                self._handle_left_click()
            
            # 右键点击 - 取消选择
            elif button == 3:
                self.ui.deselect_all()
        
        elif self.game_state == 'game_over':
            result = self.game_over_screen.handle_click(self.mouse_pos, (True, False, False))
            if result == 'restart':
                self.init_game()
                self.game_state = 'playing'
            elif result == 'menu':
                self.game_state = 'menu'
    
    def _handle_left_click(self):
        """处理左键点击"""
        # 检查是否点击在UI区域
        if self.mouse_pos[0] >= UI_PANEL_X:
            action, data = self.ui.handle_click(self.mouse_pos, (True, False, False))
            
            if action == 'select_tower':
                # 选择防御塔类型
                pass
            
            elif action == 'start_wave':
                # 开始下一波
                if self.wave_manager.is_wave_ready():
                    self.wave_manager.start_wave()
                    self.ui.add_message(f"第 {self.wave_manager.current_wave + 1} 波开始!", (255, 255, 100))
                    self.sound.play('wave_start')
            
            elif action == 'upgrade_tower':
                # 升级防御塔
                tower = data
                tower_info = tower.get_info()
                if tower_info['upgrade_cost'] and self.money >= tower_info['upgrade_cost']:
                    self.money -= tower_info['upgrade_cost']
                    tower.upgrade()
                    self.ui.add_message(f"{tower.name} 升级成功!", (100, 255, 100))
                else:
                    self.ui.add_message("金币不足!", (255, 100, 100))
            
            elif action == 'sell_tower':
                # 出售防御塔
                tower = data
                sell_value = tower.get_sell_value()
                self.money += sell_value
                self.tower_manager.remove_tower(tower.grid_x, tower.grid_y)
                self.game_map.remove_tower(tower.grid_x, tower.grid_y)
                self.ui.deselect_all()
                self.ui.add_message(f"出售获得 {sell_value} 金币", (255, 200, 100))
            
            return
        
        # 点击在游戏区域
        grid_x, grid_y = self.mouse_grid_pos
        
        # 检查是否点击了已有的防御塔
        existing_tower = self.tower_manager.get_tower_at(grid_x, grid_y)
        if existing_tower:
            self.ui.select_tower(existing_tower)
            return
        
        # 尝试放置防御塔
        if self.ui.selected_tower_type:
            if self.game_map.is_valid_tower_position(grid_x, grid_y):
                tower_config = TOWER_TYPES[self.ui.selected_tower_type]
                if self.money >= tower_config['cost']:
                    # 扣除金币
                    self.money -= tower_config['cost']
                    
                    # 放置防御塔
                    self.game_map.place_tower(grid_x, grid_y, self.ui.selected_tower_type)
                    self.tower_manager.add_tower(grid_x, grid_y, self.ui.selected_tower_type)
                    
                    self.ui.add_message(f"放置 {tower_config['name']}", (100, 255, 100))
                    self.sound.play('place')
                    
                    # 取消选择（可选：保持选择以便连续放置）
                    # self.ui.deselect_all()
                else:
                    self.ui.add_message("金币不足!", (255, 100, 100))
            else:
                self.ui.add_message("无法在此位置放置!", (255, 100, 100))
    
    def _update(self, dt):
        """更新游戏逻辑"""
        if self.game_state == 'menu':
            self.menu_screen.update(self.mouse_pos)
        
        elif self.game_state == 'playing' and not self.paused:
            # 更新波次管理器
            self.wave_manager.update(dt)
            
            # 获取敌人对基地的伤害
            base_damage = self.wave_manager.get_base_damage()
            if base_damage > 0:
                self.health -= base_damage
                self.ui.add_message(f"基地受到攻击! 生命值 -{base_damage}", (255, 100, 100))
                
                # 检查游戏结束
                if self.health <= 0:
                    self.health = 0
                    self.game_over_screen.victory = False
                    self.game_over_screen.score = self.score
                    self.game_over_screen.wave = self.wave_manager.current_wave
                    self.game_over_screen.total_waves = len(self.wave_manager.waves)
                    self.game_state = 'game_over'
                    self.sound.play('defeat')
                    return
            
            # 更新防御塔并获取击杀奖励（传入金币掉落概率）
            tower_rewards = self.tower_manager.update(dt, self.wave_manager.enemies, self.effect_manager, self.drop_chance)
            if tower_rewards > 0:
                adjusted = int(tower_rewards * self.gold_multiplier)
                self.money += adjusted
                self.score += adjusted
                if adjusted > 0:
                    self.ui.add_message(f"获得 {adjusted} 金币!", COLOR_MONEY)
                    self.sound.play('coin')
            
            # 波次完成奖励
            wave_rewards = self.wave_manager.get_rewards()
            if wave_rewards > 0:
                adjusted = int(wave_rewards * self.gold_multiplier)
                self.money += adjusted
                self.score += adjusted
            
            # 检查是否完成所有波次（等冷却结束后再判断，给玩家奖励时间）
            if (self.wave_manager.is_game_complete() and 
                self.wave_manager.cooldown_timer <= 0):
                # 检查是否还有下一关
                if self.current_level < max(LEVELS.keys()):
                    self.current_level += 1
                    self.ui.add_message(f"第 {self.current_level} 关解锁!", (100, 255, 100))
                    # 重新初始化游戏，进入下一关
                    self.init_game(level=self.current_level)
                    return
                else:
                    self.game_over_screen.victory = True
                    self.game_over_screen.score = self.score
                    self.game_over_screen.wave = self.wave_manager.current_wave
                    self.game_over_screen.total_waves = len(self.wave_manager.waves)
                    self.game_state = 'game_over'
                    self.sound.play('victory')
                    return
            
            # 更新地图动画
            self.game_map.update(dt)
            
            # 更新特效
            self.effect_manager.update(dt)
            
            # 更新UI
            wave_ready = self.wave_manager.is_wave_ready()
            self.ui.update(self.mouse_pos, self.money, self.health, 
                          self.wave_manager.current_wave, self.score, wave_ready,
                          self.current_level)
        
        elif self.game_state == 'game_over':
            self.game_over_screen.update(self.mouse_pos)
    
    def _draw(self):
        """绘制游戏画面"""
        if self.game_state == 'menu':
            self.menu_screen.draw(self.screen)
        
        elif self.game_state == 'playing':
            # 获取屏幕震动偏移
            shake_x, shake_y = self.effect_manager.get_shake_offset()
            
            # 创建游戏区域表面
            game_surface = pygame.Surface((GAME_AREA_WIDTH, GAME_AREA_HEIGHT))
            
            # 绘制地图
            self.game_map.draw(game_surface)
            
            # 绘制防御塔范围（如果选中了防御塔）
            if self.ui.selected_tower:
                tower = self.ui.selected_tower
                self.game_map.draw_range_circle(game_surface, tower.x, tower.y, 
                                               tower.range, tower.color)
            
            # 绘制防御塔放置预览
            if self.ui.selected_tower_type:
                grid_x, grid_y = self.mouse_grid_pos
                valid = self.game_map.is_valid_tower_position(grid_x, grid_y)
                self.ui.draw_tower_preview(game_surface, grid_x, grid_y, valid)
            
            # 绘制防御塔
            self.tower_manager.draw(game_surface)
            
            # 绘制敌人
            self.wave_manager.draw(game_surface)
            
            # 绘制特效
            self.effect_manager.draw(game_surface)
            
            # 将游戏区域绘制到主屏幕（应用震动效果）
            self.screen.blit(game_surface, (shake_x, shake_y))
            
            # 绘制UI
            self.ui.draw(self.screen)
            
            # 绘制暂停提示
            if self.paused:
                self._draw_pause_overlay()
        
        elif self.game_state == 'game_over':
            # 先绘制游戏画面作为背景
            if self.game_map:
                self.game_map.draw(self.screen)
                self.tower_manager.draw(self.screen)
                self.wave_manager.draw(self.screen)
            
            # 绘制结束界面
            self.game_over_screen.draw(self.screen)
        
        # 更新显示
        pygame.display.flip()
    
    def _draw_pause_overlay(self):
        """绘制暂停覆盖层"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        font = pygame.font.SysFont('simhei', 48)
        pause_text = font.render("游戏暂停", True, (255, 255, 255))
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(pause_text, text_rect)
        
        font_small = pygame.font.SysFont('simhei', 24)
        hint_text = font_small.render("按空格键继续", True, (200, 200, 200))
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(hint_text, hint_rect)


def main():
    """游戏入口函数"""
    game = Game()
    game.run()


if __name__ == '__main__':
    main()
