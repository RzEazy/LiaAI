import sys
from PyQt6 import QtWidgets, QtCore
from lia_ai import Lia  # Import the Lia class

class Liagui(QtWidgets.QWidget):
    send_message_signal = QtCore.pyqtSignal(str)  # Signal to send message to speech recognition

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lia Assistant")
        self.setGeometry(100, 100, 400, 300)

        # Layout setup
        self.layout = QtWidgets.QVBoxLayout(self)

        # Text display area
        self.text_display = QtWidgets.QTextEdit(self)
        self.text_display.setReadOnly(True)
        self.layout.addWidget(self.text_display)

        # Text input field
        self.text_input = QtWidgets.QLineEdit(self)
        self.layout.addWidget(self.text_input)

        # Send button
        self.send_button = QtWidgets.QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        self.layout.addWidget(self.send_button)

        # Initialize Lia
        self.lia = Lia(api_key='T1Bc1ugk1s3scjMkgKCqXDk6l8utMuBcHABskBoR')

        # Connect the signal to handle incoming messages
        self.send_message_signal.connect(self.handle_received_message)

    def send_message(self):
        user_input = self.text_input.text()
        if user_input:
            self.text_display.append(f"You: {user_input}")  # Show user input in the display
            self.text_input.clear()  # Clear the input field
            response = self.lia.generate_response(user_input)  # Get response from Lia
            self.text_display.append(f"Lia: {response}")  # Show Lia's response

    def handle_received_message(self, message):
        # This method can handle messages received from speech recognition
        if message:
            self.text_display.append(f"Lia: {message}")  # Display the message from speech recognition

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Liagui()
    window.show()
    sys.exit(app.exec())
