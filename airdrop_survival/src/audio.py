from __future__ import annotations
import os

def ensure_urgent_bgm(path: str) -> str:
    if os.path.exists(path):
        return path

    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        try:
            os.makedirs(parent)
        except Exception:
            pass

    try:
        import numpy as np
        import wave

        sr = 44100
        duration = 8.0
        t = np.linspace(0.0, duration, int(sr * duration), endpoint=False)
        rng = np.random.RandomState(424242)

        # Bass envelope for smoothness
        bass_env = 0.6 + 0.4 * np.sin(2 * np.pi * 0.05 * t)

        # Sub and drone layers
        sub = 0.35 * np.sin(2 * np.pi * 27.5 * t) * bass_env
        drone = 0.55 * np.sin(2 * np.pi * 55.0 * t) * bass_env
        drone += 0.18 * np.sin(2 * np.pi * 58.5 * t) * bass_env

        # Pulse rhythm
        pulse_base = np.sin(2 * np.pi * 2.8 * t)
        pulse_env = (np.abs(np.sin(2 * np.pi * 2.8 * t)) ** 0.45)
        pulse = 0.28 * pulse_base * pulse_env

        # Arpeggiated dissonant tones
        arp = np.zeros_like(t)
        freqs = [220.0, 233.08, 196.0]
        step_len = int(sr * 0.25)
        for i in range(0, len(t), step_len):
            idx = i
            dur = min(step_len, len(t) - idx)
            f = freqs[(i // step_len) % len(freqs)] * (1.0 + 0.02 * ((i // step_len) % 3))
            arp[idx:idx + dur] += 0.09 * np.sin(2 * np.pi * f * t[idx:idx + dur]) * np.exp(-np.linspace(0, 3.0, dur))

        # Combine base layers
        signal = sub + drone + pulse + arp

        # Add low harmony fill
        low_harmony = 0.2 * np.sin(2 * np.pi * 85.0 * t) + 0.15 * np.sin(2 * np.pi * 95.0 * t)
        signal += low_harmony * (np.sin(2 * np.pi * 0.2 * t) + 1.0) * 0.5

        # Add kick and snare rhythm
        kick = 0.3 * np.sin(2 * np.pi * 60 * t) * (np.sin(2 * np.pi * 1.0 * t) > 0).astype(float)
        snare_env = (np.sin(2 * np.pi * 4.0 * t) > 0).astype(float)
        snare = 0.15 * rng.randn(len(t)) * snare_env
        signal += kick + snare

        # Metallic hits
        hit_interval = 0.5
        hit_dur = 0.10
        for offset in [0.0, 0.25]:
            for beat in np.arange(offset, duration, hit_interval):
                start = int(beat * sr)
                end = min(len(t), start + int(hit_dur * sr))
                if start >= len(t):
                    break
                burst = rng.randn(end - start) * np.exp(-np.linspace(0.0, 5.0, end - start))
                carrier = np.sin(2 * np.pi * 900.0 * t[start:end])
                metal = (burst * carrier) * (1.0 + 0.3 * np.sin(2 * np.pi * 60.0 * t[start:end]))
                signal[start:end] += metal * 1.2

        # High-frequency shimmer
        hf = 0.08 * (rng.randn(len(t)) * 0.4) * (np.sin(2 * np.pi * 0.15 * t) + 1.0)
        signal += hf

        # Harmonic synth layer
        harmony = 0.1 * np.sin(2 * np.pi * 330.0 * t) + 0.08 * np.sin(2 * np.pi * 440.0 * t)
        signal += harmony * (np.sin(2 * np.pi * 0.5 * t) + 1.0) * 0.5

        # Volume envelope
        volume_env = 0.85 + 0.15 * np.sin(2 * np.pi * 0.1 * t)
        signal *= volume_env

        # Low-frequency reverb (delay)
        delay = int(sr * 0.03)
        reverb = np.zeros_like(signal)
        reverb[delay:] = signal[:-delay] * 0.3
        signal += reverb

        # Smoothing with Hanning window
        try:
            kernel = np.hanning(32)
            kernel /= kernel.sum()
            signal = np.convolve(signal, kernel, mode='same')
        except Exception:
            pass

        # Stereo-like detune
        try:
            detune = 0.997
            signal += 0.06 * np.sin(2 * np.pi * 55.0 * t * detune)
        except Exception:
            pass

        # Normalize and convert to PCM
        maxv = np.max(np.abs(signal))
        norm = signal if maxv < 1e-9 else signal / maxv * 0.95
        pcm = (norm * 32767.0).astype(np.int16)

        with wave.open(path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(pcm.tobytes())
        return path

    except Exception:
        try:
            import wave
            sr = 22050
            frames = b'\x00\x00' * (sr * 4)
            with wave.open(path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sr)
                wf.writeframes(frames)
            return path
        except Exception:
            return path


def ensure_urgent_bgm_variants(base_mono_path: str) -> list[str]:
    """Create multiple variations from the mono urgent BGM.

    This function ensures the mono base exists (calling `ensure_urgent_bgm`),
    then produces three variants in the same directory:
      - urgent_bgm_punchy.wav       (stereo subtle widen, slightly louder left)
      - urgent_bgm_rhythmic.wav     (stereo with a delayed right channel giving groove)
      - urgent_bgm_metallic_stereo.wav (stereo with ring-modulated right for industrial sheen)

    Returns list of created file paths (may include the base mono path).
    """
    created = []
    try:
        # ensure base mono exists
        base = ensure_urgent_bgm(base_mono_path)
        created.append(base)
        import wave
        import numpy as _np

        # read mono PCM
        with wave.open(base, 'rb') as wf:
            nch = wf.getnchannels()
            sampw = wf.getsampwidth()
            sr = wf.getframerate()
            frames = wf.readframes(wf.getnframes())
        if sampw != 2:
            # unexpected sample width; skip variant generation
            return created
        mono = _np.frombuffer(frames, dtype=_np.int16).astype(_np.float32) / 32767.0

        # helper to write stereo wav from two float32 channels (-1..1)
        def write_stereo(path, left, right, sr=sr):
            # clamp
            L = _np.clip(left, -1.0, 1.0)
            R = _np.clip(right, -1.0, 1.0)
            interleaved = _np.empty((L.size + R.size,), dtype=_np.int16)
            # convert to int16 and interleave
            Li = (L * 32767.0).astype(_np.int16)
            Ri = (R * 32767.0).astype(_np.int16)
            interleaved[0::2] = Li
            interleaved[1::2] = Ri
            with wave.open(path, 'wb') as wf:
                wf.setnchannels(2)
                wf.setsampwidth(2)
                wf.setframerate(sr)
                wf.writeframes(interleaved.tobytes())

        # Variant 1: punchy widen (slight level offset and tiny detune via resample shift)
        # right channel is a slightly delayed/attenuated copy
        delay_samples = int(0.002 * sr)  # 2ms
        right = _np.concatenate((_np.zeros(delay_samples), mono[:-delay_samples])) * 0.92
        left = mono * 1.0
        p_path = base.replace('.wav', '_punchy.wav')
        write_stereo(p_path, left, right)
        created.append(p_path)

        # Variant 2: rhythmic (right channel delayed and amplitude-modulated)
        delay_samples = int(0.012 * sr)  # 12ms
        right = _np.concatenate((_np.zeros(delay_samples), mono[:-delay_samples]))
        # apply slow tremolo on right channel to add groove
        trem = 0.85 + 0.25 * _np.sin(2 * _np.pi * 2.5 * _np.arange(len(right)) / sr)
        right = right * trem
        left = mono * 0.98
        r_path = base.replace('.wav', '_rhythmic.wav')
        write_stereo(r_path, left, right)
        created.append(r_path)

        # Variant 3: metallic_stereo (right is ring-modulated + highpass-ish)
        # ring modulation: multiply by a sine at ~900Hz; then slightly high-pass
        carrier = _np.sin(2 * _np.pi * 880.0 * _np.arange(len(mono)) / sr)
        right = mono * carrier * 0.9
        # simple high-pass by subtracting a low-moving-average
        window = int(sr * 0.02)
        if window < 1:
            window = 1
        try:
            avg = _np.convolve(right, _np.ones(window) / window, mode='same')
            right = right - 0.6 * avg
        except Exception:
            pass
        left = mono * 0.9
        m_path = base.replace('.wav', '_metallic_stereo.wav')
        write_stereo(m_path, left, right)
        created.append(m_path)

    except Exception:
        # if anything fails, just return whatever we managed to create
        return created
    return created


def ensure_urgent_bgm_dynamic(base_mono_path: str) -> str:
    """Create a more 'dynamic' stereo variant emphasizing transients and movement.

    Returns the path to the created dynamic file or the base if creation failed.
    """
    try:
        base = ensure_urgent_bgm(base_mono_path)
        import wave
        import numpy as _np

        with wave.open(base, 'rb') as wf:
            sampw = wf.getsampwidth()
            sr = wf.getframerate()
            frames = wf.readframes(wf.getnframes())
        if sampw != 2:
            return base
        mono = _np.frombuffer(frames, dtype=_np.int16).astype(_np.float32) / 32767.0

        # create stronger transient emphasis using short-time novelty (derivative of abs)
        abs_sig = _np.abs(mono)
        # novelty proxy: derivative of smoothed absolute
        smooth = _np.convolve(abs_sig, _np.ones(256) / 256.0, mode='same')
        novelty = _np.clip(_np.concatenate(([0.0], _np.diff(smooth))), 0.0, None)
        # transient boost envelope (normalized)
        if novelty.max() > 1e-9:
            t_env = 1.0 + 4.0 * (novelty / novelty.max())
        else:
            t_env = 1.0

        # rhythmic gating: create a tempo-synced tremolo (3.2Hz) for extra groove
        trem = 0.7 + 0.6 * _np.abs(_np.sin(2 * _np.pi * 3.2 * _np.arange(len(mono)) / sr))

        # apply transient boost and tremolo to emphasize movement
        left = mono * (0.9 * trem * (0.8 + 0.5 * t_env))

        # right channel: delayed, slightly detuned with ping-pong panning LFO
        delay = int(0.01 * sr)  # 10ms
        right_base = _np.concatenate((_np.zeros(delay), mono[:-delay]))
        detune = 0.9995
        right_detuned = _np.interp(_np.arange(0, len(right_base)) * detune, _np.arange(len(right_base)), right_base)
        pan_lfo = 0.5 + 0.5 * _np.sin(2 * _np.pi * 0.25 * _np.arange(len(mono)) / sr)
        right = right_detuned * (0.85 * trem * (0.7 + 0.6 * t_env)) * (0.6 + 0.8 * pan_lfo)

        # subtle stereo widening: add inverse-phase small band to each channel
        hf = _np.convolve(mono, _np.array([1, -0.5, 0.25]), mode='same') * 0.04
        left = left + hf
        right = right - hf

        # normalize channels
        peak = max(_np.max(_np.abs(left)), _np.max(_np.abs(right)), 1e-9)
        left = left / peak * 0.95
        right = right / peak * 0.95

        # write stereo file
        dyn_path = base.replace('.wav', '_dynamic.wav')
        interleaved = _np.empty((left.size + right.size,), dtype=_np.int16)
        Li = (left * 32767.0).astype(_np.int16)
        Ri = (right * 32767.0).astype(_np.int16)
        interleaved[0::2] = Li
        interleaved[1::2] = Ri
        with wave.open(dyn_path, 'wb') as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(interleaved.tobytes())
        return dyn_path
    except Exception:
        return base_mono_path
