import os
import sys
import io
import random
from PIL import Image, ImageFilter, ImageOps, ImageDraw, ImageFont
from cryptography.fernet import Fernet
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFileDialog, QScrollArea, QMessageBox, 
                             QFrame, QSizePolicy, QCheckBox)
from PyQt5.QtGui import QPixmap, QImage, QFont, QPalette, QColor
from PyQt5.QtCore import Qt

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
    
    def closeEvent(self, event):
        if self.current_image_data:
            try:
                encrypted_data = self.encryptor.encrypt_image(self.current_image_data)
                base_name = os.path.basename(self.current_image_path or "auto_saved")
                name, _ = os.path.splitext(base_name)
                auto_save_path = os.path.join(os.path.dirname(self.current_image_path or "."), f"{name}_auto.enc")
                with open(auto_save_path, 'wb') as f:
                    f.write(encrypted_data)
                print(f"Auto-encrypted image saved to {auto_save_path}")
            except Exception as e:
                print(f"Auto-encryption failed: {e}")
        event.accept()

    def __init__(self):
        super().__init__()
        self.encryptor = ImageEncryptor()
        self.current_image_path = None
        self.current_image_data = None
        self.encrypted_data = None
        self.original_image = None
        self.is_encryption_preview = False
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Secure Image Browser")
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
            QCheckBox {
                color: #ffffff;
                font-size: 12px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
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
        
        # Checkbox for encryption preview
        self.preview_checkbox = QCheckBox("Show Encryption Preview")
        self.preview_checkbox.toggled.connect(self.toggle_encryption_preview)
        main_layout.addWidget(self.preview_checkbox)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        self.open_btn = QPushButton("📷 Open Image")
        self.open_btn.clicked.connect(self.open_image)
        self.save_btn = QPushButton("💾 Save Image")
        self.save_btn.clicked.connect(self.save_image)
        self.save_btn.setEnabled(False)

        button_layout.addWidget(self.open_btn)
        button_layout.addWidget(self.save_btn)
        
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Courier", 10))
        self.status_label.setStyleSheet("color: #cccccc; margin-top: 5px;")
        
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.status_label)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def toggle_encryption_preview(self, checked):
        if not self.original_image:
            return
            
        self.is_encryption_preview = checked
        if checked:
            self.display_encrypted_version()
            self.status_label.setText("Showing encryption preview")
        else:
            self.display_film_style_image(self.original_image)
            self.status_label.setText("Showing normal image")

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
                # Handle encrypted file
                with open(file_path, 'rb') as f:
                    self.encrypted_data = f.read()
                
                # Auto-decrypt
                decrypted_data = self.encryptor.decrypt_image(self.encrypted_data)
                if decrypted_data is None:
                    QMessageBox.critical(self, "Error", "Failed to decrypt image")
                    return
                    
                self.current_image_data = decrypted_data
                image = Image.open(io.BytesIO(decrypted_data))
                if image.mode == 'RGBA':
                    image = image.convert('RGB')
                self.original_image = image.copy()
                self.current_image_path = file_path
                
                # Reset encryption preview checkbox for encrypted files
                self.preview_checkbox.setChecked(False)
                self.is_encryption_preview = False
                
                self.display_film_style_image(image)
                self.save_btn.setEnabled(True)
                self.status_label.setText(f"Encrypted image loaded and decrypted successfully: {os.path.basename(file_path)}")
            else:
                # Handle regular image file
                image = Image.open(file_path)
                if image.mode == 'RGBA':
                    image = image.convert('RGB')
                self.original_image = image.copy()
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format=image.format or 'BMP')
                self.current_image_data = img_byte_arr.getvalue()
                self.current_image_path = file_path
                
                # Auto-encrypt (just for storing internally)
                self.encrypted_data = self.encryptor.encrypt_image(self.current_image_data)
                
                # Automatically check encryption preview checkbox for regular images
                self.preview_checkbox.setChecked(True)
                self.is_encryption_preview = True
                
                # Display the encrypted version immediately
                self.display_encrypted_version()
                self.save_btn.setEnabled(True)
                self.status_label.setText(f"Image loaded and encryption preview shown: {os.path.basename(file_path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open image: {str(e)}")

    def save_image(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Image", "",
            "BMP Files (*.bmp);;JPEG Files (*.jpg);;PNG Files (*.png);;Encrypted Files (*.enc)",
            options=options
        )
        if not file_path:
            return

        try:
            if file_path.lower().endswith('.enc'):
                # Save as encrypted file
                if self.current_image_data:
                    encrypted_data = self.encryptor.encrypt_image(self.current_image_data)
                    with open(file_path, 'wb') as f:
                        f.write(encrypted_data)
                    self.status_label.setText(f"Image automatically encrypted and saved: {os.path.basename(file_path)}")
                else:
                    QMessageBox.warning(self, "Save Error", "No image data to encrypt.")
            else:
                # Save as regular image file
                if self.current_image_data:
                    image = Image.open(io.BytesIO(self.current_image_data))
                    if image.mode == 'RGBA':
                        image = image.convert('RGB')
                    image.save(file_path)
                    
                    # Also create an encrypted version automatically
                    encrypted_path = file_path + ".enc"
                    encrypted_data = self.encryptor.encrypt_image(self.current_image_data)
                    with open(encrypted_path, 'wb') as ef:
                        ef.write(encrypted_data)
                    self.status_label.setText(f"Image saved and automatically encrypted: {os.path.basename(file_path)}")
                else:
                    QMessageBox.warning(self, "Save Error", "No image data available.")
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
            self.display_image_from_pil(film_image)

    def display_encrypted_version(self):
        if self.original_image:
            encrypted_image = self.original_image.copy()
            if encrypted_image.mode != "RGB":
                encrypted_image = encrypted_image.convert("RGB")
            
            # Apply visual effects to represent encryption
            encrypted_image = ImageOps.grayscale(encrypted_image)
            encrypted_image = ImageOps.autocontrast(encrypted_image, cutoff=5)
            encrypted_image = ImageOps.solarize(encrypted_image, threshold=128)
            encrypted_image = encrypted_image.convert("RGB")
            
            width, height = encrypted_image.size
            draw = ImageDraw.Draw(encrypted_image)
            
            # Add a grid pattern
            for y in range(0, height, 10):
                draw.line([(0, y), (width, y)], fill=(0, 100, 200), width=1)
            for x in range(0, width, 10):
                draw.line([(x, 0), (x, height)], fill=(0, 100, 200), width=1)
            
            # Add "ENCRYPTED" text overlay
            text_position = (width//2-60, height//2)
            draw.text((text_position[0]+2, text_position[1]+2), "ENCRYPTED", fill=(0, 0, 0))
            draw.text(text_position, "ENCRYPTED", fill=(255, 50, 50))
            
            # Add some scanline effects
            for i in range(0, height, 40):
                box = (0, i, width, min(i+5, height))
                region = encrypted_image.crop(box)
                region = ImageOps.invert(region)
                encrypted_image.paste(region, box)
            
            self.display_image_from_pil(encrypted_image)


def main():
    app = QApplication(sys.argv)
    browser = SecureImageBrowser()
    browser.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()