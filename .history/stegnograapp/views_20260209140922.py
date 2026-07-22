# ... (Previous imports remain the same)

def main(request):
    context = {}
    if request.method == 'POST':
        action = request.POST.get('action_type')
        steg_mode = request.POST.get('steg_mode')
        password = request.POST.get('password')
        
        # Get the stats object (Fix: use first() or get() instead of all())
        d = models.detail.objects.first() 
        # If no object exists, you might need: d = models.detail.objects.create() if not d else d

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
                        if d: d.encode_text_in_image_number += 1
                    else:
                        # Handles: image-in-image, video-in-image, audio-in-image
                        secret_file = request.FILES.get('secret_file')
                        secret_data = secret_file.read()
                        
                        # Stats
                        if d:
                            if steg_mode == 'image-in-image': d.encode_image_in_image_number += 1
                            elif steg_mode == 'video-in-image': d.encode_video_in_image_number += 1
                            elif steg_mode == 'audio-in-image': d.encode_audio_in_image_number += 1

                    result_img = steg.encode_in_image(carrier, secret_data, password, is_text)
                    result_img.save(output_io, format='PNG')
                    filename += ".png"

                # --- 2. CARRIER: AUDIO ---
                elif 'in-audio' in steg_mode:
                    # Save uploaded carrier temporarily
                    suffix = os.path.splitext(carrier.name)[1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        for chunk in carrier.chunks(): tmp.write(chunk)
                        tmp_carrier = tmp.name
                    
                    # Convert to WAV if needed
                    carrier_wav = tmp_carrier + "_converted.wav"
                    clip = None
                    process_path = tmp_carrier

                    try:
                        # Attempt conversion for MP3 stability
                        if AudioFileClip:
                            clip = AudioFileClip(tmp_carrier)
                            clip.write_audiofile(carrier_wav, codec='pcm_s16le', verbose=False, logger=None)
                            process_path = carrier_wav
                    except Exception:
                        pass # Fallback to original file
                    finally:
                        if clip: 
                            try: clip.close() 
                            except: pass

                    tmp_out = process_path + "_out.wav"
                    
                    try:
                        if steg_mode == 'text-in-audio':
                            steg.encode_in_audio(process_path, request.POST.get('secret_text'), tmp_out, password, True)
                            if d: d.encode_text_in_audio_number += 1
                        else:
                            # Handles: image-in-audio, audio-in-audio, video-in-audio
                            secret_data = request.FILES.get('secret_file').read()
                            steg.encode_in_audio(process_path, secret_data, tmp_out, password, False)
                            
                            if d:
                                if steg_mode == 'image-in-audio': d.encode_image_in_audio_number += 1
                                elif steg_mode == 'audio-in-audio': d.encode_audio_in_audio_number += 1 # NEW
                                elif steg_mode == 'video-in-audio': d.encode_video_in_audio_number += 1 # NEW

                        with open(tmp_out, 'rb') as f: output_io.write(f.read())
                        filename += ".wav"
                    finally:
                        # Cleanup
                        for p in [tmp_carrier, carrier_wav, tmp_out]:
                            if os.path.exists(p): 
                                try: os.unlink(p) 
                                except: pass

                # --- 3. CARRIER: VIDEO ---
                elif 'in-video' in steg_mode:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".avi") as tmp:
                        for chunk in carrier.chunks(): tmp.write(chunk)
                        tmp_carrier = tmp.name
                    tmp_out = tmp_carrier + "_out.avi"
                    
                    try:
                        if steg_mode == 'text-in-video':
                            steg.encode_in_video(tmp_carrier, request.POST.get('secret_text'), tmp_out, password, True)
                            if d: d.encode_text_in_video_number += 1
                        else:
                            # Handles: image-in-video, audio-in-video, video-in-video
                            secret_data = request.FILES.get('secret_file').read()
                            steg.encode_in_video(tmp_carrier, secret_data, tmp_out, password, False)
                            
                            if d:
                                if steg_mode == 'image-in-video': d.encode_image_in_video_number += 1
                                elif steg_mode == 'audio-in-video': d.encode_audio_in_video_number += 1 # NEW
                                elif steg_mode == 'video-in-video': d.encode_video_in_video_number += 1 # NEW

                        with open(tmp_out, 'rb') as f: output_io.write(f.read())
                        filename += ".avi"
                    finally:
                        if os.path.exists(tmp_carrier): os.unlink(tmp_carrier)
                        if os.path.exists(tmp_out): os.unlink(tmp_out)

                # Save Stats
                if d: d.save()

                output_io.seek(0)
                return FileResponse(output_io, as_attachment=True, filename=filename)

            # ================= DECODING =================
            elif action == 'decode':
                stego_file = request.FILES.get('stego_file')
                result_data = None
                
                # ... (Decoding logic remains largely the same, just stats update) ...
                
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
                        # Update text decode stats here if needed
                    else:
                        out_io = io.BytesIO(result_data)
                        ext = get_file_extension(result_data)
                        fname = f"revealed_file{ext}"
                        
                        # Generic success message for files
                        context['success_msg'] = f"File Decoded Successfully! ({ext})"
                        return FileResponse(out_io, as_attachment=True, filename=fname)
                else:
                    context['error'] = "No hidden data found or incorrect password."

        except ValueError as ve:
             context['error'] = f"Data Error: {str(ve)} (The file might be too large for this carrier)"
        except Exception as e:
            context['error'] = f"System Error: {str(e)}"

    return render(request, 'main.html', context)