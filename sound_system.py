"""
网络守护者 - 音效系统
使用 pygame.mixer 生成程序化音效（无需外部音频文件，无需numpy）
纯 Python 标准库实现
"""

import pygame
import math
import random
import io
import struct
import array


class SoundSystem:
    """音效系统 - 程序化生成所有音效"""
    
    SAMPLE_RATE = 44100
    
    def __init__(self):
        self.enabled = True
        self.sounds = {}
        self._init_sounds()
    
    def _init_sounds(self):
        """生成所有音效"""
        try:
            pygame.mixer.init(frequency=self.SAMPLE_RATE, size=-16, channels=1, buffer=512)
            self.sounds = {
                'shoot': self._generate_shoot(),
                'hit': self._generate_hit(),
                'explosion': self._generate_explosion(),
                'coin': self._generate_coin(),
                'wave_start': self._generate_wave_start(),
                'victory': self._generate_victory(),
                'defeat': self._generate_defeat(),
                'enrage': self._generate_enrage(),
                'place': self._generate_place(),
                'error': self._generate_error(),
            }
        except Exception:
            self.enabled = False
    
    def _make_sound(self, samples_list):
        """将采样列表转换为 pygame Sound 对象"""
        # 确保采样值在 -32768 到 32767 之间
        samples = array.array('h', [max(-32768, min(32767, int(s))) for s in samples_list])
        # 创建 WAV 格式的字节流
        buf = io.BytesIO()
        num_samples = len(samples)
        data_size = num_samples * 2  # 16-bit = 2 bytes per sample
        # WAV 文件头
        buf.write(b'RIFF')
        buf.write(struct.pack('<I', 36 + data_size))
        buf.write(b'WAVE')
        buf.write(b'fmt ')
        buf.write(struct.pack('<I', 16))
        buf.write(struct.pack('<H', 1))    # PCM
        buf.write(struct.pack('<H', 1))    # mono
        buf.write(struct.pack('<I', self.SAMPLE_RATE))
        buf.write(struct.pack('<I', self.SAMPLE_RATE * 2))
        buf.write(struct.pack('<H', 2))    # block align
        buf.write(struct.pack('<H', 16))   # bits per sample
        buf.write(b'data')
        buf.write(struct.pack('<I', data_size))
        buf.write(samples.tobytes())
        buf.seek(0)
        return pygame.mixer.Sound(buf)
    
    def _gen_samples(self, duration):
        """生成时间轴采样点"""
        n = int(self.SAMPLE_RATE * duration)
        return [i / self.SAMPLE_RATE for i in range(n)]
    
    def _generate_shoot(self):
        """射击音效 - 短促电子脉冲"""
        duration = 0.08
        t = self._gen_samples(duration)
        samples = []
        for ti in t:
            freq = 800 - 400 * (ti / duration)
            val = math.sin(2 * math.pi * freq * ti) * math.exp(-ti * 40) * 8000
            samples.append(val)
        return self._make_sound(samples)
    
    def _generate_hit(self):
        """击中音效 - 金属撞击"""
        duration = 0.1
        t = self._gen_samples(duration)
        samples = []
        for ti in t:
            noise = random.uniform(-1, 1) * math.exp(-ti * 30)
            tone = math.sin(2 * math.pi * 200 * ti) * math.exp(-ti * 25)
            val = (noise * 0.5 + tone * 0.5) * 6000
            samples.append(val)
        return self._make_sound(samples)
    
    def _generate_explosion(self):
        """爆炸音效 - 低频轰鸣"""
        duration = 0.3
        t = self._gen_samples(duration)
        samples = []
        for ti in t:
            noise = random.uniform(-1, 1)
            low = math.sin(2 * math.pi * 60 * ti)
            val = (noise * 0.6 + low * 0.4) * math.exp(-ti * 8) * 12000
            samples.append(val)
        return self._make_sound(samples)
    
    def _generate_coin(self):
        """金币音效 - 清脆双音"""
        duration = 0.15
        t = self._gen_samples(duration)
        samples = []
        for ti in t:
            w1 = math.sin(2 * math.pi * 1200 * ti) * math.exp(-ti * 20)
            w2 = math.sin(2 * math.pi * 1600 * ti) * math.exp(-(ti - 0.05) * 20) * (1 if ti > 0.05 else 0)
            val = (w1 + w2 * 0.7) * 5000
            samples.append(val)
        return self._make_sound(samples)
    
    def _generate_wave_start(self):
        """波次开始音效 - 警报声"""
        duration = 0.5
        t = self._gen_samples(duration)
        samples = []
        for ti in t:
            freq = 400 + 600 * (ti / duration)
            wave = math.sin(2 * math.pi * freq * ti) * 0.5
            pulse = 0.5 + 0.5 * math.sin(2 * math.pi * 8 * ti)
            val = wave * pulse * math.exp(-ti * 3) * 7000
            samples.append(val)
        return self._make_sound(samples)
    
    def _generate_victory(self):
        """胜利音效 - 上升和弦"""
        duration = 1.0
        t = self._gen_samples(duration)
        samples = []
        for ti in t:
            w1 = math.sin(2 * math.pi * 523 * ti) * math.exp(-ti * 2)
            w2 = math.sin(2 * math.pi * 659 * ti) * math.exp(-(ti - 0.1) * 2) * (1 if ti > 0.1 else 0)
            w3 = math.sin(2 * math.pi * 784 * ti) * math.exp(-(ti - 0.2) * 2) * (1 if ti > 0.2 else 0)
            val = (w1 + w2 + w3) / 3 * 8000
            samples.append(val)
        return self._make_sound(samples)
    
    def _generate_defeat(self):
        """失败音效 - 下降音调"""
        duration = 0.8
        t = self._gen_samples(duration)
        samples = []
        for ti in t:
            freq = 400 - 200 * (ti / duration)
            val = math.sin(2 * math.pi * freq * ti) * math.exp(-ti * 2) * 8000
            samples.append(val)
        return self._make_sound(samples)
    
    def _generate_enrage(self):
        """激怒音效 - 低沉咆哮"""
        duration = 0.4
        t = self._gen_samples(duration)
        samples = []
        for ti in t:
            noise = random.uniform(-1, 1) * math.exp(-ti * 5)
            low = math.sin(2 * math.pi * 80 * ti) * math.exp(-ti * 4)
            wave = noise * 0.4 + low * 0.6
            envelope = min(ti * 20, 1.0) * math.exp(-ti * 5)
            val = wave * envelope * 10000
            samples.append(val)
        return self._make_sound(samples)
    
    def _generate_place(self):
        """放置音效 - 电子确认"""
        duration = 0.1
        t = self._gen_samples(duration)
        samples = []
        for ti in t:
            val = math.sin(2 * math.pi * 600 * ti) * math.exp(-ti * 25) * 5000
            samples.append(val)
        return self._make_sound(samples)
    
    def _generate_error(self):
        """错误音效 - 低沉蜂鸣"""
        duration = 0.15
        t = self._gen_samples(duration)
        samples = []
        for ti in t:
            val = math.sin(2 * math.pi * 150 * ti) * math.exp(-ti * 15) * 4000
            samples.append(val)
        return self._make_sound(samples)
    
    def play(self, sound_name):
        """播放音效"""
        if not self.enabled or sound_name not in self.sounds:
            return
        try:
            self.sounds[sound_name].play()
        except Exception:
            pass
    
    def stop_all(self):
        """停止所有音效"""
        if self.enabled:
            try:
                pygame.mixer.stop()
            except Exception:
                pass
