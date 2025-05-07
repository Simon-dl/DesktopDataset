#Display random images from a folder of collected images
#going to use Pyside6 to display the images in a window that will move around the screen.

import os
import random
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QVBoxLayout, QLineEdit, QMainWindow, QLabel
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtCore import Qt,QTimer, QRect
import sys

from screenshot import take_and_save_screenshot


def grab_random_image(image_files):
    image_path = os.getcwd() + "/images"
    if image_files:
        random_image = random.choice(image_files)
        return os.path.join(image_path, random_image)
    return None

class DisplayImage(QWidget):
    def __init__(self):
        super().__init__()

        flags = (
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint      # Keep it on top
        )

        self.resize(400, 300)

        self.setWindowFlags(flags)
        self.setWindowTitle("Quit Pannel")


        initial_image = os.getcwd() + "/starter.png"
        self.background_pixmap = QPixmap(initial_image)


        # Get all screens
        self.screens = QApplication.screens()
        # Store the combined geometry of all screens
        self.combined_geometry = self.get_combined_screen_geometry()


        # Get the screen geometry and move the window
        screen = QApplication.primaryScreen()
        self.screen_geometry = screen.availableGeometry()
        x = self.screen_geometry.left() + 100
        y = self.screen_geometry.bottom() - self.height() + 100
        self.move(x, y)

        self.show()

    def get_combined_screen_geometry(self):
        """Calculate the combined geometry of all screens"""
        combined = QRect()
        for screen in self.screens:
            combined = combined.united(screen.geometry())
        return combined
    
    def get_current_screen(self):
        """Get the screen that contains the center of the window"""
        window_center = self.geometry().center()
        for screen in self.screens:
            if screen.geometry().contains(window_center):
                return screen
        return QApplication.primaryScreen()  # fallback to primary screen


    def set_image(self, image_path):
        self.image_path = image_path
        self.background_pixmap = QPixmap(image_path)

        random_image_width = random.randint(200, 500)
        self.resize(random_image_width, random_image_width)

        # First, randomly select a screen
        target_screen = random.choice(self.screens)
        screen_rect = target_screen.geometry()

        
        random_x = random.randint(
            screen_rect.left(),
            screen_rect.right() - random_image_width
        )
        random_y = random.randint(
            screen_rect.top(),
            screen_rect.bottom() - random_image_width
        )

        self.move(random_x, random_y)


        target_screen = None
        for screen in self.screens:
            screen_rect = screen.geometry()
            if (screen_rect.left() <= random_x <= screen_rect.right() and 
                screen_rect.top() <= random_y <= screen_rect.bottom()):
                target_screen = screen
                break

        current_screen = self.get_current_screen()

        self.update()

        if target_screen == current_screen:
            return current_screen.geometry()
        else:
            print("target screen is not the current screen")
            return None

    def paintEvent(self, event):
        painter = QPainter(self)
        # Draw the pixmap scaled to the widget size
        painter.drawPixmap(self.rect(), self.background_pixmap)
        super().paintEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dataset Generator")
        self.setGeometry(100, 100, 400, 200)
        self.images_captured = 0

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.frequency_label = QLabel("Image appearance frequency in seconds (>= 1)")
        layout.addWidget(self.frequency_label)

        self.frequency_textbox = QLineEdit()
        self.frequency_textbox.setPlaceholderText("10")
        layout.addWidget(self.frequency_textbox)

        # Create button
        self.button = QPushButton("Start Program")
        self.button.clicked.connect(self.check_and_start_program)
        layout.addWidget(self.button)

    def message_box(self,message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText("Invalid Input")
        msg_box.setInformativeText(message)
        msg_box.setDefaultButton(QMessageBox.Ok)
        msg_box.exec()

    def check_image_directory(self):
        image_path = os.getcwd() + "/images"
        image_files = [f for f in os.listdir(image_path) if f.endswith(('.jpg', '.jpeg', '.png','.gif'))]
        if image_files == []:
            self.message_box("No images found in the images directory")
            return False
        else:
            self.image_files = image_files
            return True
            
    def check_input(self,text,case):
        if not text.strip():
            self.message_box(f"Please enter some text for the {case} input!")
            return False
        elif self.check_specific(text,case) == False:
            return False
        elif self.check_image_directory() == False:
            return False
        else:
            return True
        
    def check_specific(self,text,case):
        if case == "frequency":
            if not text.isdigit() or int(text) <= 0:
                self.message_box("Frequency must be a whole number greater than 0")
                return False
            else:
                return True
        
    def start_program(self):
        frequency = self.frequency_textbox.text()
        print(f"Frequency: {frequency}")
        
        # Create new window with quit button
        self.quit_window = QMainWindow()
        self.quit_window.setWindowTitle("Program Running")
        self.quit_window.setGeometry(100, 100, 200, 100)
        
        # Create central widget and layout for quit window
        quit_widget = QWidget()
        self.quit_window.setCentralWidget(quit_widget)
        quit_layout = QVBoxLayout(quit_widget)

        self.captured_label = QLabel(f"Program running and has captured {self.images_captured} images so far")
        quit_layout.addWidget(self.captured_label)
        
        # Create quit button
        quit_button = QPushButton("Quit")
        quit_button.clicked.connect(self.quit_program)
        quit_layout.addWidget(quit_button)
        
        # Hide main window and show quit window
        self.hide()
        self.quit_window.show()
        
        # Create display panel and start timer here
        self.display_panel = DisplayImage()
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.display_process())
        self.timer.start(int(frequency) * 1000)  # Convert frequency to milliseconds

    def display_process(self):
        self.display_panel.show()
        image_path = grab_random_image(self.image_files)
        screen_geometry = self.display_panel.set_image(image_path)
        if screen_geometry:
            # Add a small delay to ensure window has moved
            QTimer.singleShot(100, lambda: take_and_save_screenshot(screen_geometry))
        self.images_captured += 1
        self.captured_label.setText(f"Program running and has captured {self.images_captured} images so far")
        QTimer.singleShot(100, lambda: self.display_panel.hide())

    def quit_program(self):
        if hasattr(self, 'timer'):
            self.timer.stop()
        if hasattr(self, 'display_panel'):
            self.display_panel.close()
        self.quit_window.close()
        self.close()

    def check_and_start_program(self):
        frequency_valid = self.check_input(self.frequency_textbox.text(),"frequency")

        if frequency_valid:
            self.start_program()

def start_main_program():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
    
if __name__ == "__main__":
    start_main_program()


