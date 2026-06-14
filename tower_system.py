"""
网络守护者 - 防御塔系统
处理所有防御塔的类型、攻击、升级逻辑
"""

import pygame
import math
import time
from config import *


class Tower:
    """防御塔基类"""
    
    def __init__(self, grid_x, grid_y, tower_type):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.x = grid_x * GRID_SIZE + GRID_SIZE // 2
        self.y = grid_y * GRID_SIZE + GRID_SIZE // 2
        self.tower_type = tower_type
        
        # 获取配置
        config = TOWER_TYPES[tower_type]
        self.name = config['name']
        self.damage = config['damage']
        self.range = config['range']
        self.fire_rate = config['fire_rate']
        self.color = config['color']
        self.symbol = config['symbol']
        self.upgrade_cost = config['upgrade_cost']
        self.max_level = config['max_level']
        
        # 特殊属性
        self.slow_effect = config.get('slow_effect', 0)
        self.slow_duration = config.get('slow_duration', 0)
        self.pierce = config.get('pierce', False)
        self.aoe_range = config.get('aoe_range', 0)
        
        # 状态
        self.level = 1
        self.last_fire_time = 0
        self.target = None
        self.angle = 0
        
        # 动画
        self.shoot_animation = 0
        self.upgrade_animation = 0
        
        # 字体
        self.font = pygame.font.SysFont('simhei', 16)
        self.symbol_font = pygame.font.SysFont('simhei', 20)
    
    def can_fire(self):
        """检查是否可以射击"""
        current_time = time.time() * 1000
        return current_time - self.last_fire_time >= self.fire_rate
    
    def fire(self):
        """射击"""
        self.last_fire_time = time.time() * 1000
        self.shoot_animation = 0.3  # 射击动画持续时间
    
    def find_target(self, enemies):
        """寻找目标 - 优先攻击血量最低的敌人"""
        target_enemy = None
        lowest_health = float('inf')
        
        for enemy in enemies:
            if not enemy.alive:
                continue
            
            distance = math.sqrt((enemy.x - self.x) ** 2 + (enemy.y - self.y) ** 2)
            if distance <= self.range:
                # 优先选择血量最低的敌人
                if enemy.health < lowest_health:
                    lowest_health = enemy.health
                    target_enemy = enemy
        
        self.target = target_enemy
        
        if self.target:
            # 计算朝向角度
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            self.angle = math.atan2(dy, dx)
        
        return target_enemy
    
    def upgrade(self):
        """升级防御塔"""
        if self.level < self.max_level:
            self.level += 1
            self.damage = int(self.damage * 1.5)
            self.range = int(self.range * 1.1)
            self.fire_rate = int(self.fire_rate * 0.9)
            self.upgrade_cost = int(self.upgrade_cost * 1.5)
            self.upgrade_animation = 1.0
            return True
        return False
    
    def get_sell_value(self):
        """获取出售价值"""
        base_cost = TOWER_TYPES[self.tower_type]['cost']
        total_invested = base_cost
        
        # 计算升级投入
        upgrade_cost = TOWER_TYPES[self.tower_type]['upgrade_cost']
        for i in range(1, self.level):
            total_invested += int(upgrade_cost * (1.5 ** (i - 1)))
        
        return int(total_invested * 0.7)  # 70%返还
    
    def update(self, dt, enemies, projectiles, effect_manager):
        """更新防御塔状态"""
        # 更新动画
        if self.shoot_animation > 0:
            self.shoot_animation -= dt
        if self.upgrade_animation > 0:
            self.upgrade_animation -= dt
        
        # 寻找目标
        target = self.find_target(enemies)
        
        if target and self.can_fire():
            self.fire()
            # 创建投射物
            projectile = Projectile(
                self.x, self.y, target, 
                self.damage, self.color, self.tower_type
            )
            projectiles.append(projectile)
            
            # 添加射击特效
            effect_manager.add_tower_shot(self.x, self.y, target.x, target.y, self.color)
    
    def draw(self, screen):
        """绘制防御塔"""
        # 绘制范围圈（如果选中）
        # self._draw_range(screen)
        
        # 绘制底座
        base_size = GRID_SIZE // 2 - 6
        pygame.draw.circle(screen, (40, 50, 70), (int(self.x), int(self.y)), base_size)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), base_size - 2)
        
        # 绘制射击动画
        if self.shoot_animation > 0:
            flash_size = base_size + int(8 * self.shoot_animation / 0.3)
            flash_alpha = int(255 * self.shoot_animation / 0.3)
            flash_surface = pygame.Surface((flash_size * 2, flash_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(flash_surface, (*self.color, flash_alpha), 
                             (flash_size, flash_size), flash_size)
            screen.blit(flash_surface, (int(self.x - flash_size), int(self.y - flash_size)))
        
        # 绘制升级动画
        if self.upgrade_animation > 0:
            upgrade_size = base_size + int(12 * self.upgrade_animation)
            upgrade_alpha = int(200 * self.upgrade_animation)
            upgrade_surface = pygame.Surface((upgrade_size * 2, upgrade_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(upgrade_surface, (255, 255, 100, upgrade_alpha), 
                             (upgrade_size, upgrade_size), upgrade_size, 3)
            screen.blit(upgrade_surface, (int(self.x - upgrade_size), int(self.y - upgrade_size)))
        
        # 绘制炮管/方向
        barrel_length = base_size + 8
        end_x = self.x + math.cos(self.angle) * barrel_length
        end_y = self.y + math.sin(self.angle) * barrel_length
        pygame.draw.line(screen, (60, 70, 90), (self.x, self.y), (end_x, end_y), 6)
        pygame.draw.line(screen, self.color, (self.x, self.y), (end_x, end_y), 4)
        
        # 绘制符号
        symbol_text = self.symbol_font.render(self.symbol, True, COLOR_TEXT)
        symbol_rect = symbol_text.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(symbol_text, symbol_rect)
        
        # 绘制等级
        if self.level > 1:
            level_text = self.font.render(f'Lv.{self.level}', True, (255, 255, 100))
            screen.blit(level_text, (int(self.x - 15), int(self.y - base_size - 15)))
    
    def draw_range(self, screen):
        """绘制攻击范围"""
        range_surface = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
        pygame.draw.circle(range_surface, (*self.color, 40), (self.range, self.range), self.range)
        pygame.draw.circle(range_surface, (*self.color, 100), (self.range, self.range), self.range, 2)
        screen.blit(range_surface, (int(self.x - self.range), int(self.y - self.range)))
    
    def get_info(self):
        """获取防御塔信息"""
        return {
            'name': self.name,
            'level': self.level,
            'damage': self.damage,
            'range': self.range,
            'fire_rate': self.fire_rate,
            'upgrade_cost': self.upgrade_cost if self.level < self.max_level else None,
            'sell_value': self.get_sell_value()
        }


class Projectile:
    """投射物类"""
    
    def __init__(self, x, y, target, damage, color, tower_type):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.color = color
        self.tower_type = tower_type
        self.speed = 400
        self.alive = True
        self.radius = 4
        
        # 计算方向
        dx = target.x - x
        dy = target.y - y
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 0:
            self.vx = (dx / distance) * self.speed
            self.vy = (dy / distance) * self.speed
        else:
            self.vx = 0
            self.vy = 0
    
    def update(self, dt, enemies, effect_manager, drop_chance=1.0):
        """更新投射物位置"""
        if not self.alive:
            return 0
        
        # 如果目标已死亡，继续沿原方向飞行
        if self.target and self.target.alive:
            # 重新计算方向（追踪）
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            distance = math.sqrt(dx * dx + dy * dy)
            if distance > 0:
                self.vx = (dx / distance) * self.speed
                self.vy = (dy / distance) * self.speed
        
        # 移动
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # 检查是否击中目标
        if self.target and self.target.alive:
            distance = math.sqrt((self.x - self.target.x) ** 2 + (self.y - self.target.y) ** 2)
            if distance < self.target.size + self.radius:
                reward = self.hit(self.target, enemies, effect_manager, drop_chance)
                return reward
        
        # 检查是否超出边界
        if (self.x < 0 or self.x > GAME_AREA_WIDTH or 
            self.y < 0 or self.y > GAME_AREA_HEIGHT):
            self.alive = False
        
        return 0
    
    def hit(self, enemy, enemies, effect_manager, drop_chance=1.0):
        """击中敌人，返回击杀奖励"""
        self.alive = False
        total_reward = 0
        
        # 获取防御塔配置
        tower_config = TOWER_TYPES[self.tower_type]
        
        # 处理蜜罐的范围伤害
        if self.tower_type == 'honeypot' and tower_config.get('aoe_range', 0) > 0:
            aoe_range = tower_config['aoe_range']
            # 对范围内所有敌人造成伤害
            for other_enemy in enemies:
                if not other_enemy.alive:
                    continue
                distance = math.sqrt((self.x - other_enemy.x) ** 2 + (self.y - other_enemy.y) ** 2)
                if distance <= aoe_range:
                    reward = other_enemy.take_damage(self.damage, effect_manager, drop_chance)
                    total_reward += reward
            
            # 添加爆炸特效
            effect_manager.add_explosion(self.x, self.y, self.color, 20)
        else:
            # 普通伤害
            reward = enemy.take_damage(self.damage, effect_manager, drop_chance)
            total_reward += reward
            
            # 处理减速效果
            if tower_config.get('slow_effect', 0) > 0:
                enemy.apply_slow(tower_config['slow_effect'], tower_config['slow_duration'])
                effect_manager.add_slow_effect(enemy.x, enemy.y)
            
            # 处理穿透效果
            if tower_config.get('pierce', False):
                # 穿透攻击会继续飞行一段距离
                self.alive = True
                self.damage = int(self.damage * 0.7)  # 穿透后伤害降低
                if self.damage < 5:
                    self.alive = False
        
        return total_reward
    
    def draw(self, screen):
        """绘制投射物"""
        if not self.alive:
            return
        
        # 绘制光晕
        glow_surface = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*self.color, 100), 
                          (self.radius * 2, self.radius * 2), self.radius * 2)
        screen.blit(glow_surface, (int(self.x - self.radius * 2), int(self.y - self.radius * 2)))
        
        # 绘制核心
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, COLOR_TEXT, (int(self.x), int(self.y)), self.radius - 1)


class TowerManager:
    """防御塔管理器"""
    
    def __init__(self):
        self.towers = []
        self.projectiles = []
    
    def add_tower(self, grid_x, grid_y, tower_type):
        """添加防御塔"""
        tower = Tower(grid_x, grid_y, tower_type)
        self.towers.append(tower)
        return tower
    
    def remove_tower(self, grid_x, grid_y):
        """移除防御塔"""
        for tower in self.towers:
            if tower.grid_x == grid_x and tower.grid_y == grid_y:
                self.towers.remove(tower)
                return True
        return False
    
    def get_tower_at(self, grid_x, grid_y):
        """获取指定位置的防御塔"""
        for tower in self.towers:
            if tower.grid_x == grid_x and tower.grid_y == grid_y:
                return tower
        return None
    
    def update(self, dt, enemies, effect_manager, drop_chance=1.0):
        """更新所有防御塔和投射物，返回击杀奖励"""
        total_rewards = 0
        
        # 更新防御塔
        for tower in self.towers:
            tower.update(dt, enemies, self.projectiles, effect_manager)
        
        # 更新投射物
        for projectile in self.projectiles[:]:
            reward = projectile.update(dt, enemies, effect_manager, drop_chance)
            total_rewards += (reward or 0)
            if not projectile.alive:
                self.projectiles.remove(projectile)
        
        return total_rewards
    
    def draw(self, screen):
        """绘制所有防御塔和投射物"""
        # 先绘制投射物
        for projectile in self.projectiles:
            projectile.draw(screen)
        
        # 再绘制防御塔
        for tower in self.towers:
            tower.draw(screen)
    
    def draw_ranges(self, screen, grid_x, grid_y):
        """绘制指定位置防御塔的范围"""
        tower = self.get_tower_at(grid_x, grid_y)
        if tower:
            tower.draw_range(screen)
    
    def clear(self):
        """清除所有防御塔和投射物"""
        self.towers.clear()
        self.projectiles.clear()
