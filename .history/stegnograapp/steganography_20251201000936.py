import cv2
import numpy as np
from PIL import Image
import io
import wave
import os
import tempfile

# --- HELPER: Encryption/Decryption ---
def xor_encrypt_decrypt(data_bytes, key):
    if not key: return data_bytes
    key_bytes = key.encode('utf-8')
    key_len = len(key_bytes)
    # Ensure input is bytes-like
    if isinstance(data_bytes, str):
        data_bytes = data_bytes.encode('utf-8')
        
    return bytearray([b ^ key_bytes[i % key_len] for i, b in enumerate(data_bytes)])

def bytes_to_bin(data):
    # Generates binary string from bytes/bytearray
    return ''.join(format(b, '08b') for b in data)

def bin_to_bytes(binary):
    return bytearray(int(binary[i:i+8], 2) for i in range(0, len(binary), 8))

#Delimiter to mark end of data
DELIMITER = '11111111111111101111111111111110' 

# ==========================================
# 1. CARRIER: IMAGE
# ==========================================

def encode_in_image(carrier_img_file, secret_data, key=None, is_text=True):
    img = Image.open(carrier_img_file).convert('RGB')
    arr = np.array(img)
    
    # ROBUST DATA PREPARATION (Fixes the 'str' error)
    if isinstance(secret_data, str):
        data_bytes = secret_data.encode('utf-8')
    elif isinstance(secret_data, (bytes, bytearray)):
        data_bytes = secret_data
    else:
        # Fallback for None or other types
        data_bytes = str(secret_data or '').encode('utf-8')

    # Encrypt
    if key: data_bytes = xor_encrypt_decrypt(data_bytes, key)

    # Convert to binary
    bits = bytes_to_bin(data_bytes) + DELIMITER
    
    if len(bits) > arr.size:
        raise ValueError(f"Data too large. Need {len(bits)} bits, have {arr.size}.")

    flat = arr.flatten()
    
    # Embed Bits
    bit_array = np.array(list(bits), dtype=int)
    flat[:len(bits)] = (flat[:len(bits)] & 0xFE) | bit_array
    
    encoded_arr = flat.reshape(arr.shape)
    return Image.fromarray(encoded_arr.astype('uint8'))

def decode_from_image(stego_img_file, key=None, is_text=True):
    img = Image.open(stego_img_file).convert('RGB')
    arr = np.array(img)
    flat = arr.flatten()
    
    lsb = flat & 1
    # Check first 1MB for speed
    bits_str = "".join(lsb[:1000000].astype(str))
    
    if DELIMITER not in bits_str:
        bits_str = "".join(lsb.astype(str))
    
    end_idx = bits_str.find(DELIMITER)
    if end_idx == -1: return None
    
    data_bytes = bin_to_bytes(bits_str[:end_idx])
    
    if key: data_bytes = xor_encrypt_decrypt(data_bytes, key)
    
    if is_text:
        try: return data_bytes.decode('utf-8')
        except: return str(data_bytes)
    else:
        return data_bytes

# ==========================================
# 2. CARRIER: AUDIO
# ==========================================

def encode_in_audio(carrier_audio_path, secret_data, output_path, key=None, is_text=True):
    song = wave.open(carrier_audio_path, mode='rb')
    n_frames = song.getnframes()
    frames = bytearray(song.readframes(n_frames))
    
    # ROBUST DATA PREPARATION
    if isinstance(secret_data, str):
        data_bytes = secret_data.encode('utf-8')
    elif isinstance(secret_data, (bytes, bytearray)):
        data_bytes = secret_data
    else:
        data_bytes = str(secret_data or '').encode('utf-8')
        
    if key: data_bytes = xor_encrypt_decrypt(data_bytes, key)
    
    bits = bytes_to_bin(data_bytes) + DELIMITER
    
    if len(bits) > len(frames):
        raise ValueError("Audio file too short.")
        
    for i, bit in enumerate(bits):
        frames[i] = (frames[i] & 254) | int(bit)
        
    with wave.open(output_path, 'wb') as fd:
        fd.setparams(song.getparams())
        fd.writeframes(frames)
    song.close()
    return output_path

def decode_from_audio(stego_audio_path, key=None, is_text=True):
    song = wave.open(stego_audio_path, mode='rb')
    n_frames = song.getnframes()
    frames = bytearray(song.readframes(n_frames))
    
    bits = "".join([str(b & 1) for b in frames])
    
    end_idx = bits.find(DELIMITER)
    if end_idx == -1: return None
    
    data_bytes = bin_to_bytes(bits[:end_idx])
    
    if key: data_bytes = xor_encrypt_decrypt(data_bytes, key)
    
    if is_text:
        try: return data_bytes.decode('utf-8', errors='ignore')
        except: return str(data_bytes)
    else:
        return data_bytes

# ==========================================
# 3. CARRIER: VIDEO
# ==========================================

def encode_in_video(video_path, secret_data, output_path, key=None, is_text=True):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'FFV1') 
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # ROBUST DATA PREPARATION
    if isinstance(secret_data, str):
        data_bytes = secret_data.encode('utf-8')
    elif isinstance(secret_data, (bytes, bytearray)):
        data_bytes = secret_data
    else:
        data_bytes = str(secret_data or '').encode('utf-8')

    if key: data_bytes = xor_encrypt_decrypt(data_bytes, key)
    bits = bytes_to_bin(data_bytes) + DELIMITER
    bit_idx = 0
    bits_len = len(bits)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        if bit_idx < bits_len:
            flat = frame.flatten()
            available = len(flat)
            needed = bits_len - bit_idx
            to_write = min(available, needed)
            
            chunk = np.array(list(bits[bit_idx : bit_idx+to_write]), dtype=int)
            flat[:to_write] = (flat[:to_write] & 0xFE) | chunk
            frame = flat.reshape(frame.shape)
            bit_idx += to_write
            
        out.write(frame)
        
    cap.release()
    out.release()
    return output_path

def decode_from_video(video_path, key=None, is_text=True):
    cap = cv2.VideoCapture(video_path)
    bits_list = []
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        flat = frame.flatten()
        b = (flat & 1).astype(str)
        bits_list.append("".join(b))
        
        current_bits = "".join(bits_list)
        if DELIMITER in current_bits:
            break
            
    cap.release()
    full_bits = "".join(bits_list)
    end_idx = full_bits.find(DELIMITER)
    
    if end_idx == -1: return None
    
    data_bytes = bin_to_bytes(full_bits[:end_idx])
    if key: data_bytes = xor_encrypt_decrypt(data_bytes, key)
    
    if is_text:
        try: return data_bytes.decode('utf-8', errors='ignore')
        except: return str(data_bytes)
    else:
        return data_bytes