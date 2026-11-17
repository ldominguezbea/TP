from pathlib import Path

import numpy as np
import pygame


class Audio:
    def __init__(self):
        self.ok = False
        self.muted = False
        self.master = 0.5
        self.sr = 44100
        self.ch = 2
        self._sfx = {}
        self._amb = {}
        self._amb_ch = {}
        self._travel_sound = None

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 2, 512)

            init = pygame.mixer.get_init()
            if init is None:
                raise RuntimeError("pygame.mixer no inicializado")

            self.sr, _, self.ch = init
            pygame.mixer.set_num_channels(12)
            self._build()
            self.ok = True
        except Exception as error:
            print(f"[Audio] desactivado: {error}")

    def _t(self, dur):
        return np.arange(int(self.sr * dur)) / self.sr

    def _sound(self, mono, gain=1.0):
        if mono is None:
            return None
        m = np.clip(mono * gain, -1.0, 1.0)
        data = (m * 32767).astype(np.int16)
        if self.ch == 2:
            data = np.column_stack((data, data))
        return pygame.sndarray.make_sound(np.ascontiguousarray(data))

    def _play(self, sound, vol=1.0):
        if not self.ok or self.muted or sound is None:
            return
        channel = sound.play()
        if channel:
            channel.set_volume(vol * self.master)

    def _build(self):
        sr = self.sr

        # --- Efectos de sonido (SFX) ---
        travel_path = Path(__file__).resolve().parent / "musica" / "space transition.mp3"
        try:
            self._travel_sound = pygame.mixer.Sound(str(travel_path))
            self._travel_sound.set_volume(0.8)
        except (pygame.error, OSError) as error:
            print(f"[Audio] No se pudo cargar space transition.mp3: {error}")

        out = np.zeros(int(sr * 0.9))
        for i, f in enumerate((523.25, 659.25, 783.99, 1046.5)):
            st = int(i * 0.07 * sr)
            tt = np.arange(len(out) - st) / sr
            out[st:] += (
                np.sin(2 * np.pi * f * tt) * np.exp(-tt * 5) * 0.4
                + np.sin(2 * np.pi * f * 2 * tt) * np.exp(-tt * 8) * 0.1
            )
        self._sfx["confirm"] = self._sound(out, 0.7)

        denied_duration = 0.35
        denied_t = self._t(denied_duration)
        denied_phase = 2 * np.pi * np.cumsum(
            260 - 120 * denied_t / denied_duration
        ) / sr
        denied_env = np.exp(-denied_t * 7)
        self._sfx["denied"] = self._sound(
            np.sin(denied_phase) * denied_env, 0.45
        )

        # --- Ambientes Sintetizados (Loopped) ---
        t_amb = self._t(8.0)
        tau = 2 * np.pi
        earth = np.zeros_like(t_amb)
        for f, a in ((110, 0.5), (165, 0.35), (220, 0.3), (275, 0.18)):
            earth += a * np.sin(tau * f * t_amb) * (0.6 + 0.4 * np.sin(tau * 0.25 * t_amb + f))
        earth += 0.1 * np.sin(tau * 440 * t_amb) * (0.5 + 0.5 * np.sin(tau * 0.125 * t_amb))

        rng = np.random.default_rng(3)
        gehena = np.zeros_like(t_amb)
        for k in rng.integers(240, 1200, size=36):
            f = k / 8.0
            gehena += (0.08 / (1 + ((f - 30) / 40) ** 2)) * np.sin(tau * f * t_amb + rng.uniform(0, 6.28))
        gehena += 0.35 * np.sin(tau * 55 * t_amb) * (0.7 + 0.3 * np.sin(tau * 0.25 * t_amb))
        gehena += 0.2 * np.sin(tau * 82.5 * t_amb + 1)

        self._amb = {
            "earth": self._sound(earth, 0.35),
            "gehena": self._sound(gehena, 0.6),
        }

        self._amb_ch = {}
        for key, snd in self._amb.items():
            if snd:
                ch = snd.play(loops=-1)
                if ch:
                    ch.set_volume(0.0)
                self._amb_ch[key] = ch

    def travel(self):
        self._play(self._travel_sound, 0.8)

    def stop_ambient(self):
        for channel in self._amb_ch.values():
            if channel is not None:
                channel.stop()

    def planet_switch(self):
        self.travel()

    def confirm(self):
        self._play(self._sfx.get("confirm"), 0.9)

    def denied(self):
        self._play(self._sfx.get("denied"), 0.8)

    def toggle_mute(self):
        self.muted = not self.muted
        if self.muted:
            for ch in self._amb_ch.values():
                if ch:
                    ch.set_volume(0.0)
        return self.muted

    def update_ambient(self, env, active=True):
        if not self.ok:
            return
        k = 0.0 if self.muted or not active else self.master
        volumes = {
            "earth": (1.0 - env) * 0.55,
            "gehena": env * 0.7,
        }
        for key, vol in volumes.items():
            ch = self._amb_ch.get(key)
            if ch is not None:
                ch.set_volume(vol * k)