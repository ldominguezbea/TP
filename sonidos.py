"""
Sonido procedural para el selector de niveles (no necesita archivos de audio).
 
  - travel():        "whoosh" al viajar de un nivel a otro
  - confirm():       acorde brillante al entrar a un nivel
  - denied():        zumbido grave si el nivel no está disponible
  - planet_switch(): retumbar al viajar entre Tierra y Gehena
  - update_ambient(env): ambiente de fondo; se mezcla de Tierra (0) a Gehena (1)
 
Si el equipo no tiene audio, todo se desactiva en silencio y el selector sigue andando.
"""
import numpy as np
import pygame
 
 
class Audio:
    def __init__(self):
        self.ok = False
        self.muted = False
        self.master = 0.5
        self._amb = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 2, 512)
            init = pygame.mixer.get_init()
            if init is None or init[1] != -16 or init[2] not in (1, 2):
                return
            self.sr, _, self.ch = init
            pygame.mixer.set_num_channels(12)
            self._build()
            self.ok = True
        except Exception as error:   # sin dispositivo de audio, etc.
            print(f"[Audio] desactivado: {error}")
 
    # ------------------------------------------------------------------ utilidades
    def _t(self, dur):
        return np.arange(int(self.sr * dur)) / self.sr
 
    def _sound(self, mono, gain=1.0):
        m = np.clip(mono * gain, -1.0, 1.0)
        data = (m * 32767).astype(np.int16)
        if self.ch == 2:
            data = np.column_stack((data, data))
        return pygame.sndarray.make_sound(np.ascontiguousarray(data))
 
    # ------------------------------------------------------------------ sintesis
    def _build(self):
        sr = self.sr
 
        # Whoosh: ruido suavizado + barrido de tono
        dur = 0.55
        t = self._t(dur)
        n = np.random.default_rng(1).standard_normal(len(t))
        n = np.convolve(n, np.ones(60) / 60, "same") * 5
        env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
        ph = 2 * np.pi * np.cumsum(220 + 900 * (t / dur) ** 2) / sr
        self.s_travel = self._sound((n * 0.5 + np.sin(ph) * 0.25) * env, 0.8)
 
        # Confirmar: arpegio brillante
        out = np.zeros(int(sr * 0.9))
        for i, f in enumerate((523.25, 659.25, 783.99, 1046.5)):
            st = int(i * 0.07 * sr)
            tt = np.arange(len(out) - st) / sr
            out[st:] += (np.sin(2 * np.pi * f * tt) * np.exp(-tt * 5) * 0.4
                         + np.sin(2 * np.pi * f * 2 * tt) * np.exp(-tt * 8) * 0.1)
        self.s_confirm = self._sound(out, 0.7)
 
        # No disponible: dos ondas cuadradas graves, suavizadas
        t = self._t(0.28)
        tone = (np.sign(np.sin(2 * np.pi * 150 * t)) + np.sign(np.sin(2 * np.pi * 113 * t))) * 0.3
        tone = np.convolve(tone, np.ones(8) / 8, "same") * np.exp(-t * 9)
        self.s_denied = self._sound(tone, 0.7)
 
        # Cambio de planeta: retumbar grave que crece y se apaga
        dur = 1.6
        t = self._t(dur)
        n = np.random.default_rng(2).standard_normal(len(t))
        n = np.convolve(n, np.ones(200) / 200, "same") * 14
        ph = 2 * np.pi * np.cumsum(50 + 140 * (t / dur) ** 2) / sr
        env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.5
        self.s_planet = self._sound((n * 0.5 + np.sin(ph) * 0.5) * env, 0.8)
 
        # Ambientes en bucle (frecuencias con ciclos enteros en 8 s => sin clic al repetir)
        t = self._t(8.0)
        tau = 2 * np.pi
        earth = np.zeros_like(t)
        for f, a in ((110, 0.5), (165, 0.35), (220, 0.3), (275, 0.18)):
            earth += a * np.sin(tau * f * t) * (0.6 + 0.4 * np.sin(tau * 0.25 * t + f))
        earth += 0.1 * np.sin(tau * 440 * t) * (0.5 + 0.5 * np.sin(tau * 0.125 * t))
 
        rng = np.random.default_rng(3)
        gehena = np.zeros_like(t)
        for k in rng.integers(240, 1200, size=36):
            f = k / 8.0
            gehena += (0.08 / (1 + (f - 30) / 40)) * np.sin(tau * f * t + rng.uniform(0, 6.28))
        gehena += 0.35 * np.sin(tau * 55 * t) * (0.7 + 0.3 * np.sin(tau * 0.25 * t))
        gehena += 0.2 * np.sin(tau * 82.5 * t + 1)
 
        self._amb = {"earth": self._sound(earth, 0.35), "gehena": self._sound(gehena, 0.6)}
        self._amb_ch = {}
        for key, snd in self._amb.items():
            ch = snd.play(loops=-1)
            if ch is not None:
                ch.set_volume(0.0)
            self._amb_ch[key] = ch
 
    # ------------------------------------------------------------------ uso
    def _play(self, snd, vol=1.0):
        if self.ok and not self.muted:
            ch = snd.play()
            if ch is not None:
                ch.set_volume(vol * self.master)
 
    def travel(self):
        if self.ok:
            self._play(self.s_travel, 0.8)
 
    def confirm(self):
        if self.ok:
            self._play(self.s_confirm, 0.9)
 
    def denied(self):
        if self.ok:
            self._play(self.s_denied, 0.8)
 
    def planet_switch(self):
        if self.ok:
            self._play(self.s_planet, 1.0)
 
    def update_ambient(self, env):
        if not self.ok:
            return
        k = 0.0 if self.muted else self.master
        for key, vol in (("earth", (1 - env) * 0.55), ("gehena", env * 0.7)):
            ch = self._amb_ch.get(key)
            if ch is not None:
                ch.set_volume(vol * k)
 
    def toggle_mute(self):
        self.muted = not self.muted
        return self.muted