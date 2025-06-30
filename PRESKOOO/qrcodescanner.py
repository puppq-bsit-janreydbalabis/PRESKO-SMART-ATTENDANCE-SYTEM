import os
import ctypes
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.graphics import Color, Line, RoundedRectangle
from kivy.core.window import Window
from kivy.utils import platform
from pyzbar import pyzbar
import cv2
import numpy as np

# Set fullscreen for mobile
if platform in ("android", "ios"):
    Window.fullscreen = "auto"
else:
    # For desktop testing, set a mobile-like resolution
    Window.size = (360, 640)  # Common mobile resolution

# Load libzbar-64.dll explicitly for Windows (desktop testing)
if platform == "win":
    zbar_dll_path = os.path.join(os.path.dirname(__file__), "libzbar-64.dll")
    if os.path.exists(zbar_dll_path):
        ctypes.WinDLL(zbar_dll_path)
    else:
        print(
            f"Warning: {zbar_dll_path} not found. Ensure libzbar-64.dll is in the script directory."
        )


class ScanLine(Widget):
    def __init__(self, image_widget, **kwargs):
        super().__init__(**kwargs)
        self.image_widget = image_widget
        self.y_pos = 0
        self.direction = 1  # Start moving down
        self.is_animating = False
        with self.canvas:
            Color(0, 0.7, 1, 1)  # A nice cyan color
            self.line = Line(points=[0, 0, 0, 0], width=2)
        self.image_widget.bind(size=self.update_size, pos=self.update_size)

    def update_size(self, *args):
        self.size = self.image_widget.size
        self.pos = self.image_widget.pos
        self.y_pos = self.size[1]  # Start from the top

    def start_animation(self):
        if not self.is_animating:
            self.is_animating = True
            Clock.schedule_interval(self.update_line, 1.0 / 60)

    def stop_animation(self):
        if self.is_animating:
            self.is_animating = False
            Clock.unschedule(self.update_line)
            self.canvas.clear()

    def update_line(self, dt):
        self.y_pos -= self.direction * 3  # Slower, more elegant speed
        if self.y_pos <= 0 or self.y_pos >= self.size[1]:
            self.direction *= -1
        self.canvas.clear()
        with self.canvas:
            Color(0, 0.7, 1, 1)  # Cyan color
            self.line = Line(
                points=[
                    self.x,
                    self.y + self.y_pos,
                    self.x + self.size[0],
                    self.y + self.y_pos,
                ],
                width=2,
            )


class CornerMarkers(Widget):
    def __init__(self, image_widget, **kwargs):
        super().__init__(**kwargs)
        self.image_widget = image_widget
        self.size_hint = (None, None)
        self.image_widget.bind(size=self.update_corners, pos=self.update_corners)
        self.update_corners()

    def update_corners(self, *args):
        self.size = self.image_widget.size
        self.pos = self.image_widget.pos
        self.canvas.clear()
        with self.canvas:
            Color(1, 1, 1, 0.8)  # White with some transparency
            marker_size = min(self.size[0], self.size[1]) * 0.15  # Larger markers
            line_width = 4  # Thicker lines
            # Top-left corner
            Line(
                points=[
                    self.x + marker_size,
                    self.y + self.size[1],
                    self.x,
                    self.y + self.size[1],
                    self.x,
                    self.y + self.size[1] - marker_size,
                ],
                width=line_width,
                cap="square",
            )
            # Top-right corner
            Line(
                points=[
                    self.x + self.size[0] - marker_size,
                    self.y + self.size[1],
                    self.x + self.size[0],
                    self.y + self.size[1],
                    self.x + self.size[0],
                    self.y + self.size[1] - marker_size,
                ],
                width=line_width,
                cap="square",
            )
            # Bottom-left corner
            Line(
                points=[
                    self.x + marker_size,
                    self.y,
                    self.x,
                    self.y,
                    self.x,
                    self.y + marker_size,
                ],
                width=line_width,
                cap="square",
            )
            # Bottom-right corner
            Line(
                points=[
                    self.x + self.size[0] - marker_size,
                    self.y,
                    self.x + self.size[0],
                    self.y,
                    self.x + self.size[0],
                    self.y + marker_size,
                ],
                width=line_width,
                cap="square",
            )


class ModernButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        with self.canvas.before:
            Color(0.1, 0.5, 0.8, 1)
            self.rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[25]  # Pill shape
            )

    def update_graphics(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class QRScanner(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Dark background
        with self.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            self.bg = RoundedRectangle(size=Window.size, pos=(0, 0))

        # Semi-transparent overlay for the viewfinder effect
        self.overlay = Widget()
        with self.overlay.canvas:
            Color(0, 0, 0, 0.5)
            # This will be updated to punch a hole for the camera view
            RoundedRectangle(size=Window.size, pos=(0, 0))
        self.add_widget(self.overlay)

        # Container for the camera feed and its decorative elements
        self.image_container = RelativeLayout(
            size=(300, 300),
            size_hint=(None, None),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        self.image = Image(size_hint=(1, 1), allow_stretch=True, keep_ratio=False)
        self.scan_line = ScanLine(image_widget=self.image, size_hint=(None, None))
        self.corner_markers = CornerMarkers(image_widget=self.image)
        self.image_container.add_widget(self.image)
        self.image_container.add_widget(self.scan_line)
        self.image_container.add_widget(self.corner_markers)

        # UI elements
        self.result_label = Label(
            text="Align QR Code within the frame to scan",
            size_hint=(0.8, 0.15),
            pos_hint={"center_x": 0.5, "y": 0.75},
            font_size="18sp",
            halign="center",
            valign="middle",
        )
        self.scan_button = ModernButton(
            text="Stop Scanning",
            size_hint=(0.6, 0.08),
            pos_hint={"center_x": 0.5, "y": 0.1},
            font_size="16sp",
        )
        self.scan_button.bind(on_press=self.toggle_scanning)

        # Add widgets to the main layout
        self.add_widget(self.image_container)
        self.add_widget(self.result_label)
        self.add_widget(self.scan_button)

        # Camera and state variables
        self.is_scanning = False
        self.is_camera_active = False
        self.capture = None
        Clock.schedule_once(self.start_camera, 1)  # Give a moment for UI to build

    def start_camera(self, dt):
        if self.is_camera_active:
            return
        self.is_camera_active = True
        self.is_scanning = True
        self.scan_button.text = "Stop Scanning"
        self.scan_line.start_animation()
        try:
            backend = cv2.CAP_DSHOW if platform == "win" else cv2.CAP_ANY
            self.capture = cv2.VideoCapture(0, backend)
            if not self.capture.isOpened():
                self.result_label.text = "Error: Could not open camera."
                self.stop_camera()
                return
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 300)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 300)
            Clock.schedule_interval(self.update_camera_feed, 1.0 / 30)
        except Exception as e:
            self.result_label.text = f"Error: {str(e)}"
            self.stop_camera()

    def update_camera_feed(self, dt):
        if not self.is_camera_active or not self.capture:
            return
        ret, frame = self.capture.read()
        if not ret:
            self.result_label.text = "Error: Failed to capture frame."
            self.stop_camera()
            return
        try:
            frame = cv2.resize(frame, (300, 300), interpolation=cv2.INTER_AREA)
            frame = cv2.flip(frame, 0)
            texture = Texture.create(size=(300, 300), colorfmt="bgr")
            texture.blit_buffer(frame.tobytes(), colorfmt="bgr", bufferfmt="ubyte")
            self.image.texture = texture
            if self.is_scanning:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                qr_codes = pyzbar.decode(gray)
                for qr_code in qr_codes:
                    qr_data = qr_code.data.decode("utf-8")
                    self.result_label.text = f"QR Code Found:\n{qr_data}"
                    self.is_scanning = False
                    self.scan_button.text = "Start Scanning"
                    self.scan_line.stop_animation()
                    break
        except Exception as e:
            self.result_label.text = f"Error decoding QR: {str(e)}"
            self.stop_camera()

    def toggle_scanning(self, instance):
        self.is_scanning = not self.is_scanning
        if self.is_scanning:
            self.scan_button.text = "Stop Scanning"
            self.scan_line.start_animation()
            self.result_label.text = "Align QR Code within the frame to scan"
        else:
            self.scan_button.text = "Start Scanning"
            self.scan_line.stop_animation()

    def stop_camera(self):
        self.is_scanning = False
        self.is_camera_active = False
        self.scan_button.text = "Start Scanning"
        self.scan_line.stop_animation()
        Clock.unschedule(self.update_camera_feed)
        if self.capture:
            self.capture.release()
            self.capture = None

    def on_stop(self):
        self.stop_camera()


class QRScannerApp(App):
    def build(self):
        return QRScanner()

    def on_stop(self):
        self.root.on_stop()


if __name__ == "__main__":
    QRScannerApp().run()
