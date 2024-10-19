import sys
import mysql.connector
from mysql.connector import Error
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QLineEdit, QPushButton, QTextEdit,
    QWidget, QScrollArea, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import datetime

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'userNameHere',     # Replace with your MariaDB username
    'password': 'passwordHere',     # Replace with your MariaDB password
    'database': 'readability_analyzer'  # Replace with your database name
}

class ReadabilityAnalyzerGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle("Readability Analyzer")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #2E2E2E; color: #FFFFFF;")

        # Main layout
        main_layout = QVBoxLayout()

        # Create a drop-down for users
        self.user_label = QLabel("Select User:")
        self.user_label.setFont(QFont("Arial", 10))
        self.user_label.setStyleSheet("color: #FFFFFF;")
        self.user_dropdown = QComboBox()
        self.user_dropdown.setFont(QFont("Arial", 10))
        self.user_dropdown.setStyleSheet("background-color: #3A3A3A; color: #FFFFFF;")
        self.load_users()
        self.user_dropdown.addItem("ALL USERS")

        # Create a line edit for keyword search
        self.keyword_label = QLabel("Search Keyword:")
        self.keyword_label.setFont(QFont("Arial", 10))
        self.keyword_label.setStyleSheet("color: #FFFFFF;")
        self.keyword_edit = QLineEdit()
        self.keyword_edit.setFont(QFont("Arial", 10))
        self.keyword_edit.setStyleSheet("background-color: #3A3A3A; color: #FFFFFF;")

        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.setFont(QFont("Arial", 10))
        self.search_button.setStyleSheet("background-color: #007ACC; color: #FFFFFF;")
        self.search_button.clicked.connect(self.search_messages)

        # Show Averages button
        self.show_averages_button = QPushButton("Show Averages")
        self.show_averages_button.setFont(QFont("Arial", 10))
        self.show_averages_button.setStyleSheet("background-color: #007ACC; color: #FFFFFF;")
        self.show_averages_button.clicked.connect(self.show_averages)

        # Copy to Clipboard button
        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.setFont(QFont("Arial", 10))
        self.copy_button.setStyleSheet("background-color: #007ACC; color: #FFFFFF;")
        self.copy_button.clicked.connect(self.copy_to_clipboard)

        # Textbox for displaying results
        self.result_text = QTextEdit()
        self.result_text.setFont(QFont("Arial", 10))
        self.result_text.setStyleSheet("background-color: #3A3A3A; color: #FFFFFF;")
        self.result_text.setReadOnly(True)

        # Scroll area for the result text
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.result_text)

        # Layouts for the components
        form_layout = QHBoxLayout()
        form_layout.addWidget(self.user_label)
        form_layout.addWidget(self.user_dropdown)
        form_layout.addWidget(self.keyword_label)
        form_layout.addWidget(self.keyword_edit)
        form_layout.addWidget(self.search_button)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.show_averages_button)
        button_layout.addWidget(self.copy_button)

        # Add all widgets to the main layout
        main_layout.addLayout(form_layout)
        main_layout.addWidget(scroll_area)
        main_layout.addLayout(button_layout)

        # Set the main layout
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def load_users(self):
        """Load users from the database into the dropdown."""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT username FROM messages")
            users = cursor.fetchall()
            for user in users:
                self.user_dropdown.addItem(user[0])
            cursor.close()
            conn.close()
        except Error as e:
            QMessageBox.critical(self, "Database Error", f"Error loading users from database: {e}")

    def search_messages(self):
        """Search the database for messages based on user and keyword."""
        user = self.user_dropdown.currentText()
        keyword = self.keyword_edit.text()

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Formulate the SQL query
            if user == "ALL USERS":
                query = "SELECT username, message, readability_score, timestamp FROM messages WHERE message LIKE %s"
                cursor.execute(query, (f"%{keyword}%",))
            else:
                query = "SELECT username, message, readability_score, timestamp FROM messages WHERE username = %s AND message LIKE %s"
                cursor.execute(query, (user, f"%{keyword}%"))

            # Fetch the results
            results = cursor.fetchall()
            self.result_text.clear()
            if results:
                for row in results:
                    # Remove first 3 characters from the username
                    modified_username = row[0][3:] if len(row[0]) > 3 else row[0]
                    self.result_text.append(f"User: {modified_username}\nMessage: {row[1]}\nReadability Score: {row[2]:.2f}\nTimestamp: {row[3]}\n")
                    self.result_text.append("-" * 50)
            else:
                self.result_text.append("No results found.")

            cursor.close()
            conn.close()
        except Error as e:
            QMessageBox.critical(self, "Database Error", f"Error searching messages in the database: {e}")

    def show_averages(self):
        """Calculate and display the average readability scores for all users."""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Query to get average readability score for each user
            cursor.execute("SELECT username, AVG(readability_score) FROM messages GROUP BY username")
            results = cursor.fetchall()

            # Query to get the total number of messages
            cursor.execute("SELECT COUNT(*) FROM messages")
            total_messages = cursor.fetchone()[0]
            
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.result_text.clear()

            if results:
                self.result_text.append("--- Average Readability Scores for All Users ---")
                self.result_text.append(f"--- Total Messages Analyzed {total_messages} ---")
                self.result_text.append(f"--- {timestamp} ---")

                for row in results:
                    # Remove first 3 characters from the username
                    modified_username = row[0][3:] if len(row[0]) > 3 else row[0]
                    avg_score = row[1]
                    grade_level = self.score_to_grade_level(avg_score)
                    self.result_text.append(f"{modified_username}'s average Dale-Chall readability score: {avg_score:.2f} ({grade_level})")
                
                self.result_text.append("--- End of Average Readability Scores ---\n")
            else:
                self.result_text.append("No data available.")

            cursor.close()
            conn.close()
        except Error as e:
            QMessageBox.critical(self, "Database Error", f"Error calculating averages: {e}")

    def copy_to_clipboard(self):
        """Copy the contents of the result text box to the clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.result_text.toPlainText())
        QMessageBox.information(self, "Copy to Clipboard", "Results copied to clipboard.")

    def score_to_grade_level(self, score):
        """Convert the Dale-Chall readability score to a grade level."""
        if score <= 4.9:
            return "4th Grade or below"
        elif score <= 5.9:
            return "5th - 6th Grade"
        elif score <= 6.9:
            return "7th - 8th Grade"
        elif score <= 7.9:
            return "9th - 10th Grade"
        elif score <= 8.9:
            return "11th - 12th Grade"
        else:
            return "College Level"

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ReadabilityAnalyzerGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
