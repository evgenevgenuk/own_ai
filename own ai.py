import tkinter as tk
import PyPDF2
import json
import os
import pyttsx3
from googlesearch import search
import openai
import difflib

class AIApp:
    def __init__(self, master):
        self.master = master
        master.title("AI Assistant")

        # Ініціалізація голосового синтезу
        self.engine = pyttsx3.init()
        self.speech_enabled = False
        self.api_key = ""

        # Графічний інтерфейс
        self.chat_display = tk.Text(master, state='disabled', width=60, height=15, wrap='word')
        self.chat_display.pack()

        self.pdf_entry = self.create_entry(master, "Введіть шлях до PDF")
        self.analyze_button = tk.Button(master, text="Аналізувати PDF", command=self.analyze_pdf)
        self.analyze_button.pack()

        self.message_entry = self.create_entry(master, "Введіть повідомлення")
        self.send_button = tk.Button(master, text="Відправити", command=self.send_message)
        self.send_button.pack()

        self.search_entry = self.create_entry(master, "Введіть пошуковий запит")
        self.search_button = tk.Button(master, text="Загуглити", command=self.search_google)
        self.search_button.pack()

        self.api_entry = self.create_entry(master, "Введіть API-ключ", show="*")
        self.api_button = tk.Button(master, text="Ввести API-ключ", command=self.set_api_key)
        self.api_button.pack()

        self.tutorial_button = tk.Button(master, text="Як отримати API-ключ?", command=self.show_tutorial)
        self.tutorial_button.pack()

        self.speech_button = tk.Button(master, text="Включити озвучку", command=self.toggle_speech)
        self.speech_button.pack()

        # Завантаження бази знань
        self.knowledge_base = {}
        self.load_knowledge()

    def create_entry(self, master, placeholder, show=None):
        entry = tk.Entry(master, width=50, show=show)
        entry.insert(0, placeholder)
        entry.bind("<FocusIn>", lambda event: self.clear_placeholder(entry, placeholder))
        entry.bind("<FocusOut>", lambda event: self.restore_placeholder(entry, placeholder))
        entry.pack()
        return entry

    def clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)

    def restore_placeholder(self, entry, placeholder):
        if not entry.get():
            entry.insert(0, placeholder)

    def set_api_key(self):
        self.api_key = self.api_entry.get()
        self.display_message("AI: API-ключ збережено!")

    def show_tutorial(self):
        tutorial = ("1. Перейди на https://platform.openai.com/signup\n"
                    "2. Зареєструйся або увійди в акаунт OpenAI.\n"
                    "3. Перейди в розділ API Keys: https://platform.openai.com/api-keys\n"
                    "4. Створи новий API-ключ і скопіюй його.\n"
                    "5. Введи його у поле вище та натисни 'Ввести API-ключ'.")
        self.display_message(tutorial)

    def toggle_speech(self):
        self.speech_enabled = not self.speech_enabled
        self.speech_button.config(text="Виключити озвучку" if self.speech_enabled else "Включити озвучку")

    def analyze_pdf(self):
        pdf_path = self.pdf_entry.get()
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
                word_count = len(text.split())
                keywords = self.extract_keywords(text)
                self.knowledge_base[pdf_path] = {"text": text, "keywords": keywords}
                self.save_knowledge()
                self.display_message(f"AI: Аналіз завершено. Кількість слів: {word_count}\nКлючові слова: {', '.join(keywords[:10])}")
        except Exception as e:
            self.display_message(f"Помилка: {str(e)}")

    def extract_keywords(self, text):
        words = text.split()
        word_freq = {}
        for word in words:
            word = word.lower().strip(",.!?()[]{}")
            if len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        return sorted(word_freq, key=word_freq.get, reverse=True)[:15]

    def send_message(self):
        user_message = self.message_entry.get()
        self.display_message(f"Ви: {user_message}")
        self.message_entry.delete(0, tk.END)
        self.handle_learning(user_message)

    def handle_learning(self, user_message):
        user_message = user_message.lower()
        if "це" in user_message:
            parts = user_message.split("це")
            if len(parts) == 2:
                self.knowledge_base[parts[0].strip()] = parts[1].strip()
                self.display_message("AI: Я запам'ятав!")
                self.save_knowledge()
        else:
            response = self.get_response(user_message)
            self.display_message(f"AI: {response}")
            if self.speech_enabled:
                self.speak(response)

    def get_response(self, user_message):
        match = self.find_best_match(user_message)
        if match:
            return f"{match} - {self.knowledge_base[match]}"

        if self.api_key:
            try:
                openai.api_key = self.api_key
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": user_message}]
                )
                return response["choices"][0]["message"]["content"]
            except Exception as e:
                return f"Помилка підключення до OpenAI: {str(e)}"

        return "Я не знаю відповіді, навчіть мене!"

    def find_best_match(self, user_message):
        keys = list(self.knowledge_base.keys())
        best_match = difflib.get_close_matches(user_message, keys, n=1, cutoff=0.6)
        return best_match[0] if best_match else None

    def search_google(self):
        query = self.search_entry.get()
        if query:
            self.display_message("AI: Шукаю в Google...")
            try:
                results = search(query, num_results=3)
                for result in results:
                    self.display_message(f"AI: {result}")
            except Exception as e:
                self.display_message(f"Помилка пошуку: {str(e)}")

    def save_knowledge(self):
        with open('knowledge.json', 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, ensure_ascii=False, indent=4)

    def load_knowledge(self):
        if os.path.exists('knowledge.json'):
            with open('knowledge.json', 'r', encoding='utf-8') as f:
                try:
                    self.knowledge_base = json.load(f)
                except json.JSONDecodeError:
                    self.knowledge_base = {}

    def display_message(self, message):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, message + "\n")
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

if __name__ == "__main__":
    root = tk.Tk()
    app = AIApp(root)
    root.mainloop()
