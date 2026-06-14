"""
网络守护者 - 敌人系统
处理所有敌人类型、移动、攻击和状态
"""

import pygame
import math
import random
from config import *


class Enemy:
    """敌人基类"""
    
    def __init__(self, enemy_type, path):
        self.enemy_type = enemy_type
        self.path = path
        self.path_index = 0
        
        # 获取配置
        config = ENEMY_TYPES[enemy_type]
        self.name = config['name']
        self.max_health = config['health']
        self.health = self.max_health
        self.base_speed = config['speed']
        self.speed = self.base_speed
        self.reward = config['reward']
        self.color = config['color']
        self.size = config['size']
        self.description = config['description']
        
        # 位置
        if path:
            self.x, self.y = path[0]
        else:
            self.x, self.y = 0, 0
        
        # 状态
        self.alive = True
        self.reached_base = False
        
        # 减速效果
        self.slow_timer = 0
        self.slow_factor = 1.0
        
        # 动画
        self.pulse_animation = 0
        self.hit_flash = 0
        
        # 特殊属性
        self.dodge_chance = 0.1 if enemy_type == 'hacker' else 0
        
        # 激怒系统
        self.hit_count = 0              # 累计受击次数
        self.enrage_threshold = 4       # 触发激怒的受击次数（降低为4次）
        self.enraged = False            # 是否处于激怒状态
        self.enrage_speed_bonus = 0.5   # 激怒后速度提升50%
        self.enrage_defense = 0.3       # 激怒后减伤30%
        self.enrage_regen = 2           # 激怒后每秒恢复2点血量
        self.enrage_anim = 0            # 激怒动画计时器
        
        # 字体
        self.font = pygame.font.SysFont('simhei', 12)
    
    def take_damage(self, damage, effect_manager, drop_chance=1.0):
        """受到伤害，返回击杀奖励（未死亡返回0，概率不掉落金币）"""
        # 黑客有闪避几率
        if self.dodge_chance > 0 and random.random() < self.dodge_chance:
            effect_manager.add_damage_number(self.x, self.y - 20, "闪避!", (200, 200, 200))
            return 0
        
        # 激怒减伤
        actual_damage = damage
        if self.enraged:
            actual_damage = int(damage * (1 - self.enrage_defense))
            if actual_damage < 1:
                actual_damage = 1
        
        self.health -= actual_damage
        self.hit_flash = 0.2
        self.hit_count += 1
        
        # 检查是否触发激怒
        if not self.enraged and self.hit_count >= self.enrage_threshold:
            self._trigger_enrage(effect_manager)
        
        # 添加受击特效
        effect_manager.add_hit_effect(self.x, self.y, self.color)
        
        # 添加伤害数字（激怒时显示减伤后的值）
        if self.enraged and actual_damage < damage:
            effect_manager.add_damage_number(self.x, self.y - 10, actual_damage, (255, 150, 50))
        else:
            effect_manager.add_damage_number(self.x, self.y - 10, actual_damage, self.color)
        
        if self.health <= 0:
            self.alive = False
            self.health = 0
            # 添加死亡爆炸特效
            effect_manager.add_explosion(self.x, self.y, self.color)
            # 概率掉落金币
            if random.random() < drop_chance:
                return self.reward
            else:
                effect_manager.add_damage_number(self.x, self.y - 25, "无掉落", (150, 150, 150))
                return 0
        
        return 0
    
    def _trigger_enrage(self, effect_manager):
        """触发激怒状态"""
        self.enraged = True
        self.enrage_anim = 2.0  # 激怒动画持续2秒
        effect_manager.add_damage_number(self.x, self.y - 30, "激怒!", (255, 100, 0))
        effect_manager.add_explosion(self.x, self.y, (255, 150, 0), 10)
    
    def apply_slow(self, slow_factor, duration):
        """应用减速效果"""
        self.slow_factor = slow_factor
        self.slow_timer = duration
    
    def update(self, dt):
        """更新敌人状态"""
        if not self.alive:
            return
        
        # 更新动画
        self.pulse_animation += dt * 3
        if self.hit_flash > 0:
            self.hit_flash -= dt
        if self.enrage_anim > 0:
            self.enrage_anim -= dt
        
        # 更新减速效果
        if self.slow_timer > 0:
            self.slow_timer -= dt * 1000
            if self.slow_timer <= 0:
                self.slow_factor = 1.0
                self.slow_timer = 0
        
        # 激怒回血
        if self.enraged:
            self.health = min(self.max_health, self.health + self.enrage_regen * dt)
        
        # 计算当前速度（含激怒加速）
        speed_multiplier = 1.0
        if self.enraged:
            speed_multiplier += self.enrage_speed_bonus
        current_speed = self.base_speed * self.slow_factor * speed_multiplier * 60 * dt
        
        # 沿路径移动
        if self.path_index < len(self.path) - 1:
            target_x, target_y = self.path[self.path_index + 1]
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance <= current_speed:
                # 到达路径点
                self.x = target_x
                self.y = target_y
                self.path_index += 1
            else:
                # 向目标移动
                self.x += (dx / distance) * current_speed
                self.y += (dy / distance) * current_speed
        else:
            # 到达基地
            self.reached_base = True
            self.alive = False
    
    def draw(self, screen):
        """绘制敌人"""
        if not self.alive:
            return
        
        # 计算脉冲大小
        pulse = math.sin(self.pulse_animation) * 2
        current_size = self.size + pulse
        
        # 绘制激怒光环
        if self.enraged:
            enrage_pulse = math.sin(self.pulse_animation * 5) * 3
            enrage_surface = pygame.Surface((int(current_size * 2 + 16 + enrage_pulse), 
                                            int(current_size * 2 + 16 + enrage_pulse)), pygame.SRCALPHA)
            center = int(current_size + 8 + enrage_pulse / 2)
            # 外圈红色光环
            pygame.draw.circle(enrage_surface, (255, 100, 0, 80), (center, center), center)
            pygame.draw.circle(enrage_surface, (255, 150, 0, 120), (center, center), center, 2)
            screen.blit(enrage_surface, (int(self.x - center), int(self.y - center)))
        
        # 绘制减速效果
        if self.slow_timer > 0:
            slow_surface = pygame.Surface((current_size * 2 + 8, current_size * 2 + 8), pygame.SRCALPHA)
            pygame.draw.circle(slow_surface, (150, 255, 150, 128), 
                             (current_size + 4, current_size + 4), current_size + 4)
            screen.blit(slow_surface, (int(self.x - current_size - 4), int(self.y - current_size - 4)))
        
        # 绘制敌人主体
        color = self.color
        if self.enraged:
            # 激怒时颜色偏红橙
            enrage_flicker = int(30 * math.sin(self.pulse_animation * 8))
            color = (
                min(255, color[0] + 60 + enrage_flicker),
                max(0, color[1] - 30),
                max(0, color[2] - 30)
            )
        if self.hit_flash > 0:
            # 受击时变白
            flash_intensity = int(255 * (self.hit_flash / 0.2))
            color = (
                min(255, color[0] + flash_intensity),
                min(255, color[1] + flash_intensity),
                min(255, color[2] + flash_intensity)
            )
        
        # 外圈
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(current_size))
        # 内圈
        inner_color = (
            min(255, color[0] + 40),
            min(255, color[1] + 40),
            min(255, color[2] + 40)
        )
        pygame.draw.circle(screen, inner_color, (int(self.x), int(self.y)), int(current_size * 0.6))
        # 核心
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), int(current_size * 0.3))
        
        # 绘制血条背景
        bar_width = self.size * 2
        bar_height = 4
        bar_x = self.x - bar_width / 2
        bar_y = self.y - self.size - 10
        
        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        
        # 绘制血条
        health_ratio = self.health / self.max_health
        health_width = bar_width * health_ratio
        health_color = (100, 255, 100) if health_ratio > 0.5 else (255, 255, 100) if health_ratio > 0.25 else (255, 100, 100)
        
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
        
        # 绘制敌人名称（小字体）
        name_text = self.font.render(self.name, True, COLOR_TEXT)
        name_rect = name_text.get_rect(center=(int(self.x), int(bar_y - 8)))
        screen.blit(name_text, name_rect)
        
        # 绘制激怒状态标记
        if self.enraged:
            enrage_text = self.font.render("激怒", True, (255, 100, 0))
            enrage_rect = enrage_text.get_rect(center=(int(self.x), int(bar_y - 20)))
            screen.blit(enrage_text, enrage_rect)
    
    def get_position(self):
        """获取当前位置"""
        return (self.x, self.y)
    
    def get_distance_to_base(self):
        """获取到基地的距离"""
        if self.path_index < len(self.path) - 1:
            remaining_path = self.path[self.path_index:]
            total_distance = 0
            for i in range(len(remaining_path) - 1):
                dx = remaining_path[i + 1][0] - remaining_path[i][0]
                dy = remaining_path[i + 1][1] - remaining_path[i][1]
                total_distance += math.sqrt(dx * dx + dy * dy)
            
            # 加上当前位置到下一个路径点的距离
            if len(remaining_path) > 1:
                dx = remaining_path[1][0] - self.x
                dy = remaining_path[1][1] - self.y
                total_distance += math.sqrt(dx * dx + dy * dy)
            
            return total_distance
        return 0


class WaveManager:
    """波次管理器"""
    
    def __init__(self):
        self.current_wave = 0
        self.wave_in_progress = False
        self.wave_completed = False
        self.enemies_to_spawn = []
        self.spawn_timer = 0
        self.spawn_interval = 1000
        self.wave_reward = 0
        self.enemies = []
        self.path = []
        self.waves = []  # 动态波次配置
        
        # 波次间隔
        self.wave_cooldown = 3000  # 波次之间的冷却时间
        self.cooldown_timer = 0
    
    def set_path(self, path):
        """设置敌人路径"""
        self.path = path
    
    def start_wave(self):
        """开始新波次"""
        waves_config = self.waves if self.waves else []
        if self.current_wave >= len(waves_config):
            return False
        
        wave_config = waves_config[self.current_wave]
        self.enemies_to_spawn = []
        
        # 生成敌人列表
        for enemy_type, count in wave_config['enemies']:
            for _ in range(count):
                self.enemies_to_spawn.append(enemy_type)
        
        self.spawn_interval = wave_config['interval']
        self.wave_reward = wave_config['reward']
        self.spawn_timer = 0
        self.wave_in_progress = True
        self.wave_completed = False
        
        return True
    
    def update(self, dt):
        """更新波次状态"""
        # 更新冷却时间
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt * 1000
            if self.cooldown_timer < 0:
                self.cooldown_timer = 0
        
        # 生成敌人
        if self.wave_in_progress and self.enemies_to_spawn:
            self.spawn_timer -= dt * 1000
            
            if self.spawn_timer <= 0:
                # 生成下一个敌人
                enemy_type = self.enemies_to_spawn.pop(0)
                enemy = Enemy(enemy_type, self.path)
                self.enemies.append(enemy)
                self.spawn_timer = self.spawn_interval
        
        # 更新所有敌人
        for enemy in self.enemies[:]:
            enemy.update(dt)
            
            if not enemy.alive:
                if enemy.reached_base:
                    # 敌人到达基地，返回伤害信息
                    pass
                self.enemies.remove(enemy)
        
        # 检查波次是否完成
        if self.wave_in_progress and not self.enemies_to_spawn and not self.enemies:
            self.wave_in_progress = False
            self.wave_completed = True
            self.current_wave += 1
            self.cooldown_timer = self.wave_cooldown
    
    def get_base_damage(self):
        """获取对基地造成的伤害"""
        damage = 0
        for enemy in self.enemies[:]:
            if enemy.reached_base:
                damage += 1
                self.enemies.remove(enemy)
        return damage
    
    def get_rewards(self):
        """获取击杀奖励"""
        rewards = 0
        for enemy in self.enemies[:]:
            if not enemy.alive and not enemy.reached_base:
                rewards += enemy.reward
        return rewards
    
    def is_wave_ready(self):
        """检查是否可以开始下一波"""
        waves_config = self.waves if self.waves else []
        return (not self.wave_in_progress and 
                self.cooldown_timer <= 0 and 
                self.current_wave < len(waves_config))
    
    def is_game_complete(self):
        """检查是否完成所有波次"""
        waves_config = self.waves if self.waves else []
        return (self.current_wave >= len(waves_config) and 
                not self.wave_in_progress and 
                not self.enemies)
    
    def draw(self, screen):
        """绘制所有敌人"""
        for enemy in self.enemies:
            enemy.draw(screen)
    
    def clear(self):
        """清除所有敌人"""
        self.enemies.clear()
        self.enemies_to_spawn.clear()
        self.wave_in_progress = False
        self.wave_completed = False
        self.spawn_timer = 0
        self.cooldown_timer = 0
