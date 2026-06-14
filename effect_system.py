"""
网络守护者 - 特效系统
处理粒子效果、爆炸动画、伤害数字等视觉特效
"""

import pygame
import random
import math
from config import *


class Particle:
    """粒子类，用于各种视觉效果"""
    
    def __init__(self, x, y, color, velocity, lifetime, size=3):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.alive = True
    
    def update(self, dt):
        """更新粒子状态"""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt * 1000
        
        # 粒子逐渐变小
        progress = 1 - (self.lifetime / self.max_lifetime)
        self.current_size = max(1, self.size * (1 - progress))
        
        if self.lifetime <= 0:
            self.alive = False
    
    def draw(self, screen):
        """绘制粒子"""
        if not self.alive:
            return
        
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        color_with_alpha = (*self.color[:3], alpha)
        
        # 创建带透明度的表面
        particle_surface = pygame.Surface((self.current_size * 2, self.current_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, color_with_alpha, 
                          (self.current_size, self.current_size), self.current_size)
        screen.blit(particle_surface, (int(self.x - self.current_size), int(self.y - self.current_size)))


class DamageNumber:
    """伤害数字显示"""
    
    def __init__(self, x, y, damage, color=COLOR_TEXT):
        self.x = x
        self.y = y
        self.damage = damage
        self.color = color
        self.lifetime = 800
        self.max_lifetime = 800
        self.vy = -80  # 向上飘动
        self.alive = True
        self.font = pygame.font.SysFont('simhei', 20)
    
    def update(self, dt):
        """更新伤害数字"""
        self.y += self.vy * dt
        self.lifetime -= dt * 1000
        
        if self.lifetime <= 0:
            self.alive = False
    
    def draw(self, screen):
        """绘制伤害数字"""
        if not self.alive:
            return
        
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        text = self.font.render(str(self.damage), True, self.color)
        text.set_alpha(alpha)
        screen.blit(text, (int(self.x - text.get_width() / 2), int(self.y)))


class EffectManager:
    """特效管理器，统一管理所有特效"""
    
    def __init__(self):
        self.particles = []
        self.damage_numbers = []
        self.screen_shake = 0
        self.shake_intensity = 0
    
    def add_explosion(self, x, y, color, count=EXPLOSION_PARTICLES):
        """添加爆炸效果"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 200)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.uniform(300, 800)
            size = random.randint(2, 6)
            
            # 颜色变化
            color_var = (
                min(255, max(0, color[0] + random.randint(-30, 30))),
                min(255, max(0, color[1] + random.randint(-30, 30))),
                min(255, max(0, color[2] + random.randint(-30, 30)))
            )
            
            self.particles.append(Particle(x, y, color_var, (vx, vy), lifetime, size))
        
        # 屏幕震动
        self.screen_shake = 0.2
        self.shake_intensity = 5
    
    def add_hit_effect(self, x, y, color):
        """添加受击效果"""
        for _ in range(HIT_PARTICLES):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(30, 100)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.uniform(200, 500)
            size = random.randint(2, 4)
            
            self.particles.append(Particle(x, y, color, (vx, vy), lifetime, size))
    
    def add_damage_number(self, x, y, damage, color=COLOR_TEXT):
        """添加伤害数字"""
        self.damage_numbers.append(DamageNumber(x, y, damage, color))
    
    def add_tower_shot(self, start_x, start_y, end_x, end_y, color):
        """添加塔射击轨迹效果"""
        # 在轨迹上添加粒子
        distance = math.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2)
        steps = int(distance / 10)
        
        for i in range(steps):
            t = i / steps
            x = start_x + (end_x - start_x) * t
            y = start_y + (end_y - start_y) * t
            
            vx = random.uniform(-20, 20)
            vy = random.uniform(-20, 20)
            lifetime = random.uniform(100, 300)
            size = random.randint(1, 3)
            
            self.particles.append(Particle(x, y, color, (vx, vy), lifetime, size))
    
    def add_slow_effect(self, x, y):
        """添加减速效果"""
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(20, 60)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.uniform(400, 700)
            size = random.randint(2, 5)
            
            self.particles.append(Particle(x, y, (150, 255, 150), (vx, vy), lifetime, size))
    
    def update(self, dt):
        """更新所有特效"""
        # 更新粒子
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.alive:
                self.particles.remove(particle)
        
        # 更新伤害数字
        for dmg_num in self.damage_numbers[:]:
            dmg_num.update(dt)
            if not dmg_num.alive:
                self.damage_numbers.remove(dmg_num)
        
        # 更新屏幕震动
        if self.screen_shake > 0:
            self.screen_shake -= dt
            if self.screen_shake < 0:
                self.screen_shake = 0
    
    def get_shake_offset(self):
        """获取屏幕震动偏移量"""
        if self.screen_shake > 0:
            return (
                random.uniform(-self.shake_intensity, self.shake_intensity),
                random.uniform(-self.shake_intensity, self.shake_intensity)
            )
        return (0, 0)
    
    def draw(self, screen):
        """绘制所有特效"""
        for particle in self.particles:
            particle.draw(screen)
        
        for dmg_num in self.damage_numbers:
            dmg_num.draw(screen)
    
    def clear(self):
        """清除所有特效"""
        self.particles.clear()
        self.damage_numbers.clear()
        self.screen_shake = 0
