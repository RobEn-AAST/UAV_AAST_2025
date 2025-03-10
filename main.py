import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QTextEdit, QFrame, QPushButton,
                            QShortcut)
from PyQt5.QtGui import QPixmap, QColor, QPainter, QFont, QKeySequence
from PyQt5.QtCore import Qt, QSize

class StatusIndicator(QWidget):
    """Custom widget for colored circle indicators."""
    def __init__(self, color="green", parent=None):
        super().__init__(parent)
        self.color = color
        self.setMinimumSize(20, 20)
        self.setMaximumSize(20, 20)
    
    def set_color(self, color):
        """Set the color of the indicator."""
        self.color = color
        self.update()
    
    def paintEvent(self, event):
        """Paint the indicator."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if self.color == "green":
            painter.setBrush(QColor(0, 255, 0))
        elif self.color == "yellow":
            painter.setBrush(QColor(255, 255, 0))
        elif self.color == "red":
            painter.setBrush(QColor(255, 0, 0))
        else:
            painter.setBrush(QColor(128, 128, 128))  # Gray for unknown status
        
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 20, 20)

class CameraInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        # Set fixed font sizes
        self.font_size = 24  # For status/action headers
        self.label_size = 20  # For status/action values
        self.terminal_size = 14  # Increased from 10
        self.title_size = 32  # For the RobEn UAV title
        self.terminal_prompt = "RobEn/UAV> "
        self.initUI()
    
    # Custom terminal handling methods
    def enforce_prompt(self):
        """Ensure the terminal prompt is always visible and can't be deleted."""
        cursor = self.terminal.textCursor()
        text = self.terminal.toPlainText()
        
        # Check if prompt is intact
        if not text.endswith(self.terminal_prompt) and not text.endswith(self.terminal_prompt + " "):
            if self.terminal_prompt not in text:
                # Prompt is completely gone, reset it
                self.terminal.setText(self.terminal_prompt)
                cursor = self.terminal.textCursor()
                cursor.movePosition(cursor.End)
            else:
                # Get the current line
                current_line = text.split('\n')[-1]
                
                # If current line doesn't start with prompt, add it
                if not current_line.startswith(self.terminal_prompt):
                    lines = text.split('\n')
                    lines[-1] = self.terminal_prompt + current_line
                    self.terminal.setText('\n'.join(lines))
                    
                # Set cursor position at end
                cursor = self.terminal.textCursor()
                cursor.movePosition(cursor.End)
            
            self.terminal.setTextCursor(cursor)
    
    def terminal_key_press(self, event):
        """Custom key press handler for terminal."""
        cursor = self.terminal.textCursor()
        current_text = self.terminal.toPlainText()
        
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Handle Enter key - add a new line with prompt
            command = current_text.split('\n')[-1][len(self.terminal_prompt):].strip()
            
            # Process the command here if needed
            # For now, just echo it
            
            # Add new line with prompt
            self.terminal.append(self.terminal_prompt)
            
            # Set cursor at the end
            cursor = self.terminal.textCursor()
            cursor.movePosition(cursor.End)
            self.terminal.setTextCursor(cursor)
            return  # Skip default event processing
        
        elif event.key() == Qt.Key_Backspace:
            # Prevent deleting prompt
            lines = current_text.split('\n')
            current_line = lines[-1]
            
            if len(current_line) <= len(self.terminal_prompt):
                return  # Don't allow backspace into or before prompt
            else:
                # Allow normal backspace behavior
                QTextEdit.keyPressEvent(self.terminal, event)
            return  # Skip default event processing
        
        elif event.key() == Qt.Key_Home:
            # Move to beginning of text (after prompt)
            lines = current_text.split('\n')
            current_line_number = len(lines) - 1
            cursor.setPosition(sum(len(lines[i]) + 1 for i in range(current_line_number)) + len(self.terminal_prompt))
            self.terminal.setTextCursor(cursor)
            return  # Skip default event processing
        
        else:
            # For any other key, ensure we're not in the prompt area
            lines = current_text.split('\n')
            current_line = lines[-1]
            
            if cursor.position() < (len(current_text) - len(current_line) + len(self.terminal_prompt)):
                # If cursor is before the prompt position, move it to after prompt
                cursor.setPosition(len(current_text) - len(current_line) + len(self.terminal_prompt))
                self.terminal.setTextCursor(cursor)
            
            # Process the key as normal
            QTextEdit.keyPressEvent(self.terminal, event)

    def initUI(self):
        # Main widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Set dark blue background color
        self.setStyleSheet("background-color: #001133;")
        central_widget.setStyleSheet("background-color: #001133; color: white;")
        
        # Content section (left and right panels)
        content_layout = QHBoxLayout()
        
        # Left panel - Title, Status and Action
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Add spacer at top to center content vertically
        left_layout.addStretch(1)
        
        # Title at the top of left panel
        self.title_label = QLabel("RobEn UAV")
        self.title_label.setFont(QFont("Arial", self.title_size, QFont.Bold))
        self.title_label.setStyleSheet(f"color: white; font-size: {self.title_size}pt;")
        self.title_label.setAlignment(Qt.AlignCenter)  # Center in the left panel
        left_layout.addWidget(self.title_label)
        left_layout.addSpacing(20)  # Add space after title
        
        # Status section - increase spacing
        status_layout = QVBoxLayout()
        status_layout.setSpacing(15)  # Increase vertical spacing
        
        self.status_header = QLabel("Status:")
        self.status_header.setStyleSheet(f"font-weight: bold; font-size: {self.font_size}pt; font-family: Arial; color: white;")
        self.status_header.setContentsMargins(20, 0, 0, 0)  # Add left margin to move text right
        
        status_content = QHBoxLayout()
        status_content.setContentsMargins(40, 0, 0, 0)  # Add left margin to move content right
        self.status_indicator = StatusIndicator("green")
        self.status_indicator.setMinimumSize(20, 20)  # Make indicator bigger
        self.status_indicator.setMaximumSize(20, 20)
        self.status_label = QLabel("Online")
        self.status_label.setStyleSheet(f"font-size: {self.label_size}pt; font-family: Arial; color: white;")
        status_content.addWidget(self.status_indicator)
        status_content.addWidget(self.status_label)
        status_content.addStretch()
        
        status_layout.addWidget(self.status_header)
        status_layout.addLayout(status_content)
        # Add spacing between sections
        status_layout.addSpacing(25)  # Add more space after status section
        
        # Action section - increase spacing
        action_layout = QVBoxLayout()
        action_layout.setSpacing(15)  # Increase vertical spacing
        
        self.action_header = QLabel("Action:")
        self.action_header.setStyleSheet(f"font-weight: bold; font-size: {self.font_size}pt; font-family: Arial; color: white;")
        self.action_header.setContentsMargins(20, 0, 0, 0)  # Add left margin to move text right
        
        action_content = QHBoxLayout()
        action_content.setContentsMargins(40, 0, 0, 0)  # Add left margin to move content right
        self.action_indicator = StatusIndicator("yellow")
        self.action_indicator.setMinimumSize(20, 20)  # Make indicator bigger
        self.action_indicator.setMaximumSize(20, 20)
        self.action_label = QLabel("Standby")
        self.action_label.setStyleSheet(f"font-size: {self.label_size}pt; font-family: Arial; color: white;")
        action_content.addWidget(self.action_indicator)
        action_content.addWidget(self.action_label)
        action_content.addStretch()
        
        action_layout.addWidget(self.action_header)
        action_layout.addLayout(action_content)
        
        # Add status and action layouts directly to the left panel
        left_layout.addLayout(status_layout)
        left_layout.addLayout(action_layout)
        
        # Add spacer at bottom to center content
        left_layout.addStretch(1)
        
        # Right panel - SSH-like terminal
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.terminal = QTextEdit()
        self.terminal.setStyleSheet(f"background-color: black; color: #00FF00; font-family: 'Courier New'; font-size: {self.terminal_size}pt;")
        self.terminal.setText(self.terminal_prompt)
        self.terminal.setReadOnly(False)  # Allow user input
        
        # Set cursor at the end after prompt
        cursor = self.terminal.textCursor()
        cursor.movePosition(cursor.End)
        self.terminal.setTextCursor(cursor)
        
        # Connect custom handlers
        self.terminal.cursorPositionChanged.connect(self.enforce_prompt)
        self.terminal.keyPressEvent = self.terminal_key_press
        
        right_layout.addWidget(self.terminal)
        
        # Add left and right panels to content layout
        content_layout.addWidget(left_panel, 1)
        content_layout.addWidget(right_panel, 2)  # Terminal takes more space
        
        # Add content layout to main layout
        main_layout.addLayout(content_layout)
        
        # Add window controls for full screen mode
        controls_layout = QHBoxLayout()
        controls_layout.addStretch()
        
        minimize_btn = QPushButton("Minimize")
        minimize_btn.setStyleSheet("background-color: #333366; color: white; padding: 5px;")
        minimize_btn.clicked.connect(self.showMinimized)
        
        exit_btn = QPushButton("Exit")
        exit_btn.setStyleSheet("background-color: #663333; color: white; padding: 5px;")
        exit_btn.clicked.connect(self.close)
        
        controls_layout.addWidget(minimize_btn)
        controls_layout.addWidget(exit_btn)
        
        main_layout.addLayout(controls_layout)
        
        # Add keyboard shortcuts
        minimize_shortcut = QShortcut(QKeySequence("F10"), self)
        minimize_shortcut.activated.connect(self.showMinimized)
        
        exit_shortcut = QShortcut(QKeySequence("Escape"), self)
        exit_shortcut.activated.connect(self.close)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Window properties
        self.setWindowTitle('UAV Camera Interface')
        # Try windowed mode first for debugging
        self.setGeometry(100, 100, 1200, 800)
        self.show()  # Use show instead of showFullScreen for debug
    
    def set_status(self, status_text, color):
        """
        Set the status display.
        
        Args:
            status_text (str): Status text to display
            color (str): Color for indicator ('green', 'yellow', or 'red')
        """
        self.status_label.setText(status_text)
        self.status_indicator.set_color(color)
    
    def set_action(self, action_text, color):
        """
        Set the action display.
        
        Args:
            action_text (str): Action text to display
            color (str): Color for indicator ('green', 'yellow', or 'red')
        """
        self.action_label.setText(action_text)
        self.action_indicator.set_color(color)
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CameraInterface()
    
    # Example of setting different statuses and actions
    window.set_status("Online", "green")
    # window.set_status("Connecting", "yellow")
    # window.set_status("Offline", "red")
    
    # window.set_action("Recording", "green")
    window.set_action("Standby", "yellow")
    # window.set_action("Error", "red")
    
    sys.exit(app.exec_())