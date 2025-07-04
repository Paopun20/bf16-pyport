import pygame
import numpy as np
import threading

class bf16audio:
    SAMPLE_RATE = 48000
    AMPLITUDE = 28000
    _INIT = False

    @staticmethod
    def _ensure_initialized():
        if not bf16audio._INIT:
            pygame.mixer.pre_init(bf16audio.SAMPLE_RATE, -16, 2, 512)
            pygame.init()
            bf16audio._INIT = True

    @staticmethod
    def play_note(pitch: int, waveform: str = "sine"):
        bf16audio._ensure_initialized()
        freq = 440.0 * (2.0 ** ((pitch - 69.0) / 12.0))
        duration = 0.166
        samples = int(bf16audio.SAMPLE_RATE * duration)
        t = np.linspace(0, duration, samples, endpoint=False)

        envelope = np.ones(samples)
        attack = int(bf16audio.SAMPLE_RATE * 0.02)
        release = int(bf16audio.SAMPLE_RATE * 0.02)
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

        audio = (bf16audio.AMPLITUDE * envelope * wave).astype(np.int16)
        stereo_audio = np.column_stack((audio, audio))
        pygame.sndarray.make_sound(stereo_audio).play()

    @staticmethod
    def play_bass_note(pitch: int):
        bf16audio._ensure_initialized()
        freq = 440.0 * (2.0 ** ((pitch - 69.0 - 12.0) / 12.0))
        duration = 0.25
        samples = int(bf16audio.SAMPLE_RATE * duration)
        t = np.linspace(0, duration, samples, endpoint=False)

        envelope = np.ones(samples)
        attack = int(bf16audio.SAMPLE_RATE * 0.05)
        release = int(bf16audio.SAMPLE_RATE * 0.05)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)

        wave = np.sign(np.sin(2 * np.pi * freq * t))
        audio = (bf16audio.AMPLITUDE * envelope * wave).astype(np.int16)
        stereo_audio = np.column_stack((audio, audio))
        pygame.sndarray.make_sound(stereo_audio).play()

    @staticmethod
    def play_drum_sound(drum_type: int):
        bf16audio._ensure_initialized()
        samples = int(bf16audio.SAMPLE_RATE * 0.1)
        t = np.linspace(0, 0.1, samples, endpoint=False)

        if drum_type == 0:  # Kick
            freq1, freq2 = 60, 30
            decay = np.exp(-5 * t)
            wave = np.sin(2 * np.pi * freq1 * t) + 0.5 * np.sin(2 * np.pi * freq2 * t)
        elif drum_type == 1:  # Snare
            wave = np.random.uniform(-1, 1, samples)
            decay = np.exp(-8 * t)
        elif drum_type == 2:  # Hi-hat
            wave = np.random.uniform(-1, 1, samples)
            decay = np.exp(-15 * t) * 0.5
        else:
            return

        audio = (bf16audio.AMPLITUDE * wave * decay).astype(np.int16)
        stereo_audio = np.column_stack((audio, audio))
        pygame.sndarray.make_sound(stereo_audio).play()

    @staticmethod
    def play_arpeggio(start_pitch: int, num_notes: int = 4, delay: float = 0.05):
        bf16audio._ensure_initialized()

        def _play():
            for i in range(num_notes):
                bf16audio.play_note(start_pitch + i * 4)
                pygame.time.wait(int(delay * 1000))

        threading.Thread(target=_play).start()

    @staticmethod
    def play_chord(root_pitch: int, chord_type: str = "major", duration: float = 0.5):
        bf16audio._ensure_initialized()

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
        samples = int(bf16audio.SAMPLE_RATE * duration)
        t = np.linspace(0, duration, samples, endpoint=False)
        combined_wave = np.zeros(samples)

        envelope = np.ones(samples)
        attack = int(bf16audio.SAMPLE_RATE * 0.02)
        release = int(bf16audio.SAMPLE_RATE * 0.05)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)

        for pitch in pitches:
            freq = 440.0 * (2.0 ** ((pitch - 69.0) / 12.0))
            combined_wave += np.sin(2 * np.pi * freq * t)

        wave = bf16audio.AMPLITUDE * envelope * (combined_wave / len(pitches))
        audio = wave.astype(np.int16)
        stereo_audio = np.column_stack((audio, audio))
        pygame.sndarray.make_sound(stereo_audio).play()

    @staticmethod
    def play_sequence(pitches: list[int], delays: list[float]):
        bf16audio._ensure_initialized()

        def _play():
            for pitch, d in zip(pitches, delays):
                bf16audio.play_note(pitch)
                pygame.time.wait(int(d * 1000))

        threading.Thread(target=_play).start()

    @staticmethod
    def stop_all_sounds():
        bf16audio._ensure_initialized()
        pygame.mixer.stop()

    @staticmethod
    def set_volume(volume: float):
        """
        Sets the global volume for all channels.
        volume: float between 0.0 and 1.0
        """
        bf16audio._ensure_initialized()
        if 0.0 <= volume <= 1.0:
            for i in range(pygame.mixer.get_num_channels()):
                pygame.mixer.Channel(i).set_volume(volume)
        else:
            print("Volume must be between 0.0 and 1.0")
