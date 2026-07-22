from django.db import models

class user(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    confirmpassword = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/', null=True, blank=True)

class detail(models.Model):
    # --- IMAGE CARRIER STATS ---
    encode_text_in_image_number = models.IntegerField(default=0)
    decode_text_in_image_number = models.IntegerField(default=0)
    
    encode_image_in_image_number = models.IntegerField(default=0)
    decode_image_in_image_number = models.IntegerField(default=0)
    
    encode_video_in_image_number = models.IntegerField(default=0)
    decode_video_in_image_number = models.IntegerField(default=0)
    
    encode_audio_in_image_number = models.IntegerField(default=0)
    decode_audio_in_image_number = models.IntegerField(default=0)

    # --- AUDIO CARRIER STATS ---
    encode_text_in_audio_number = models.IntegerField(default=0)
    decode_text_in_audio_number = models.IntegerField(default=0)
    
    encode_image_in_audio_number = models.IntegerField(default=0)
    decode_image_in_audio_number = models.IntegerField(default=0)

    # New Audio Fields
    encode_audio_in_audio_number = models.IntegerField(default=0)
    decode_audio_in_audio_number = models.IntegerField(default=0)

    encode_video_in_audio_number = models.IntegerField(default=0)
    decode_video_in_audio_number = models.IntegerField(default=0)

    # --- VIDEO CARRIER STATS ---
    encode_text_in_video_number = models.IntegerField(default=0)
    decode_text_in_video_number = models.IntegerField(default=0)
    
    encode_image_in_video_number = models.IntegerField(default=0)
    decode_image_in_video_number = models.IntegerField(default=0)

    # New Video Fields
    encode_audio_in_video_number = models.IntegerField(default=0)
    decode_audio_in_video_number = models.IntegerField(default=0)

    encode_video_in_video_number = models.IntegerField(default=0)
    decode_video_in_video_number = models.IntegerField(default=0)