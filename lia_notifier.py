import speech_recognition as sr

def listen_for_speech(send_message_signal):
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        while True:
            try:
                audio = recognizer.listen(source)
                user_input = recognizer.recognize_google(audio)
                print(f"You said: {user_input}")
                send_message_signal.emit(user_input)  # Send input to GUI
            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
