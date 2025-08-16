import speech_recognition as sr
from deep_translator import GoogleTranslator
import pyttsx3

# Inicializa o motor de voz
engine = pyttsx3.init()

# Função para falar
def speak(text, lang="en"):
    # Tenta ajustar a voz para o idioma (depende do sistema)
    voices = engine.getProperty('voices')
    for voice in voices:
        if lang in voice.languages or lang in voice.id:
            engine.setProperty('voice', voice.id)
            break
    engine.say(text)
    engine.runAndWait()

# Função para ouvir e transcrever
def listen(language="pt-BR"):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print(f"[{language}] Fale agora...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio, language=language)
        print(f"Você disse: {text}")
        return text
    except sr.UnknownValueError:
        print("Não entendi o que foi dito.")
        return ""
    except sr.RequestError:
        print("Erro na conexão com o serviço de reconhecimento.")
        return ""

# Loop principal
if __name__ == "__main__":
    print("=== Tradutor Simultâneo PT <-> EN ===")
    print("Modo 1: Você fala em português e ele traduz para inglês")
    print("Modo 2: Você fala em inglês e ele traduz para português")
    print("Pressione CTRL+C para sair.\n")

    try:
        while True:
            # Modo 1 - PT -> EN
            texto_pt = listen("pt-BR")
            if texto_pt:
                traducao_en = GoogleTranslator(source='pt', target='en').translate(texto_pt)
                print("Tradução EN:", traducao_en)
                speak(traducao_en, "en")

            # Modo 2 - EN -> PT
            texto_en = listen("en-US")
            if texto_en:
                traducao_pt = GoogleTranslator(source='en', target='pt').translate(texto_en)
                print("Tradução PT:", traducao_pt)
                speak(traducao_pt, "pt")

    except KeyboardInterrupt:
        print("\nEncerrado pelo usuário.")
