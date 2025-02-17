import tkinter as tk
import PyPDF2
import pandas as pd
import json
import os
from googlesearch import search  # Для пошуку в Google

class AIApp:
    def __init__(self, master):
        self.master = master
        master.title("AI Assistant")

        # Віджет для відображення чату
        self.chat_display = tk.Text(master, state='disabled', width=50, height=15)
        self.chat_display.pack()

        # Віджет для вибору PDF-файлу
        self.label = tk.Label(master, text="Введіть шлях до PDF-файлу:")
        self.label.pack()

        self.pdf_entry = tk.Entry(master, width=50)
        self.pdf_entry.pack()

        self.analyze_button = tk.Button(master, text="Аналізувати PDF", command=self.analyze_pdf)
        self.analyze_button.pack()

        self.result_label = tk.Label(master, text="")
        self.result_label.pack()

        # Віджет для введення повідомлень
        self.message_entry = tk.Entry(master)
        self.message_entry.pack()

        self.send_button = tk.Button(master, text="Відправити", command=self.send_message)
        self.send_button.pack()

        # Віджет для пошуку в Google
        self.search_entry = tk.Entry(master, width=50)
        self.search_entry.pack()

        self.search_button = tk.Button(master, text="Загуглити", command=self.search_google)
        self.search_button.pack()

        self.knowledge_base = {}  # Словник для зберігання знань
        self.load_knowledge()  # Завантажити знання з файлу

    def analyze_pdf(self):
        pdf_path = self.pdf_entry.get()
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"

                # Показати кількість слів
                word_count = len(text.split())
                self.result_label.config(text=f"Кількість слів у PDF: {word_count}")

                # Зберегти текст у базі знань
                self.knowledge_base[pdf_path] = text
                self.save_knowledge()  # Зберегти оновлену базу знань

                self.display_message("AI: Аналіз завершено. Кількість слів: " + str(word_count))
        except Exception as e:
            self.display_message(f"Помилка: {str(e)}")

    def send_message(self):
        user_message = self.message_entry.get()
        self.display_message("Ви: " + user_message)
        self.message_entry.delete(0, tk.END)  # Очистити поле введення

        # Обробка запитання або навчання
        self.handle_learning(user_message)

    def handle_learning(self, user_message):
        user_message = user_message.lower()

        if "це" in user_message:
            # Витягти відповідь з повідомлення
            parts = user_message.split("це")
            if len(parts) == 2:
                question = parts[0].strip()
                answer = parts[1].strip()
                self.knowledge_base[question] = answer
                self.display_message("AI: Дякую! Я запам'ятав, що " + question + " " + answer + ".")
                self.save_knowledge()  # Зберегти оновлену базу знань
        else:
            # Перевірити, чи є відповідь на запитання
            response = self.get_response(user_message)
            self.display_message("AI: " + response)

    def get_response(self, user_message):
        # Перевірка наявності запитання в базі знань
        for question in self.knowledge_base:
            if question in user_message:
                return self.knowledge_base[question]

        # Якщо запитання не знайдено
        return "Вибачте, я не знаю відповіді на це питання. Можете навчити мене?"

    def display_message(self, message):
        self.chat_display.config(state='normal')  # Дозволити редагування
        self.chat_display.insert(tk.END, message + "\n")  # Додати повідомлення
        self.chat_display.config(state='disabled')  # Заборонити редагування
        self.chat_display.see(tk.END)  # Прокрутити вниз

    def search_google(self):
        query = self.search_entry.get()
        if query:
            self.display_message("AI: Шукаю в Google...")
            try:
                search_results = search(query, num_results=3)  # Ліміт на 3 результати
                if search_results:
                    for result in search_results:
                        self.display_message("AI: " + result)
                else:
                    self.display_message("AI: Вибачте, нічого не знайдено.")
            except Exception as e:
                self.display_message(f"Помилка під час пошуку: {str(e)}")

    def save_knowledge(self):
        with open('knowledge.json', 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, ensure_ascii=False, indent=4)

    def load_knowledge(self):
        if os.path.exists('knowledge.json'):
            with open('knowledge.json', 'r', encoding='utf-8') as f:
                try:
                    self.knowledge_base = json.load(f)
                except json.JSONDecodeError:
                    self.knowledge_base = {}  # Якщо файл порожній або не дійсний, ініціалізуємо порожній словник
                    print("Файл knowledge.json порожній або не дійсний. Ініціалізую порожню базу знань.")
        else:
            self.knowledge_base = {}  # Якщо файл не існує, ініціалізуємо порожній словник

if __name__ == "__main__":
    root = tk.Tk()
    app = AIApp(root)
    root.mainloop()  # Запуск основного циклу Tkinter
