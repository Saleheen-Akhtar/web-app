import sys
import os
import requests
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QTableWidget,
    QTableWidgetItem, QMessageBox, QListWidget, QListWidgetItem,
    QStackedWidget, QFrame, QSizePolicy, QHeaderView, QDialog,
    QGraphicsDropShadowEffect, QScrollArea, QSpacerItem, QGridLayout
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QBrush
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use('Qt5Agg')

API_URL = "http://localhost:8000/api/"

# ─── Color Palette (matches web UI) ──────────────────────────────────────────

COLORS = {
    'bg_primary':       '#f8fafc',
    'bg_secondary':     '#ffffff',
    'bg_sidebar':       '#0f172a',
    'bg_sidebar_hover': '#1e293b',
    'text_primary':     '#0f172a',
    'text_secondary':   '#475569',
    'text_tertiary':    '#94a3b8',
    'text_inverse':     '#f1f5f9',
    'border':           '#e2e8f0',
    'border_light':     '#f1f5f9',
    'accent':           '#6366f1',
    'accent_hover':     '#4f46e5',
    'accent_light':     '#eef2ff',
    'success':          '#10b981',
    'warning':          '#f59e0b',
    'danger':           '#ef4444',
    'info':             '#0ea5e9',
    'chart_1': '#6366f1', 'chart_2': '#10b981', 'chart_3': '#f59e0b',
    'chart_4': '#ef4444', 'chart_5': '#0ea5e9', 'chart_6': '#a855f7',
    'chart_7': '#ec4899',
}

CHART_COLORS_HEX = [COLORS['chart_1'], COLORS['chart_2'], COLORS['chart_3'],
                     COLORS['chart_4'], COLORS['chart_5'], COLORS['chart_6'], COLORS['chart_7']]

CHART_COLORS_RGBA = [
    (99/255, 102/255, 241/255, 0.8),
    (16/255, 185/255, 129/255, 0.8),
    (245/255, 158/255, 11/255, 0.8),
    (239/255, 68/255,  68/255, 0.8),
    (14/255, 165/255, 233/255, 0.8),
    (168/255, 85/255, 247/255, 0.8),
    (236/255, 72/255, 153/255, 0.8),
]

# ─── Stylesheet ───────────────────────────────────────────────────────────────

GLOBAL_STYLE = """
* {
    font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
}

QMainWindow {
    background-color: #f8fafc;
}

/* ─── Login Page ───────────────────── */

#loginPage {
    background-color: #f8fafc;
}

#loginLeftPanel {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #0f172a, stop:0.5 #1e293b, stop:1 #334155);
}

#loginBrandIconBox {
    background-color: rgba(99, 102, 241, 60);
    border-radius: 16px;
}

#loginBrandTitle {
    color: white;
    font-size: 36px;
    font-weight: bold;
}

#loginBrandSubtitle {
    color: #94a3b8;
    font-size: 15px;
}

#loginFeature {
    color: #cbd5e1;
    font-size: 14px;
}

#featureDot {
    background-color: #6366f1;
    border-radius: 4px;
}

#loginCardTitle {
    color: #0f172a;
    font-size: 26px;
    font-weight: bold;
}

#loginCardSubtitle {
    color: #475569;
    font-size: 14px;
}

#fieldLabel {
    color: #0f172a;
    font-size: 13px;
    font-weight: 600;
}

#loginInput {
    padding: 10px 14px 10px 40px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    font-size: 14px;
    background: white;
    color: #0f172a;
}
#loginInput:focus {
    border: 2px solid #6366f1;
}

#loginBtn {
    background-color: #6366f1;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px;
    font-size: 15px;
    font-weight: bold;
}
#loginBtn:hover {
    background-color: #4f46e5;
}
#loginBtn:disabled {
    background-color: #a5b4fc;
}

#toggleBtn {
    background: none;
    border: none;
    color: #6366f1;
    font-size: 14px;
    font-weight: bold;
}
#toggleBtn:hover {
    color: #4f46e5;
    text-decoration: underline;
}

#toggleLabel {
    color: #94a3b8;
    font-size: 14px;
}

#toggleSeparator {
    border: none;
    border-top: 1px solid #f1f5f9;
}

#errorLabel {
    color: #ef4444;
    background-color: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
}

/* ─── Topbar ───────────────────────── */

#topbar {
    background-color: white;
    border-bottom: 1px solid #e2e8f0;
}

#topbarBrand {
    color: #6366f1;
    font-size: 17px;
    font-weight: bold;
}

#topbarAvatar {
    background-color: #eef2ff;
    border-radius: 16px;
    color: #6366f1;
}

#topbarUser {
    color: #475569;
    font-size: 13px;
    font-weight: 500;
}

#logoutBtn {
    background: transparent;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 12px;
    color: #475569;
}
#logoutBtn:hover {
    background: #fef2f2;
    color: #ef4444;
    border-color: #fecaca;
}

/* ─── Sidebar ──────────────────────── */

#sidebar {
    background-color: #0f172a;
}

#sidebarTitle {
    color: #94a3b8;
    font-size: 13px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}

#sidebarBadge {
    color: #818cf8;
    background: rgba(99, 102, 241, 0.2);
    border-radius: 10px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: bold;
}

#uploadBtn {
    border: 1px dashed rgba(148, 163, 184, 76);
    border-radius: 8px;
    background: transparent;
    color: #94a3b8;
    padding: 10px;
    font-size: 13px;
    font-weight: 500;
}
#uploadBtn:hover {
    border-color: #6366f1;
    color: #818cf8;
    background: rgba(99, 102, 241, 13);
}

#sidebarList {
    background: transparent;
    border: none;
    color: #f1f5f9;
    font-size: 13px;
    outline: none;
}
#sidebarList::item {
    padding: 6px 4px;
    border-radius: 8px;
    margin-bottom: 2px;
}
#sidebarList::item:hover {
    background: #1e293b;
}
#sidebarList::item:selected {
    background: rgba(99, 102, 241, 38);
}

#sidebarItemIcon {
    background-color: #1e293b;
    border-radius: 6px;
}

#sidebarItemIconActive {
    background-color: rgba(99, 102, 241, 51);
    border-radius: 6px;
}

#sidebarItemTitle {
    color: #f1f5f9;
    font-size: 13px;
    font-weight: 500;
}

#sidebarItemTitleActive {
    color: #818cf8;
    font-size: 13px;
    font-weight: 500;
}

#sidebarItemMeta {
    color: #64748b;
    font-size: 11px;
}

#deleteBtn {
    background: transparent;
    border: none;
    color: #64748b;
    font-size: 11px;
    padding: 4px 8px;
    border-radius: 4px;
}
#deleteBtn:hover {
    background: rgba(239, 68, 68, 38);
    color: #f87171;
}

#sidebarEmpty {
    color: #475569;
    font-size: 13px;
}

/* ─── Dashboard Main ───────────────── */

#dashboardMain {
    background: #f8fafc;
}

#dashboardTitle {
    color: #0f172a;
    font-size: 26px;
    font-weight: bold;
}

#dashboardSubtitle {
    color: #94a3b8;
    font-size: 13px;
}

#pdfBtn {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 8px 18px;
    font-size: 13px;
    color: #475569;
    font-weight: 500;
}
#pdfBtn:hover {
    background: #6366f1;
    color: white;
    border-color: #6366f1;
}

/* ─── Stat Cards ───────────────────── */

#statCard {
    background: white;
    border: 1px solid #f1f5f9;
    border-radius: 12px;
    padding: 18px 20px;
}

#statIconBox {
    border-radius: 10px;
    padding: 12px;
}

#statLabel {
    color: #94a3b8;
    font-size: 12px;
    font-weight: 500;
}

#statValue {
    color: #0f172a;
    font-size: 21px;
    font-weight: bold;
}

/* ─── Chart Cards ──────────────────── */

#chartCard {
    background: white;
    border: 1px solid #f1f5f9;
    border-radius: 12px;
    padding: 22px;
}

#chartCardTitle {
    color: #0f172a;
    font-size: 15px;
    font-weight: 600;
}

#chartCardIcon {
    color: #475569;
    font-size: 14px;
}

/* ─── Table ────────────────────────── */

#tableCard {
    background: white;
    border: 1px solid #f1f5f9;
    border-radius: 12px;
}

#tableCardHeader {
    padding: 18px 22px;
    border-bottom: 1px solid #f1f5f9;
}

#tableTitle {
    color: #0f172a;
    font-size: 15px;
    font-weight: 600;
}

#tableSubtitle {
    color: #94a3b8;
    font-size: 12px;
}

QTableWidget {
    background: white;
    border: none;
    gridline-color: #f1f5f9;
    font-size: 13px;
    color: #475569;
}

QTableWidget::item {
    padding: 12px 22px;
    border-bottom: 1px solid #f1f5f9;
}

QTableWidget::item:selected {
    background: rgba(99, 102, 241, 0.08);
    color: #0f172a;
}

QHeaderView::section {
    background: #f8fafc;
    color: #94a3b8;
    font-size: 11px;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 11px 22px;
    border: none;
    border-bottom: 1px solid #f1f5f9;
}

/* ─── Empty State ──────────────────── */

#emptyCircle {
    background: #eef2ff;
    border-radius: 60px;
}

#emptyTitle {
    color: #0f172a;
    font-size: 21px;
    font-weight: 600;
}

#emptySubtitle {
    color: #94a3b8;
    font-size: 14px;
}

/* ─── Scrollbar ────────────────────── */

QScrollBar:vertical {
    background: transparent;
    width: 6px;
}
QScrollBar::handle:vertical {
    background: #cbd5e1;
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #94a3b8;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

/* ─── Delete Dialog ────────────────── */

#deleteDialog {
    background: white;
    border-radius: 16px;
}

#deleteDialogIconCircle {
    background-color: #fef2f2;
    border-radius: 28px;
}

#deleteDialogTitle {
    color: #0f172a;
    font-size: 17px;
    font-weight: 600;
}

#deleteDialogMsg {
    color: #475569;
    font-size: 13px;
    line-height: 22px;
}

#modalCloseBtn {
    background: transparent;
    border: none;
    color: #94a3b8;
    font-size: 16px;
    padding: 4px 8px;
    border-radius: 6px;
}
#modalCloseBtn:hover {
    background: #f1f5f9;
    color: #0f172a;
}

#cancelBtn {
    background: #f1f5f9;
    color: #475569;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 600;
}
#cancelBtn:hover {
    background: #e2e8f0;
    color: #0f172a;
}

#confirmDeleteBtn {
    background: #ef4444;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 600;
}
#confirmDeleteBtn:hover {
    background: #dc2626;
}

/* ─── Type badge ───────────────────── */

#typeBadge {
    background-color: #eef2ff;
    color: #6366f1;
    border-radius: 10px;
    padding: 2px 10px;
    font-size: 12px;
    font-weight: 600;
}
"""

# ─── Helper: configure matplotlib axes ────────────────────────────────────────

def setup_chart_style(fig, ax, title=""):
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    if title:
        ax.set_title(title, fontsize=12, fontweight='600', color='#0f172a', pad=12)
    ax.tick_params(colors='#94a3b8', labelsize=9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#f1f5f9')
    ax.spines['bottom'].set_color('#f1f5f9')
    ax.yaxis.grid(True, color='#f1f5f9', linewidth=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout(pad=2.0)


def format_datetime(iso_str):
    """Format an ISO datetime string like the web does: 'Feb 9, 2026, 08:30 PM'"""
    try:
        dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        return dt.strftime('%b %d, %Y, %I:%M %p')
    except Exception:
        return iso_str


# ─── Custom Delete Dialog (matches web modal) ────────────────────────────────

class DeleteDialog(QDialog):
    def __init__(self, filename, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Delete Upload")
        self.setFixedSize(400, 260)
        self.setObjectName("deleteDialog")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)

        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(30, 24, 30, 28)

        # Close button row (top right)
        close_row = QHBoxLayout()
        close_row.addStretch()
        close_btn = QPushButton("✕")
        close_btn.setObjectName("modalCloseBtn")
        close_btn.setFixedSize(32, 32)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.reject)
        close_row.addWidget(close_btn)
        layout.addLayout(close_row)

        # Red icon circle
        icon_circle = QLabel("🗑")
        icon_circle.setObjectName("deleteDialogIconCircle")
        icon_circle.setFixedSize(56, 56)
        icon_circle.setAlignment(Qt.AlignCenter)
        icon_circle.setFont(QFont("Segoe UI Emoji", 20))
        layout.addWidget(icon_circle, alignment=Qt.AlignCenter)

        layout.addSpacing(12)

        title = QLabel("Delete Upload")
        title.setObjectName("deleteDialogTitle")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(4)

        msg = QLabel(f'Are you sure you want to delete <b>{filename}</b>? This action cannot be undone.')
        msg.setObjectName("deleteDialogMsg")
        msg.setAlignment(Qt.AlignCenter)
        msg.setWordWrap(True)
        msg.setTextFormat(Qt.RichText)
        layout.addWidget(msg)

        layout.addSpacing(16)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedHeight(38)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("confirmDeleteBtn")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setFixedHeight(38)
        delete_btn.clicked.connect(self.accept)
        btn_layout.addWidget(delete_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)


# ─── MplCanvas ────────────────────────────────────────────────────────────────

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=3.5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setMinimumHeight(260)


# ─── Login Page ───────────────────────────────────────────────────────────────

class LoginPage(QWidget):
    def __init__(self, on_login, parent=None):
        super().__init__(parent)
        self.on_login = on_login
        self.is_signup = False
        self.setObjectName("loginPage")
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ─ Left branded panel (gradient) ─
        left = QWidget()
        left.setObjectName("loginLeftPanel")
        left.setFixedWidth(460)
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(60, 0, 60, 0)
        left_layout.addStretch(2)

        # Brand icon box (like web's .login-brand-icon)
        brand_icon = QLabel("⚗")
        brand_icon.setObjectName("loginBrandIconBox")
        brand_icon.setFixedSize(72, 72)
        brand_icon.setAlignment(Qt.AlignCenter)
        brand_icon.setFont(QFont("Segoe UI Emoji", 28))
        brand_icon.setStyleSheet("""
            background-color: rgba(99, 102, 241, 60);
            border-radius: 16px;
            color: #818cf8;
        """)
        left_layout.addWidget(brand_icon)
        left_layout.addSpacing(20)

        brand_title = QLabel("ChemViz")
        brand_title.setObjectName("loginBrandTitle")
        left_layout.addWidget(brand_title)

        left_layout.addSpacing(6)

        brand_sub = QLabel("Chemical Equipment Monitoring\n& Analytics Platform")
        brand_sub.setObjectName("loginBrandSubtitle")
        left_layout.addWidget(brand_sub)

        left_layout.addSpacing(40)

        features = [
            "Real-time equipment monitoring",
            "Advanced data visualization",
            "PDF report generation",
            "Historical trend analysis",
        ]
        for f in features:
            row = QHBoxLayout()
            row.setSpacing(12)
            dot = QLabel()
            dot.setObjectName("featureDot")
            dot.setFixedSize(8, 8)
            row.addWidget(dot, alignment=Qt.AlignVCenter)
            lbl = QLabel(f)
            lbl.setObjectName("loginFeature")
            row.addWidget(lbl, 1)
            left_layout.addLayout(row)
            left_layout.addSpacing(10)

        left_layout.addStretch(3)
        left.setLayout(left_layout)
        root.addWidget(left)

        # ─ Right form panel (scrollable so button is never clipped) ─
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setFrameShape(QFrame.NoFrame)
        right_scroll.setStyleSheet("QScrollArea { background-color: #f8fafc; border: none; }")

        right = QWidget()
        right.setObjectName("loginRightPanel")
        right.setStyleSheet("#loginRightPanel { background-color: #f8fafc; }")
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignCenter)
        right_layout.setContentsMargins(40, 30, 40, 30)

        form_container = QWidget()
        form_container.setFixedWidth(400)
        form_layout = QVBoxLayout()
        form_layout.setSpacing(10)

        self.title_label = QLabel("Welcome back")
        self.title_label.setObjectName("loginCardTitle")
        form_layout.addWidget(self.title_label)
        form_layout.addSpacing(2)

        self.subtitle_label = QLabel("Sign in to your account to continue")
        self.subtitle_label.setObjectName("loginCardSubtitle")
        form_layout.addWidget(self.subtitle_label)

        form_layout.addSpacing(18)

        self.error_label = QLabel("")
        self.error_label.setObjectName("errorLabel")
        self.error_label.setVisible(False)
        self.error_label.setWordWrap(True)
        form_layout.addWidget(self.error_label)

        # Username field with label
        self.username_label = QLabel("Username")
        self.username_label.setObjectName("fieldLabel")
        form_layout.addWidget(self.username_label)
        self.username_input = QLineEdit()
        self.username_input.setObjectName("loginInput")
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setFixedHeight(44)
        form_layout.addWidget(self.username_input)

        form_layout.addSpacing(4)

        # Email field with label
        self.email_label = QLabel("Email")
        self.email_label.setObjectName("fieldLabel")
        self.email_label.setVisible(False)
        form_layout.addWidget(self.email_label)
        self.email_input = QLineEdit()
        self.email_input.setObjectName("loginInput")
        self.email_input.setPlaceholderText("Enter your email")
        self.email_input.setFixedHeight(44)
        self.email_input.setVisible(False)
        form_layout.addWidget(self.email_input)

        # Password field with label
        self.password_label = QLabel("Password")
        self.password_label.setObjectName("fieldLabel")
        form_layout.addWidget(self.password_label)
        self.password_input = QLineEdit()
        self.password_input.setObjectName("loginInput")
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(44)
        form_layout.addWidget(self.password_input)

        form_layout.addSpacing(4)

        # Confirm password field with label
        self.confirm_password_label = QLabel("Confirm Password")
        self.confirm_password_label.setObjectName("fieldLabel")
        self.confirm_password_label.setVisible(False)
        form_layout.addWidget(self.confirm_password_label)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setObjectName("loginInput")
        self.confirm_password_input.setPlaceholderText("Confirm your password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setFixedHeight(44)
        self.confirm_password_input.setVisible(False)
        form_layout.addWidget(self.confirm_password_input)

        form_layout.addSpacing(6)

        self.submit_btn = QPushButton("Sign In")
        self.submit_btn.setObjectName("loginBtn")
        self.submit_btn.setFixedHeight(46)
        self.submit_btn.setCursor(Qt.PointingHandCursor)
        self.submit_btn.clicked.connect(self._handle_submit)
        form_layout.addWidget(self.submit_btn)

        # Enter key triggers submit
        self.username_input.returnPressed.connect(self._handle_submit)
        self.password_input.returnPressed.connect(self._handle_submit)
        self.confirm_password_input.returnPressed.connect(self._handle_submit)

        form_layout.addSpacing(16)

        # Separator line (matches web .login-toggle border-top)
        separator = QFrame()
        separator.setObjectName("toggleSeparator")
        separator.setFrameShape(QFrame.HLine)
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #f1f5f9; border: none;")
        form_layout.addWidget(separator)

        form_layout.addSpacing(14)

        # Toggle row
        toggle_row = QHBoxLayout()
        toggle_row.setAlignment(Qt.AlignCenter)
        self.toggle_label = QLabel("Don't have an account?")
        self.toggle_label.setObjectName("toggleLabel")
        toggle_row.addWidget(self.toggle_label)

        self.toggle_btn = QPushButton("Sign Up")
        self.toggle_btn.setObjectName("toggleBtn")
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.clicked.connect(self._toggle_mode)
        toggle_row.addWidget(self.toggle_btn)
        form_layout.addLayout(toggle_row)

        form_container.setLayout(form_layout)
        right_layout.addWidget(form_container, alignment=Qt.AlignCenter)
        right.setLayout(right_layout)
        right_scroll.setWidget(right)
        root.addWidget(right_scroll, 1)

        self.setLayout(root)

    def _toggle_mode(self):
        self.is_signup = not self.is_signup
        self.error_label.setVisible(False)
        self.username_input.clear()
        self.email_input.clear()
        self.password_input.clear()
        self.confirm_password_input.clear()

        if self.is_signup:
            self.title_label.setText("Create account")
            self.subtitle_label.setText("Sign up to get started with ChemViz")
            self.email_label.setVisible(True)
            self.email_input.setVisible(True)
            self.confirm_password_label.setVisible(True)
            self.confirm_password_input.setVisible(True)
            self.submit_btn.setText("Create Account")
            self.toggle_label.setText("Already have an account?")
            self.toggle_btn.setText("Sign In")
        else:
            self.title_label.setText("Welcome back")
            self.subtitle_label.setText("Sign in to your account to continue")
            self.email_label.setVisible(False)
            self.email_input.setVisible(False)
            self.confirm_password_label.setVisible(False)
            self.confirm_password_input.setVisible(False)
            self.submit_btn.setText("Sign In")
            self.toggle_label.setText("Don't have an account?")
            self.toggle_btn.setText("Sign Up")

    def _show_error(self, msg):
        self.error_label.setText(msg)
        self.error_label.setVisible(True)

    def _handle_submit(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        self.error_label.setVisible(False)

        if not username or not password:
            self._show_error("Username and password are required.")
            return

        if self.is_signup:
            email = self.email_input.text().strip()
            confirm = self.confirm_password_input.text().strip()
            if password != confirm:
                self._show_error("Passwords do not match.")
                return
            try:
                resp = requests.post(API_URL + "register/", json={
                    "username": username,
                    "email": email,
                    "password": password,
                })
                if resp.status_code == 201:
                    data = resp.json()
                    self.on_login(data['username'], data['token'])
                else:
                    err = resp.json().get('error', 'Registration failed.')
                    self._show_error(err)
            except Exception as e:
                self._show_error(f"Connection failed: {e}")
        else:
            try:
                resp = requests.post(API_URL + "token-auth/", json={
                    "username": username,
                    "password": password,
                })
                if resp.status_code == 200:
                    token = resp.json()['token']
                    self.on_login(username, token)
                else:
                    self._show_error("Invalid credentials. Please try again.")
            except Exception as e:
                self._show_error(f"Connection failed: {e}")


# ─── Dashboard Page ───────────────────────────────────────────────────────────

class DashboardPage(QWidget):
    def __init__(self, username, token, on_logout, parent=None):
        super().__init__(parent)
        self.username = username
        self.token = token
        self.on_logout = on_logout
        self.headers = {"Authorization": f"Token {token}"}
        self.current_upload_id = None
        self.history_data = []
        self._build_ui()
        self.load_history()
        self.load_dashboard()

    def _build_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ─ Topbar (56px like web) ─
        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar.setFixedHeight(56)
        topbar_layout = QHBoxLayout()
        topbar_layout.setContentsMargins(24, 0, 24, 0)

        brand = QLabel("⚗  ChemViz")
        brand.setObjectName("topbarBrand")
        topbar_layout.addWidget(brand)

        topbar_layout.addStretch()

        # Avatar circle (like web's .topbar-avatar)
        avatar = QLabel("👤")
        avatar.setObjectName("topbarAvatar")
        avatar.setFixedSize(32, 32)
        avatar.setAlignment(Qt.AlignCenter)
        topbar_layout.addWidget(avatar)

        topbar_layout.addSpacing(6)

        user_lbl = QLabel(self.username)
        user_lbl.setObjectName("topbarUser")
        topbar_layout.addWidget(user_lbl)

        topbar_layout.addSpacing(12)

        logout_btn = QPushButton("⎋  Logout")
        logout_btn.setObjectName("logoutBtn")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.clicked.connect(self.on_logout)
        topbar_layout.addWidget(logout_btn)

        topbar.setLayout(topbar_layout)
        root.addWidget(topbar)

        # ─ Body (Sidebar + Main) ─
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        # Sidebar (280px like web)
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(280)
        sb_layout = QVBoxLayout()
        sb_layout.setContentsMargins(16, 20, 16, 16)
        sb_layout.setSpacing(12)

        sb_header = QHBoxLayout()
        sb_title = QLabel("Uploads")
        sb_title.setObjectName("sidebarTitle")
        sb_header.addWidget(sb_title)
        sb_header.addStretch()
        self.badge = QLabel("0")
        self.badge.setObjectName("sidebarBadge")
        sb_header.addWidget(self.badge)
        sb_layout.addLayout(sb_header)

        self.upload_btn = QPushButton("⬆  Upload CSV")
        self.upload_btn.setObjectName("uploadBtn")
        self.upload_btn.setCursor(Qt.PointingHandCursor)
        self.upload_btn.setFixedHeight(42)
        self.upload_btn.clicked.connect(self.upload_file)
        sb_layout.addWidget(self.upload_btn)

        self.history_list = QListWidget()
        self.history_list.setObjectName("sidebarList")
        self.history_list.itemClicked.connect(self._on_history_click)
        sb_layout.addWidget(self.history_list, 1)

        self.empty_label = QLabel("No uploads yet")
        self.empty_label.setObjectName("sidebarEmpty")
        self.empty_label.setAlignment(Qt.AlignCenter)
        sb_layout.addWidget(self.empty_label)

        sidebar.setLayout(sb_layout)
        body.addWidget(sidebar)

        # Main content with scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("dashboardMain")
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(30, 28, 30, 28)
        self.main_layout.setSpacing(22)
        self.main_widget.setLayout(self.main_layout)

        # Header row
        header = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(4)
        self.dash_title = QLabel("Dashboard")
        self.dash_title.setObjectName("dashboardTitle")
        title_col.addWidget(self.dash_title)
        self.dash_subtitle = QLabel("Upload a CSV to begin")
        self.dash_subtitle.setObjectName("dashboardSubtitle")
        title_col.addWidget(self.dash_subtitle)
        header.addLayout(title_col)
        header.addStretch()

        self.pdf_btn = QPushButton("📥  Export PDF")
        self.pdf_btn.setObjectName("pdfBtn")
        self.pdf_btn.setCursor(Qt.PointingHandCursor)
        self.pdf_btn.clicked.connect(self.download_pdf)
        self.pdf_btn.setVisible(False)
        header.addWidget(self.pdf_btn, alignment=Qt.AlignTop)
        self.main_layout.addLayout(header)

        # Stats row (horizontal cards with icon circles, like web's .stat-card)
        self.stats_row = QHBoxLayout()
        self.stats_row.setSpacing(18)
        self.stat_cards = {}
        stat_defs = [
            ('Total Equipment', '📊', COLORS['accent'],  '#eef2ff'),
            ('Avg. Flowrate',   '💧', COLORS['success'], '#ecfdf5'),
            ('Avg. Pressure',   '⏱',  COLORS['info'],    '#ecfeff'),
            ('Avg. Temperature','🌡',  COLORS['warning'], '#fffbeb'),
        ]
        for label, icon, color, bg_color in stat_defs:
            card = self._make_stat_card(label, "-", icon, color, bg_color)
            self.stats_row.addWidget(card)
        self.main_layout.addLayout(self.stats_row)

        # Charts row (Doughnut + Line, like web)
        charts_row = QHBoxLayout()
        charts_row.setSpacing(18)

        # Doughnut chart (pie chart with hole)
        self.chart_type_card = QFrame()
        self.chart_type_card.setObjectName("chartCard")
        ct_layout = QVBoxLayout()
        ct_header = QHBoxLayout()
        ct_icon = QLabel("📊")
        ct_icon.setObjectName("chartCardIcon")
        ct_header.addWidget(ct_icon)
        ct_title = QLabel("Equipment Type Distribution")
        ct_title.setObjectName("chartCardTitle")
        ct_header.addWidget(ct_title)
        ct_header.addStretch()
        ct_layout.addLayout(ct_header)
        self.canvas_doughnut = MplCanvas(self, width=4.5, height=3.2)
        ct_layout.addWidget(self.canvas_doughnut)
        self.chart_type_card.setLayout(ct_layout)
        charts_row.addWidget(self.chart_type_card, 2)

        # Line chart (Parameter Trends)
        self.chart_params_card = QFrame()
        self.chart_params_card.setObjectName("chartCard")
        cp_layout = QVBoxLayout()
        cp_header = QHBoxLayout()
        cp_icon = QLabel("📈")
        cp_icon.setObjectName("chartCardIcon")
        cp_header.addWidget(cp_icon)
        cp_title = QLabel("Parameter Trends")
        cp_title.setObjectName("chartCardTitle")
        cp_header.addWidget(cp_title)
        cp_header.addStretch()
        cp_layout.addLayout(cp_header)
        self.canvas_params = MplCanvas(self, width=6.5, height=3.2)
        cp_layout.addWidget(self.canvas_params)
        self.chart_params_card.setLayout(cp_layout)
        charts_row.addWidget(self.chart_params_card, 3)
        self.main_layout.addLayout(charts_row)

        # Full-width bar chart (Equipment Count by Type — matches web)
        self.chart_bar_card = QFrame()
        self.chart_bar_card.setObjectName("chartCard")
        bar_layout = QVBoxLayout()
        bar_header = QHBoxLayout()
        bar_icon = QLabel("📊")
        bar_icon.setObjectName("chartCardIcon")
        bar_header.addWidget(bar_icon)
        bar_title = QLabel("Equipment Count by Type")
        bar_title.setObjectName("chartCardTitle")
        bar_header.addWidget(bar_title)
        bar_header.addStretch()
        bar_layout.addLayout(bar_header)
        self.canvas_bar = MplCanvas(self, width=10, height=2.8)
        bar_layout.addWidget(self.canvas_bar)
        self.chart_bar_card.setLayout(bar_layout)
        self.main_layout.addWidget(self.chart_bar_card)

        # Table
        self.table_card = QFrame()
        self.table_card.setObjectName("tableCard")
        tc_layout = QVBoxLayout()
        tc_layout.setContentsMargins(0, 0, 0, 0)
        tc_layout.setSpacing(0)

        tc_header = QFrame()
        tc_header.setObjectName("tableCardHeader")
        tc_header_layout = QVBoxLayout()
        tc_header_layout.setContentsMargins(22, 16, 22, 16)
        tc_header_layout.setSpacing(2)
        self.table_title = QLabel("Equipment Data")
        self.table_title.setObjectName("tableTitle")
        tc_header_layout.addWidget(self.table_title)
        self.table_subtitle = QLabel("")
        self.table_subtitle.setObjectName("tableSubtitle")
        tc_header_layout.addWidget(self.table_subtitle)
        tc_header.setLayout(tc_header_layout)
        tc_layout.addWidget(tc_header)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Name", "Type", "Flowrate", "Pressure", "Temperature"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(False)
        self.table.setMinimumHeight(220)
        tc_layout.addWidget(self.table)

        self.table_card.setLayout(tc_layout)
        self.main_layout.addWidget(self.table_card)

        # Empty state (circle illustration like web)
        self.empty_state = QWidget()
        es_layout = QVBoxLayout()
        es_layout.setAlignment(Qt.AlignCenter)
        es_layout.addSpacing(80)

        empty_circle = QLabel("⬆")
        empty_circle.setObjectName("emptyCircle")
        empty_circle.setFixedSize(120, 120)
        empty_circle.setAlignment(Qt.AlignCenter)
        empty_circle.setFont(QFont("Segoe UI Emoji", 40))
        empty_circle.setStyleSheet("background: #eef2ff; border-radius: 60px; color: #6366f1;")
        es_layout.addWidget(empty_circle, alignment=Qt.AlignCenter)

        es_layout.addSpacing(20)

        es_title = QLabel("No Data Available")
        es_title.setObjectName("emptyTitle")
        es_title.setAlignment(Qt.AlignCenter)
        es_layout.addWidget(es_title)

        es_layout.addSpacing(6)

        es_sub = QLabel("Upload a CSV file from the sidebar to get started\nwith your equipment analytics.")
        es_sub.setObjectName("emptySubtitle")
        es_sub.setAlignment(Qt.AlignCenter)
        es_layout.addWidget(es_sub)

        es_layout.addSpacing(80)
        self.empty_state.setLayout(es_layout)
        self.main_layout.addWidget(self.empty_state)

        self.main_layout.addStretch()

        self.scroll_area.setWidget(self.main_widget)
        body.addWidget(self.scroll_area, 1)

        root.addLayout(body, 1)
        self.setLayout(root)

        self._toggle_data_visible(False)

    # ─ Stat card (horizontal: icon circle + label/value — matches web) ─

    def _make_stat_card(self, label, value, icon_text, color, bg_color):
        card = QFrame()
        card.setObjectName("statCard")

        card_layout = QHBoxLayout()
        card_layout.setSpacing(14)
        card_layout.setContentsMargins(18, 16, 18, 16)

        # Icon circle (48x48 like web's .stat-card-icon)
        icon_box = QLabel(icon_text)
        icon_box.setObjectName("statIconBox")
        icon_box.setFixedSize(48, 48)
        icon_box.setAlignment(Qt.AlignCenter)
        icon_box.setFont(QFont("Segoe UI Emoji", 18))
        icon_box.setStyleSheet(f"background-color: {bg_color}; border-radius: 10px; color: {color};")
        card_layout.addWidget(icon_box)

        # Content column
        content = QVBoxLayout()
        content.setSpacing(2)

        lbl = QLabel(label)
        lbl.setObjectName("statLabel")
        content.addWidget(lbl)

        val = QLabel(str(value))
        val.setObjectName("statValue")
        content.addWidget(val)

        card_layout.addLayout(content, 1)

        card.setLayout(card_layout)
        self.stat_cards[label] = val
        return card

    def _toggle_data_visible(self, visible):
        for i in range(self.stats_row.count()):
            w = self.stats_row.itemAt(i).widget()
            if w:
                w.setVisible(visible)
        self.chart_type_card.setVisible(visible)
        self.chart_params_card.setVisible(visible)
        self.chart_bar_card.setVisible(visible)
        self.table_card.setVisible(visible)
        self.pdf_btn.setVisible(visible)
        self.empty_state.setVisible(not visible)

    # ─ Data loading ─

    def load_history(self):
        try:
            resp = requests.get(API_URL + "history/", headers=self.headers)
            if resp.status_code == 200:
                self.history_data = resp.json()
                self._refresh_history_list()
        except Exception as e:
            print(f"Error loading history: {e}")

    def _refresh_history_list(self):
        self.history_list.clear()
        self.badge.setText(str(len(self.history_data)))
        self.empty_label.setVisible(len(self.history_data) == 0)
        self.history_list.setVisible(len(self.history_data) > 0)

        for upload in self.history_data:
            uid = upload['id']
            name = upload.get('original_filename') or f"Upload #{uid}"
            uploaded_at = upload.get('uploaded_at', '')
            is_active = (self.current_upload_id == uid)

            item_widget = QWidget()
            item_widget.setStyleSheet("background: transparent;")
            item_layout = QHBoxLayout()
            item_layout.setContentsMargins(6, 6, 6, 6)
            item_layout.setSpacing(10)

            # File icon (32x32 like web's .sidebar-item-icon)
            file_icon = QLabel("📄")
            file_icon.setFixedSize(32, 32)
            file_icon.setAlignment(Qt.AlignCenter)
            file_icon.setFont(QFont("Segoe UI Emoji", 13))
            if is_active:
                file_icon.setObjectName("sidebarItemIconActive")
                file_icon.setStyleSheet("background: rgba(99,102,241,51); border-radius: 6px;")
            else:
                file_icon.setObjectName("sidebarItemIcon")
                file_icon.setStyleSheet("background: #1e293b; border-radius: 6px;")
            item_layout.addWidget(file_icon)

            # Content (title + date meta)
            content_col = QVBoxLayout()
            content_col.setSpacing(1)

            name_label = QLabel(name)
            name_label.setObjectName("sidebarItemTitleActive" if is_active else "sidebarItemTitle")
            name_label.setToolTip(name)
            # Elide long names
            fm = name_label.fontMetrics()
            elided = fm.elidedText(name, Qt.ElideRight, 140)
            name_label.setText(elided)
            content_col.addWidget(name_label)

            meta_label = QLabel(f"🕐 {format_datetime(uploaded_at)}")
            meta_label.setObjectName("sidebarItemMeta")
            content_col.addWidget(meta_label)

            item_layout.addLayout(content_col, 1)

            # Delete button
            del_btn = QPushButton("🗑")
            del_btn.setObjectName("deleteBtn")
            del_btn.setCursor(Qt.PointingHandCursor)
            del_btn.setFixedSize(28, 28)
            del_btn.clicked.connect(lambda checked, u=uid, fn=name: self._confirm_delete(u, fn))
            item_layout.addWidget(del_btn)

            item_widget.setLayout(item_layout)

            list_item = QListWidgetItem()
            list_item.setSizeHint(QSize(0, 52))
            list_item.setData(Qt.UserRole, uid)
            self.history_list.addItem(list_item)
            self.history_list.setItemWidget(list_item, item_widget)

    def _on_history_click(self, item):
        upload_id = item.data(Qt.UserRole)
        if upload_id:
            self.load_dashboard(upload_id)

    def _confirm_delete(self, upload_id, filename):
        dlg = DeleteDialog(filename, self)
        if dlg.exec_() == QDialog.Accepted:
            self._delete_upload(upload_id)

    def _delete_upload(self, upload_id):
        try:
            resp = requests.delete(API_URL + f"upload/{upload_id}/", headers=self.headers)
            if resp.status_code == 200:
                self.load_history()
                if self.current_upload_id == upload_id:
                    if self.history_data:
                        self.load_dashboard(self.history_data[0]['id'])
                    else:
                        self.current_upload_id = None
                        self._toggle_data_visible(False)
        except Exception as e:
            print(f"Delete error: {e}")

    def upload_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open CSV', '.', "CSV Files (*.csv)")
        if fname:
            try:
                with open(fname, 'rb') as f:
                    files = {'file': f}
                    resp = requests.post(API_URL + "upload/", files=files, headers=self.headers)
                if resp.status_code == 201:
                    upload_id = resp.json()['id']
                    self.load_history()
                    self.load_dashboard(upload_id)
                else:
                    QMessageBox.warning(self, "Error", f"Upload failed: {resp.text}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Upload error: {e}")

    def load_dashboard(self, upload_id=None):
        url = API_URL + ("dashboard/" if not upload_id else f"dashboard/{upload_id}/")
        try:
            resp = requests.get(url, headers=self.headers)
            if resp.status_code == 200:
                data = resp.json()
                self.current_upload_id = data['upload_id']
                self._update_dashboard(data)
                # Refresh sidebar to highlight active item
                self._refresh_history_list()
            else:
                self._toggle_data_visible(False)
        except Exception as e:
            print(f"Connection error: {e}")

    def _update_dashboard(self, data):
        self._toggle_data_visible(True)
        summary = data['summary']

        self.dash_subtitle.setText(f"Upload #{data['upload_id']} overview")

        # Stats
        stat_values = {
            'Total Equipment':  str(summary['count']),
            'Avg. Flowrate':    f"{summary.get('avg_flowrate', 0):.2f}",
            'Avg. Pressure':    f"{summary.get('avg_pressure', 0):.2f}",
            'Avg. Temperature': f"{summary.get('avg_temperature', 0):.2f}",
        }
        for key, val in stat_values.items():
            if key in self.stat_cards:
                self.stat_cards[key].setText(val)

        types = [d['equipment_type'] for d in summary['type_distribution']]
        counts = [d['count'] for d in summary['type_distribution']]
        colors = CHART_COLORS_RGBA[:len(types)]
        colors_hex = CHART_COLORS_HEX[:len(types)]

        # ── Doughnut chart (pie with hole, like web's Doughnut with cutout 65%) ──
        self.canvas_doughnut.fig.clf()
        ax1 = self.canvas_doughnut.fig.add_subplot(111)
        ax1.set_facecolor('white')
        self.canvas_doughnut.fig.patch.set_facecolor('white')

        wedges, texts, autotexts = ax1.pie(
            counts, labels=None, colors=colors,
            autopct='%1.0f%%', startangle=90,
            pctdistance=0.82,
            wedgeprops=dict(width=0.35, edgecolor='white', linewidth=2)
        )
        for t in autotexts:
            t.set_fontsize(9)
            t.set_color('#475569')

        ax1.legend(wedges, types, loc='lower center', ncol=min(len(types), 3),
                   fontsize=9, frameon=False, bbox_to_anchor=(0.5, -0.08),
                   handlelength=1.0, handletextpad=0.5)
        self.canvas_doughnut.fig.tight_layout(pad=1.0)
        self.canvas_doughnut.draw()

        # ── Parameter Trends (line chart with area fill, like web) ──
        rows = data['data']
        self.canvas_params.fig.clf()
        ax2 = self.canvas_params.fig.add_subplot(111)
        x = list(range(len(rows)))
        x_labels = [d.get('equipment_name', f'#{i+1}') for i, d in enumerate(rows)]

        flowrates = [d['flowrate'] for d in rows]
        pressures = [d['pressure'] for d in rows]
        temperatures = [d['temperature'] for d in rows]

        ax2.fill_between(x, flowrates, alpha=0.08, color=COLORS['success'])
        ax2.plot(x, flowrates, label='Flowrate', color=COLORS['success'], linewidth=1.8)
        ax2.fill_between(x, pressures, alpha=0.08, color=COLORS['danger'])
        ax2.plot(x, pressures, label='Pressure', color=COLORS['danger'], linewidth=1.8)
        ax2.fill_between(x, temperatures, alpha=0.08, color=COLORS['warning'])
        ax2.plot(x, temperatures, label='Temperature', color=COLORS['warning'], linewidth=1.8)

        ax2.legend(fontsize=9, frameon=False, loc='upper right')
        setup_chart_style(self.canvas_params.fig, ax2, "")
        # Rotate x labels if too many
        if len(x) > 8:
            ax2.set_xticks(x[::max(1, len(x)//8)])
        self.canvas_params.draw()

        # ── Bar chart (Equipment Count by Type, full width, like web) ──
        self.canvas_bar.fig.clf()
        ax3 = self.canvas_bar.fig.add_subplot(111)
        bar_x = np.arange(len(types))
        bar_width = min(0.6, 60.0 / max(len(types), 1) / 100)
        bars = ax3.bar(bar_x, counts, width=max(bar_width, 0.3), color=colors, edgecolor='none')
        # Round bar tops (simulate borderRadius)
        for bar in bars:
            bar.set_linewidth(0)
        ax3.set_xticks(bar_x)
        ax3.set_xticklabels(types, fontsize=10, color='#94a3b8')
        setup_chart_style(self.canvas_bar.fig, ax3, "")
        self.canvas_bar.draw()

        # ── Table with type badges ──
        self.table.setRowCount(len(rows))
        self.table_subtitle.setText(f"{len(rows)} records")
        for i, row in enumerate(rows):
            # Name (bold like web's .td-name)
            name_item = QTableWidgetItem(str(row['equipment_name']))
            name_item.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
            name_item.setForeground(QColor('#0f172a'))
            self.table.setItem(i, 0, name_item)

            # Type badge (as a QLabel widget, like web's .type-badge)
            badge = QLabel(str(row['equipment_type']))
            badge.setObjectName("typeBadge")
            badge.setAlignment(Qt.AlignCenter)
            badge.setFixedHeight(24)
            self.table.setCellWidget(i, 1, badge)

            self.table.setItem(i, 2, QTableWidgetItem(str(row['flowrate'])))
            self.table.setItem(i, 3, QTableWidgetItem(str(row['pressure'])))
            self.table.setItem(i, 4, QTableWidgetItem(str(row['temperature'])))

    def download_pdf(self):
        if not self.current_upload_id:
            return
        try:
            resp = requests.get(API_URL + f"report/{self.current_upload_id}/", headers=self.headers)
            if resp.status_code == 200:
                fname, _ = QFileDialog.getSaveFileName(
                    self, 'Save PDF', f"report_{self.current_upload_id}.pdf", "PDF Files (*.pdf)")
                if fname:
                    with open(fname, 'wb') as f:
                        f.write(resp.content)
                    QMessageBox.information(self, "Success", "PDF saved successfully")
            else:
                QMessageBox.warning(self, "Error", "Failed to download PDF")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Download error: {e}")


# ─── Main Window ──────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChemViz – Equipment Analytics")
        self.resize(1280, 820)
        self.setMinimumSize(960, 640)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.login_page = LoginPage(self._on_login)
        self.stack.addWidget(self.login_page)

    def _on_login(self, username, token):
        self.dashboard_page = DashboardPage(username, token, self._on_logout)
        self.stack.addWidget(self.dashboard_page)
        self.stack.setCurrentWidget(self.dashboard_page)

    def _on_logout(self):
        self.stack.setCurrentIndex(0)
        if self.stack.count() > 1:
            widget = self.stack.widget(1)
            self.stack.removeWidget(widget)
            widget.deleteLater()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(GLOBAL_STYLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
