from django.db import models

class user(models.Model):
    image = models.ImageField(upload_to='profile/', null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True, unique=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    confirmpassword = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=50, null=True, blank=True, unique=True)
    phone = models.IntegerField(null=True, blank=True, unique=True)

class upload(models.Model):
    media = models.FileField(upload_to='uploads/', null=True, blank=True)
    stego_media = models.FileField(upload_to='stego_images/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    result = models.FileField(upload_to='results/', null=True, blank=True)
    
    # --- NEW FIELD REQUIRED FOR ACTIVITY LOG ---
    # This stores strings like "Encoded: Text in Image" or "Decoded File"
    activity_type = models.CharField(max_length=100, null=True, blank=True)

class detail(models.Model):
    username = models.CharField(max_length=100, null=True, blank=True)
    files_processed_number = models.IntegerField(default=0, null=True, blank=True)
    encode_number = models.IntegerField(default=0, null=True, blank=True)
    decode_number = models.IntegerField(default=0, null=True, blank=True)

    # --- ENCODE STATS ---
    encode_text_in_image_number = models.IntegerField(default=0, null=True, blank=True)
    decode_text_in_image_number = models.IntegerField(default=0, null=True, blank=True)
    encode_image_in_image_number = models.IntegerField(default=0, null=True, blank=True)
    decode_image_in_image_number = models.IntegerField(default=0, null=True, blank=True)
    encode_video_in_image_number = models.IntegerField(default=0, null=True, blank=True)
    decode_video_in_image_number = models.IntegerField(default=0, null=True, blank=True)
    encode_audio_in_image_number = models.IntegerField(default=0, null=True, blank=True)
    decode_audio_in_image_number = models.IntegerField(default=0, null=True, blank=True)
    
    encode_text_in_video_number = models.IntegerField(default=0, null=True, blank=True)
    decode_text_in_video_number = models.IntegerField(default=0, null=True, blank=True)
    encode_image_in_video_number = models.IntegerField(default=0, null=True, blank=True)
    decode_image_in_video_number = models.IntegerField(default=0, null=True, blank=True)
    
    encode_text_in_audio_number = models.IntegerField(default=0, null=True, blank=True)
    decode_text_in_audio_number = models.IntegerField(default=0, null=True, blank=True)
    encode_image_in_audio_number = models.IntegerField(default=0, null=True, blank=True)
    decode_image_in_audio_number = models.IntegerField(default=0, null=True, blank=True)

    # --- NEW AUDIO/VIDEO STATS ---
    # Audio in Audio
    encode_audio_in_audio_number = models.IntegerField(default=0, null=True, blank=True)
    decode_audio_in_audio_number = models.IntegerField(default=0, null=True, blank=True)
    # Video in Audio
    encode_video_in_audio_number = models.IntegerField(default=0, null=True, blank=True)
    decode_video_in_audio_number = models.IntegerField(default=0, null=True, blank=True)
    # Audio in Video
    encode_audio_in_video_number = models.IntegerField(default=0, null=True, blank=True)
    decode_audio_in_video_number = models.IntegerField(default=0, null=True, blank=True)
    # Video in Video
    encode_video_in_video_number = models.IntegerField(default=0, null=True, blank=True)
    decode_video_in_video_number = models.IntegerField(default=0, null=True, blank=True)

    # --- DATE FIELDS ---
    date_encode_text_in_image_number = models.DateTimeField(auto_now_add=True)
    date_decode_text_in_image_number = models.DateTimeField(auto_now_add=True)
    date_encode_image_in_image_number = models.DateTimeField(auto_now_add=True)
    date_decode_image_in_image_number = models.DateTimeField(auto_now_add=True)
    date_encode_video_in_image_number = models.DateTimeField(auto_now_add=True)
    date_decode_video_in_image_number = models.DateTimeField(auto_now_add=True)
    date_encode_audio_in_image_number = models.DateTimeField(auto_now_add=True)
    date_decode_audio_in_image_number = models.DateTimeField(auto_now_add=True)
    
    date_encode_text_in_video_number = models.DateTimeField(auto_now_add=True)
    date_decode_text_in_video_number = models.DateTimeField(auto_now_add=True)
    date_encode_image_in_video_number = models.DateTimeField(auto_now_add=True)
    date_decode_image_in_video_number = models.DateTimeField(auto_now_add=True)
    
    date_encode_text_in_audio_number = models.DateTimeField(auto_now_add=True)
    date_decode_text_in_audio_number = models.DateTimeField(auto_now_add=True)
    date_encode_image_in_audio_number = models.DateTimeField(auto_now_add=True)
    date_decode_image_in_audio_number = models.DateTimeField(auto_now_add=True)

    last_encryption_type = models.DateTimeField(auto_now=True)
    second_last_encryption_type = models.DateTimeField(auto_now=True)
    third_last_encryption_type = models.DateTimeField(auto_now=True)
    last_decryption_type = models.DateTimeField(auto_now=True)
    second_last_decryption_type = models.DateTimeField(auto_now=True)
    third_last_decryption_type = models.DateTimeField(auto_now=True)