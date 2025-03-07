import customtkinter as ctk
import tkinter as tk  # Додано імпорт tkinter
import PyPDF2
import json
import os
import pyttsx3
from googlesearch import search
import openai
import difflib


class AIApp:
    def __init__(self, master):
        # Основне вікно програми
        self.master = master
        master.title("AI Assistant")  # Назва вікна
        master.geometry("800x600")  # Розмір вікна
        ctk.set_appearance_mode("Dark")  # Темна тема
        ctk.set_default_color_theme("blue")  # Колірна тема

        # Ініціалізація голосового синтезу
        self.engine = pyttsx3.init()  # Ініціалізація pyttsx3 для голосу
        self.speech_enabled = False  # Спочатку озвучка вимкнена
        self.api_key = ""  # API ключ OpenAI (спочатку порожній)

        # Графічний інтерфейс
        self.chat_display = ctk.CTkTextbox(master, width=700, height=300, wrap='word', font=("Arial", 12))
        self.chat_display.pack(pady=10)  # Виведення повідомлень у вікно чату

        # Введення шляху до PDF файлу
        self.pdf_entry = self.create_entry(master, "Введіть шлях до PDF")
        self.analyze_button = self.create_button(master, "Аналізувати PDF", self.analyze_pdf)

        # Введення повідомлення для чат-бота
        self.message_entry = self.create_entry(master, "Введіть повідомлення")
        self.send_button = self.create_button(master, "Відправити", self.send_message)

        # Введення запиту для пошуку в Google
        self.search_entry = self.create_entry(master, "Введіть пошуковий запит")
        self.search_button = self.create_button(master, "Загуглити", self.search_google)

        # Введення API-ключа для OpenAI
        self.api_entry = self.create_entry(master, "Введіть API-ключ", show="*")
        self.api_button = self.create_button(master, "Ввести API-ключ", self.set_api_key)

        # Кнопка для показу інструкцій щодо отримання API-ключа
        self.tutorial_button = self.create_button(master, "Як отримати API-ключ?", self.show_tutorial)

        # Кнопка для увімкнення/вимкнення озвучки
        self.speech_button = self.create_button(master, "Включити озвучку", self.toggle_speech)

        # Завантаження бази знань із файлу
        self.knowledge_base = {}
        self.load_knowledge()

    def create_entry(self, master, placeholder, show=None):
        # Створення текстового поля для введення даних
        entry = ctk.CTkEntry(master, width=500, show=show, font=("Arial", 12), placeholder_text=placeholder)
        entry.pack(pady=5)
        return entry

    def create_button(self, master, text, command):
        # Створення кнопки
        button = ctk.CTkButton(master, text=text, command=command, width=200, height=40, font=("Arial", 12, "bold"))
        button.pack(pady=8)  # Відстань між кнопками
        return button

    def set_api_key(self):
        # Збереження API-ключа, введеного користувачем
        self.api_key = self.api_entry.get()
        self.display_message("AI: API-ключ збережено!")

    def show_tutorial(self):
        # Виведення інструкцій щодо отримання API-ключа
        tutorial = ("1. Перейди на https://platform.openai.com/signup\n"
                    "2. Зареєструйся або увійди в акаунт OpenAI.\n"
                    "3. Перейди в розділ API Keys: https://platform.openai.com/api-keys\n"
                    "4. Створи новий API-ключ і скопіюй його.\n"
                    "5. Введи його у поле вище та натисни 'Ввести API-ключ'.")
        self.display_message(tutorial)

    def toggle_speech(self):
        # Перемикання між включенням та вимкненням озвучки
        self.speech_enabled = not self.speech_enabled
        self.speech_button.configure(text="Виключити озвучку" if self.speech_enabled else "Включити озвучку")

    def analyze_pdf(self):
        # Аналіз PDF файлу та збереження ключових слів
        pdf_path = self.pdf_entry.get()
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
                word_count = len(text.split())
                keywords = self.extract_keywords(text)
                self.knowledge_base[pdf_path] = {"text": text, "keywords": keywords}
                self.save_knowledge()
                self.display_message(
                    f"AI: Аналіз завершено. Кількість слів: {word_count}\nКлючові слова: {', '.join(keywords[:10])}")
        except Exception as e:
            self.display_message(f"Помилка: {str(e)}")

    def extract_keywords(self, text):
        # Видобуток ключових слів з тексту
        words = text.split()
        word_freq = {}
        for word in words:
            word = word.lower().strip(",.!?()[]{}")
            if len(word) > 3:  # Враховуються тільки слова довжиною більше 3 символів
                word_freq[word] = word_freq.get(word, 0) + 1
        return sorted(word_freq, key=word_freq.get, reverse=True)[:15]

    def send_message(self):
        # Обробка повідомлення користувача
        user_message = self.message_entry.get()
        self.display_message(f"Ви: {user_message}")
        self.message_entry.delete(0, tk.END)
        self.handle_learning(user_message)

    def handle_learning(self, user_message):
        # Обробка навчання та відповіді
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
        # Отримання відповіді від AI або OpenAI API
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
        # Пошук найкращого співпадіння в базі знань
        keys = list(self.knowledge_base.keys())
        best_match = difflib.get_close_matches(user_message, keys, n=1, cutoff=0.6)
        return best_match[0] if best_match else None

    def search_google(self):
        # Пошук в Google за запитом користувача
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
        # Збереження бази знань у файл
        with open('knowledge.json', 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, ensure_ascii=False, indent=4)

    def load_knowledge(self):
        # Завантаження бази знань із файлу
        if os.path.exists('knowledge.json'):
            with open('knowledge.json', 'r', encoding='utf-8') as f:
                try:
                    self.knowledge_base = json.load(f)
                except json.JSONDecodeError:
                    self.knowledge_base = {}

    def display_message(self, message):
        # Виведення повідомлень у вікно чату
        self.chat_display.configure(state='normal')
        self.chat_display.insert(tk.END, message + "\n")  # Використання tk.END
        self.chat_display.configure(state='disabled')
        self.chat_display.see(tk.END)  # Використання tk.END

    def speak(self, text):
        # Озвучування тексту
        self.engine.say(text)
        self.engine.runAndWait()


if __name__ == "__main__":
    root = ctk.CTk()
    app = AIApp(root)
    root.mainloop()