import pygame
import numpy as np
import threading
from scipy import signal

class BF16audio:
    SAMPLE_RATE = 48000
    AMPLITUDE = 28000
    _INIT = False

    @staticmethod
    def _ensure_initialized():
        if not BF16audio._INIT:
            pygame.mixer.pre_init(BF16audio.SAMPLE_RATE, -16, 2, 512)
            pygame.init()
            BF16audio._INIT = True

    @staticmethod
    def play_note(pitch: int, waveform: str = "sine"):
        BF16audio._ensure_initialized()
        freq = 440.0 * (2.0 ** ((pitch - 69.0) / 12.0))
        duration = 0.166
        samples = int(BF16audio.SAMPLE_RATE * duration)
        t = np.linspace(0, duration, samples, endpoint=False)

        envelope = np.ones(samples)
        attack = int(BF16audio.SAMPLE_RATE * 0.02)
        release = int(BF16audio.SAMPLE_RATE * 0.02)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)

        if waveform == "sine":
            wave = np.sin(2 * np.pi * freq * t)
        elif waveform == "square":
            wave = np.sign(np.sin(2 * np.pi * freq * t))
        elif waveform == "triangle":
            wave = 2 * np.abs(2 * (t * freq % 1) - 1) - 1
        else:
            wave = np.sin(2 * np.pi * freq * t)  # default to sine

        audio = (BF16audio.AMPLITUDE * envelope * wave).astype(np.int16)
        stereo_audio = np.column_stack((audio, audio))
        pygame.sndarray.make_sound(stereo_audio).play()

    @staticmethod
    def play_bass_note(pitch: int):
        BF16audio._ensure_initialized()
        freq = 440.0 * (2.0 ** ((pitch - 69.0 - 12.0) / 12.0))
        duration = 0.25
        samples = int(BF16audio.SAMPLE_RATE * duration)
        t = np.linspace(0, duration, samples, endpoint=False)

        envelope = np.ones(samples)
        attack = int(BF16audio.SAMPLE_RATE * 0.05)
        release = int(BF16audio.SAMPLE_RATE * 0.05)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)

        wave = np.sign(np.sin(2 * np.pi * freq * t))
        audio = (BF16audio.AMPLITUDE * envelope * wave).astype(np.int16)
        stereo_audio = np.column_stack((audio, audio))
        pygame.sndarray.make_sound(stereo_audio).play()

    @staticmethod
    def play_drum_sound(pitch: int):
        BF16audio._ensure_initialized()
        freq = 440.0 * (2.0 ** ((pitch - 69.0) / 12.0))
        duration = 0.1
        samples = int(BF16audio.SAMPLE_RATE * duration)
        t = np.linspace(0, duration, samples, endpoint=False)

        envelope = np.ones(samples)
        attack = int(BF16audio.SAMPLE_RATE * 0.01)
        decay = int(BF16audio.SAMPLE_RATE * 0.05)
        release = int(BF16audio.SAMPLE_RATE * 0.04)

        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[attack:attack + decay] = np.linspace(1, 0.5, decay)
        envelope[attack + decay:samples - release] = 0.5
        envelope[samples - release:] = np.linspace(0.5, 0, release)

        # Simple noise burst for drum sound
        noise = np.random.uniform(-1, 1, samples)
        
        # Apply a low-pass filter effect for a more percussive sound
        b, a = signal.butter(4, freq / (BF16audio.SAMPLE_RATE / 2), btype='low')
        filtered_noise = signal.lfilter(b, a, noise)

        audio = (BF16audio.AMPLITUDE * envelope * filtered_noise).astype(np.int16)
        stereo_audio = np.column_stack((audio, audio))
        pygame.sndarray.make_sound(stereo_audio).play()

    @staticmethod
    def play_arpeggio(start_pitch: int, num_notes: int = 4, delay: float = 0.05):
        BF16audio._ensure_initialized()

        def _play():
            for i in range(num_notes):
                BF16audio.play_note(start_pitch + i * 4)
                pygame.time.wait(int(delay * 1000))

        threading.Thread(target=_play).start()

    @staticmethod
    def play_chord(root_pitch: int, chord_type: str = "major", duration: float = 0.5):
        BF16audio._ensure_initialized()

        chord_types = {
            "major": [0, 4, 7],
            "minor": [0, 3, 7],
            "diminished": [0, 3, 6],
            "augmented": [0, 4, 8],
            "major7": [0, 4, 7, 11],
            "minor7": [0, 3, 7, 10],
        }

        intervals = chord_types.get(chord_type.lower(), [0, 4, 7])
        if chord_type.lower() not in chord_types:
            print(f"Warning: Unknown chord '{chord_type}', using major.")

        pitches = [root_pitch + i for i in intervals]
        samples = int(BF16audio.SAMPLE_RATE * duration)
        t = np.linspace(0, duration, samples, endpoint=False)
        combined_wave = np.zeros(samples)

        envelope = np.ones(samples)
        attack = int(BF16audio.SAMPLE_RATE * 0.02)
        release = int(BF16audio.SAMPLE_RATE * 0.05)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)

        for pitch in pitches:
            freq = 440.0 * (2.0 ** ((pitch - 69.0) / 12.0))
            combined_wave += np.sin(2 * np.pi * freq * t)

        wave = BF16audio.AMPLITUDE * envelope * (combined_wave / len(pitches))
        audio = wave.astype(np.int16)
        stereo_audio = np.column_stack((audio, audio))
        pygame.sndarray.make_sound(stereo_audio).play()

    @staticmethod
    def play_sequence(pitches: list[int], delays: list[float]):
        BF16audio._ensure_initialized()

        def _play():
            for pitch, d in zip(pitches, delays):
                BF16audio.play_note(pitch)
                pygame.time.wait(int(d * 1000))

        threading.Thread(target=_play).start()

    @staticmethod
    def stop_all_sounds():
        BF16audio._ensure_initialized()
        pygame.mixer.stop()

    @staticmethod
    def set_volume(volume: float):
        """
        Sets the global volume for all channels.
        volume: float between 0.0 and 1.0
        """
        BF16audio._ensure_initialized()
        if 0.0 <= volume <= 1.0:
            for i in range(pygame.mixer.get_num_channels()):
                pygame.mixer.Channel(i).set_volume(volume)
        else:
            print("Volume must be between 0.0 and 1.0")
