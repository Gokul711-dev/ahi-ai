"""
ui/gui.py
Jarvis-style PyQt6 desktop GUI for A.H.I.
Dark holographic aesthetic — animated rings, live system stats, voice controls.
"""
import sys
import threading
import time
import platform
from datetime import datetime
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QFrame, QSplitter,
    QScrollArea, QProgressBar, QTabWidget, QListWidget, QListWidgetItem,
    QSizePolicy, QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation,
    QEasingCurve, QSize, pyqtProperty, QRect,
)
from PyQt6.QtGui import (
    QFont, QColor, QPainter, QPen, QBrush, QLinearGradient,
    QRadialGradient, QPixmap, QIcon, QTextCursor, QPalette,
    QFontDatabase, QConicalGradient,
)


# ══════════════════════════════════════════════════════════════════════════════
# THEME
# ══════════════════════════════════════════════════════════════════════════════

THEME = {
    "bg_dark":      "#050a0f",
    "bg_panel":     "#080e15",
    "bg_input":     "#0a1520",
    "accent":       "#00d4ff",
    "accent2":      "#0066ff",
    "accent_dim":   "#004466",
    "green":        "#00ff88",
    "red":          "#ff3366",
    "yellow":       "#ffcc00",
    "text":         "#c8e8ff",
    "text_dim":     "#445566",
    "border":       "#0a2030",
    "border_glow":  "#003355",
    "user_bubble":  "#0a2540",
    "jane_bubble":  "#050f1a",
}

QSS = f"""
QMainWindow, QWidget {{
    background-color: {THEME['bg_dark']};
    color: {THEME['text']};
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
}}
QTextEdit, QListWidget {{
    background-color: {THEME['bg_panel']};
    color: {THEME['text']};
    border: 1px solid {THEME['border']};
    border-radius: 6px;
    selection-background-color: {THEME['accent_dim']};
}}
QLineEdit {{
    background-color: {THEME['bg_input']};
    color: {THEME['text']};
    border: 1px solid {THEME['border_glow']};
    border-radius: 20px;
    padding: 10px 20px;
    font-size: 14px;
}}
QLineEdit:focus {{
    border: 1px solid {THEME['accent']};
}}
QPushButton {{
    background-color: transparent;
    color: {THEME['accent']};
    border: 1px solid {THEME['accent_dim']};
    border-radius: 6px;
    padding: 8px 16px;
    font-family: 'Consolas', monospace;
}}
QPushButton:hover {{
    background-color: {THEME['accent_dim']};
    border-color: {THEME['accent']};
}}
QPushButton:pressed {{
    background-color: {THEME['accent']};
    color: {THEME['bg_dark']};
}}
QPushButton#mic_btn {{
    border-radius: 28px;
    min-width: 56px;
    min-height: 56px;
    max-width: 56px;
    max-height: 56px;
    font-size: 22px;
    border: 2px solid {THEME['accent']};
}}
QPushButton#mic_btn:checked {{
    background-color: {THEME['red']};
    border-color: {THEME['red']};
    color: white;
}}
QPushButton#send_btn {{
    border-radius: 20px;
    min-width: 56px;
    min-height: 40px;
    font-size: 18px;
}}
QTabWidget::pane {{
    border: 1px solid {THEME['border']};
    background-color: {THEME['bg_panel']};
}}
QTabBar::tab {{
    background-color: {THEME['bg_dark']};
    color: {THEME['text_dim']};
    border: 1px solid {THEME['border']};
    padding: 8px 16px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    color: {THEME['accent']};
    border-bottom: 2px solid {THEME['accent']};
    background-color: {THEME['bg_panel']};
}}
QScrollBar:vertical {{
    background: {THEME['bg_dark']};
    width: 6px;
}}
QScrollBar::handle:vertical {{
    background: {THEME['accent_dim']};
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QProgressBar {{
    background-color: {THEME['bg_dark']};
    border: 1px solid {THEME['border']};
    border-radius: 3px;
    text-align: center;
    color: {THEME['accent']};
    font-size: 10px;
}}
QProgressBar::chunk {{
    background-color: {THEME['accent']};
    border-radius: 3px;
}}
QLabel {{
    color: {THEME['text']};
}}
QSplitter::handle {{
    background-color: {THEME['border']};
    width: 1px;
}}
"""


# ══════════════════════════════════════════════════════════════════════════════
# ANIMATED RING WIDGET (Jarvis-style)
# ══════════════════════════════════════════════════════════════════════════════

class RingWidget(QWidget):
    """Animated concentric rings — the visual identity of Jane OS."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(160, 160)
        self.setMaximumSize(160, 160)
        self._angle = 0
        self._angle2 = 180
        self._pulse = 0.0
        self._pulse_dir = 1
        self._listening = False
        self._thinking = False

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(30)

    def _tick(self):
        self._angle = (self._angle + 2) % 360
        self._angle2 = (self._angle2 - 1.5) % 360
        self._pulse += 0.04 * self._pulse_dir
        if self._pulse >= 1.0 or self._pulse <= 0.0:
            self._pulse_dir *= -1
        self.update()

    def set_listening(self, val: bool):
        self._listening = val

    def set_thinking(self, val: bool):
        self._thinking = val

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() // 2, self.height() // 2
        base_color = QColor(THEME["accent"])
        dim_color = QColor(THEME["accent_dim"])

        if self._listening:
            base_color = QColor(THEME["green"])
        elif self._thinking:
            base_color = QColor(THEME["yellow"])

        # Glow background
        grad = QRadialGradient(cx, cy, 75)
        glow = QColor(base_color)
        glow.setAlpha(30)
        grad.setColorAt(0, glow)
        grad.setColorAt(1, Qt.GlobalColor.transparent)
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(cx - 75, cy - 75, 150, 150)

        # Rings
        rings = [
            (70, 1.5, 120, 0),
            (54, 1.0, 80,  self._angle),
            (38, 1.2, 100, self._angle2),
            (22, 0.8, 60,  -self._angle),
        ]
        for radius, width, alpha, start_angle in rings:
            c = QColor(base_color)
            c.setAlpha(int(alpha * (0.6 + 0.4 * self._pulse)))
            pen = QPen(c, width)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            # Dashed arc for outer rings
            if radius > 50:
                pen.setStyle(Qt.PenStyle.DashLine)
                painter.setPen(pen)
            painter.drawArc(cx - radius, cy - radius,
                            radius * 2, radius * 2,
                            int(start_angle * 16), int(270 * 16))

        # Center dot
        dot_size = int(8 + 4 * self._pulse)
        c = QColor(base_color)
        c.setAlpha(220)
        painter.setBrush(QBrush(c))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(cx - dot_size // 2, cy - dot_size // 2, dot_size, dot_size)

        painter.end()


# ══════════════════════════════════════════════════════════════════════════════
# SYSTEM MONITOR WIDGET
# ══════════════════════════════════════════════════════════════════════════════

class SystemMonitor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(2000)
        self._refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        title = QLabel("SYSTEM MONITOR")
        title.setStyleSheet(f"color: {THEME['accent']}; font-size: 11px; letter-spacing: 3px;")
        layout.addWidget(title)

        self._cpu_bar = self._make_bar("CPU", layout)
        self._ram_bar = self._make_bar("RAM", layout)
        self._disk_bar = self._make_bar("DISK", layout)

        self._info_label = QLabel("")
        self._info_label.setStyleSheet(f"color: {THEME['text_dim']}; font-size: 11px;")
        self._info_label.setWordWrap(True)
        layout.addWidget(self._info_label)
        layout.addStretch()

    def _make_bar(self, label: str, layout) -> QProgressBar:
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setFixedWidth(36)
        lbl.setStyleSheet(f"color: {THEME['text_dim']}; font-size: 11px;")
        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setFixedHeight(12)
        row.addWidget(lbl)
        row.addWidget(bar)
        layout.addLayout(row)
        return bar

    def _refresh(self):
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("/" if platform.system() != "Windows" else "C:\\")

            self._cpu_bar.setValue(int(cpu))
            self._cpu_bar.setFormat(f"{cpu:.0f}%")
            self._ram_bar.setValue(int(mem.percent))
            self._ram_bar.setFormat(f"{mem.used/1e9:.1f}/{mem.total/1e9:.1f} GB")
            self._disk_bar.setValue(int(disk.percent))
            self._disk_bar.setFormat(f"{disk.used/1e9:.0f}/{disk.total/1e9:.0f} GB")

            uptime_s = time.time() - psutil.boot_time()
            h, m = divmod(int(uptime_s / 60), 60)
            self._info_label.setText(
                f"HOST: {platform.node()}\n"
                f"OS:   {platform.system()} {platform.release()}\n"
                f"UP:   {h}h {m}m"
            )
        except ImportError:
            self._info_label.setText("Install psutil for stats")
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════════════════════
# WORKER THREADS
# ══════════════════════════════════════════════════════════════════════════════

class ProcessWorker(QThread):
    """Runs orchestrator.process() in background thread."""
    response_ready = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, orchestrator, user_input: str):
        super().__init__()
        self.orchestrator = orchestrator
        self.user_input = user_input

    def run(self):
        try:
            response = self.orchestrator.process(self.user_input)
            self.response_ready.emit(response)
        except Exception as e:
            self.error_signal.emit(str(e))


class VoiceWorker(QThread):
    """Runs STT listen() in background thread."""
    text_ready = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, voice_manager):
        super().__init__()
        self.voice_manager = voice_manager

    def run(self):
        try:
            text = self.voice_manager.listen()
            self.text_ready.emit(text)
        except Exception as e:
            self.error_signal.emit(str(e))


# ══════════════════════════════════════════════════════════════════════════════
# CHAT BUBBLE
# ══════════════════════════════════════════════════════════════════════════════

class ChatBubble(QFrame):
    def __init__(self, text: str, is_user: bool, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)

        # Header
        header = QHBoxLayout()
        who = QLabel("YOU" if is_user else "JANE")
        who.setStyleSheet(
            f"color: {THEME['accent'] if is_user else THEME['green']};"
            f"font-size: 10px; letter-spacing: 2px; font-weight: bold;"
        )
        ts = QLabel(datetime.now().strftime("%H:%M:%S"))
        ts.setStyleSheet(f"color: {THEME['text_dim']}; font-size: 10px;")
        header.addWidget(who)
        header.addStretch()
        header.addWidget(ts)
        layout.addLayout(header)

        # Text
        msg = QLabel(text)
        msg.setWordWrap(True)
        msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        msg.setStyleSheet(f"color: {THEME['text']}; font-size: 13px; line-height: 1.5;")
        layout.addWidget(msg)

        bg = THEME["user_bubble"] if is_user else THEME["jane_bubble"]
        border = THEME["accent_dim"] if is_user else THEME["border"]
        self.setStyleSheet(
            f"QFrame {{ background-color: {bg}; border: 1px solid {border};"
            f"border-radius: 8px; margin: 2px 0; }}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# CYBER TOOLS PANEL
# ══════════════════════════════════════════════════════════════════════════════

class CyberPanel(QWidget):
    command_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        title = QLabel("CYBER TOOLKIT")
        title.setStyleSheet(f"color: {THEME['red']}; font-size: 11px; letter-spacing: 3px;")
        layout.addWidget(title)

        # Quick-fire tool buttons
        tools = [
            ("🔍 Scan scanme.nmap.org", "run an nmap scan on scanme.nmap.org"),
            ("🌐 DNS Lookup",           "do a DNS lookup for google.com"),
            ("📋 WHOIS",                "do a whois lookup for google.com"),
            ("🧱 Explain XSS",          "explain XSS attack in detail"),
            ("💉 Explain SQLi",         "explain SQL injection in detail"),
            ("🎣 Explain Phishing",     "explain phishing attack in detail"),
            ("🕵️ Explain MITM",         "explain man in the middle attack"),
            ("💀 Explain Ransomware",   "explain ransomware in detail"),
            ("🔑 Privesc Explained",    "explain privilege escalation"),
            ("📦 Craft TCP SYN",        "show me how to craft a TCP SYN packet using scapy targeting localhost"),
            ("📡 Craft ICMP",           "show me how to craft an ICMP packet using scapy targeting localhost"),
            ("🖥️ System Info",          "show me the current system status"),
        ]
        for label, cmd in tools:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, c=cmd: self.command_requested.emit(c))
            btn.setStyleSheet(
                f"QPushButton {{ text-align: left; padding: 6px 10px;"
                f"border-color: {THEME['accent_dim']}; font-size: 12px; }}"
            )
            layout.addWidget(btn)

        # Custom target input
        layout.addSpacing(8)
        lbl = QLabel("CUSTOM COMMAND")
        lbl.setStyleSheet(f"color: {THEME['text_dim']}; font-size: 10px; letter-spacing: 2px;")
        layout.addWidget(lbl)

        self._custom_input = QLineEdit()
        self._custom_input.setPlaceholderText("Type any query...")
        self._custom_input.returnPressed.connect(self._send_custom)
        layout.addWidget(self._custom_input)

        layout.addStretch()

    def _send_custom(self):
        text = self._custom_input.text().strip()
        if text:
            self.command_requested.emit(text)
            self._custom_input.clear()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN WINDOW
# ══════════════════════════════════════════════════════════════════════════════

class JaneWindow(QMainWindow):
    def __init__(self, orchestrator, voice_manager=None):
        super().__init__()
        self.orchestrator = orchestrator
        self.voice_manager = voice_manager
        self._worker: Optional[ProcessWorker] = None
        self._voice_worker: Optional[VoiceWorker] = None
        self._voice_active = False

        self.setWindowTitle("A.H.I. — Jane OS v2.0")
        self.setMinimumSize(1100, 720)
        self.resize(1280, 800)

        self._setup_ui()
        self._apply_drop_shadow()
        self._start_clock()
        self._welcome()

    # ── UI Setup ──────────────────────────────────────────────────────────────

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # LEFT SIDEBAR
        sidebar = self._build_sidebar()
        root.addWidget(sidebar)

        # MAIN AREA (splitter: chat | right panel)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)

        chat_area = self._build_chat_area()
        right_panel = self._build_right_panel()

        splitter.addWidget(chat_area)
        splitter.addWidget(right_panel)
        splitter.setSizes([780, 320])
        root.addWidget(splitter)

    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setFixedWidth(190)
        sidebar.setStyleSheet(
            f"QFrame {{ background-color: {THEME['bg_panel']};"
            f"border-right: 1px solid {THEME['border']}; }}"
        )
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(12)

        # Logo
        logo = QLabel("A·H·I")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(
            f"color: {THEME['accent']}; font-size: 22px; font-weight: bold;"
            f"letter-spacing: 6px;"
        )
        layout.addWidget(logo)

        tagline = QLabel("Jane OS v2.0")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tagline.setStyleSheet(f"color: {THEME['text_dim']}; font-size: 10px; letter-spacing: 2px;")
        layout.addWidget(tagline)

        layout.addSpacing(8)

        # Animated ring
        self._ring = RingWidget()
        self._ring.setAlignment = lambda _: None  # duck-typing layout
        ring_row = QHBoxLayout()
        ring_row.addStretch()
        ring_row.addWidget(self._ring)
        ring_row.addStretch()
        layout.addLayout(ring_row)

        layout.addSpacing(8)

        # Status
        self._status_lbl = QLabel("● ONLINE")
        self._status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_lbl.setStyleSheet(f"color: {THEME['green']}; font-size: 11px; letter-spacing: 2px;")
        layout.addWidget(self._status_lbl)

        self._clock_lbl = QLabel("00:00:00")
        self._clock_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._clock_lbl.setStyleSheet(f"color: {THEME['text_dim']}; font-size: 12px;")
        layout.addWidget(self._clock_lbl)

        layout.addSpacing(16)

        # Sidebar nav buttons
        nav_items = [
            ("💬  Chat",         self._tab_chat),
            ("🔐  Cyber Tools",  self._tab_cyber),
            ("🖥️  System",       self._tab_system),
        ]
        self._nav_btns = []
        for label, slot in nav_items:
            btn = QPushButton(label)
            btn.setStyleSheet(
                f"QPushButton {{ text-align: left; padding: 10px 12px;"
                f"border-radius: 6px; font-size: 13px; }}"
            )
            btn.clicked.connect(slot)
            layout.addWidget(btn)
            self._nav_btns.append(btn)

        layout.addStretch()

        # Voice status
        self._voice_status = QLabel("🔇 Voice: Text Mode")
        self._voice_status.setWordWrap(True)
        self._voice_status.setStyleSheet(f"color: {THEME['text_dim']}; font-size: 10px;")
        layout.addWidget(self._voice_status)

        # Clear memory button
        clear_btn = QPushButton("🗑  Clear Memory")
        clear_btn.clicked.connect(self._clear_memory)
        layout.addWidget(clear_btn)

        if self.voice_manager:
            status = self.voice_manager.get_status()
            tts = status.get("tts", "unavailable")
            self._voice_status.setText(f"🔊 TTS: {tts[:22]}")

        return sidebar

    def _build_chat_area(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # Header
        header = QHBoxLayout()
        hdr_lbl = QLabel("CONVERSATION")
        hdr_lbl.setStyleSheet(
            f"color: {THEME['accent']}; font-size: 11px; letter-spacing: 3px;"
        )
        header.addWidget(hdr_lbl)
        header.addStretch()
        layout.addLayout(header)

        # Chat scroll area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._chat_container = QWidget()
        self._chat_layout = QVBoxLayout(self._chat_container)
        self._chat_layout.setContentsMargins(4, 4, 4, 4)
        self._chat_layout.setSpacing(6)
        self._chat_layout.addStretch()

        self._scroll.setWidget(self._chat_container)
        layout.addWidget(self._scroll)

        # Thinking indicator
        self._thinking_lbl = QLabel("⟳  Jane is processing...")
        self._thinking_lbl.setStyleSheet(
            f"color: {THEME['yellow']}; font-size: 12px; padding: 4px;"
        )
        self._thinking_lbl.hide()
        layout.addWidget(self._thinking_lbl)

        # Input row
        input_row = QHBoxLayout()
        input_row.setSpacing(10)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Talk to Jane... or press 🎤 to speak")
        self._input.returnPressed.connect(self._send_text)
        self._input.setFixedHeight(44)
        input_row.addWidget(self._input)

        # Mic button
        self._mic_btn = QPushButton("🎤")
        self._mic_btn.setObjectName("mic_btn")
        self._mic_btn.setCheckable(True)
        self._mic_btn.setToolTip("Hold to speak (requires faster-whisper)")
        self._mic_btn.clicked.connect(self._toggle_voice)
        self._mic_btn.setFixedSize(QSize(48, 44))
        input_row.addWidget(self._mic_btn)

        # Send button
        send_btn = QPushButton("➤")
        send_btn.setObjectName("send_btn")
        send_btn.setFixedSize(QSize(48, 44))
        send_btn.clicked.connect(self._send_text)
        input_row.addWidget(send_btn)

        layout.addLayout(input_row)
        return widget

    def _build_right_panel(self) -> QWidget:
        self._tabs = QTabWidget()

        # Tab 1: System Monitor
        self._sys_monitor = SystemMonitor()
        self._tabs.addTab(self._sys_monitor, "System")

        # Tab 2: Cyber Tools
        self._cyber_panel = CyberPanel()
        self._cyber_panel.command_requested.connect(self._inject_command)
        self._tabs.addTab(self._cyber_panel, "Cyber")

        # Tab 3: Memory / History
        mem_widget = QWidget()
        mem_layout = QVBoxLayout(mem_widget)
        mem_layout.setContentsMargins(10, 10, 10, 10)
        lbl = QLabel("RECENT MEMORY")
        lbl.setStyleSheet(f"color: {THEME['accent']}; font-size: 11px; letter-spacing: 3px;")
        mem_layout.addWidget(lbl)
        self._memory_list = QListWidget()
        mem_layout.addWidget(self._memory_list)
        refresh_btn = QPushButton("↻ Refresh")
        refresh_btn.clicked.connect(self._refresh_memory)
        mem_layout.addWidget(refresh_btn)
        self._tabs.addTab(mem_widget, "Memory")

        return self._tabs

    # ── Navigation ────────────────────────────────────────────────────────────

    def _tab_chat(self):
        pass  # chat is always visible

    def _tab_cyber(self):
        self._tabs.setCurrentWidget(self._cyber_panel)

    def _tab_system(self):
        self._tabs.setCurrentWidget(self._sys_monitor)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _apply_drop_shadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(THEME["accent"]))
        shadow.setOffset(0, 0)

    def _start_clock(self):
        clock_timer = QTimer(self)
        clock_timer.timeout.connect(self._update_clock)
        clock_timer.start(1000)

    def _update_clock(self):
        self._clock_lbl.setText(datetime.now().strftime("%H:%M:%S"))

    def _welcome(self):
        self._add_bubble(
            "*settles into the chair and sips tea*\n\n"
            "Good to see you. I'm Jane — fully operational, tools loaded, "
            "memory intact.\n\n"
            "You can type or click the 🎤 mic button to speak. "
            "The **Cyber** tab has quick-fire tools. "
            "What shall we work on?",
            is_user=False,
        )

    # ── Chat ──────────────────────────────────────────────────────────────────

    def _add_bubble(self, text: str, is_user: bool):
        bubble = ChatBubble(text, is_user)
        # Insert before the trailing stretch
        count = self._chat_layout.count()
        self._chat_layout.insertWidget(count - 1, bubble)
        # Scroll to bottom
        QTimer.singleShot(50, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()
        )

    def _send_text(self):
        text = self._input.text().strip()
        if not text or self._worker:
            return
        self._input.clear()
        self._dispatch(text)

    def _inject_command(self, cmd: str):
        """Called by cyber panel buttons."""
        self._dispatch(cmd)

    def _dispatch(self, user_text: str):
        """Send a message to the orchestrator in a background thread."""
        self._add_bubble(user_text, is_user=True)
        self._set_thinking(True)

        self._worker = ProcessWorker(self.orchestrator, user_text)
        self._worker.response_ready.connect(self._on_response)
        self._worker.error_signal.connect(self._on_error)
        self._worker.finished.connect(self._on_worker_done)
        self._worker.start()

    def _on_response(self, text: str):
        self._add_bubble(text, is_user=False)
        if self.voice_manager:
            self.voice_manager.speak(text)

    def _on_error(self, err: str):
        self._add_bubble(f"⚠ Error: {err}", is_user=False)

    def _on_worker_done(self):
        self._worker = None
        self._set_thinking(False)

    def _set_thinking(self, active: bool):
        if active:
            self._thinking_lbl.show()
            self._ring.set_thinking(True)
            self._status_lbl.setText("⟳ THINKING")
            self._status_lbl.setStyleSheet(f"color: {THEME['yellow']}; font-size: 11px; letter-spacing: 2px;")
        else:
            self._thinking_lbl.hide()
            self._ring.set_thinking(False)
            self._status_lbl.setText("● ONLINE")
            self._status_lbl.setStyleSheet(f"color: {THEME['green']}; font-size: 11px; letter-spacing: 2px;")

    # ── Voice ─────────────────────────────────────────────────────────────────

    def _toggle_voice(self, checked: bool):
        if not self.voice_manager:
            self._add_bubble(
                "Voice isn't configured. Install voice dependencies:\n"
                "`pip install faster-whisper sounddevice pyttsx3`\n"
                "Then run with `--voice` flag.",
                is_user=False,
            )
            self._mic_btn.setChecked(False)
            return

        if checked:
            self._mic_btn.setText("⏹")
            self._ring.set_listening(True)
            self._status_lbl.setText("🎤 LISTENING")
            self._status_lbl.setStyleSheet(f"color: {THEME['green']}; font-size: 11px; letter-spacing: 2px;")
            self._voice_worker = VoiceWorker(self.voice_manager)
            self._voice_worker.text_ready.connect(self._on_voice_text)
            self._voice_worker.error_signal.connect(self._on_voice_error)
            self._voice_worker.finished.connect(self._on_voice_done)
            self._voice_worker.start()
        else:
            self._mic_btn.setText("🎤")

    def _on_voice_text(self, text: str):
        if text.strip():
            self._input.setText(text)
            self._dispatch(text)
        else:
            self._add_bubble("*I didn't catch that — try again.*", is_user=False)

    def _on_voice_error(self, err: str):
        self._add_bubble(f"⚠ Voice error: {err}", is_user=False)

    def _on_voice_done(self):
        self._mic_btn.setChecked(False)
        self._mic_btn.setText("🎤")
        self._ring.set_listening(False)
        self._status_lbl.setText("● ONLINE")
        self._status_lbl.setStyleSheet(f"color: {THEME['green']}; font-size: 11px; letter-spacing: 2px;")
        self._voice_worker = None

    # ── Memory ────────────────────────────────────────────────────────────────

    def _refresh_memory(self):
        self._memory_list.clear()
        exchanges = self.orchestrator.short_memory.get_last(20)
        for ex in reversed(exchanges):
            item = QListWidgetItem(f"You: {ex['user'][:60]}...")
            item.setForeground(QColor(THEME["text_dim"]))
            self._memory_list.addItem(item)

    def _clear_memory(self):
        self.orchestrator.short_memory.clear()
        self._add_bubble("*Short-term memory cleared. Fresh slate.*", is_user=False)

    # ── Window ────────────────────────────────────────────────────────────────

    def closeEvent(self, event):
        if self.voice_manager:
            self.voice_manager.shutdown()
        event.accept()


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def run_gui(orchestrator, voice_manager=None):
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyleSheet(QSS)

    # High-DPI
    try:
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    except AttributeError:
        pass

    window = JaneWindow(orchestrator, voice_manager)
    window.show()
    sys.exit(app.exec())
