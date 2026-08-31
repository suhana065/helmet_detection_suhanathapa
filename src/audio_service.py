import subprocess
import os
from pathlib import Path
import time

class AudioService:
    def __init__(self):
        self.beep_sound_path = str(Path(__file__).parent.parent / "assets" / "beep.wav")
        self.last_beep_time = 0
        print(self.beep_sound_path)
        self._ensure_beep_sound_exists()
        
    def _ensure_beep_sound_exists(self):
        """Ensure the beep sound file exists"""
        os.makedirs(os.path.dirname(self.beep_sound_path), exist_ok=True)
        if not os.path.exists(self.beep_sound_path):
            import numpy as np
            from scipy.io import wavfile
            
            sample_rate = 44100
            duration = 0.5  
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            note = np.sin(2 * np.pi * 440 * t)
            audio = note * 32767
            audio = audio.astype(np.int16)
            wavfile.write(self.beep_sound_path, sample_rate, audio)
    
    def play_beep(self):  
        """Play beep sound with 1 second cooldown"""
        current_time = time.time()
        if current_time - self.last_beep_time >= 1.0:
            subprocess.Popen(['afplay', self.beep_sound_path], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            self.last_beep_time = current_time