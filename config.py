"""
网络守护者 - 游戏配置文件
包含所有游戏常量、颜色定义、防御塔和敌人属性配置
"""

import pygame

# ============== 窗口设置 ==============
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
GAME_TITLE = "网络守护者 - Network Defender"

# ============== 颜色定义 ==============
COLOR_BACKGROUND = (15, 20, 35)          # 深蓝黑色背景
COLOR_GRID = (30, 40, 60)                # 网格线颜色
COLOR_PATH = (60, 70, 90)                # 路径颜色
COLOR_UI_BG = (25, 30, 45)               # UI背景色
COLOR_UI_BORDER = (80, 120, 200)         # UI边框色
COLOR_TEXT = (220, 230, 240)             # 主文字颜色
COLOR_TEXT_HIGHLIGHT = (100, 200, 255)   # 高亮文字
COLOR_BUTTON = (50, 80, 140)             # 按钮颜色
COLOR_BUTTON_HOVER = (70, 110, 180)      # 按钮悬停颜色
COLOR_MONEY = (255, 215, 0)              # 金币颜色
COLOR_HEALTH = (255, 80, 80)             # 生命值颜色
COLOR_WAVE = (100, 255, 150)             # 波次颜色

# ============== 游戏区域 ==============
GAME_AREA_X = 0
GAME_AREA_Y = 0
GAME_AREA_WIDTH = 960
GAME_AREA_HEIGHT = 720

UI_PANEL_X = 960
UI_PANEL_WIDTH = 320
UI_PANEL_HEIGHT = 720

GRID_SIZE = 48
GRID_COLS = GAME_AREA_WIDTH // GRID_SIZE
GRID_ROWS = GAME_AREA_HEIGHT // GRID_SIZE

# ============== 防御塔配置 ==============
TOWER_TYPES = {
    'firewall': {
        'name': '防火墙',
        'description': '基础防御，中等射速和伤害',
        'cost': 50,
        'damage': 8,
        'range': 120,
        'fire_rate': 800,      # 毫秒
        'color': (80, 150, 255),
        'symbol': 'FW',
        'upgrade_cost': 40,
        'max_level': 3
    },
    'antivirus': {
        'name': '杀毒软件',
        'description': '高伤害，攻击速度较慢',
        'cost': 100,
        'damage': 22,
        'range': 140,
        'fire_rate': 1500,
        'color': (255, 100, 100),
        'symbol': 'AV',
        'upgrade_cost': 80,
        'max_level': 3
    },
    'encryptor': {
        'name': '加密节点',
        'description': '减速敌人，低伤害',
        'cost': 80,
        'damage': 3,
        'range': 100,
        'fire_rate': 500,
        'color': (150, 255, 150),
        'symbol': 'EN',
        'slow_effect': 0.5,    # 减速50%
        'slow_duration': 2000, # 减速持续2秒
        'upgrade_cost': 60,
        'max_level': 3
    },
    'ids': {
        'name': '入侵检测',
        'description': '超远射程，可以穿透攻击',
        'cost': 150,
        'damage': 14,
        'range': 200,
        'fire_rate': 1200,
        'color': (255, 200, 80),
        'symbol': 'ID',
        'pierce': True,
        'upgrade_cost': 120,
        'max_level': 3
    },
    'honeypot': {
        'name': '蜜罐陷阱',
        'description': '吸引敌人并造成范围爆炸',
        'cost': 120,
        'damage': 35,
        'range': 90,
        'fire_rate': 2000,
        'color': (200, 100, 255),
        'symbol': 'HP',
        'aoe_range': 80,
        'upgrade_cost': 100,
        'max_level': 3
    }
}

# ============== 敌人类型配置 ==============
ENEMY_TYPES = {
    'virus': {
        'name': '病毒',
        'health': 60,
        'speed': 1.5,
        'reward': 10,
        'color': (255, 80, 80),
        'size': 12,
        'description': '普通敌人，数量多'
    },
    'worm': {
        'name': '蠕虫',
        'health': 40,
        'speed': 2.5,
        'reward': 15,
        'color': (255, 150, 50),
        'size': 10,
        'description': '速度快但生命值低'
    },
    'trojan': {
        'name': '木马',
        'health': 120,
        'speed': 1.0,
        'reward': 20,
        'color': (150, 50, 200),
        'size': 14,
        'description': '生命值高，速度较慢'
    },
    'ransomware': {
        'name': '勒索软件',
        'health': 180,
        'speed': 0.8,
        'reward': 30,
        'color': (255, 50, 150),
        'size': 16,
        'description': '高生命值，需要集中火力'
    },
    'ddos': {
        'name': 'DDoS攻击',
        'health': 350,
        'speed': 0.5,
        'reward': 50,
        'color': (255, 0, 0),
        'size': 20,
        'description': 'Boss级敌人，超厚血量'
    },
    'hacker': {
        'name': '黑客',
        'health': 90,
        'speed': 1.8,
        'reward': 25,
        'color': (0, 255, 200),
        'size': 13,
        'description': '会躲避部分攻击'
    },
    'spyware': {
        'name': '间谍软件',
        'health': 35,
        'speed': 2.0,
        'reward': 12,
        'color': (180, 120, 255),
        'size': 11,
        'description': '隐身接近，靠近才显形'
    },
    'rootkit': {
        'name': 'Rootkit',
        'health': 150,
        'speed': 0.9,
        'reward': 35,
        'color': (80, 80, 80),
        'size': 15,
        'description': '高血量，死亡后复活一次'
    },
    'botnet': {
        'name': '僵尸网络',
        'health': 50,
        'speed': 1.2,
        'reward': 18,
        'color': (100, 200, 50),
        'size': 12,
        'description': '死亡时分裂为2个小病毒'
    },
    'apt': {
        'name': 'APT攻击',
        'health': 300,
        'speed': 0.6,
        'reward': 80,
        'color': (180, 0, 0),
        'size': 22,
        'description': '终极Boss，超高血量，缓慢恢复'
    }
}

# ============== 关卡配置 ==============
LEVELS = {
    1: {
        'name': '入门网络',
        'description': '基础网络拓扑，适合新手',
        'path_type': 'zigzag',
        'initial_money': 200,
        'initial_health': 20,
        'gold_multiplier': 1.0,  # 金币倍率
        'waves': [
            {'enemies': [('virus', 5)], 'interval': 1500, 'reward': 100},
            {'enemies': [('virus', 8)], 'interval': 1200, 'reward': 120},
            {'enemies': [('virus', 5), ('worm', 3)], 'interval': 1200, 'reward': 150},
            {'enemies': [('worm', 6), ('virus', 5)], 'interval': 1000, 'reward': 180},
            {'enemies': [('trojan', 4)], 'interval': 1500, 'reward': 200},
            {'enemies': [('virus', 8), ('worm', 5), ('trojan', 3)], 'interval': 1000, 'reward': 250},
            {'enemies': [('ransomware', 3), ('virus', 5)], 'interval': 1200, 'reward': 300},
            {'enemies': [('hacker', 5), ('worm', 5)], 'interval': 1000, 'reward': 350},
            {'enemies': [('trojan', 6), ('ransomware', 3)], 'interval': 1000, 'reward': 400},
            {'enemies': [('ddos', 1), ('virus', 10)], 'interval': 1500, 'reward': 500},
            {'enemies': [('hacker', 8), ('ransomware', 4)], 'interval': 800, 'reward': 550},
            {'enemies': [('ddos', 2), ('trojan', 8), ('hacker', 5)], 'interval': 800, 'reward': 700},
        ]
    },
    2: {
        'name': '企业内网',
        'description': '更复杂的网络结构',
        'path_type': 'spiral',
        'initial_money': 250,
        'initial_health': 15,
        'gold_multiplier': 0.8,  # 金币倍率降低
        'waves': [
            {'enemies': [('virus', 8)], 'interval': 1200, 'reward': 120},
            {'enemies': [('worm', 5), ('spyware', 3)], 'interval': 1000, 'reward': 150},
            {'enemies': [('trojan', 5)], 'interval': 1200, 'reward': 200},
            {'enemies': [('virus', 10), ('spyware', 5)], 'interval': 800, 'reward': 250},
            {'enemies': [('ransomware', 3), ('trojan', 3)], 'interval': 1000, 'reward': 300},
            {'enemies': [('hacker', 5), ('spyware', 5)], 'interval': 800, 'reward': 350},
            {'enemies': [('trojan', 8), ('ransomware', 3)], 'interval': 800, 'reward': 400},
            {'enemies': [('ddos', 1), ('hacker', 5)], 'interval': 1200, 'reward': 500},
            {'enemies': [('hacker', 8), ('spyware', 8)], 'interval': 600, 'reward': 600},
            {'enemies': [('ddos', 2), ('trojan', 10), ('hacker', 8)], 'interval': 600, 'reward': 800},
        ]
    },
    3: {
        'name': '数据中心',
        'description': '高难度挑战',
        'path_type': 'cross',
        'initial_money': 300,
        'initial_health': 10,
        'gold_multiplier': 0.6,  # 金币倍率更低
        'waves': [
            {'enemies': [('worm', 8)], 'interval': 1000, 'reward': 150},
            {'enemies': [('trojan', 6)], 'interval': 1000, 'reward': 200},
            {'enemies': [('virus', 10), ('botnet', 5)], 'interval': 700, 'reward': 250},
            {'enemies': [('ransomware', 5), ('botnet', 5)], 'interval': 800, 'reward': 350},
            {'enemies': [('hacker', 8), ('spyware', 8)], 'interval': 600, 'reward': 400},
            {'enemies': [('ddos', 2), ('ransomware', 5)], 'interval': 1000, 'reward': 500},
            {'enemies': [('rootkit', 3), ('hacker', 8)], 'interval': 600, 'reward': 600},
            {'enemies': [('ddos', 3), ('rootkit', 5), ('hacker', 10)], 'interval': 500, 'reward': 1000},
        ]
    },
    4: {
        'name': '云服务器',
        'description': '双路进攻，考验布局',
        'path_type': 'zigzag',
        'initial_money': 350,
        'initial_health': 12,
        'gold_multiplier': 0.5,  # 金币紧张
        'waves': [
            {'enemies': [('virus', 10), ('botnet', 5)], 'interval': 800, 'reward': 200},
            {'enemies': [('trojan', 8), ('spyware', 8)], 'interval': 800, 'reward': 250},
            {'enemies': [('hacker', 6), ('ransomware', 3)], 'interval': 800, 'reward': 300},
            {'enemies': [('ddos', 1), ('rootkit', 3), ('worm', 10)], 'interval': 700, 'reward': 400},
            {'enemies': [('ransomware', 6), ('hacker', 8)], 'interval': 600, 'reward': 500},
            {'enemies': [('ddos', 2), ('rootkit', 5), ('trojan', 10)], 'interval': 500, 'reward': 700},
            {'enemies': [('apt', 1), ('ransomware', 8), ('hacker', 12)], 'interval': 400, 'reward': 1000},
        ]
    },
    5: {
        'name': '物联网网络',
        'description': '海量设备，极速攻击',
        'path_type': 'spiral',
        'initial_money': 400,
        'initial_health': 8,
        'gold_multiplier': 0.4,  # 金币非常紧张
        'waves': [
            {'enemies': [('worm', 15)], 'interval': 500, 'reward': 200},
            {'enemies': [('virus', 15), ('botnet', 8)], 'interval': 500, 'reward': 300},
            {'enemies': [('trojan', 10), ('rootkit', 3)], 'interval': 600, 'reward': 400},
            {'enemies': [('ddos', 2), ('botnet', 12), ('hacker', 8)], 'interval': 500, 'reward': 500},
            {'enemies': [('ransomware', 8), ('rootkit', 5)], 'interval': 500, 'reward': 600},
            {'enemies': [('apt', 1), ('hacker', 15), ('ransomware', 8)], 'interval': 400, 'reward': 800},
            {'enemies': [('ddos', 5), ('rootkit', 8), ('hacker', 15), ('ransomware', 10)], 'interval': 300, 'reward': 1500},
        ]
    },
    6: {
        'name': '终极防线',
        'description': '最终Boss战，极限挑战',
        'path_type': 'cross',
        'initial_money': 500,
        'initial_health': 5,
        'gold_multiplier': 0.3,  # 极限金币限制
        'waves': [
            {'enemies': [('virus', 20), ('botnet', 10)], 'interval': 400, 'reward': 300},
            {'enemies': [('trojan', 15), ('rootkit', 5)], 'interval': 500, 'reward': 400},
            {'enemies': [('ransomware', 10), ('ddos', 2)], 'interval': 600, 'reward': 500},
            {'enemies': [('apt', 1), ('hacker', 15), ('trojan', 15)], 'interval': 400, 'reward': 700},
            {'enemies': [('ransomware', 15), ('ddos', 4), ('rootkit', 8)], 'interval': 300, 'reward': 1000},
            {'enemies': [('apt', 2), ('ddos', 5), ('trojan', 20), ('hacker', 20)], 'interval': 250, 'reward': 2000},
        ]
    }
}

# ============== 游戏初始设置 ==============
INITIAL_MONEY = 200
INITIAL_HEALTH = 20
INITIAL_WAVE = 0
INITIAL_LEVEL = 1

# ============== 特效配置 ==============
PARTICLE_LIFETIME = 1000
EXPLOSION_PARTICLES = 15
HIT_PARTICLES = 5

# ============== 金币掉落配置 ==============
COIN_DROP_CHANCE = 0.6     # 击杀敌人掉落金币的基础概率 (60%)
COIN_DROP_BONUS = 0.05     # 每关降低的概率 (第6关为 60% - 5*5% = 35%)

# ============== 自动机制 ==============
AUTO_REPAIR_COST = 30      # 自动修复成本
AUTO_REPAIR_INTERVAL = 5000  # 自动修复间隔（毫秒）
AUTO_UPGRADE_COST = 50     # 自动升级成本
AUTO_COLLECT_INTERVAL = 3000  # 自动收集奖励间隔
