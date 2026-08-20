"""
analysis.py
-----------
Frequency-domain analysis for EEG signals: FFT spectra, Welch power
spectral density (PSD), and standard EEG band-power extraction.

Standard EEG frequency bands (Hz):
    delta: 0.5–4
    theta: 4–8
    alpha: 8–13
    beta:  13–30
    gamma: 30–45
"""

import numpy as np

EEG_BANDS = {
    "delta": (0.5, 4.0),
    "theta": (4.0, 8.0),
    "alpha": (8.0, 13.0),
    "beta": (13.0, 30.0),
    "gamma": (30.0, 45.0),
}


def compute_fft(signal, sfreq):
    """
    Compute the single-sided amplitude spectrum of a 1D signal via FFT.

    Parameters
    ----------
    signal : array-like
        Time-domain signal (single channel).
    sfreq : float
        Sampling frequency in Hz.

    Returns
    -------
    freqs : np.ndarray
        Frequency bins (Hz), 0 up to Nyquist.
    amplitudes : np.ndarray
        Amplitude at each frequency bin.
    """
    signal = np.asarray(signal)
    n = len(signal)

    fft_vals = np.fft.rfft(signal)
    freqs = np.fft.rfftfreq(n, d=1.0 / sfreq)

    # Normalize to get true amplitude, single-sided spectrum
    amplitudes = np.abs(fft_vals) / n
    amplitudes[1:] *= 2  # account for folding negative frequencies in

    return freqs, amplitudes


def compute_psd(raw, fmin=0.5, fmax=45.0, verbose=False):
    """
    Compute the Welch power spectral density for every channel in an
    MNE Raw object.

    Parameters
    ----------
    raw : mne.io.Raw
    fmin, fmax : float
        Frequency range of interest, in Hz.
    verbose : bool

    Returns
    -------
    freqs : np.ndarray
        Frequency bins (Hz).
    psd : np.ndarray, shape (n_channels, n_freqs)
        Power spectral density per channel (V^2/Hz).
    ch_names : list of str
    """
    spectrum = raw.compute_psd(method="welch", fmin=fmin, fmax=fmax,
                                verbose=verbose)
    psd, freqs = spectrum.get_data(return_freqs=True)
    return freqs, psd, raw.ch_names


def band_power(freqs, psd, band):
    """
    Integrate PSD within a frequency band to get band power.

    Parameters
    ----------
    freqs : np.ndarray
        Frequency bins (Hz), matching the last axis of `psd`.
    psd : np.ndarray
        Power spectral density, shape (..., n_freqs).
    band : tuple(float, float)
        (low, high) frequency bounds in Hz. Can also pass a key from
        `EEG_BANDS`, e.g. `band_power(freqs, psd, EEG_BANDS["alpha"])`.

    Returns
    -------
    np.ndarray or float
        Band power, integrated via the trapezoidal rule over the band.
    """
    low, high = band
    mask = (freqs >= low) & (freqs <= high)
    if not np.any(mask):
        return np.zeros(psd.shape[:-1])

    trapezoid_fn = getattr(np, "trapezoid", None) or np.trapz
    return trapezoid_fn(psd[..., mask], freqs[mask], axis=-1)


def band_powers_all(freqs, psd, ch_names, bands=None):
    """
    Compute power in each standard EEG band, for every channel.

    Parameters
    ----------
    freqs : np.ndarray
    psd : np.ndarray, shape (n_channels, n_freqs)
    ch_names : list of str
    bands : dict, optional
        Mapping of band name -> (low, high) Hz. Defaults to `EEG_BANDS`.

    Returns
    -------
    dict[str, dict[str, float]]
        Nested mapping: {channel_name: {band_name: power}}.
    """
    bands = bands or EEG_BANDS
    results = {}
    for i, ch in enumerate(ch_names):
        results[ch] = {
            band_name: float(band_power(freqs, psd[i], band_range))
            for band_name, band_range in bands.items()
        }
    return results
