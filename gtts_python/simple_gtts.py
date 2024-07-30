from gtts import gTTS
import os
import warnings
import urllib3

warnings.filterwarnings("ignore")

# Reference
# https://www.youtube.com/watch?v=r22uVwFK5e0
# https://medium.com/@pelinokutan/how-to-convert-text-to-speech-with-python-using-the-gtts-library-dbe3d56730f1
# python -m pip install gTTS

def text_to_speech(text):
    # Initialize gTTS with the text to convert
    # speech = gTTS(text, lang='en-uk', slow=False, tld='com')
    speech = gTTS(text, lang='ur') # for Urdu

    # Save the audio file to a temporary file
    speech_file = 'speech.mp3'
    speech.save(speech_file)

    # Play the audio file
    os.system('afplay ' + speech_file)

def input_text_to_speech():
    while True:
        try:
            # Take the question as an input
            text = input('Say: ')
            
            # Initialize gTTS with the text to convert
            speech = gTTS(text, lang='en-us', slow=False, tld='com')

            # Save the audio file to a temporary file
            speech_file = 'speech.mp3'
            speech.save(speech_file)

            # Play the audio file
            os.system('afplay ' + speech_file)
        except KeyboardInterrupt:
            print("Program terminated.")
            break
    
# text_to_speech('look wot')
# text_to_speech("میرا نام رفیع ہے")
input_text_to_speech()