"""
visualization.py
-----------------
Matplotlib-based plotting helpers for EEG data: raw waveforms,
filtered-vs-raw comparisons, FFT spectra, power spectral density,
multi-channel plots, and band-power summaries.
"""

import numpy as np
import matplotlib.pyplot as plt

from . import analysis


def _get_channel_data(raw, channel):
    """Return (data, times) for a single channel name from an MNE Raw."""
    idx = raw.ch_names.index(channel)
    data, times = raw[idx, :]
    return data[0], times


def plot_raw_signal(raw, channel=None, duration=None, ax=None,
                     title=None):
    """
    Plot the raw time-domain EEG waveform for a single channel.

    Parameters
    ----------
    raw : mne.io.Raw
    channel : str, optional
        Channel name to plot. Defaults to the first channel.
    duration : float, optional
        Number of seconds to plot, starting from t=0. Defaults to
        the full recording.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 3.5))

    channel = channel or raw.ch_names[0]
    data, times = _get_channel_data(raw, channel)

    if duration is not None:
        n_samples = int(duration * raw.info["sfreq"])
        data, times = data[:n_samples], times[:n_samples]

    # convert Volts -> microvolts for readability
    ax.plot(times, data * 1e6, color="black", linewidth=0.7)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude (\u00b5V)")
    ax.set_title(title or f"Raw EEG Signal — {channel}")
    return ax


def plot_filtered_comparison(raw_before, raw_after, channel=None,
                              duration=5.0, ax=None,
                              title=None):
    """
    Overlay raw vs. filtered EEG for a single channel, so the effect
    of filtering is directly visible.

    Parameters
    ----------
    raw_before : mne.io.Raw
        Signal before filtering.
    raw_after : mne.io.Raw
        Signal after filtering.
    channel : str, optional
    duration : float
        Seconds to plot (short windows make filtering effects easier
        to see). Defaults to 5 seconds.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 3.5))

    channel = channel or raw_before.ch_names[0]
    before, times = _get_channel_data(raw_before, channel)
    after, _ = _get_channel_data(raw_after, channel)

    n_samples = int(duration * raw_before.info["sfreq"])
    before, after, times = before[:n_samples], after[:n_samples], times[:n_samples]

    ax.plot(times, before * 1e6, color="lightgray", linewidth=1.0, label="Raw")
    ax.plot(times, after * 1e6, color="crimson", linewidth=1.0, label="Filtered")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude (\u00b5V)")
    ax.set_title(title or f"Raw vs. Filtered — {channel}")
    ax.legend(loc="upper right")
    return ax


def plot_multichannel(raw, duration=None, channels=None, ax=None,
                       title="Multi-Channel EEG"):
    """
    Stack-plot multiple EEG channels, offset vertically for visibility
    (a simplified version of MNE's built-in browser view).

    Parameters
    ----------
    raw : mne.io.Raw
    duration : float, optional
        Seconds to plot. Defaults to full recording.
    channels : list of str, optional
        Channels to include. Defaults to all channels.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))

    channels = channels or raw.ch_names
    data, times = raw.get_data(picks=channels, return_times=True)

    if duration is not None:
        n_samples = int(duration * raw.info["sfreq"])
        data, times = data[:, :n_samples], times[:n_samples]

    data_uv = data * 1e6
    # Offset each channel so traces don't overlap
    offset_step = np.max(np.abs(data_uv)) * 2.2 if data_uv.size else 1.0

    for i, ch in enumerate(channels):
        offset = -i * offset_step
        ax.plot(times, data_uv[i] + offset, color="black", linewidth=0.6)

    ax.set_yticks([-i * offset_step for i in range(len(channels))])
    ax.set_yticklabels(channels)
    ax.set_xlabel("Time (s)")
    ax.set_title(title)
    return ax


def plot_fft(signal, sfreq, fmax=60.0, ax=None, title="Frequency Spectrum (FFT)"):
    """
    Plot the single-sided FFT amplitude spectrum of a signal.

    Parameters
    ----------
    signal : array-like
        Time-domain signal for one channel.
    sfreq : float
        Sampling frequency in Hz.
    fmax : float
        Upper frequency limit to display, in Hz.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 4))

    freqs, amplitudes = analysis.compute_fft(signal, sfreq)
    mask = freqs <= fmax

    ax.plot(freqs[mask], amplitudes[mask] * 1e6, color="darkorange", linewidth=1.0)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Amplitude (\u00b5V)")
    ax.set_title(title)
    return ax


def plot_psd(raw, fmin=0.5, fmax=45.0, ax=None, title="Power Spectral Density"):
    """
    Plot Welch power spectral density for every channel in a Raw object.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 4.5))

    freqs, psd, ch_names = analysis.compute_psd(raw, fmin=fmin, fmax=fmax)

    for i, ch in enumerate(ch_names):
        # convert V^2/Hz -> microvolts^2/Hz and use log scale for readability
        ax.semilogy(freqs, psd[i] * 1e12, linewidth=1.0, label=ch)

    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("PSD (\u00b5V\u00b2/Hz)")
    ax.set_title(title)
    ax.legend(loc="upper right", fontsize=8, ncol=2)
    return ax


def plot_band_powers(freqs, psd, ch_names, ax=None,
                      title="EEG Band Power by Channel"):
    """
    Grouped bar chart of band power (delta/theta/alpha/beta/gamma) for
    every channel.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 4.5))

    powers = analysis.band_powers_all(freqs, psd, ch_names)
    band_names = list(analysis.EEG_BANDS.keys())

    x = np.arange(len(ch_names))
    width = 0.15

    for i, band in enumerate(band_names):
        values = [powers[ch][band] * 1e12 for ch in ch_names]  # -> uV^2
        ax.bar(x + i * width, values, width=width, label=band)

    ax.set_xticks(x + width * (len(band_names) - 1) / 2)
    ax.set_xticklabels(ch_names)
    ax.set_ylabel("Band power (\u00b5V\u00b2)")
    ax.set_title(title)
    ax.legend(loc="upper right", fontsize=8)
    return ax
