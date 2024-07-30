import pyttsx3

text = "Hello, how are you?"

engine = pyttsx3.init()
voices = engine.getProperty('voices')

# Iterate through available voices to find a male voice
male_voice = None
for voice in voices:
    if voice.gender == 'male':
        male_voice = voice
        break

# Set the male voice if found, otherwise use the default voice
if male_voice:
    engine.setProperty('voice', male_voice.id)

engine.say(text)
engine.save_to_file(text, 'output.mp3')
engine.runAndWait()
