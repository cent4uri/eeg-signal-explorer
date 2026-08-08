# Data

## `sample_eeg.edf`

A small synthetic EEG recording (8 channels, 60 seconds, 256 Hz) in
standard EDF format, so the project runs out of the box with no
external downloads.

- **Channels**: Fp1, Fp2, F3, F4, C3, C4, O1, O2 (standard 10–20 positions)
- **Sampling rate**: 256 Hz
- **Duration**: 60 seconds
- **Signal content**: simulated alpha (10 Hz, boosted at occipital
  channels O1/O2 — mimicking a relaxed, eyes-closed state), beta
  (20 Hz, boosted frontally), theta (6 Hz), 1/f-like background noise,
  and simulated 60 Hz power-line interference — useful for testing the
  notch filter.

This is **synthetic data for demonstration purposes only** — it is not
a real physiological recording and shouldn't be used to draw any
conclusions about real brain activity.

## Using your own data

`src/loader.py` supports any `.edf`, `.bdf`, or `.fif` file via
MNE-Python. Point `loader.load_eeg()` at your file path and it will
pick the right MNE reader automatically. For other formats supported
by MNE (e.g. BrainVision, EEGLAB `.set`), call the matching
`mne.io.read_raw_*` function directly.

## Public datasets

If you'd like real EEG recordings instead of synthetic data:

- **PhysioNet** — https://physionet.org/
  Hosts many open EEG datasets (e.g. the EEG Motor Movement/Imagery
  Dataset, sleep-EDF, and more), most already in EDF format.
- **OpenNeuro** — https://openneuro.org/
  A large repository of open neuroimaging datasets, including EEG,
  typically in BIDS format (often `.set` or `.fif` after conversion).

Download a recording, note its file path, and load it with:

```python
from src import loader
raw = loader.load_eeg("path/to/your_file.edf")
```
