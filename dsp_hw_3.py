import sounddevice as sd
import numpy as np
from scipy.signal import butter, lfilter

# Define the sampling rate
fs = 44100  # 44.1 kHz sampling rate

# Function to create a Butterworth filter
def butter_lowpass(cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band', analog=False)
    return b, a

# Define the cutoff frequencies for the filters
lowcut = 1000  # Low-pass filter cutoff frequency (1 kHz)
highcut = 5000  # High-pass filter cutoff frequency (5 kHz)

# Create the Butterworth filters
lowpass_b, lowpass_a = butter_lowpass(lowcut, fs)
bandpass_b, bandpass_a = butter_bandpass(lowcut, highcut, fs)

# Initialize variables to store the filtered signals
left_filtered_signal = np.zeros(0)
right_filtered_signal = np.zeros(0)

# Callback function to process the audio in real-time
def callback(indata, outdata, frames, time, status):
    if status:
        print('Error:', status)
    # Apply the filters to the input audio
    left_filtered = lfilter(lowpass_b, lowpass_a, indata[:, 0])  # Apply low-pass filter to left channel
    right_filtered = lfilter(bandpass_b, bandpass_a, indata[:, 0])  # Apply band-pass filter to right channel
    # Play the filtered audio
    outdata[:, 0] = left_filtered  # Left channel is the low-pass filtered signal
    outdata[:, 1] = right_filtered  # Right channel is the band-pass filtered signal

# Start streaming audio with the filters applied
with sd.Stream(callback=callback, blocksize=1024, channels=2, samplerate=fs):
    print('Filters applied. Press Ctrl+C to stop.')
    while True:
        sd.sleep(100)  # Sleep for a short duration to allow the stream to continue running
