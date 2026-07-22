from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from django.core.files.storage import FileSystemStorage
from .models import user, detail  # Ensure 'detail' is imported
from . import steganography as steg
import io
import os
import tempfile

# Import moviepy for audio conversion (MP3 -> WAV)
try:
    from moviepy import AudioFileClip
except ImportError:
    try:
        from moviepy.audio.io.AudioFileClip import AudioFileClip
    except ImportError:
        AudioFileClip = None

# --- Helper to detect file type from binary data ---
def get_file_extension(data_bytes):
    if len(data_bytes) < 4: return '.bin' 
    
    # --- Images ---
    if data_bytes.startswith(b'\x89PNG\r\n\x1a\n'): return '.png'
    if data_bytes.startswith(b'\xff\xd8'): return '.jpg'
    if data_bytes.startswith(b'GIF87a') or data_bytes.startswith(b'GIF89a'): return '.gif'
    if data_bytes.startswith(b'BM'): return '.bmp'
    if data_bytes.startswith(b'MM\x00\x2a') or data_bytes.startswith(b'II\x2a\x00'): return '.tiff'
    if data_bytes.startswith(b'RIFF') and data_bytes[8:12] == b'WEBP': return '.webp'

    # --- Audio ---
    if data_bytes.startswith(b'ID3'): return '.mp3' 
    if data_bytes.startswith(b'\xff\xfb'): return '.mp3' 
    if data_bytes.startswith(b'fLaC'): return '.flac'
    if data_bytes.startswith(b'OggS'): return '.ogg'
    if data_bytes.startswith(b'RIFF') and data_bytes[8:12] == b'WAVE': return '.wav'

    # --- Video ---
    if data_bytes.startswith(b'RIFF') and data_bytes[8:12] == b'AVI ': return '.avi'
    if len(data_bytes) > 12 and data_bytes[4:8] == b'ftyp': return '.mp4'
    if data_bytes.startswith(b'\x1aE\xdf\xa3'): return '.mkv'
    
    return '.bin'

# --- VIEWS ---

def index(request):
    return render(request, 'index.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if user.objects.filter(email=email, password=password).exists():
            request.session['email'] = email
            return redirect('main')
        else:
            return HttpResponse("Invalid email or password")
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confirmpassword')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        image = request.FILES.get('image')
        
        if user.objects.filter(email=email).exists():
            return HttpResponse("Email already exists")
        elif user.objects.filter(phone=phone).exists():
            return HttpResponse("Phone number already exists")
        elif user.objects.filter(username=username).exists():
            return HttpResponse("Username already exists")
        else:
            if password != confirmpassword:
                return HttpResponse("Password and Confirm Password are not matching")
            else:
                new_user = user(username=username, password=password, confirmpassword=confirmpassword, email=email, phone=phone, image=image)
                new_user.save()
                return redirect('login')
    return render(request, 'register.html')

def main(request):
    context = {}
    
    # Get user details for navbar if needed
    if 'email' in request.session:
        try:
            current_user = user.objects.get(email=request.session['email'])
            context['user'] = current_user
        except: pass

    if request.method == 'POST':
        action = request.POST.get('action_type') # 'encode' or 'decode'
        steg_mode = request.POST.get('steg_mode') # e.g. 'text-in-image'
        password = request.POST.get('password')
        
        # stats object
        d = detail.objects.first()
        if not d:
             # Create a default stats object if none exists to avoid crash
            d = detail.objects.create()

        try:
            # ================= ENCODING =================
            if action == 'encode':
                carrier = request.FILES.get('carrier_file')
                output_io = io.BytesIO()
                filename = "stego_output"
                
                # --- 1. CARRIER: IMAGE ---
                if 'in-image' in steg_mode:
                    secret_data = None
                    is_text = False
                    
                    if steg_mode == 'text-in-image':
                        secret_data = request.POST.get('secret_text')
                        is_text = True
                        d.encode_text_in_image_number += 1
                    else:
                        secret_file = request.FILES.get('secret_file')
                        secret_data = secret_file.read()
                        
                        if steg_mode == 'image-in-image': d.encode_image_in_image_number += 1
                        elif steg_mode == 'video-in-image': d.encode_video_in_image_number += 1
                        elif steg_mode == 'audio-in-image': d.encode_audio_in_image_number += 1

                    result_img = steg.encode_in_image(carrier, secret_data, password, is_text)
                    result_img.save(output_io, format='PNG')
                    filename += ".png"
                    
                # --- 2. CARRIER: AUDIO ---
                elif 'in-audio' in steg_mode:
                    # Save uploaded file
                    suffix = os.path.splitext(carrier.name)[1]
                    if not suffix: suffix = '.wav'
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        for chunk in carrier.chunks(): tmp.write(chunk)
                        tmp_carrier = tmp.name
                    
                    # Convert to WAV (PCM-16)
                    carrier_wav = tmp_carrier + "_converted.wav"
                    process_path = tmp_carrier
                    clip = None

                    try:
                        if AudioFileClip:
                            clip = AudioFileClip(tmp_carrier)
                            clip.write_audiofile(carrier_wav, codec='pcm_s16le', verbose=False, logger=None)
                            process_path = carrier_wav
                    except Exception:
                        pass 
                    finally:
                        if clip: 
                            try: clip.close() 
                            except: pass

                    tmp_out = process_path + "_out.wav"
                    
                    try:
                        if steg_mode == 'text-in-audio':
                            steg.encode_in_audio(process_path, request.POST.get('secret_text'), tmp_out, password, True)
                            d.encode_text_in_audio_number += 1
                        else:
                            secret_data = request.FILES.get('secret_file').read()
                            steg.encode_in_audio(process_path, secret_data, tmp_out, password, False)
                            
                            if steg_mode == 'image-in-audio': d.encode_image_in_audio_number += 1
                            elif steg_mode == 'audio-in-audio': d.encode_audio_in_audio_number += 1
                            elif steg_mode == 'video-in-audio': d.encode_video_in_audio_number += 1

                        with open(tmp_out, 'rb') as f: output_io.write(f.read())
                        filename += ".wav"
                    finally:
                        # Clean up
                        for p in [tmp_carrier, carrier_wav, tmp_out]:
                            if os.path.exists(p): 
                                try: os.unlink(p) 
                                except: pass

                # --- 3. CARRIER: VIDEO ---
                elif 'in-video' in steg_mode:
                    suffix = os.path.splitext(carrier.name)[1]
                    if not suffix: suffix = '.avi'

                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        for chunk in carrier.chunks(): tmp.write(chunk)
                        tmp_carrier = tmp.name
                    
                    tmp_out = tmp_carrier + "_out.avi"
                    
                    try:
                        if steg_mode == 'text-in-video':
                            steg.encode_in_video(tmp_carrier, request.POST.get('secret_text'), tmp_out, password, True)
                            d.encode_text_in_video_number += 1
                        else:
                            secret_data = request.FILES.get('secret_file').read()
                            steg.encode_in_video(tmp_carrier, secret_data, tmp_out, password, False)
                            
                            if steg_mode == 'image-in-video': d.encode_image_in_video_number += 1
                            elif steg_mode == 'audio-in-video': d.encode_audio_in_video_number += 1
                            elif steg_mode == 'video-in-video': d.encode_video_in_video_number += 1

                        with open(tmp_out, 'rb') as f: output_io.write(f.read())
                        filename += ".avi"
                    finally:
                        if os.path.exists(tmp_carrier): os.unlink(tmp_carrier)
                        if os.path.exists(tmp_out): os.unlink(tmp_out)

                d.save()
                output_io.seek(0)
                return FileResponse(output_io, as_attachment=True, filename=filename)

            # ================= DECODING =================
            elif action == 'decode':
                stego_file = request.FILES.get('stego_file')
                result_data = None
                
                # --- DECODE IMAGE ---
                if 'image' in stego_file.content_type or stego_file.name.lower().endswith(('png','jpg','jpeg')):
                    result_data = steg.decode_from_image(stego_file, password, 'text' in steg_mode)

                # --- DECODE AUDIO ---
                elif 'audio' in stego_file.content_type or stego_file.name.lower().endswith('wav'):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                        for chunk in stego_file.chunks(): tmp.write(chunk)
                        tmp_path = tmp.name
                    try:
                        result_data = steg.decode_from_audio(tmp_path, password, 'text' in steg_mode)
                    finally:
                        os.unlink(tmp_path)
                      
                # --- DECODE VIDEO ---
                elif 'video' in stego_file.content_type or stego_file.name.lower().endswith(('avi', 'mp4')):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".avi") as tmp:
                        for chunk in stego_file.chunks(): tmp.write(chunk)
                        tmp_path = tmp.name
                    try:
                        result_data = steg.decode_from_video(tmp_path, password, 'text' in steg_mode)
                    finally:
                        os.unlink(tmp_path)

                if result_data is not None:
                    # Success
                    if 'text' in steg_mode:
                        context['result_text'] = result_data
                        context['success_msg'] = "Text Decoded Successfully!"
                        
                        # Stats for text decoding
                        if steg_mode == 'text-in-image': d.decode_text_in_image_number += 1
                        elif steg_mode == 'text-in-video': d.decode_text_in_video_number += 1
                        elif steg_mode == 'text-in-audio': d.decode_text_in_audio_number += 1
                        d.save()
                    else:
                        out_io = io.BytesIO(result_data)
                        ext = get_file_extension(result_data)
                        fname = f"revealed_file{ext}"
                        
                        # Stats for file decoding
                        if steg_mode == 'image-in-image': d.decode_image_in_image_number += 1
                        elif steg_mode == 'video-in-image': d.decode_video_in_image_number += 1
                        elif steg_mode == 'audio-in-image': d.decode_audio_in_image_number += 1
                        elif steg_mode == 'image-in-video': d.decode_image_in_video_number += 1
                        elif steg_mode == 'image-in-audio': d.decode_image_in_audio_number += 1
                        
                        # NEW STATS (Ensure these fields exist in your model)
                        elif steg_mode == 'audio-in-audio': d.decode_audio_in_audio_number += 1
                        elif steg_mode == 'video-in-audio': d.decode_video_in_audio_number += 1
                        elif steg_mode == 'audio-in-video': d.decode_audio_in_video_number += 1
                        elif steg_mode == 'video-in-video': d.decode_video_in_video_number += 1

                        d.save()
                        
                        context['success_msg'] = f"File Decoded Successfully! ({ext})"
                        return FileResponse(out_io, as_attachment=True, filename=fname)
                else:
                    context['error'] = "No hidden data found or incorrect password."

        except ValueError as ve:
             context['error'] = f"Data Error: {str(ve)} (The file might be too large for this carrier)"
        except Exception as e:
            context['error'] = f"System Error: {str(e)}"

    return render(request, 'main.html', context)

# --- ADMIN & PROFILE VIEWS ---

def adminlogin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if email == "admin@bca" and password == "bca123":
            request.session['email'] = email
            return redirect('admindash')
        else:
            return HttpResponse("Invalid email or password")
    return render(request, 'adminlogin.html')

def profile(request):
    if 'email' in request.session:
        email = request.session['email']
        try:
            current_user = user.objects.get(email=email)
            return render(request, 'profile.html', {'user': current_user})
        except user.DoesNotExist:
            return HttpResponse("User not found")
    return redirect('login')

def admindash(request):
    d = detail.objects.first()
    b = user.objects.all()
    # Pass 'd' to template so you can see the stats
    return render(request, 'admindash.html', {'b': b, 'stats': d})

def editprofile(request):
    if 'email' in request.session:
        email = request.session['email']
        try:
            client = user.objects.get(email=email)

            if request.method == 'POST':
                username = request.POST.get('username')
                if user.objects.exclude(id=client.id).filter(username=username).exists():
                    return HttpResponse("Username already exists")
                client.username = username
                
                phone = request.POST.get('phone')
                if user.objects.exclude(id=client.id).filter(phone=phone).exists():
                    return HttpResponse("Phone number already exists")
                client.phone = phone

                new_image = request.FILES.get('image')
                if new_image:  
                    client.image = new_image  

                password = request.POST.get('password')
                conf = request.POST.get('confirmpassword')

                if password:
                    if password == conf:
                        client.password = password
                    else:
                        return HttpResponse("Passwords do not match")

                client.save()
                return redirect('profile')

            return render(request, 'editprofile.html', {'client': client})

        except user.DoesNotExist:
            return HttpResponse("User not found")

    return redirect('login')

def logout(request):
    request.session.flush()
    return redirect('index')

def userlist(request):
    a = user.objects.all()
    return render(request, 'userlist.html', {'a': a})

def deleteuser(request, email):
    try:
        u = user.objects.get(email=email)
        u.delete()
        return redirect('userlist')
    except user.DoesNotExist:
        return HttpResponse("User not found")
    
    