import sys
from PyQt5.QtCore import QUrl, Qt, QSettings
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                            QTabWidget, QToolBar, QAction, QSystemTrayIcon, 
                            QMenu, QMessageBox, QDialog, QLabel, 
                            QLineEdit, QPushButton, QVBoxLayout, QShortcut,
                            QCheckBox)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtGui import QIcon, QKeySequence, QPalette, QColor

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 200)  # Reduced height since we removed quick chat
        
        layout = QVBoxLayout()
        
        # Hotkey setting
        self.hotkey_label = QLabel("New Tab Hotkey:")
        self.hotkey_input = QLineEdit()
        self.hotkey_input.setPlaceholderText("e.g., Ctrl+T")
        
        # Dark mode setting
        self.dark_mode_checkbox = QCheckBox("Enable Dark Mode")
        
        # Save button
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        
        layout.addWidget(self.hotkey_label)
        layout.addWidget(self.hotkey_input)
        layout.addWidget(self.dark_mode_checkbox)
        layout.addWidget(self.save_button)
        
        self.setLayout(layout)
        self.load_settings()
    
    def load_settings(self):
        settings = QSettings("DeepSeek", "DesktopApp")
        hotkey = settings.value("new_tab_hotkey", "Ctrl+T")  # Changed from quick_chat_hotkey
        dark_mode = settings.value("dark_mode", False, type=bool)
        
        self.hotkey_input.setText(hotkey)
        self.dark_mode_checkbox.setChecked(dark_mode)
    
    def save_settings(self):
        settings = QSettings("DeepSeek", "DesktopApp")
        settings.setValue("new_tab_hotkey", self.hotkey_input.text())  # Changed from quick_chat_hotkey
        settings.setValue("dark_mode", self.dark_mode_checkbox.isChecked())
        self.parent().apply_settings()
        self.accept()

class DeepSeekTab(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dark_mode = QSettings("DeepSeek", "DesktopApp").value("dark_mode", False, type=bool)
        
        if self.dark_mode:
            self.set_web_dark_mode()
        
        self.load(QUrl("https://chat.deepseek.com"))
        self.setAttribute(Qt.WA_DeleteOnClose, True)
    
    def set_web_dark_mode(self):
        """Simplified dark mode - just sets dark color scheme"""
        self.page().runJavaScript("document.documentElement.style.setProperty('color-scheme', 'dark');")
        self.page().setBackgroundColor(QColor(30, 30, 30))

class DeepSeekDesktop(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("DeepSeek", "DesktopApp")
        self.setWindowTitle("DeepSeek Desktop")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize UI components first
        self.init_ui()
        
        # Then connect signals
        self.connect_signals()
        
        # Apply settings after UI is ready
        self.apply_settings()
        
        # Final setup
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
    
    def init_ui(self):
        """Initialize all UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        main_layout.addWidget(self.tabs)
        
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)
        
        # Keep system icons for toolbar actions
        self.reload_action = QAction(QIcon.fromTheme("view-refresh"), "Reload", self)
        self.new_tab_action = QAction(QIcon.fromTheme("tab-new"), "New Tab", self)
        self.settings_action = QAction(QIcon.fromTheme("preferences-system"), "Settings", self)
        
        self.toolbar.addAction(self.reload_action)
        self.toolbar.addAction(self.new_tab_action)
        self.toolbar.addAction(self.settings_action)
        
        self.add_new_tab()
    
    def connect_signals(self):
        """Connect all signals after UI is initialized"""
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.tab_changed)
        self.reload_action.triggered.connect(self.reload_current_tab)
        self.new_tab_action.triggered.connect(self.add_new_tab)
        self.settings_action.triggered.connect(self.show_settings)
        
        self.setup_system_tray()
        self.setup_hotkey()
    
    def close_tab(self, index):
        if self.tabs.count() > 1:
            widget = self.tabs.widget(index)
            widget.deleteLater()
            self.tabs.removeTab(index)
    
    def tab_changed(self, index):
        pass
    
    def add_new_tab(self):
        tab = DeepSeekTab()
        tab_index = self.tabs.addTab(tab, "DeepSeek Chat")
        self.tabs.setCurrentIndex(tab_index)
        tab.loadFinished.connect(lambda _, i=tab_index: self.update_tab_title(i))
    
    def update_tab_title(self, index):
        widget = self.tabs.widget(index)
        if widget:
            title = widget.page().title()
            self.tabs.setTabText(index, title[:15] + "..." if len(title) > 15 else title)
    
    def reload_current_tab(self):
        current_widget = self.tabs.currentWidget()
        if current_widget:
            current_widget.reload()
    
    def apply_settings(self):
        dark_mode = self.settings.value("dark_mode", False, type=bool)
        
        if dark_mode:
            self.set_dark_mode()
        else:
            self.set_light_mode()
        
        if hasattr(self, 'tabs'):
            for i in range(self.tabs.count()):
                tab = self.tabs.widget(i)
                if isinstance(tab, DeepSeekTab):
                    if dark_mode:
                        tab.set_web_dark_mode()
                    else:
                        tab.page().setBackgroundColor(QColor(255, 255, 255))
                        tab.page().runJavaScript("document.documentElement.style.setProperty('color-scheme', 'light');")
    
    def set_dark_mode(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        dark_palette.setColor(QPalette.Disabled, QPalette.Text, Qt.darkGray)
        dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, Qt.darkGray)
        
        QApplication.setPalette(dark_palette)
    
    def set_light_mode(self):
        QApplication.setPalette(QApplication.style().standardPalette())
    
    def setup_hotkey(self):
        hotkey_str = self.settings.value("new_tab_hotkey", "Ctrl+T")  # Changed from quick_chat_hotkey
        
        if hasattr(self, 'new_tab_shortcut'):
            self.new_tab_shortcut.disconnect()
            del self.new_tab_shortcut
        
        try:
            sequence = QKeySequence(hotkey_str)
            self.new_tab_shortcut = QShortcut(sequence, self)
            self.new_tab_shortcut.activated.connect(self.add_new_tab)  # Now opens new tab instead of quick chat
        except:
            sequence = QKeySequence("Ctrl+T")
            self.new_tab_shortcut = QShortcut(sequence, self)
            self.new_tab_shortcut.activated.connect(self.add_new_tab)
    
    def show_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec_()
    
    def setup_system_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        
        # Load and properly scale the 1300x1300 icon for system tray
        icon = QIcon("icon.png")
        icon = QIcon.fromTheme("internet-web-browser")
        
        self.tray_icon.setIcon(icon)
        
        tray_menu = QMenu()
        self.toggle_action = QAction("Show/Hide", self)
        self.toggle_action.triggered.connect(self.toggle_window_visibility)
        tray_menu.addAction(self.toggle_action)
        
        # Removed Quick Chat action
        tray_menu.addSeparator()
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.tray_icon_clicked)
    
    def toggle_window_visibility(self):
        if self.isVisible():
            self.hide_to_tray()
        else:
            self.show_normal()
    
    def tray_icon_clicked(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.toggle_window_visibility()
    
    def show_normal(self):
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized)
        self.activateWindow()
    
    def hide_to_tray(self):
        self.hide()
    
    def quit_application(self):
        reply = QMessageBox.question(
            self, 'Quit',
            'Are you sure you want to quit DeepSeek Desktop?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.tray_icon.hide()
            QApplication.quit()
    
    def closeEvent(self, event):
        event.ignore()
        self.hide_to_tray()

if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    app.setApplicationName("DeepSeek Desktop")
    app.setQuitOnLastWindowClosed(False)
    
    window = DeepSeekDesktop()
    window.show()
    
    sys.exit(app.exec_())