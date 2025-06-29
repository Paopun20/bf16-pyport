import pygame
import numpy as np

class bf16audio:
    SAMPLE_RATE = 48000
    AMPLITUDE = 28000
    _INIT = False

    @staticmethod
    def play_note(pitch: int):
        if not bf16audio._INIT:
            pygame.mixer.pre_init(bf16audio.SAMPLE_RATE, -16, 2, 512)
            pygame.init()
            bf16audio._INIT = True

        # MIDI note number to frequency
        freq = 440.0 * (2.0 ** ((pitch - 69.0) / 12.0))

        duration = 0.166  # in seconds
        samples = int(bf16audio.SAMPLE_RATE * duration)
        t = np.linspace(0, duration, samples, endpoint=False)

        # Basic envelope: attack + sustain + release
        envelope = np.ones(samples)
        attack = int(bf16audio.SAMPLE_RATE * 0.02)
        release = int(bf16audio.SAMPLE_RATE * 0.02)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)

        # Generate sine wave
        wave = bf16audio.AMPLITUDE * envelope * np.sin(2 * np.pi * freq * t)
        audio = wave.astype(np.int16)

        # Stereo
        stereo_audio = np.column_stack((audio, audio))

        # Play sound
        sound = pygame.sndarray.make_sound(stereo_audio)
        sound.play()
