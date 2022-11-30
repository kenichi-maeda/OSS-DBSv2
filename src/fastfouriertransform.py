
from dataclasses import dataclass
from src.signals import Signal
import numpy as np


@dataclass
class FFTSineWave:
    amplitude: float
    frequency: float

    def __gt__(self, other: 'FFTSineWave') -> bool:
        amplitude1 = abs(self.amplitude)
        amplitude2 = abs(other.amplitude)

        if amplitude1 < amplitude2:
            return False

        if amplitude1 == amplitude2 and self.frequency >= other.frequency:
            return False

        return True


class FFT:

    SPACING_FACTOR = 1e5

    def __init__(self, signal: Signal) -> None:
        self.__signal = signal

    def sine_waves(self) -> list:
        sample_spacing = 1 / (self.__signal.frequency * self.SPACING_FACTOR)
        samples = self.__signal.generate_samples(sample_spacing=sample_spacing)
        amplitudes = np.fft.rfft(samples) / len(samples) * 2
        frequencies = np.fft.rfftfreq(len(samples), sample_spacing)
        return [FFTSineWave(amplitude=amp, frequency=freq)
                for amp, freq in zip(amplitudes, frequencies)]

    def octave_bands(self) -> list:
        sample_spacing = 1 / (self.__signal.frequency * self.SPACING_FACTOR)
        samples = self.__signal.generate_samples(sample_spacing=sample_spacing)
        amplitudes = np.fft.rfft(samples) / len(samples) * 2
        frequencies = np.fft.rfftfreq(len(samples), sample_spacing)
        n_octave_bands = int(np.log2(len(frequencies) - 1))
        indices = [2 ** index for index in range(n_octave_bands)]
        octave_freq = frequencies[indices] * np.sqrt(2)
        octave_ampl = [amplitudes[idx] for idx in indices]
        waves = [FFTSineWave(amplitude, frequency)
                 for amplitude, frequency in zip(octave_ampl, octave_freq)]
        return [FFTSineWave(amplitudes[0], frequencies[0])] + waves
