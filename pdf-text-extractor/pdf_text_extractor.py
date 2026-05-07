#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Text Extractor
==================
A beautiful, fully offline macOS desktop app for extracting text from PDFs.

Features:
  • Drag-and-drop PDF files directly onto the window
  • Multi-file sidebar — open as many PDFs as you want
  • Full-text search with match highlighting (⌘F)
  • Copy extracted text to clipboard
  • Save extracted text as .txt file
  • Page-by-page breakdown with page markers
  • Native macOS look with automatic Dark/Light mode

Requirements (installed automatically by run.sh):
  pip install PyMuPDF PyQt6
"""

import sys
import os
from pathlib import Path

# ── Dependency check ────────────────────────────────────────────────────────

def _check_deps():
    missing = []
    try:
        import fitz  # noqa: F401
    except ImportError:
        missing.append("PyMuPDF")
    try:
        import PyQt6  # noqa: F401
    except ImportError:
        missing.append("PyQt6")
    if missing:
        print("─" * 60)
        print("Missing dependencies:", ", ".join(missing))
        print("Please run:  pip install " + " ".join(missing))
        print("  or simply: ./run.sh")
        print("─" * 60)
        sys.exit(1)

_check_deps()

# ── Imports ──────────────────────────────────────────────────────────────────

import fitz  # PyMuPDF

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QListWidget, QListWidgetItem, QTextEdit, QLabel,
    QPushButton, QToolBar, QFileDialog, QFrame, QLineEdit,
    QSizePolicy, QMessageBox, QScrollArea, QAbstractItemView,
)
from PyQt6.QtCore import (
    Qt, QUrl, QTimer, QSize, pyqtSignal, QThread, QObject,
)
from PyQt6.QtGui import (
    QFont, QColor, QDragEnterEvent, QDropEvent, QKeySequence,
    QTextCharFormat, QTextCursor, QTextDocument, QAction,
    QPainter, QPixmap, QFontDatabase, QIcon, QShortcut,
    QPalette,
)

# ── Constants ────────────────────────────────────────────────────────────────

APP_NAME    = "PDF Text Extractor"
APP_VERSION = "1.0"

# Detect macOS system font name
if sys.platform == "darwin":
    BODY_FONT   = "SF Pro Text"
    MONO_FONT   = "SF Mono"
    UI_FONT     = ".AppleSystemUIFont"
else:
    BODY_FONT   = "Segoe UI"
    MONO_FONT   = "Consolas"
    UI_FONT     = "Segoe UI"

SIDEBAR_WIDTH    = 220
MIN_WINDOW_W     = 900
MIN_WINDOW_H     = 600
DEFAULT_WINDOW_W = 1240
DEFAULT_WINDOW_H = 820

# ── Worker thread for PDF loading ────────────────────────────────────────────

class PDFWorker(QObject):
    """Loads a PDF on a background thread to keep the UI responsive."""
    finished  = pyqtSignal(str, str, int)   # path, text, page_count
    error     = pyqtSignal(str, str)        # path, error_message

    def __init__(self, path: str):
        super().__init__()
        self.path = path

    def run(self):
        try:
            doc   = fitz.open(self.path)
            pages = doc.page_count
            parts = []
            for i, page in enumerate(doc):
                text = page.get_text("text")
                if text.strip():
                    parts.append(f"── Page {i + 1} of {pages} ──\n\n{text.rstrip()}")
            doc.close()
            full_text = "\n\n\n".join(parts) if parts else "(No extractable text found in this PDF.)"
            self.finished.emit(self.path, full_text, pages)
        except Exception as exc:
            self.error.emit(self.path, str(exc))


# ── Data model ───────────────────────────────────────────────────────────────

class PDFDocument:
    """Holds all data for one loaded PDF."""
    def __init__(self, path: str):
        self.path       : str  = path
        self.name       : str  = Path(path).name
        self.stem       : str  = Path(path).stem
        self.text       : str  = ""
        self.page_count : int  = 0
        self.loading    : bool = True
        self.error      : str | None = None

    @property
    def status_line(self) -> str:
        if self.loading:
            return f"{self.name}  ·  Loading…"
        if self.error:
            return f"{self.name}  ·  ⚠ {self.error}"
        pages = f"{self.page_count} page{'s' if self.page_count != 1 else ''}"
        chars = f"{len(self.text):,} chars"
        return f"{self.name}  ·  {pages}  ·  {chars}"


# ── Custom sidebar item ───────────────────────────────────────────────────────

class FileListItem(QListWidgetItem):
    def __init__(self, doc: PDFDocument):
        super().__init__()
        self.doc = doc
        self._refresh()

    def _refresh(self):
        self.setText(self.doc.name)
        self.setToolTip(self.doc.path)
        if self.doc.error:
            self.setForeground(QColor("#E05252"))
        elif self.doc.loading:
            self.setForeground(QColor("#888888"))
        else:
            self.setForeground(QColor())  # reset to default


# ── Drop zone (shown when no files are loaded) ────────────────────────────────

class DropZoneWidget(QWidget):
    """Full-window drag-and-drop landing page."""
    filesDropped = pyqtSignal(list)   # list[str] of PDF paths

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._dragging_over = False
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        # PDF icon (drawn with emoji / Unicode)
        icon_label = QLabel("📄")
        icon_font = QFont(UI_FONT, 56)
        icon_label.setFont(icon_font)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Drop PDF files here")
        title_font = QFont(UI_FONT, 22, QFont.Weight.Medium)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("…or click Open PDF in the toolbar above")
        sub_font = QFont(UI_FONT, 13)
        subtitle.setFont(sub_font)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setObjectName("subtitle")

        layout.addStretch(2)
        layout.addWidget(icon_label)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch(3)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if self._has_pdfs(event):
            event.acceptProposedAction()
            self._dragging_over = True
            self.update()

    def dragLeaveEvent(self, event):
        self._dragging_over = False
        self.update()

    def dropEvent(self, event: QDropEvent):
        self._dragging_over = False
        self.update()
        paths = self._pdf_paths(event)
        if paths:
            self.filesDropped.emit(paths)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._dragging_over:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            color = QColor(0, 120, 215, 40)
            painter.fillRect(self.rect(), color)

    @staticmethod
    def _has_pdfs(event) -> bool:
        if not event.mimeData().hasUrls():
            return False
        return any(u.toLocalFile().lower().endswith(".pdf")
                   for u in event.mimeData().urls())

    @staticmethod
    def _pdf_paths(event) -> list:
        return [u.toLocalFile() for u in event.mimeData().urls()
                if u.toLocalFile().lower().endswith(".pdf")]


# ── Text viewer ───────────────────────────────────────────────────────────────

class TextViewer(QTextEdit):
    """Read-only text display with search-highlight support."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setAcceptDrops(False)
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)

        font = QFont(BODY_FONT, 13)
        font.setStyleHint(QFont.StyleHint.SansSerif)
        self.setFont(font)

        self.setStyleSheet("""
            QTextEdit {
                border: none;
                padding: 20px 28px;
                background: transparent;
            }
        """)

    def highlight_search(self, query: str) -> int:
        """Highlight all occurrences of *query*; return match count."""
        # First, clear all existing highlights
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        clear_fmt = QTextCharFormat()
        cursor.setCharFormat(clear_fmt)

        if not query:
            return 0

        hi_fmt = QTextCharFormat()
        hi_fmt.setBackground(QColor("#FFD60A"))   # iOS/macOS yellow highlight
        hi_fmt.setForeground(QColor("#1C1C1E"))

        count   = 0
        cursor  = QTextCursor(self.document())
        flags   = QTextDocument.FindFlag(0)       # case-insensitive by default

        while True:
            cursor = self.document().find(query, cursor, flags)
            if cursor.isNull():
                break
            cursor.mergeCharFormat(hi_fmt)
            count += 1

        # Scroll to first match
        if count:
            c2 = QTextCursor(self.document())
            c2 = self.document().find(query, c2, flags)
            if not c2.isNull():
                self.setTextCursor(c2)
                self.ensureCursorVisible()

        return count


# ── Search bar widget ─────────────────────────────────────────────────────────

class SearchBar(QFrame):
    """Slide-down search bar attached above the text viewer."""
    queryChanged = pyqtSignal(str)
    closeClicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setObjectName("SearchBar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(8)

        search_icon = QLabel("🔍")
        search_icon.setFont(QFont(UI_FONT, 13))

        self.input = QLineEdit()
        self.input.setPlaceholderText("Search in extracted text…")
        self.input.setFont(QFont(UI_FONT, 13))
        self.input.textChanged.connect(self.queryChanged)
        self.input.setMinimumWidth(260)

        self.match_label = QLabel("")
        self.match_label.setFont(QFont(UI_FONT, 12))
        self.match_label.setFixedWidth(90)
        self.match_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.match_label.setObjectName("matchLabel")

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(22, 22)
        close_btn.setFont(QFont(UI_FONT, 11))
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setObjectName("closeSearchBtn")
        close_btn.clicked.connect(self.closeClicked)

        layout.addWidget(search_icon)
        layout.addWidget(self.input)
        layout.addWidget(self.match_label)
        layout.addWidget(close_btn)

    def focus(self):
        self.input.setFocus()
        self.input.selectAll()

    def clear(self):
        self.input.clear()
        self.match_label.setText("")

    def set_match_count(self, count: int, query: str):
        if not query:
            self.match_label.setText("")
        elif count == 0:
            self.match_label.setText("No matches")
        else:
            self.match_label.setText(f"{count} match{'es' if count != 1 else ''}")


# ── Main window ───────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.documents  : list[PDFDocument] = []
        self.current_doc: PDFDocument | None = None
        self._workers   : list[tuple] = []   # keep (thread, worker) alive

        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(MIN_WINDOW_W, MIN_WINDOW_H)
        self.resize(DEFAULT_WINDOW_W, DEFAULT_WINDOW_H)
        self.setAcceptDrops(True)

        self._build_ui()
        self._build_toolbar()
        self._apply_stylesheet()
        self._bind_shortcuts()

    # ── UI construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Search bar (hidden by default) ─────
        self.search_bar = SearchBar()
        self.search_bar.setVisible(False)
        self.search_bar.queryChanged.connect(self._on_search_changed)
        self.search_bar.closeClicked.connect(self._hide_search)

        # ── Main splitter ──────────────────────
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)
        self.splitter.setChildrenCollapsible(False)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setMinimumWidth(160)
        self.sidebar.setMaximumWidth(320)
        self.sidebar.setFixedWidth(SIDEBAR_WIDTH)
        self.sidebar.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.sidebar.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.currentItemChanged.connect(self._on_sidebar_changed)
        self.sidebar.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.sidebar.customContextMenuRequested.connect(self._sidebar_context_menu)

        # Right panel (content area)
        right_panel = QWidget()
        right_panel.setObjectName("RightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Drop zone (shown when no docs loaded)
        self.drop_zone = DropZoneWidget()
        self.drop_zone.filesDropped.connect(self._load_pdfs)

        # Text viewer (shown when doc is selected)
        self.text_viewer = TextViewer()
        self.text_viewer.setVisible(False)

        right_layout.addWidget(self.search_bar)
        right_layout.addWidget(self.drop_zone)
        right_layout.addWidget(self.text_viewer)

        # Status bar
        self.status_label = QLabel("Open a PDF to get started")
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setContentsMargins(14, 4, 14, 5)
        right_layout.addWidget(self.status_label)

        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(right_panel)
        self.splitter.setSizes([SIDEBAR_WIDTH, DEFAULT_WINDOW_W - SIDEBAR_WIDTH])

        root.addWidget(self.splitter)

    def _build_toolbar(self):
        tb = QToolBar("Main Toolbar")
        tb.setMovable(False)
        tb.setFloatable(False)
        tb.setIconSize(QSize(16, 16))
        tb.setObjectName("MainToolbar")

        def _action(label: str, shortcut: str | None, slot):
            a = QAction(label, self)
            if shortcut:
                a.setShortcut(QKeySequence(shortcut))
            a.triggered.connect(slot)
            tb.addAction(a)
            return a

        _action("Open PDF…",    "Ctrl+O",       self._open_files)
        tb.addSeparator()
        self.act_copy  = _action("Copy Text",    "Ctrl+Shift+C", self._copy_text)
        self.act_save  = _action("Save as .txt…","Ctrl+S",       self._save_text)
        tb.addSeparator()
        self.act_search = _action("Search…",     "Ctrl+F",       self._show_search)
        tb.addSeparator()
        self.act_clear  = _action("Remove File", None,           self._remove_current)

        self.act_copy.setEnabled(False)
        self.act_save.setEnabled(False)
        self.act_search.setEnabled(False)
        self.act_clear.setEnabled(False)

        self.addToolBar(tb)

    def _bind_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+F"),   self).activated.connect(self._show_search)
        QShortcut(QKeySequence("Escape"),   self).activated.connect(self._hide_search)
        QShortcut(QKeySequence("Ctrl+W"),   self).activated.connect(self._remove_current)

    def _apply_stylesheet(self):
        # Detect dark mode via palette
        palette   = QApplication.palette()
        is_dark   = palette.color(QPalette.ColorRole.Window).lightness() < 128
        bg        = "#1E1E1E"  if is_dark else "#F5F5F7"
        sidebar_bg= "#2A2A2A"  if is_dark else "#ECECEC"
        border    = "#3A3A3A"  if is_dark else "#D0D0D0"
        text_dim  = "#999999"  if is_dark else "#6E6E6E"
        sel_bg    = "#3A3A3C"  if is_dark else "#D1E8FF"
        search_bg = "#2C2C2E"  if is_dark else "#FFFFFF"
        status_bg = "#252525"  if is_dark else "#EBEBED"

        self.setStyleSheet(f"""
            QMainWindow {{
                background: {bg};
            }}

            /* ── Toolbar ── */
            QToolBar#MainToolbar {{
                background: {sidebar_bg};
                border-bottom: 1px solid {border};
                spacing: 4px;
                padding: 4px 8px;
            }}
            QToolBar#MainToolbar QToolButton {{
                font-family: "{UI_FONT}";
                font-size: 13px;
                padding: 3px 10px;
                border-radius: 5px;
                border: none;
            }}
            QToolBar#MainToolbar QToolButton:hover {{
                background: {sel_bg};
            }}
            QToolBar#MainToolbar QToolButton:pressed {{
                background: {border};
            }}
            QToolBar#MainToolbar QToolButton:disabled {{
                color: {text_dim};
            }}

            /* ── Sidebar ── */
            QListWidget#Sidebar {{
                background: {sidebar_bg};
                border: none;
                border-right: 1px solid {border};
                font-family: "{UI_FONT}";
                font-size: 13px;
                padding: 4px 0px;
                outline: 0;
            }}
            QListWidget#Sidebar::item {{
                padding: 7px 12px;
                border-radius: 6px;
                margin: 1px 6px;
            }}
            QListWidget#Sidebar::item:selected {{
                background: {sel_bg};
            }}
            QListWidget#Sidebar::item:hover:!selected {{
                background: {border};
            }}

            /* ── Drop zone ── */
            DropZoneWidget QLabel {{
                color: {text_dim};
            }}
            DropZoneWidget QLabel#subtitle {{
                font-size: 13px;
            }}

            /* ── Search bar ── */
            SearchBar {{
                background: {search_bg};
                border-bottom: 1px solid {border};
            }}
            SearchBar QLineEdit {{
                background: {bg};
                border: 1px solid {border};
                border-radius: 6px;
                padding: 4px 8px;
                font-family: "{UI_FONT}";
                font-size: 13px;
            }}
            SearchBar QLineEdit:focus {{
                border-color: #0A84FF;
            }}
            QLabel#matchLabel {{
                color: {text_dim};
                font-size: 12px;
            }}
            QPushButton#closeSearchBtn {{
                background: transparent;
                border: none;
                color: {text_dim};
                font-size: 13px;
                border-radius: 11px;
            }}
            QPushButton#closeSearchBtn:hover {{
                background: {border};
                color: #FFFFFF;
            }}

            /* ── Status bar ── */
            QLabel#StatusLabel {{
                background: {status_bg};
                border-top: 1px solid {border};
                color: {text_dim};
                font-family: "{UI_FONT}";
                font-size: 12px;
                padding: 4px 14px;
            }}

            /* ── Scrollbar ── */
            QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 8px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {border};
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            QScrollBar:horizontal {{
                height: 0;
            }}
        """)

    # ── Drag & drop onto main window ──────────────────────────────────────────

    def dragEnterEvent(self, event: QDragEnterEvent):
        if self._event_has_pdfs(event):
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        paths = self._pdf_paths_from_event(event)
        if paths:
            self._load_pdfs(paths)

    # ── File loading ──────────────────────────────────────────────────────────

    def _open_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Open PDF Files", "",
            "PDF Files (*.pdf);;All Files (*.*)"
        )
        if paths:
            self._load_pdfs(paths)

    def _load_pdfs(self, paths: list):
        for path in paths:
            path = os.path.abspath(path)
            if any(d.path == path for d in self.documents):
                continue   # already loaded

            doc = PDFDocument(path)
            self.documents.append(doc)
            item = FileListItem(doc)
            self.sidebar.addItem(item)

            # Load on background thread
            thread = QThread()
            worker = PDFWorker(path)
            worker.moveToThread(thread)

            worker.finished.connect(self._on_pdf_loaded)
            worker.error.connect(self._on_pdf_error)
            thread.started.connect(worker.run)

            # Clean up when done
            worker.finished.connect(thread.quit)
            worker.error.connect(thread.quit)
            thread.finished.connect(thread.deleteLater)

            self._workers.append((thread, worker))
            thread.start()

        # Show last added file
        if self.documents:
            last_row = self.sidebar.count() - 1
            self.sidebar.setCurrentRow(last_row)

    def _on_pdf_loaded(self, path: str, text: str, page_count: int):
        doc = self._find_doc(path)
        if not doc:
            return
        doc.text       = text
        doc.page_count = page_count
        doc.loading    = False
        self._refresh_sidebar_item(doc)
        if self.current_doc and self.current_doc.path == path:
            self._show_document(doc)

    def _on_pdf_error(self, path: str, error_msg: str):
        doc = self._find_doc(path)
        if not doc:
            return
        doc.error   = error_msg
        doc.loading = False
        self._refresh_sidebar_item(doc)
        if self.current_doc and self.current_doc.path == path:
            self._show_document(doc)

    def _find_doc(self, path: str) -> PDFDocument | None:
        return next((d for d in self.documents if d.path == path), None)

    def _refresh_sidebar_item(self, doc: PDFDocument):
        for i in range(self.sidebar.count()):
            item = self.sidebar.item(i)
            if isinstance(item, FileListItem) and item.doc is doc:
                item._refresh()
                break

    # ── Display ───────────────────────────────────────────────────────────────

    def _on_sidebar_changed(self, current, _previous):
        if isinstance(current, FileListItem):
            self._show_document(current.doc)

    def _show_document(self, doc: PDFDocument):
        self.current_doc = doc

        self.drop_zone.setVisible(False)
        self.text_viewer.setVisible(True)

        if doc.loading:
            self.text_viewer.setPlainText("⏳  Loading…")
        else:
            self.text_viewer.setPlainText(doc.text)

        # Re-apply any active search
        query = self.search_bar.input.text()
        if query and self.search_bar.isVisible():
            count = self.text_viewer.highlight_search(query)
            self.search_bar.set_match_count(count, query)

        # Update actions
        has_doc = not doc.loading and not doc.error
        self.act_copy.setEnabled(has_doc)
        self.act_save.setEnabled(has_doc)
        self.act_search.setEnabled(True)
        self.act_clear.setEnabled(True)

        self.status_label.setText(doc.status_line)

    def _update_empty_state(self):
        has_docs = bool(self.documents)
        self.drop_zone.setVisible(not has_docs and not self.text_viewer.isVisible())
        if not has_docs:
            self.text_viewer.setVisible(False)
            self.drop_zone.setVisible(True)
            self.status_label.setText("Open a PDF to get started")
            self.act_copy.setEnabled(False)
            self.act_save.setEnabled(False)
            self.act_search.setEnabled(False)
            self.act_clear.setEnabled(False)
            self.current_doc = None

    # ── Search ────────────────────────────────────────────────────────────────

    def _show_search(self):
        if not self.current_doc:
            return
        self.search_bar.setVisible(True)
        self.search_bar.focus()

    def _hide_search(self):
        self.search_bar.setVisible(False)
        self.search_bar.clear()
        self.text_viewer.highlight_search("")

    def _on_search_changed(self, query: str):
        count = self.text_viewer.highlight_search(query)
        self.search_bar.set_match_count(count, query)

    # ── Actions ───────────────────────────────────────────────────────────────

    def _copy_text(self):
        if self.current_doc and self.current_doc.text:
            QApplication.clipboard().setText(self.current_doc.text)
            self._flash_status("✓  Text copied to clipboard", 2500)

    def _save_text(self):
        if not self.current_doc:
            return
        default = str(Path(self.current_doc.path).with_suffix(".txt").name)
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Extracted Text", default,
            "Text Files (*.txt);;All Files (*.*)"
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(self.current_doc.text)
                self._flash_status(f"✓  Saved to {Path(path).name}", 3000)
            except OSError as exc:
                QMessageBox.critical(self, "Save Error", str(exc))

    def _remove_current(self):
        if not self.current_doc:
            return
        row = self.sidebar.currentRow()
        if row >= 0:
            self.sidebar.takeItem(row)
            self.documents.remove(self.current_doc)
            self.current_doc = None
            if self.documents:
                new_row = min(row, self.sidebar.count() - 1)
                self.sidebar.setCurrentRow(new_row)
            else:
                self._update_empty_state()
                self._hide_search()

    # ── Context menu on sidebar ───────────────────────────────────────────────

    def _sidebar_context_menu(self, pos):
        item = self.sidebar.itemAt(pos)
        if not isinstance(item, FileListItem):
            return
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        menu.addAction("Show in Finder", lambda: self._reveal_in_finder(item.doc.path))
        menu.addSeparator()
        menu.addAction("Remove from List", self._remove_current)
        menu.exec(self.sidebar.viewport().mapToGlobal(pos))

    def _reveal_in_finder(self, path: str):
        import subprocess
        subprocess.Popen(["open", "-R", path])

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _flash_status(self, msg: str, duration_ms: int = 2000):
        self.status_label.setText(msg)
        if self.current_doc:
            doc = self.current_doc
            QTimer.singleShot(duration_ms, lambda: (
                self.status_label.setText(doc.status_line)
                if self.current_doc is doc else None
            ))

    @staticmethod
    def _event_has_pdfs(event) -> bool:
        return (event.mimeData().hasUrls() and
                any(u.toLocalFile().lower().endswith(".pdf")
                    for u in event.mimeData().urls()))

    @staticmethod
    def _pdf_paths_from_event(event) -> list:
        return [u.toLocalFile() for u in event.mimeData().urls()
                if u.toLocalFile().lower().endswith(".pdf")]


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    # Enable high-DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("PDFTextExtractor")

    # Use native macOS style
    if sys.platform == "darwin":
        app.setStyle("macos")

    window = MainWindow()
    window.show()

    # Support opening files via command-line args
    args = sys.argv[1:]
    pdf_args = [a for a in args if a.lower().endswith(".pdf") and os.path.isfile(a)]
    if pdf_args:
        window._load_pdfs(pdf_args)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
