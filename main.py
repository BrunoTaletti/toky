"""
Módulo principal da aplicação Toky - Gerenciador de Tokens 2FA
"""

import sys
import os
import pyotp
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QLabel, QListWidget, QListWidgetItem, QDialog, QLineEdit,
    QHBoxLayout, QMessageBox, QComboBox, QCheckBox
)
from PyQt6.QtGui import QFont, QPixmap, QIcon
from PyQt6.QtCore import Qt, QTimer
from datetime import datetime
from config import UIConfig, TokenUtils, BASE_DIR, DataManager, ThemeManager, Translator

class BaseDialog(QDialog):
    """Classe base para diálogos com estilização consistente"""
    def __init__(self, translator, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

class AddTokenDialog(BaseDialog):
    """Diálogo para adicionar um novo token 2FA"""
    def __init__(self, translator, parent=None):
        super().__init__(translator, parent)
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle(self.translator.get("add_token_title"))
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        self.service_name = QLineEdit(placeholderText=self.translator.get("service_name_label"))
        self.token_key = QLineEdit(placeholderText=self.translator.get("token_label"))
        
        self.btn_save = QPushButton(self.translator.get("save_btn"))
        self.btn_save.setIcon(QIcon(UIConfig.ICON_PATHS["add"]))
        self.btn_save.clicked.connect(self.validate_and_accept)
        
        layout.addWidget(QLabel(self.translator.get("service_name_label")))
        layout.addWidget(self.service_name)
        layout.addWidget(QLabel(self.translator.get("token_label")))
        layout.addWidget(self.token_key)
        layout.addWidget(self.btn_save)
        
        self.setLayout(layout)

    def validate_and_accept(self):
        if not self.service_name.text().strip():
            self.show_warning("empty_service_error")
            return
            
        token = TokenUtils.normalize_token(self.token_key.text())
        
        if not token or not TokenUtils.is_valid_token(token):
            self.show_warning("invalid_token_error")
            return
            
        self.token_key.setText(token)
        self.accept()

    def show_warning(self, message_key):
        QMessageBox.warning(
            self,
            self.translator.get("invalid_token_title"),
            self.translator.get(message_key)
        )

class EditTokenDialog(BaseDialog):
    """Diálogo para editar um token existente"""
    def __init__(self, current_name, current_token, translator, parent=None):
        super().__init__(translator, parent)
        self.current_name = current_name
        self.current_token = current_token
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle(self.translator.get("edit_token_title"))
        
        layout = QVBoxLayout()
        
        self.service_name = QLineEdit(self.current_name)
        self.token_key = QLineEdit(self.current_token)
        self.token_key.setPlaceholderText(self.translator.get("token_label"))
        self.token_key.setEnabled(False)
        
        self.enable_edit_check = QCheckBox(self.translator.get("enable_edit_label"))
        self.enable_edit_check.stateChanged.connect(self.toggle_token_edit)
        
        btn_save = QPushButton(self.translator.get("save_btn"))
        btn_save.clicked.connect(self.validate_and_accept)
        
        layout.addWidget(QLabel(self.translator.get("service_name_label")))
        layout.addWidget(self.service_name)
        layout.addWidget(QLabel(self.translator.get("token_label")))
        layout.addWidget(self.token_key)
        layout.addWidget(self.enable_edit_check)
        layout.addWidget(btn_save)
        
        self.setLayout(layout)

    def toggle_token_edit(self, state):
        self.token_key.setEnabled(state == Qt.CheckState.Checked.value)
        
    def validate_and_accept(self):
        if not self.service_name.text().strip():
            self.show_warning("empty_service_error")
            return
            
        if self.token_key.isEnabled():
            token = TokenUtils.normalize_token(self.token_key.text())
            if not token or not TokenUtils.is_valid_token(token):
                self.show_warning("invalid_token_error")
                return
            self.token_key.setText(token)
            
        self.accept()

    def show_warning(self, message_key):
        QMessageBox.warning(
            self,
            self.translator.get("invalid_token_title"),
            self.translator.get(message_key)
        )

class TokenItemWidget(QWidget):
    """Widget que representa um token na lista"""
    def __init__(self, name, token, translator, main_window_ref, parent=None):
        super().__init__(parent)
        self.name = name
        self.token = token
        self.translator = translator
        self.main_window = main_window_ref
        self.totp = pyotp.TOTP(token)
        self.setup_ui()
        self.start_timer()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.name_label = QLabel(self.name)
        self.name_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        self.code_label = QLabel(self.totp.now())
        self.code_label.setObjectName("code_label")
        self.code_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #3578FC;")
        
        self.time_label = QLabel("30s")
        self.time_label.setStyleSheet("font-size: 10px; color: #AAAAAA;")
        
        btn_layout = QHBoxLayout()
        
        self.btn_copy = QPushButton()
        self.btn_copy.setIcon(QIcon(UIConfig.ICON_PATHS["copy"]))
        self.btn_copy.setToolTip(self.translator.get("copy_btn"))
        self.btn_copy.clicked.connect(lambda: self.main_window.copy_code(self.code_label.text()))
        
        self.btn_edit = QPushButton()
        self.btn_edit.setIcon(QIcon(UIConfig.ICON_PATHS["edit"]))
        self.btn_edit.setToolTip(self.translator.get("edit_btn"))
        self.btn_edit.clicked.connect(lambda: self.main_window.edit_token(self))
        
        self.btn_delete = QPushButton()
        self.btn_delete.setIcon(QIcon(UIConfig.ICON_PATHS["delete"]))
        self.btn_delete.setToolTip(self.translator.get("delete_btn"))
        self.btn_delete.clicked.connect(lambda: self.main_window.delete_token(self))
        
        btn_layout.addWidget(self.btn_copy)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        
        layout.addWidget(self.name_label)
        layout.addWidget(self.code_label)
        layout.addWidget(self.time_label)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)

    def start_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(1000)

    def update_display(self):
        self.code_label.setText(self.totp.now())
        remaining = 30 - datetime.now().second % 30
        self.time_label.setText(f"expira em {remaining}s")

class MainWindow(QMainWindow):
    """Janela principal da aplicação"""
    def __init__(self):
        super().__init__()
        self.current_theme = "dark"
        self.translator = UIConfig.init_translator()
        self.tokens = []
        self.setup_ui()
        self.load_tokens()
        self.apply_theme()

    def setup_ui(self):
        self.setWindowTitle(self.translator.get("app_title"))
        self.setFixedSize(500, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Barra de controle
        control_bar = QHBoxLayout()
        
        self.language_selector = QComboBox()
        self.load_language_flags()
        self.language_selector.currentIndexChanged.connect(self.change_language)
        
        self.theme_selector = QComboBox()
        self.theme_selector.addItem(QIcon(UIConfig.ICON_PATHS["sun"]), "")
        self.theme_selector.addItem(QIcon(UIConfig.ICON_PATHS["moon"]), "")
        self.theme_selector.setCurrentIndex(1)  # Tema escuro por padrão
        self.theme_selector.currentIndexChanged.connect(self.toggle_theme)
        
        control_bar.addWidget(self.language_selector)
        control_bar.addStretch()
        control_bar.addWidget(self.theme_selector)
        
        # Logo
        logo = QLabel()
        pixmap = QPixmap(os.path.join(BASE_DIR, "app-logo.png"))
        logo.setPixmap(pixmap.scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Lista de tokens
        self.list_widget = QListWidget()
        
        # Botão adicionar
        self.btn_add = QPushButton(self.translator.get("add_token_btn"))
        self.btn_add.setIcon(QIcon(UIConfig.ICON_PATHS["add"]))
        self.btn_add.clicked.connect(self.show_add_dialog)
        
        layout.addLayout(control_bar)
        layout.addWidget(logo)
        layout.addWidget(QLabel(self.translator.get("your_tokens_label")))
        layout.addWidget(self.list_widget)
        layout.addWidget(self.btn_add)
        
        central_widget.setLayout(layout)

    def load_language_flags(self):
        languages = {
            "en_US": ("us", "english"),
            "pt_BR": ("br", "portuguese"),
            "es_ES": ("es", "spanish"),
            "ru_RU": ("ru", "russian")
        }
        
        for lang_code, (flag, lang_key) in languages.items():
            flag_path = os.path.join(BASE_DIR, "resources", "flags", f"{flag}.png")
            self.language_selector.addItem(QIcon(flag_path), self.translator.get(lang_key))

    def toggle_theme(self, index):
        self.current_theme = "light" if index == 0 else "dark"
        self.apply_theme()

    def apply_theme(self):
        theme = ThemeManager.load_theme(self.current_theme)
        self.setStyleSheet(theme)
        for dialog in self.findChildren(QDialog):
            dialog.setStyleSheet(theme)

    def change_language(self, index):
        languages = ["en_US", "pt_BR", "es_ES", "ru_RU"]
        if index < len(languages):
            try:
                self.translator = Translator(languages[index])
                self.reload_ui()
            except Exception as e:
                print(f"Error changing language: {e}")
                self.language_selector.setCurrentIndex(0)
                self.translator = Translator("en_US")
                self.reload_ui()

    def reload_ui(self):
        self.setWindowTitle(self.translator.get("app_title"))
        self.btn_add.setText(self.translator.get("add_token_btn"))
        
        # Atualiza tooltips dos botões
        for i in range(self.list_widget.count()):
            widget = self.list_widget.itemWidget(self.list_widget.item(i))
            if widget:
                widget.btn_copy.setToolTip(self.translator.get("copy_btn"))
                widget.btn_edit.setToolTip(self.translator.get("edit_btn"))
                widget.btn_delete.setToolTip(self.translator.get("delete_btn"))

    def show_add_dialog(self):
        dialog = AddTokenDialog(self.translator, self)
        if dialog.exec():
            service = dialog.service_name.text().strip()
            token = dialog.token_key.text()
            
            if service and token:
                self.add_token(service, token)

    def load_tokens(self):
        tokens = DataManager.load_tokens()
        for token in tokens:
            if TokenUtils.is_valid_token(token['token']):
                self.add_token_to_ui(token['service'], token['token'])

    def add_token_to_ui(self, service, token):
        item = QListWidgetItem()
        widget = TokenItemWidget(service, token, self.translator, self)
        item.setSizeHint(widget.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, widget)
        self.tokens.append({'service': service, 'token': token})

    def add_token(self, service, token):
        token = TokenUtils.normalize_token(token)
        if TokenUtils.is_valid_token(token):
            self.add_token_to_ui(service, token)
            self.save_tokens()
        else:
            QMessageBox.warning(self, "Error", "Invalid token")

    def save_tokens(self):
        tokens = []
        for i in range(self.list_widget.count()):
            widget = self.list_widget.itemWidget(self.list_widget.item(i))
            tokens.append({'service': widget.name, 'token': widget.token})
        DataManager.save_tokens(tokens)

    def copy_code(self, code):
        QApplication.clipboard().setText(code)
        QMessageBox.information(self, "Copied", f"Code {code} copied to clipboard")

    def edit_token(self, token_widget):
        item = None
        for i in range(self.list_widget.count()):
            if self.list_widget.itemWidget(self.list_widget.item(i)) == token_widget:
                item = self.list_widget.item(i)
                break
        
        if item:
            dialog = EditTokenDialog(token_widget.name, token_widget.token, self.translator, self)
            if dialog.exec():
                new_name = dialog.service_name.text().strip()
                new_token = token_widget.token
                
                if dialog.token_key.isEnabled():
                    new_token = TokenUtils.normalize_token(dialog.token_key.text())
                
                if new_name and TokenUtils.is_valid_token(new_token):
                    token_widget.name = new_name
                    token_widget.token = new_token
                    token_widget.totp = pyotp.TOTP(new_token)
                    token_widget.name_label.setText(new_name)
                    self.save_tokens()

    def delete_token(self, token_widget):
        reply = QMessageBox.question(
            self,
            "Confirm",
            "Delete this token?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for i in range(self.list_widget.count()):
                if self.list_widget.itemWidget(self.list_widget.item(i)) == token_widget:
                    self.list_widget.takeItem(i)
                    del self.tokens[i]
                    self.save_tokens()
                    break

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont(UIConfig.FONT_NAME, UIConfig.FONT_SIZE))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())