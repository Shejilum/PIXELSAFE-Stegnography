from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from django.core.files.storage import FileSystemStorage
from .models import user, detail, upload  # Ensure 'upload' is imported
from . import steganography as steg
import io
import os
import tempfile
from django.utils import timezone
from django.shortcuts import render, redirect
from .models import user, detail, upload
from django.utils import timezone
from datetime import timedelta
import json

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
    if data_bytes.startswith(b'\x89PNG\r\n\x1a\n'): return '.png'
    if data_bytes.startswith(b'\xff\xd8'): return '.jpg'
    if data_bytes.startswith(b'GIF87a') or data_bytes.startswith(b'GIF89a'): return '.gif'
    if data_bytes.startswith(b'BM'): return '.bmp'
    if data_bytes.startswith(b'RIFF') and data_bytes[8:12] == b'WEBP': return '.webp'
    if data_bytes.startswith(b'ID3') or data_bytes.startswith(b'\xff\xfb'): return '.mp3' 
    if data_bytes.startswith(b'fLaC'): return '.flac'
    if data_bytes.startswith(b'OggS'): return '.ogg'
    if data_bytes.startswith(b'RIFF') and data_bytes[8:12] == b'WAVE': return '.wav'
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
    if 'email' in request.session:
        try: context['user'] = user.objects.get(email=request.session['email'])
        except: pass

    if request.method == 'POST':
        action = request.POST.get('action_type')
        steg_mode = request.POST.get('steg_mode')
        password = request.POST.get('password')
        
        # Helper to prevent NoneType error (e.g., if stats are NULL)
        def inc(val): return (val or 0) + 1

        d = detail.objects.first()
        if not d: d = detail.objects.create()

        try:
            # ================= ENCODING =================
            if action == 'encode':
                carrier = request.FILES.get('carrier_file')
                output_io = io.BytesIO()
                filename = "stego_output"
                
                # --- LOG ACTIVITY: Save to Upload Model with Activity Type ---
                try:
                    # Create readable string: "text-in-image" -> "Text In Image"
                    if steg_mode:
                        readable_mode = steg_mode.replace('-', ' ').title()
                        desc = f"Encoded: {readable_mode}"
                    else:
                        desc = "Encoded File"
                        
                    log_entry = upload(media=carrier, activity_type=desc)
                    log_entry.save()
                    # CRITICAL: Reset file pointer so processing can read it from start
                    carrier.seek(0)
                except Exception as e:
                    print(f"Logging failed: {e}")

                # --- 1. CARRIER: IMAGE ---
                if 'in-image' in steg_mode:
                    secret_data = None
                    is_text = False
                    
                    if steg_mode == 'text-in-image':
                        secret_data = request.POST.get('secret_text')
                        is_text = True
                        d.encode_text_in_image_number = inc(d.encode_text_in_image_number)
                        d.date_encode_text_in_image_number = timezone.now()
                    else:
                        secret_file = request.FILES.get('secret_file')
                        secret_data = secret_file.read()
                        
                        if steg_mode == 'image-in-image': 
                            d.encode_image_in_image_number = inc(d.encode_image_in_image_number)
                            d.date_encode_image_in_image_number = timezone.now()
                        elif steg_mode == 'video-in-image': 
                            d.encode_video_in_image_number = inc(d.encode_video_in_image_number)
                            d.date_encode_video_in_image_number = timezone.now()
                        elif steg_mode == 'audio-in-image': 
                            d.encode_audio_in_image_number = inc(d.encode_audio_in_image_number)
                            d.date_encode_audio_in_image_number = timezone.now()

                    result_img = steg.encode_in_image(carrier, secret_data, password, is_text)
                    result_img.save(output_io, format='PNG')
                    filename += ".png"
                    
                # --- 2. CARRIER: AUDIO ---
                elif 'in-audio' in steg_mode:
                    suffix = os.path.splitext(carrier.name)[1] or '.wav'
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        for chunk in carrier.chunks(): tmp.write(chunk)
                        tmp_carrier = tmp.name
                    
                    carrier_wav = tmp_carrier + "_converted.wav"
                    process_path = tmp_carrier
                    clip = None

                    try:
                        if AudioFileClip:
                            clip = AudioFileClip(tmp_carrier)
                            clip.write_audiofile(carrier_wav, codec='pcm_s16le', verbose=False, logger=None)
                            process_path = carrier_wav
                    except Exception: pass 
                    finally:
                        if clip: 
                            try: clip.close() 
                            except: pass

                    tmp_out = process_path + "_out.wav"
                    
                    try:
                        if steg_mode == 'text-in-audio':
                            steg.encode_in_audio(process_path, request.POST.get('secret_text'), tmp_out, password, True)
                            d.encode_text_in_audio_number = inc(d.encode_text_in_audio_number)
                            d.date_encode_text_in_audio_number = timezone.now()
                        else:
                            secret_data = request.FILES.get('secret_file').read()
                            steg.encode_in_audio(process_path, secret_data, tmp_out, password, False)
                            
                            if steg_mode == 'image-in-audio': 
                                d.encode_image_in_audio_number = inc(d.encode_image_in_audio_number)
                                d.date_encode_image_in_audio_number = timezone.now()
                            elif steg_mode == 'audio-in-audio': 
                                d.encode_audio_in_audio_number = inc(d.encode_audio_in_audio_number)
                                d.date_encode_image_in_audio_number = timezone.now() # Using existing date field or add new if needed
                            elif steg_mode == 'video-in-audio': 
                                d.encode_video_in_audio_number = inc(d.encode_video_in_audio_number)
                                d.date_encode_image_in_audio_number = timezone.now()

                        with open(tmp_out, 'rb') as f: output_io.write(f.read())
                        filename += ".wav"
                    finally:
                        for p in [tmp_carrier, carrier_wav, tmp_out]:
                            if os.path.exists(p): 
                                try: os.unlink(p) 
                                except: pass

                # --- 3. CARRIER: VIDEO ---
                elif 'in-video' in steg_mode:
                    suffix = os.path.splitext(carrier.name)[1] or '.avi'
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        for chunk in carrier.chunks(): tmp.write(chunk)
                        tmp_carrier = tmp.name
                    
                    tmp_out = tmp_carrier + "_out.avi"
                    try:
                        if steg_mode == 'text-in-video':
                            steg.encode_in_video(tmp_carrier, request.POST.get('secret_text'), tmp_out, password, True)
                            d.encode_text_in_video_number = inc(d.encode_text_in_video_number)
                            d.date_encode_text_in_video_number = timezone.now()
                        else:
                            secret_data = request.FILES.get('secret_file').read()
                            steg.encode_in_video(tmp_carrier, secret_data, tmp_out, password, False)
                            
                            if steg_mode == 'image-in-video': 
                                d.encode_image_in_video_number = inc(d.encode_image_in_video_number)
                                d.date_encode_image_in_video_number = timezone.now()
                            elif steg_mode == 'audio-in-video': 
                                d.encode_audio_in_video_number = inc(d.encode_audio_in_video_number)
                                d.date_encode_image_in_video_number = timezone.now()
                            elif steg_mode == 'video-in-video': 
                                d.encode_video_in_video_number = inc(d.encode_video_in_video_number)
                                d.date_encode_image_in_video_number = timezone.now()

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
                
                # --- LOG ACTIVITY ---
                try:
                    desc = "Decoded File"
                    if 'text' in str(steg_mode): desc = "Decoded Text"
                    
                    log_entry = upload(stego_media=stego_file, activity_type=desc)
                    log_entry.save()
                    stego_file.seek(0)
                except Exception: pass

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
                    if 'text' in steg_mode:
                        context['result_text'] = result_data
                        context['success_msg'] = "Text Decoded Successfully!"
                        
                        if steg_mode == 'text-in-image': d.decode_text_in_image_number = inc(d.decode_text_in_image_number)
                        elif steg_mode == 'text-in-video': d.decode_text_in_video_number = inc(d.decode_text_in_video_number)
                        elif steg_mode == 'text-in-audio': d.decode_text_in_audio_number = inc(d.decode_text_in_audio_number)
                        d.save()
                    else:
                        out_io = io.BytesIO(result_data)
                        ext = get_file_extension(result_data)
                        fname = f"revealed_file{ext}"
                        
                        # Update Decode Stats
                        d.decode_image_in_image_number = inc(d.decode_image_in_image_number) # Generic count
                        d.save()
                        
                        context['success_msg'] = f"File Decoded Successfully! ({ext})"
                        return FileResponse(out_io, as_attachment=True, filename=fname)
                else:
                    context['error'] = "No hidden data found or incorrect password."

        except ValueError as ve:
             context['error'] = f"Data Error: {str(ve)}"
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
            
            d = detail.objects.first()
            if not d: d = detail.objects.create()

            # Helper
            def g(v): return v or 0

            # Calculate Totals
            encodes = [
                g(d.encode_text_in_image_number), g(d.encode_image_in_image_number),
                g(d.encode_video_in_image_number), g(d.encode_audio_in_image_number),
                g(d.encode_text_in_video_number), g(d.encode_image_in_video_number),
                g(d.encode_audio_in_video_number), g(d.encode_video_in_video_number),
                g(d.encode_text_in_audio_number), g(d.encode_image_in_audio_number),
                g(d.encode_audio_in_audio_number), g(d.encode_video_in_audio_number)
            ]
            decodes = [
                g(d.decode_text_in_image_number), g(d.decode_image_in_image_number),
                g(d.decode_video_in_image_number), g(d.decode_audio_in_image_number),
                g(d.decode_text_in_video_number), g(d.decode_image_in_video_number),
                g(d.decode_audio_in_video_number), g(d.decode_video_in_video_number),
                g(d.decode_text_in_audio_number), g(d.decode_image_in_audio_number),
                g(d.decode_audio_in_audio_number), g(d.decode_video_in_audio_number)
            ]
            
            total_encodes = sum(encodes)
            total_decodes = sum(decodes)
            
            days_active = 0
            if d.date_encode_text_in_image_number:
                days_active = (timezone.now() - d.date_encode_text_in_image_number).days
                if days_active < 1: days_active = 1

            # Fetch Recent Activity with new Activity Type field
            recent_activity = upload.objects.order_by('-uploaded_at')[:5]

            context = {
                'user': current_user,
                'stats': {
                    'files_processed': total_encodes + total_decodes,
                    'secure_messages': total_encodes,
                    'files_downloaded': total_decodes,
                    'days_active': days_active,
                    'last_enc': d.last_encryption_type,
                    'last_dec': d.last_decryption_type
                },
                'recent_activity': recent_activity
            }
            return render(request, 'profile.html', context)
        except user.DoesNotExist:
            return HttpResponse("User not found")
    return redirect('login')

def content(request):
    return render(request, 'content.html')

# ... (keep your other views like main, login, etc.) ...

def admindash(request):
    # 1. Active Users
    active_users = user.objects.count()
    
    # 2. Total Stats (Count from history for accuracy)
    total_encoded = upload.objects.filter(activity_type__startswith='Encoded').count()
    total_decoded = upload.objects.filter(activity_type__startswith='Decoded').count()
    
    # 3. Prepare Chart Data (Last 7 Days)
    today = timezone.now().date()
    dates = [(today - timedelta(days=i)) for i in range(6, -1, -1)] # Generate list of last 7 days
    
    labels = []
    enc_data = []
    dec_data = []
    
    for date in dates:
        # Create Label (e.g., "Oct 10")
        labels.append(date.strftime('%b %d'))
        
        # Count Encodes for this specific date
        e_count = upload.objects.filter(
            activity_type__startswith='Encoded',
            uploaded_at__date=date
        ).count()
        enc_data.append(e_count)
        
        # Count Decodes for this specific date
        d_count = upload.objects.filter(
            activity_type__startswith='Decoded',
            uploaded_at__date=date
        ).count()
        dec_data.append(d_count)

    context = {
        'active_users': active_users,
        'total_encoded': total_encoded,
        'total_decoded': total_decoded,
        # Pass data as JSON strings for JavaScript
        'chart_labels': json.dumps(labels),
        'chart_enc_data': json.dumps(enc_data),
        'chart_dec_data': json.dumps(dec_data),
    }
    return render(request, 'admindash.html', context)

def editprofile(request):
    if 'email' in request.session:
        email = request.session['email']
        try:
            client = user.objects.get(email=email)
            if request.method == 'POST':
                username = request.POST.get('username')
                client.username = username
                phone = request.POST.get('phone')
                client.phone = phone
                new_image = request.FILES.get('image')
                if new_image: client.image = new_image  
                password = request.POST.get('password')
                conf = request.POST.get('confirmpassword')
                if password:
                    if password == conf: client.password = password
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