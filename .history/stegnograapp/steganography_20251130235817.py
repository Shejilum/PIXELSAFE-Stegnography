import cv2
import numpy as np
from PIL import Image
import io
import wave
import os
import tempfile

# --- HELPER: Encryption/Decryption (Simple XOR for speed) ---
def encrypt_decrypt(data_bytes, key):
    if not key:
        return data_bytes
    key_bytes = key.encode()
    key_len = len(key_bytes)
    return bytearray([b ^ key_bytes[i % key_len] for i, b in enumerate(data_bytes)])

# --- HELPER: Data to Binary ---
def to_bin(data):
    if isinstance(data, str):
        return ''.join([format(ord(i), "08b") for i in data])
    elif isinstance(data, bytes) or isinstance(data, np.ndarray):
        return [format(i, "08b") for i in data]
    elif isinstance(data, int) or isinstance(data, np.uint8):
        return format(data, "08b")
    else:
        raise TypeError("Input type not supported")

# --- 1. IMAGE STEGANOGRAPHY (Text, Audio, Video inside Image) ---
# We treat Audio/Video files simply as binary data to hide in Image

def encode_in_image(image_file, payload_data, key=None, is_file=False):
    img = Image.open(image_file)
    img = img.convert('RGB')
    image_array = np.array(img)
    
    # Prepare payload
    if is_file:
        # payload_data is bytes
        binary_payload = ''.join([format(b, "08b") for b in encrypt_decrypt(payload_data, key)])
    else:
        # payload_data is string
        binary_payload = ''.join([format(ord(i), "08b") for i in payload_data])
        if key: 
            # Simple string encryption if needed, here we just hide raw
            pass 

    # Add delimiter to know when to stop
    binary_payload += '1111111111111110' # delimiter
    
    data_len = len(binary_payload)
    max_bytes = image_array.size // 8
    
    if data_len > image_array.size:
        raise ValueError(f"Insufficient space. Carrier needs {data_len} pixels, has {image_array.size}.")

    # Fast NumPy modification
    flat_image = image_array.flatten()
    
    # Create a bitmask to clear LSB
    # We loop only through necessary pixels
    for i in range(data_len):
        flat_image[i] = (flat_image[i] & 0xFE) | int(binary_payload[i])
        
    encoded_image = flat_image.reshape(image_array.shape)
    return Image.fromarray(encoded_image.astype('uint8'))

def decode_from_image(image_file, key=None):
    img = Image.open(image_file)
    image_array = np.array(img)
    flat_image = image_array.flatten()
    
    # Extract LSBs
    lsb = flat_image & 1
    bits = "".join(lsb.astype(str))
    
    # Find delimiter
    delimiter = '1111111111111110'
    end_index = bits.find(delimiter)
    
    if end_index == -1:
        return "No hidden data found or data corrupted."
        
    binary_data = bits[:end_index]
    
    # Split into 8-bit chunks
    all_bytes = [binary_data[i: i+8] for i in range(0, len(binary_data), 8)]
    
    decoded_data = bytearray([int(byte, 2) for byte in all_bytes])
    
    if key:
        decoded_data = encrypt_decrypt(decoded_data, key)
        
    return decoded_data # Returns bytes, view handles conversion to string or file

# --- 2. IMAGE IN IMAGE ---
def merge_images(carrier_file, hidden_file):
    carrier = Image.open(carrier_file).convert('RGB')
    hidden = Image.open(hidden_file).convert('RGB')
    
    hidden = hidden.resize(carrier.size)
    
    arr_carrier = np.array(carrier)
    arr_hidden = np.array(hidden)
    
    # Take 4 MSB of hidden and put into 4 LSB of carrier
    # (Carrier & 11110000) | (Hidden >> 4)
    encoded = (arr_carrier & 0xF0) | (arr_hidden >> 4)
    
    return Image.fromarray(encoded.astype('uint8'))

def unmerge_images(steg_file):
    steg = Image.open(steg_file).convert('RGB')
    arr_steg = np.array(steg)
    
    # Extract 4 LSB and shift left
    decoded = (arr_steg & 0x0F) << 4
    
    return Image.fromarray(decoded.astype('uint8'))

# --- 3. AUDIO STEGANOGRAPHY (Text/Image inside Audio) ---
def encode_in_audio(audio_file, payload_bytes, key=None):
    # Use wave module for wav files
    song = wave.open(audio_file, mode='rb')
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))
    
    if key:
        payload_bytes = encrypt_decrypt(payload_bytes, key)
        
    # Prepare payload with delimiter
    binary_payload = ''.join([format(b, "08b") for b in payload_bytes])
    binary_payload += '1111111111111110'
    
    if len(binary_payload) > len(frame_bytes):
        raise ValueError("Audio file too short to hold data.")
        
    for i in range(len(binary_payload)):
        frame_bytes[i] = (frame_bytes[i] & 254) | int(binary_payload[i])
        
    return song.getparams(), frame_bytes

def decode_from_audio(audio_file, key=None):
    song = wave.open(audio_file, mode='rb')
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))
    
    bits = ""
    # Optimization: Don't convert ALL frames, just iterate until delimiter
    # For speed in python, we might convert chunks or use numpy
    # Here we stick to simple extraction for reliability on wav
    extracted_bits = [str(b & 1) for b in frame_bytes]
    bits = "".join(extracted_bits)
    
    delimiter = '1111111111111110'
    end_index = bits.find(delimiter)
    
    if end_index == -1: return None
    
    binary_data = bits[:end_index]
    all_bytes = [binary_data[i: i+8] for i in range(0, len(binary_data), 8)]
    decoded_data = bytearray([int(byte, 2) for byte in all_bytes])
    
    if key:
        decoded_data = encrypt_decrypt(decoded_data, key)
        
    return decoded_data

# --- 4. VIDEO STEGANOGRAPHY (Text/Image in Video) ---
# NOTE: True video steganography is slow. 
# Strategy: Hide data in the frames of the video (Frame-by-Frame LSB).
def encode_in_video(video_path, payload_bytes, output_path, key=None):
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'FFV1') # Lossless codec required
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    if key:
        payload_bytes = encrypt_decrypt(payload_bytes, key)

    binary_payload = ''.join([format(b, "08b") for b in payload_bytes])
    binary_payload += '1111111111111110'
    
    data_index = 0
    data_len = len(binary_payload)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        if data_index < data_len:
            # We treat the frame as an image and hide bits
            # Flatten only necessary part to speed up
            # This is a simplified frame encoding
            frame_flat = frame.flatten()
            remaining_bits = data_len - data_index
            available_space = len(frame_flat)
            
            bits_to_write = min(remaining_bits, available_space)
            
            for i in range(bits_to_write):
                frame_flat[i] = (frame_flat[i] & 0xFE) | int(binary_payload[data_index])
                data_index += 1
                
            frame = frame_flat.reshape(frame.shape)
            
        out.write(frame)
        
    cap.release()
    out.release()
    return True

def decode_from_video(video_path, key=None):
    cap = cv2.VideoCapture(video_path)
    bits = ""
    delimiter = '1111111111111110'
    found = False
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        frame_flat = frame.flatten()
        # Extract bits (this part can be slow for long videos)
        # Optimization: process in chunks
        chunk_bits = (frame_flat & 1).astype(str)
        bits += "".join(chunk_bits)
        
        if delimiter in bits:
            found = True
            break
            
    cap.release()
    
    if not found: return None
    
    end_index = bits.find(delimiter)
    binary_data = bits[:end_index]
    all_bytes = [binary_data[i: i+8] for i in range(0, len(binary_data), 8)]
    decoded_data = bytearray([int(byte, 2) for byte in all_bytes])
    
    if key:
        decoded_data = encrypt_decrypt(decoded_data, key)
        
    return decoded_data