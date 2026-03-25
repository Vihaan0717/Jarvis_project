import speech_recognition as sr
import pyaudio

def test_mic():
    print("--- MIC DIAGNOSTIC ---")
    print(f"PyAudio version: {pyaudio.__version__}")
    
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    
    print(f"Total Audio Devices found: {numdevices}")
    for i in range(numdevices):
        dev = p.get_device_info_by_host_api_device_index(0, i)
        print(f"Device {i}: {dev.get('name')} (Inputs: {dev.get('maxInputChannels')})")
        
    print("\nAttempting to open default microphone...")
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("✅ Hardware Access SUCCESS!")
            print("Please say something to test recognition (3 seconds)...")
            audio = r.listen(source, timeout=3, phrase_time_limit=3)
            print("Processing...")
            text = r.recognize_google(audio)
            print(f"✅ Recognition SUCCESS! You said: '{text}'")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_mic()
