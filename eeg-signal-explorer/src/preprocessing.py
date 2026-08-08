"""
preprocessing.py
-----------------
EEG preprocessing utilities: band-pass filtering and notch (line-noise)
filtering, built on top of MNE-Python's filter implementations.

All functions operate on a *copy* of the input Raw object and return
a new Raw — the original passed in is left untouched.
"""

import mne


def bandpass_filter(raw, l_freq=1.0, h_freq=40.0, verbose=False):
    """
    Apply a band-pass filter to an EEG recording.

    Parameters
    ----------
    raw : mne.io.Raw
        The EEG recording to filter.
    l_freq : float
        Low cutoff frequency in Hz (high-pass edge). Use `None` to
        disable the high-pass side.
    h_freq : float
        High cutoff frequency in Hz (low-pass edge). Use `None` to
        disable the low-pass side.
    verbose : bool
        Show MNE's filter design messages.

    Returns
    -------
    mne.io.Raw
        A new, filtered Raw object.
    """
    filtered = raw.copy()
    filtered.filter(l_freq=l_freq, h_freq=h_freq, fir_design="firwin",
                     verbose=verbose)
    return filtered


def notch_filter(raw, freqs=60.0, verbose=False):
    """
    Remove power-line noise from an EEG recording with a notch filter.

    Parameters
    ----------
    raw : mne.io.Raw
        The EEG recording to filter.
    freqs : float or list of float
        Frequency (or frequencies) to notch out, in Hz. Use 60.0 for
        US/most of the Americas, 50.0 for Europe/most of the rest of
        the world. Pass a list (e.g. [60, 120]) to also remove
        harmonics.
    verbose : bool
        Show MNE's filter design messages.

    Returns
    -------
    mne.io.Raw
        A new, notch-filtered Raw object.
    """
    filtered = raw.copy()
    filtered.notch_filter(freqs=freqs, verbose=verbose)
    return filtered


def preprocess(raw, l_freq=1.0, h_freq=40.0, notch_freq=60.0, verbose=False):
    """
    Convenience wrapper: apply a notch filter followed by a band-pass
    filter, in one call. This is a common, sensible default EEG
    cleaning pipeline.

    Parameters
    ----------
    raw : mne.io.Raw
    l_freq, h_freq : float
        Band-pass edges in Hz (see `bandpass_filter`).
    notch_freq : float or list of float or None
        Line-noise frequency to remove (see `notch_filter`). Pass
        `None` to skip notch filtering.
    verbose : bool

    Returns
    -------
    mne.io.Raw
        A new, cleaned Raw object.
    """
    cleaned = raw.copy()
    if notch_freq is not None:
        cleaned = notch_filter(cleaned, freqs=notch_freq, verbose=verbose)
    cleaned = bandpass_filter(cleaned, l_freq=l_freq, h_freq=h_freq,
                               verbose=verbose)
    return cleaned
