import sys
import os
import re
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QLabel,
    QMessageBox,
)


class MarkdownEditor(QWidget):
    def __init__(self, save_directory):
        super().__init__()
        self.save_directory = save_directory
        self.init_ui()

    def init_ui(self):
        # Set up the layout
        layout = QVBoxLayout()

        # Title input
        self.title_input = QLineEdit(self)
        self.title_input.setPlaceholderText("Title")
        layout.addWidget(self.title_input)

        # Text input
        self.text_input = QTextEdit(self)
        self.text_input.setPlaceholderText("Markdown content")
        layout.addWidget(self.text_input)

        # Save button
        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_file)
        layout.addWidget(self.save_button)

        # Notification label
        self.notification_label = QLabel("", self)
        layout.addWidget(self.notification_label)

        # Set the layout
        self.setLayout(layout)
        self.setWindowTitle("Markdown Editor")
        self.setGeometry(100, 100, 400, 300)

    def save_file(self):
        # Get the title and text
        title = self.title_input.text().strip()
        text = self.text_input.toPlainText().strip()

        if not title or not text:
            QMessageBox.warning(self, "Error", "Title and text cannot be empty!")
            return

        # Convert title to a valid filename
        filename = self.convert_to_filename(title) + ".md"
        filepath = os.path.join(self.save_directory, filename)

        try:
            # Save the file
            with open(filepath, "w") as file:
                file.write(text)
            # Notify the user
            self.notification_label.setText(f"File saved to {filepath}")
            # Clear the fields
            self.title_input.clear()
            self.text_input.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")

    def convert_to_filename(self, title):
        # Convert to lowercase
        title = title.lower()
        # Replace spaces with hyphens
        title = re.sub(r"\s+", "-", title)
        # Remove invalid characters
        title = re.sub(r"[^a-z0-9\-]", "", title)
        return title


if __name__ == "__main__":
    # Define the save directory
    save_directory = "/home/daniel/Git/llm-assistants-web-library/agent-configs"

    # Check if the directory exists
    if not os.path.exists(save_directory):
        print(f"Directory {save_directory} does not exist!")
        sys.exit(1)

    # Create the application
    app = QApplication(sys.argv)
    editor = MarkdownEditor(save_directory)
    editor.show()
    sys.exit(app.exec())