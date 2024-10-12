import logging
from flask import Flask, render_template, request, redirect
from tkinter import *
import speech_recognition as sr
from gtts import gTTS
import os
from tkinter.ttk import Combobox
from googletrans import Translator, LANGUAGES
from PIL import Image
import pytesseract

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)


def translate_text(text, dest_lang):
    translator = Translator()
    try:
        translated_text = translator.translate(text, dest=dest_lang)
        logging.debug("Translated text response: %s", translated_text)
        if translated_text and translated_text.text:
            return translated_text.text
        else:
            return "Translation failed: No text in the translated response"
    except Exception as e:
        logging.error("Translation failed: %s", e)
        return f"Translation failed: An error occurred during translation - {str(e)}"


def translate_image(image, dest_lang):
    text = pytesseract.image_to_string(image)
    translated = translate_text(text, dest_lang)
    return translated


def translate_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak now...")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError as e:
        return "Error occurred in recognizing audio: {}".format(e)


def recognize_speech():
    recog = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("Say something...")
        audio = recog.listen(source)

    try:
        text = recog.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Audio is not understood"
    except sr.RequestError as e:
        return f"Could not request results: {e}"


@app.route('/voice-translation', methods=['POST'])
def voice_translation():
    if request.method == 'POST':
        input_text = recognize_speech()
        target_lang = request.form.get('lang')

        translated = translate_text(input_text, target_lang)

        return render_template('index.html', input_text=input_text, translated=translated)

    return render_template('index.html', input_text='', translated='')


@app.route('/', methods=['POST', 'GET'])
def translate():
    if request.method == 'POST':
        input_text = request.form['data']
        target_lang = request.form.get('lang')

        if 'voice' in request.form:
            input_text = recognize_speech()
        elif 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename != '':
                image = Image.open(image_file)
                input_text = translate_image(image, target_lang)

        translated = translate_text(input_text, target_lang)

        return render_template('index.html', input_text=input_text, translated=translated)

    return render_template('index.html', input_text='', translated='')



@app.route('/voice-output', methods=['POST'])
def voice_output():
    if request.method == 'POST':
        translated_text = request.form['translated']
        tts = gTTS(text=translated_text, lang='en')  # Assuming the output text is in English
        tts.save("translated_output.mp3")
        os.system("start translated_output.mp3")
    return render_template('index.html')


# def run_gui():
#     root = Tk()
#     root.geometry('1100x320')
#     root.resizable(0, 0)
#     root.iconbitmap('etc .ico')
#     root['bg'] = 'red'

#     root.title('Language translator')
#     Label(root, text="Language Translator", font="Arial 20 bold").pack()
#     Label(root, text="Enter Text", font='arial 13 bold',
#           bg='white smoke').place(x=165, y=90)
#     Input_text = Entry(root, width=60)
#     Input_text.place(x=35, y=135)
#     Input_text.get()
#     Label(root, text="Output", font='arial 13 bold ',
#           bg='white smoke').place(x=820, y=90)
#     Output_text = Text(root, font='arial 10', height=5,
#                        wrap=WORD, padx=5, pady=5, width=50)
#     Output_text.place(x=670, y=130)

#     language = list(LANGUAGES.values())
#     dest_lang = Combobox(root, values=language, width=25)
#     dest_lang.place(x=130, y=180)
#     dest_lang.set("Choose the Language")

#     root.mainloop()


if __name__ == '__main__':
    app.run(debug=True, threaded=True,port=5002)  # Run Flask app in a separate thread
     # Run Tkinter GUI


