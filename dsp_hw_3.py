import numpy as np
import sounddevice as sd
import soundfile as sf
from scipy.signal import butter, lfilter
import threading

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
def audio_callback(indata, outdata, frames, time, status):
    if status:
        print('Error:', status)
    
    left_channel = indata[:, 0]
    right_channel = indata[:, 1]
    
    # Apply the filters in parallel using threading
    left_thread = threading.Thread(target=apply_filter, args=(left_channel, lowpass_b, lowpass_a, 0))
    right_thread = threading.Thread(target=apply_filter, args=(right_channel, bandpass_b, bandpass_a, 1))
    
    left_thread.start()
    right_thread.start()
    
    left_thread.join()
    right_thread.join()
    
    # Play the filtered audio
    outdata[:, 0] = left_filtered_signal
    outdata[:, 1] = right_filtered_signal

def apply_filter(channel, b, a, index):
    global left_filtered_signal, right_filtered_signal
    filtered_signal = lfilter(b, a, channel)
    if index == 0:
        left_filtered_signal = filtered_signal
    else:
        right_filtered_signal = filtered_signal

# Start streaming audio with the filters applied
with sd.Stream(callback=audio_callback, blocksize=1024, channels=2, samplerate=fs):
    print('Filters applied. Press Ctrl+C to stop.')
    sd.sleep(100000)  # Sleep for a longer duration to allow the stream to continue running
