import os
import sys
import io
import random
from PIL import Image, ImageFilter, ImageOps, ImageDraw, ImageFont
from cryptography.fernet import Fernet
import base64
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFileDialog, QScrollArea, QMessageBox, 
                             QFrame, QSizePolicy)
from PyQt5.QtGui import QPixmap, QImage, QFont, QPalette, QColor, QBrush, QLinearGradient
from PyQt5.QtCore import Qt, QSize

class ImageEncryptor:
    def __init__(self):
        self.key = b'ZMTlTvLMqMOJGGlrKbPQKTfqNxTI5zwvhr_qBxu2w8A='
    
    def encrypt_image(self, image_data):
        f = Fernet(self.key)
        encrypted_data = f.encrypt(image_data)
        return encrypted_data
    
    def decrypt_image(self, encrypted_data):
        f = Fernet(self.key)
        try:
            decrypted_data = f.decrypt(encrypted_data)
            return decrypted_data
        except Exception as e:
            print(f"Decryption error: {e}")
            return None

class FilmFrameWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(2)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

class SprocketHole(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(20, 20)
        self.setStyleSheet("background-color: #555555; border-radius: 10px;")

class SecureImageBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.encryptor = ImageEncryptor()
        self.current_image_path = None
        self.current_image_data = None
        self.encrypted_data = None
        self.original_image = None  
        self.is_encrypted_view = False  
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Film Roll Secure Image Browser")
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1a1a1a;
                color: #f0f0f0;
            }
            QPushButton {
                background-color: #555555;
                color: #ffffff;
                border: 1px solid #888888;
                border-radius: 5px;
                padding: 5px 15px;
                min-height: 30px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
            QPushButton:disabled {
                background-color: #333333;
                color: #888888;
            }
            QScrollArea {
                border: none;
            }
            QLabel {
                color: #ffffff;
            }
        """)

        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel("SECURE IMAGE BROWSER")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Courier", 16, QFont.Bold))
        title_label.setStyleSheet("color: #f0f0f0; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        film_container = QWidget()
        film_layout = QVBoxLayout(film_container)
        film_layout.setSpacing(0)
        film_layout.setContentsMargins(0, 0, 0, 0)
        
        top_strip = QWidget()
        top_strip_layout = QHBoxLayout(top_strip)
        top_strip_layout.setSpacing(10)
        top_strip_layout.setContentsMargins(0, 0, 0, 0)
        top_strip.setFixedHeight(40)
        top_strip.setStyleSheet("background-color: #111111;")
        for i in range(15):
            hole = SprocketHole()
            hole.setFixedSize(15, 20)
            top_strip_layout.addWidget(hole)
        film_layout.addWidget(top_strip)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameStyle(QFrame.NoFrame)
        
        self.film_frame = FilmFrameWidget()
        frame_layout = QVBoxLayout(self.film_frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        
        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("color: #f0f0f0; font-size: 14px; font-family: Courier;")
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        frame_layout.addWidget(self.image_label)
        
        self.scroll_area.setWidget(self.film_frame)
        film_layout.addWidget(self.scroll_area)
        
        bottom_strip = QWidget()
        bottom_strip_layout = QHBoxLayout(bottom_strip)
        bottom_strip_layout.setSpacing(10)
        bottom_strip_layout.setContentsMargins(0, 0, 0, 0)
        bottom_strip.setFixedHeight(40)
        bottom_strip.setStyleSheet("background-color: #111111;")
        for i in range(15):
            hole = SprocketHole()
            hole.setFixedSize(15, 20)
            bottom_strip_layout.addWidget(hole)
        film_layout.addWidget(bottom_strip)
        main_layout.addWidget(film_container)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        self.open_btn = QPushButton("📷 Open Film")
        self.open_btn.clicked.connect(self.open_image)
        self.encrypt_btn = QPushButton("🔒 Encrypt")
        self.encrypt_btn.clicked.connect(self.encrypt_image)
        self.encrypt_btn.setEnabled(False)
        self.decrypt_btn = QPushButton("🔓 Decrypt")
        self.decrypt_btn.clicked.connect(self.decrypt_image)
        self.decrypt_btn.setEnabled(False)
        self.save_btn = QPushButton("💾 Save")
        self.save_btn.clicked.connect(self.save_image)
        self.save_btn.setEnabled(False)
        button_layout.addWidget(self.open_btn)
        button_layout.addWidget(self.encrypt_btn)
        button_layout.addWidget(self.decrypt_btn)
        button_layout.addWidget(self.save_btn)
        
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Courier", 10))
        self.status_label.setStyleSheet("color: #cccccc; margin-top: 5px;")
        
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.status_label)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def open_image(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", 
            "All Images (*.bmp *.jpg *.jpeg *.png *.gif);;BMP Files (*.bmp);;JPEG Files (*.jpg *.jpeg);;PNG Files (*.png);;Encrypted Files (*.enc);;All Files (*)", 
            options=options
        )
        if not file_path:
            return
        try:
            _, ext = os.path.splitext(file_path)
            if ext.lower() == '.enc':
                with open(file_path, 'rb') as f:
                    self.encrypted_data = f.read()
                self.current_image_path = file_path
                self.decrypt_btn.setEnabled(True)
                self.encrypt_btn.setEnabled(False)
                self.save_btn.setEnabled(True)
                self.is_encrypted_view = True
                self.display_encrypted_placeholder()
                self.status_label.setText(f"Encrypted film loaded: {os.path.basename(file_path)}")
            else:
                image = Image.open(file_path)
                if image.mode == 'RGBA':
                    image = image.convert('RGB')
                self.original_image = image.copy()
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format=image.format or 'BMP')
                self.current_image_data = img_byte_arr.getvalue()
                self.current_image_path = file_path
                self.display_film_style_image(image)
                self.is_encrypted_view = False
                self.encrypt_btn.setEnabled(True)
                self.decrypt_btn.setEnabled(False)
                self.save_btn.setEnabled(True)
                self.status_label.setText(f"Film loaded: {os.path.basename(file_path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open image: {str(e)}")

    def encrypt_image(self):
        if not self.current_image_data:
            return
        try:
            self.encrypted_data = self.encryptor.encrypt_image(self.current_image_data)
            if self.original_image:
                self.display_encrypted_version()
                self.is_encrypted_view = True
            self.save_btn.setEnabled(True)
            self.decrypt_btn.setEnabled(True)
            self.encrypt_btn.setEnabled(False)
            self.status_label.setText("Film encrypted - click 'Decrypt' to view original")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to encrypt image: {str(e)}")

    def decrypt_image(self):
        if not self.encrypted_data:
            return
        try:
            decrypted_data = self.encryptor.decrypt_image(self.encrypted_data)
            if decrypted_data is None:
                QMessageBox.critical(self, "Error", "Failed to decrypt image")
                return
            self.current_image_data = decrypted_data
            image = Image.open(io.BytesIO(decrypted_data))
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            self.original_image = image.copy()
            self.display_film_style_image(image)
            self.is_encrypted_view = False
            self.save_btn.setEnabled(True)
            self.encrypt_btn.setEnabled(True)
            self.decrypt_btn.setEnabled(False)
            self.status_label.setText("Film decrypted successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to decrypt image: {str(e)}")

    def save_image(self):
        options = QFileDialog.Options()
        if self.is_encrypted_view and self.encrypted_data:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Encrypted Picture", "", 
                "Encrypted Files (*.enc)", 
                options=options
            )
            if file_path and self.encrypted_data:
                try:
                    if not file_path.lower().endswith('.enc'):
                        file_path += '.enc'
                    with open(file_path, 'wb') as f:
                        f.write(self.encrypted_data)
                    self.status_label.setText(f"Encrypted film saved to {os.path.basename(file_path)}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save encrypted image: {str(e)}")
        elif self.current_image_data and not self.is_encrypted_view:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Film", "", 
                "BMP Files (*.bmp);;JPEG Files (*.jpg);;PNG Files (*.png);;All Files (*)", 
                options=options
            )
            if not file_path:
                return
            try:
                image = Image.open(io.BytesIO(self.current_image_data))
                if image.mode == 'RGBA':
                    image = image.convert('RGB')
                image.save(file_path)
                self.status_label.setText(f"Film saved to {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save image: {str(e)}")

    def display_image_from_pil(self, pil_image):
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")
        img_data = pil_image.tobytes("raw", "RGB")
        qimage = QImage(img_data, pil_image.width, pil_image.height, pil_image.width * 3, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        max_width = self.scroll_area.width() - 50
        max_height = self.scroll_area.height() - 50
        if pixmap.width() > max_width or pixmap.height() > max_height:
            pixmap = pixmap.scaled(max_width, max_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(pixmap)
        self.image_label.adjustSize()

    def display_film_style_image(self, original_image):
        if original_image:
            film_image = original_image.copy()
            if film_image.mode != "RGB":
                film_image = film_image.convert("RGB")
            width, height = film_image.size
            self.display_image_from_pil(film_image)

    def display_encrypted_version(self):
        if self.original_image:
            encrypted_image = self.original_image.copy()
            if encrypted_image.mode != "RGB":
                encrypted_image = encrypted_image.convert("RGB")
            encrypted_image = ImageOps.grayscale(encrypted_image)
            encrypted_image = ImageOps.autocontrast(encrypted_image, cutoff=5)
            encrypted_image = ImageOps.solarize(encrypted_image, threshold=128)
            encrypted_image = encrypted_image.convert("RGB")
            width, height = encrypted_image.size
            draw = ImageDraw.Draw(encrypted_image)
            for y in range(0, height, 10):
                draw.line([(0, y), (width, y)], fill=(0, 100, 200), width=1)
            for x in range(0, width, 10):
                draw.line([(x, 0), (x, height)], fill=(0, 100, 200), width=1)
            text_position = (width//2-60, height//2)
            draw.text((text_position[0]+2, text_position[1]+2), "ENCRYPTED", fill=(0, 0, 0))
            draw.text(text_position, "ENCRYPTED", fill=(255, 50, 50))
            for i in range(0, height, 40):
                box = (0, i, width, min(i+5, height))
                region = encrypted_image.crop(box)
                region = ImageOps.invert(region)
                encrypted_image.paste(region, box)
            for i in range(5):
                x = int(width * 0.1 * i)
                draw.line([(x, 0), (x, height)], fill=(200, 200, 200), width=1)
            self.display_image_from_pil(encrypted_image)

    def display_encrypted_placeholder(self):
        width, height = 400, 300
        placeholder = Image.new('RGB', (width, height), color=(20, 20, 30))
        draw = ImageDraw.Draw(placeholder)
        for y in range(0, height, 2):
            draw.line([(0, y), (width, y)], fill=(25, 25, 35), width=1)
        for i in range(20):
            y = int(height * 0.05 * i)
            h = random.randint(2, 10)
            color = (0, 100, 200) if i % 2 == 0 else (200, 0, 50)
            draw.rectangle([(0, y), (width, y+h)], fill=color)
        draw.text((width//2-80, height//2-30), "ENCRYPTED FILM", fill=(255, 255, 255))
        draw.text((width//2-90, height//2), "CLICK DECRYPT TO VIEW", fill=(255, 200, 100))
        self.display_image_from_pil(placeholder)

def main():
    app = QApplication(sys.argv)
    browser = SecureImageBrowser()
    browser.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
