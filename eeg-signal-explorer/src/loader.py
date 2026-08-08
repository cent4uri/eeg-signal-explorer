"""
loader.py
---------
Utilities for loading EEG recordings using MNE-Python.

Supports any format MNE can read (EDF, BDF, FIF, etc.) via
`mne.io.read_raw`. The primary entry point is `load_eeg`, which
returns an `mne.io.Raw` object ready for preprocessing/analysis.
"""

from pathlib import Path
import mne


def load_eeg(filepath, preload=True, verbose=False):
    """
    Load an EEG recording into an MNE Raw object.

    Supports EDF (.edf), BDF (.bdf), and FIF (.fif) files out of the
    box (detected from the file extension). For other formats, use
    the appropriate `mne.io.read_raw_*` function directly.

    Parameters
    ----------
    filepath : str or Path
        Path to the EEG file.
    preload : bool
        Whether to load data into memory immediately (required for
        filtering). Defaults to True.
    verbose : bool
        Whether to show MNE's internal loading messages.

    Returns
    -------
    mne.io.Raw
        The loaded raw EEG recording.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"EEG file not found: {filepath}")

    suffix = filepath.suffix.lower()

    if suffix == ".edf":
        raw = mne.io.read_raw_edf(filepath, preload=preload, verbose=verbose)
    elif suffix == ".bdf":
        raw = mne.io.read_raw_bdf(filepath, preload=preload, verbose=verbose)
    elif suffix == ".fif":
        raw = mne.io.read_raw_fif(filepath, preload=preload, verbose=verbose)
    else:
        raise ValueError(
            f"Unsupported file extension '{suffix}'. "
            "Use .edf, .bdf, or .fif, or call the matching "
            "mne.io.read_raw_* function directly for other formats."
        )

    return raw


def summarize(raw):
    """
    Print a short human-readable summary of an MNE Raw object:
    channel names, sampling rate, and recording duration.
    """
    print(f"Channels ({len(raw.ch_names)}): {raw.ch_names}")
    print(f"Sampling rate: {raw.info['sfreq']} Hz")
    print(f"Duration: {raw.times[-1]:.2f} s")
    print(f"Samples per channel: {raw.n_times}")
