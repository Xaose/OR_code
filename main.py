from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.core.image import Image as CoreImage
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.graphics.texture import Texture
import qrcode
from PIL import Image as PILImage
import io
import os

# Загрузка KV файла
Builder.load_file('qrcodeapp.kv')


class QRCodeApp(App):
    def build(self):
        # Создание placeholder.png, если он не существует
        placeholder_path = 'placeholder.png'
        if not os.path.exists(placeholder_path):
            img = PILImage.new('RGB', (200, 200), color='white')
            img.save(placeholder_path)

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Поле ввода текста
        self.text_input = TextInput(
            hint_text='Введите текст для QR-кода',
            size_hint=(1, 0.3),
            multiline=False
        )
        layout.add_widget(self.text_input)

        # Кнопка генерации QR-кода
        generate_button = Button(
            text='Сгенерировать QR-код',
            size_hint=(1, 0.1)
        )
        generate_button.bind(on_press=self.generate_qr_code)
        layout.add_widget(generate_button)

        # Место для отображения QR-кода
        self.qr_image = Image(
            size_hint=(1, 0.5),
            allow_stretch=True,
            keep_ratio=True,
            source=placeholder_path  # Устанавливаем placeholder
        )
        layout.add_widget(self.qr_image)

        # Кнопка сохранения QR-кода
        save_button = Button(
            text='Сохранить QR-код',
            size_hint=(1, 0.1)
        )
        save_button.bind(on_press=self.save_qr_code)
        layout.add_widget(save_button)

        return layout

    def generate_qr_code(self, instance):
        text = self.text_input.text.strip()
        if not text:
            self.show_popup('Ошибка', 'Введите текст для генерации QR-кода!')
            return

        try:
            # Генерация QR-кода
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(text)
            qr.make(fit=True)

            # Создание изображения QR-кода
            img = qr.make_image(fill_color="black", back_color="white")

            # Сохранение изображения в буфер
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            print(f"Buffer size: {len(buffer.getvalue())} bytes")  # Debug: размер буфера

            # Создание текстуры из буфера
            core_img = CoreImage(buffer, ext='png')
            print(f"Texture created: {core_img.texture}")  # Debug: проверка текстуры

            # Обновление виджета Image
            self.qr_image.source = ''  # Сброс источника
            self.qr_image.texture = core_img.texture
            self.qr_image.texture.update()  # Синхронизация текстуры
            self.qr_image.canvas.ask_update()  # Форсируем обновление канваса
            self.qr_image.reload()

            # Сохранение изображения для последующего скачивания
            self.qr_pil_image = img

        except Exception as e:
            self.show_popup('Ошибка', f'Не удалось сгенерировать QR-код: {str(e)}')
            print(f"Error generating QR code: {str(e)}")  # Debug: ошибка
            return

    def save_qr_code(self, instance):
        if not hasattr(self, 'qr_pil_image'):
            self.show_popup('Ошибка', 'Сначала сгенерируйте QR-код!')
            return

        try:
            # Сохранение изображения в домашнюю директорию
            home_dir = os.path.expanduser("~")
            file_path = os.path.join(home_dir, 'qrcode.png')
            self.qr_pil_image.save(file_path)
            self.show_popup('Успех', f'QR-код сохранен как {file_path}')
        except Exception as e:
            self.show_popup('Ошибка', f'Не удалось сохранить QR-код: {str(e)}')
            print(f"Error saving QR code: {str(e)}")  # Debug: ошибка

    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()


if __name__ == '__main__':
    QRCodeApp().run()