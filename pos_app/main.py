import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QStackedWidget
from PyQt6.QtCore import Qt

from ui_login import LoginWindow
from ui_dashboard import DashboardWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("كاشير المنزل السوري - النظام الرئيسي")
        self.resize(1200, 800)
        
        # Central widget is a stacked widget to switch between screens
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Load Login Screen
        self.login_window = LoginWindow(self.on_login_success)
        self.stacked_widget.addWidget(self.login_window)
        
        # Load Stylesheet
        self.load_stylesheet()

    def load_stylesheet(self):
        style_path = os.path.join(os.path.dirname(__file__), "styles_dark.qss")
        if not os.path.exists(style_path):
            style_path = os.path.join(os.path.dirname(__file__), "styles.qss")
            
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
                
    def on_login_success(self, user):
        # This will be called when login is successful
        print(f"User logged in: {user.username} with role: {user.role}")
        
        # Create real dashboard
        self.dashboard = DashboardWindow(user, self.on_logout)
        self.stacked_widget.addWidget(self.dashboard)
        self.stacked_widget.setCurrentWidget(self.dashboard)
        
        self.showMaximized()

    def on_logout(self):
        # Switch back to login page
        self.stacked_widget.setCurrentWidget(self.login_window)
        # Remove dashboard widget from memory to reload fresh state next time
        if hasattr(self, 'dashboard'):
            self.stacked_widget.removeWidget(self.dashboard)
            self.dashboard.deleteLater()
            del self.dashboard
        self.showNormal()
        self.resize(1000, 700) # reset window size


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set RTL layout for Arabic
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
