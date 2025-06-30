from kivy.core.window import Window
Window.fullscreen = 'auto'

from threading import Thread
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.properties import ListProperty, StringProperty
from kivy.uix.gridlayout import GridLayout
from datetime import datetime
from kivy.clock import Clock
from io import BytesIO
from datetime import timedelta
from kivy.uix.popup import Popup
from kivy.uix.image import Image as KivyImage
from kivy.core.image import Image as CoreImage
from kivy.uix.scrollview import ScrollView
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle
from datetime import datetime
import calendar
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image as KivyImage
from kivy.graphics.texture import Texture
import time

import cv2

import qrcode
import os

# Add this near your imports or just above your App class

marked_dates_per_subject = {
    "COMP 003_Computer Programming II": {
        "2025-05-24": "pending",
        "2025-05-25": "pending"
    },
    "ITP 101_Intro to Python": {
        "2025-05-25": "pending"
    }
}

attendance_status_per_subject = {
    "COMP 003_Computer Programming II": {
        "2025-05-24": "present"
    },
    "ITP 101_Intro to Python": {
        "2025-05-25": "present"
    }
}

code_cache = {
    "COMP 003_Computer Programming II_2025-05-24": "ABC123",
    "ITP 101_Intro to Python_2025-05-25": "XYZ789"
}

qr_expiry_cache = {
    "COMP 003_Computer Programming II_2025-05-24": {
        "start": "2025-05-24 10:00:00",
        "end": "2025-05-24 11:00:00"
    },
    "ITP 101_Intro to Python_2025-05-25": {
        "start": "2025-05-25 08:00:00",
        "end": "2025-05-25 09:00:00"
    }
}

# Make sure the folder exists
os.makedirs("qrcodes", exist_ok=True)

# Dates to generate QR codes for
dates = ["2025-05-24", "2025-05-25"]

for date in dates:
    img = qrcode.make(f"QR for {date}")
    img.save(f"qrcodes/{date}.png")

# Default QR code (fallback)
img = qrcode.make("Default QR")
img.save("qrcodes/default.png")

print("QR codes generated!")

marked_dates = {
    "2025-05-24": "pending",  # Student hasn't scanned yet
    "2025-05-25": "pending"
}
# ✅ Attendance tracking (in-memory)
attendance_status = {
    # Updated only if student scans or enters correctly
    "2025-05-24": "present"
}

class ImageButton(ButtonBehavior, KivyImage):
    pass

class BigRoundedCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = [30, 30, 30, 30]
        self.spacing = 20
        self.size_hint = (None, None)
        self.size = (900, 650)
        self.pos_hint = {"center_x": 0.5, "center_y": 0.45}
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg = RoundedRectangle(radius=[30], pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

class StudentHomeScreen(Screen):
    subjects = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()

        self.subjects = [
    ("COMP 003", "Computer Programming II", "Prof. Reyes", "Mon & Wed 1PM", "BSIT 1-2")
]
        # Background
        bg = Image(source='bg_app.jpg', allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(bg)

        # Header bar
        header_bar = BoxLayout(size_hint=(1, None), height=120, pos_hint={"top": 1})
        with header_bar.canvas.before:
            Color(0.6, 0.6, 0.6, 1)
            header_bar.bg_rect = Rectangle(size=header_bar.size, pos=header_bar.pos)
        header_bar.bind(size=lambda i, v: setattr(header_bar.bg_rect, 'size', v),
                        pos=lambda i, v: setattr(header_bar.bg_rect, 'pos', v))
        self.layout.add_widget(header_bar)

        # Logo + Text
        self.layout.add_widget(Image(source='preskokooko-letter.png', size_hint=(None, None), size=(200, 200), pos_hint={"center_x": 0.5, "top": 1}))

        # ➕ Add Button
        add_btn = Button(
            background_normal='plus_sign.png',  # Use your existing image
            background_down='plus_sign.png',
            size_hint=(None, None),
            size=(50, 50),
            pos_hint={"center_x": 0.5, "y": 0.02},
            border=(0, 0, 0, 0)
        )
        add_btn.bind(on_release=self.go_to_add_subject)
        self.layout.add_widget(add_btn)


        student_label = Label(
            text="[b]STUDENT[/b]",
            markup=True,
            font_size='24sp',
            size_hint=(0.1, 0.08),
            pos_hint={"center_x": 0.5, "top": 0.88},
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle'
        )
        student_label.bind(size=student_label.setter('text_size'))
        with student_label.canvas.before:
            Color(0.5, 0.5, 0.5, 1)
            student_bg = Rectangle(size=student_label.size, pos=student_label.pos)
        student_label.bind(pos=lambda i, v: setattr(student_bg, 'pos', v),
                           size=lambda i, v: setattr(student_bg, 'size', v))
        self.layout.add_widget(student_label)

        # Date/Time
        self.datetime_label = Label(text="", size_hint=(.2, .1), pos_hint={"top": 1, "center_x": 0.5}, font_size=18, color=(1, 1, 1, 1))
        Clock.schedule_interval(self.update_datetime, 1)
        self.layout.add_widget(self.datetime_label)

        # Subject Cards (dummy for now)
        self.subject_box = BoxLayout(orientation='vertical', spacing=10, size_hint=(.9, .5), pos_hint={"center_x": 0.5, "top": 0.68})
        self.layout.add_widget(self.subject_box)
        self.load_subject_cards()
        self.add_widget(self.layout)

    def update_datetime(self, dt):
        now = datetime.now()
        self.datetime_label.text = now.strftime("%A, %B %d, %Y | %I:%M:%S %p")

    def load_subject_cards(self):
        self.subject_box.clear_widgets()

    # Example subject for display
        subjects = self.subjects

        for data in subjects:
            text = (
                f"SUBJECT CODE: {data[0]}\n"
                f"SUBJECT NAME: {data[1]}\n"
                f"PROFESSOR: {data[2]}\n"
                f"SCHEDULE: {data[3]}\n"
                f"SECTION: {data[4]}"
            )
            card = Button(
                text=text,
                halign="left",
                valign="middle",
                text_size=(None, None),
                font_size=12,
                background_normal='',
                background_color=(1, 1, 1, 1),
                color=(0, 0, 0, 1),
                size_hint_y=None,
                height=80
            )
            card.bind(
                on_release=lambda x, subject_key=f"{data[0]}_{data[1]}": self.open_calendar(subject_key),
                size=lambda instance, value: setattr(instance, 'text_size', (instance.width - 40, None))
            )
            self.subject_box.add_widget(card)

    # Add remaining placeholders
        for _ in range(7 - len(subjects)):
            placeholder = Button(
                text="",
                font_size=12,
                halign="left",
                valign="middle",
                text_size=(None, None),
                background_normal='',
                background_color=(1, 1, 1, 0.3),
                color=(1, 1, 1, 0.7),
                size_hint_y=None,
                height=80
            )
            self.subject_box.add_widget(placeholder)
    
    def open_calendar(self, subject_key):
        calendar_screen = self.manager.get_screen("student_calendar")
        calendar_screen.current_subject_key = subject_key
        calendar_screen.on_pre_enter()  # Refresh calendar
        self.manager.current = "student_calendar"

    def go_to_calendar(self, instance):
        self.manager.current = "student_calendar"  # Placeholder screen name

    def go_to_add_subject(self, instance):
        self.manager.current = "add_subject_student"

class AddSubjectStudentScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()
        self.inputs = {}

        self.layout.add_widget(Image(source='bg_app.jpg', allow_stretch=True, keep_ratio=False))

        # Header
        header = BoxLayout(size_hint=(1, None), height=120, pos_hint={"top": 1})
        with header.canvas.before:
            Color(0.6, 0.6, 0.6, 1)
            header.bg_rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=lambda i, v: setattr(header.bg_rect, 'size', v),
                    pos=lambda i, v: setattr(header.bg_rect, 'pos', v))
        
        self.layout.add_widget(header)
        
        back_btn = ImageButton(
            source='back-button.png',
            size_hint=(None, None),
            size=(45, 45),
            pos_hint={"top": .99, "x": 0.01}
        )
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'student_home'))
        self.layout.add_widget(back_btn)

        # Menu Button
        menu_icon = ImageButton(
            source='menu.png',
            size_hint=(None, None),
            size=(45, 45),
            pos_hint={"top": .99, "right": .99}
        )
        menu_icon.bind(on_release=self.open_student_menu)
        self.layout.add_widget(menu_icon)

        self.layout.add_widget(Image(source='preskokooko-letter.png', size_hint=(None, None),
                                     size=(200, 200), pos_hint={"center_x": 0.5, "top": 1}))

        student_label = Label(
            text="[b]STUDENT[/b]", markup=True, font_size='24sp',
            pos_hint={"center_x": 0.5, "top": 0.88}, color=(1, 1, 1, 1)
        )
        self.layout.add_widget(student_label)

        # REAL-TIME CLOCK (place this after the logo and student label are added)
        self.datetime_label = Label(
            text="",
            size_hint=(None, None),
            size=(400, 40),
            pos_hint={"center_x": 0.5, "top": 0.97},
            font_size=18,
            color=(1, 1, 1, 1)
        )
        self.layout.add_widget(self.datetime_label)
        Clock.schedule_interval(self.update_datetime, 1)

        # Form Inputs
        form = BoxLayout(orientation='vertical', spacing=15, padding=[50, 10, 50, 150],
                         size_hint=(None, None), size=(750, 750),
                         pos_hint={"center_x": 0.5, "center_y": 0.75})
        self.inputs = {
            'Subject Code': TextInput(hint_text='Insert Subject Code:', font_size=18, height=45),
            'Subject Name': TextInput(hint_text='Insert Subject Name:', font_size=18, height=45),
            'Professor Name': TextInput(hint_text="Professor's Name:", font_size=18, height=45),
            'Schedule': TextInput(hint_text='Time & Day Schedule:', font_size=18, height=45),
            'Section': TextInput(hint_text='Course, Year & Section:', font_size=18, height=45)
        }

        for field in self.inputs.values():
            field.size_hint = (1, None)
            form.add_widget(field)

        submit_btn = Button(text='Submit', font_size=18, height=45,
                            size_hint=(1, None), background_color=(0.2, 0.2, 0.2, 1), color=(1, 1, 1, 1))
        submit_btn.bind(on_release=self.submit)
        form.add_widget(submit_btn)

        form_container = BigRoundedCard()
        form_container.add_widget(form)
        self.layout.add_widget(form_container)
        self.add_widget(self.layout)

    def update_datetime(self, dt):
        now = datetime.now()
        self.datetime_label.text = now.strftime("%A, %B %d, %Y | %I:%M:%S %p")

    def submit(self, instance):
        values = [i.text.strip() for i in self.inputs.values()]
        if all(values):
            student_home = self.manager.get_screen("student_home")
            student_home.subjects.append(values)  # Make sure `subjects` is a ListProperty in StudentHomeScreen
            student_home.load_subject_cards()
            self.manager.current = "student_home"

    def open_student_menu(self, instance):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        layout.add_widget(Label(text="👤 Profile: Student", color=(1, 1, 1, 1)))
        layout.add_widget(Button(text="🌙 Toggle Dark/Light"))
        layout.add_widget(Button(text="📢 Send Feedback"))
        layout.add_widget(Button(text="🚪 Sign Out", on_release=lambda x: setattr(self.manager, 'current', 'login')))

        popup = Popup(title="Menu", content=layout, size_hint=(0.7, 0.6))
        popup.open()

class StudentCalendarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()

        self.current_subject_key = None

        self.current_year = datetime.now().year
        self.current_month = datetime.now().month

        bg = Image(source='bg_app.jpg', allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(bg)

        # Header bar
        header_bar = BoxLayout(size_hint=(1, None), height=120, pos_hint={"top": 1})
        with header_bar.canvas.before:
            Color(0.6, 0.6, 0.6, 1)
            header_bar.bg_rect = Rectangle(size=header_bar.size, pos=header_bar.pos)
        header_bar.bind(
            size=lambda instance, value: setattr(header_bar.bg_rect, 'size', instance.size),
            pos=lambda instance, value: setattr(header_bar.bg_rect, 'pos', instance.pos)
        )
        self.layout.add_widget(header_bar)

        back_btn = ImageButton(
            source='back-button.png',
            size_hint=(None, None),
            size=(45, 45),
            pos_hint={"top": .99, "x": 0.01}
        )
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'student_home'))
        self.layout.add_widget(back_btn)
# Menu Icon
        menu_icon = ImageButton(
            source='menu.png',
            size_hint=(None, None),
            size=(45, 45),
            pos_hint={"top": .99, "right": .99}
        )
        menu_icon.bind(on_release=self.open_student_menu)
        self.layout.add_widget(menu_icon)

        # Logo
        self.layout.add_widget(Image(source='preskokooko-letter.png', size_hint=(None, None), size=(200, 200), pos_hint={"center_x": 0.5, "top": 1}))

        # Label
        student_label = Label(
            text="[b]STUDENT[/b]",
            markup=True,
            font_size='24sp',
            size_hint=(0.1, 0.08),
            pos_hint={"center_x": 0.5, "top": 0.88},
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle'
        )
        student_label.bind(size=student_label.setter('text_size'))
        with student_label.canvas.before:
            Color(0.5, 0.5, 0.5, 1)
            student_bg = Rectangle(size=student_label.size, pos=student_label.pos)
        student_label.bind(pos=lambda i, v: setattr(student_bg, 'pos', v),
                           size=lambda i, v: setattr(student_bg, 'size', v))
        self.layout.add_widget(student_label)

        # DateTime
        self.datetime_label = Label(text="", size_hint=(.2, .1), pos_hint={"top": 1, "center_x": 0.5}, font_size=18, color=(1, 1, 1, 1))
        Clock.schedule_interval(self.update_datetime, 1)
        self.layout.add_widget(self.datetime_label)

        # Month label
        self.month_label = Label(
            text=f"{calendar.month_name[self.current_month]} {self.current_year}",
            font_size=18,
            color=(0.5, 0, 0, 1),
            bold=True,
            size_hint=(0.6, 1),
            halign='center',
            valign='middle'
        )
        self.month_label.bind(size=lambda s, *a: setattr(s, 'text_size', s.size))

        # Navigation Buttons
        nav_buttons = BoxLayout(size_hint=(1, 0.08), spacing=10)
        prev_btn = Button(text="<", font_size=20, size_hint=(0.2, 1),
                          background_normal='', background_color=(0.2, 0.2, 0.2, 1), color=(1, 1, 1, 1))
        next_btn = Button(text=">", font_size=20, size_hint=(0.2, 1),
                          background_normal='', background_color=(0.2, 0.2, 0.2, 1), color=(1, 1, 1, 1))
        prev_btn.bind(on_release=self.go_to_prev_month)
        next_btn.bind(on_release=self.go_to_next_month)
        nav_buttons.add_widget(prev_btn)
        nav_buttons.add_widget(self.month_label)
        nav_buttons.add_widget(next_btn)

        # Calendar grid
        self.calendar_grid = GridLayout(cols=7, spacing=5, size_hint=(1, 0.65))

        self.show_qr_btn = Button(
            text="Scan QR Code",
            size_hint=(1, 0.1),
            background_color=(0.2, 0.5, 0.8, 1),
            color=(1, 1, 1, 1),
            disabled=True
        )
        self.show_qr_btn.bind(on_release=self.open_qr_scanner_popup)

        self.enter_code_btn = Button(
            text="Enter QR Code",
            size_hint=(1, 0.1),
            background_color=(0.2, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            disabled=True
        )
        self.enter_code_btn.bind(on_release=self.open_code_entry_popup)
        self.generate_calendar(self.current_year, self.current_month)
        # Rounded white card
        rounded_container = BigRoundedCard()
        rounded_container.add_widget(nav_buttons)
        rounded_container.add_widget(self.calendar_grid)
        rounded_container.add_widget(self.show_qr_btn)
        rounded_container.add_widget(self.enter_code_btn)
        self.layout.add_widget(rounded_container)
        self.add_widget(self.layout)
        

    def update_datetime(self, dt):
        now = datetime.now()
        self.datetime_label.text = now.strftime("%A, %B %d, %Y | %I:%M:%S %p")

    def go_to_prev_month(self, instance):
        self.current_month -= 1
        if self.current_month == 0:
            self.current_month = 12
            self.current_year -= 1
        self.month_label.text = f"{calendar.month_name[self.current_month]} {self.current_year}"
        self.generate_calendar(self.current_year, self.current_month)

    def go_to_next_month(self, instance):
        self.current_month += 1
        if self.current_month == 13:
            self.current_month = 1
            self.current_year += 1
        self.month_label.text = f"{calendar.month_name[self.current_month]} {self.current_year}"
        self.generate_calendar(self.current_year, self.current_month)

    def generate_calendar(self, year, month):
        green = (0.2, 0.8, 0.2, 1)  # Present
        red = (1, 0.2, 0.2, 1)      # Marked but not yet scanned
        white = (1, 1, 1, 0.8)

        self.calendar_grid.clear_widgets()
        calendar.setfirstweekday(calendar.SUNDAY)

        for day in ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]:
            self.calendar_grid.add_widget(Label(text=day, color=(0.5, 0, 0, 1), bold=True))

        month_days = calendar.monthcalendar(year, month)

        for week in month_days:
            for day in week:
                if day == 0:
                    self.calendar_grid.add_widget(Label(text=""))
                else:
                    date_str = f"{year}-{month:02d}-{day:02d}"
                    marked_dates = marked_dates_per_subject.get(self.current_subject_key, {})
                    attendance = attendance_status_per_subject.get(self.current_subject_key, {})
                    status = attendance.get(date_str, None)

                    if status == "present":
                        color = green
                    elif date_str in marked_dates:
                        color = red
                    else:
                        color = white 
                                             
                    btn = Button(
                        text=str(day),
                        background_normal='',
                        background_color=color,
                        color=(0, 0, 0, 1)
                    )
                    self.calendar_grid.add_widget(btn)
                    btn.bind(on_release=lambda instance, ds=date_str: self.on_date_selected(ds))

    def on_date_selected(self, date_str):
        self.selected_date = date_str
    # Enable buttons only if the date is marked and not yet present
        marked_dates = marked_dates_per_subject.get(self.current_subject_key, {})
        attendance = attendance_status_per_subject.get(self.current_subject_key, {})
        if date_str in marked_dates and attendance.get(date_str) != "present":
            self.show_qr_btn.disabled = False
            self.enter_code_btn.disabled = False
        else:
            self.show_qr_btn.disabled = True
            self.enter_code_btn.disabled = True

    def on_pre_enter(self):
        today = datetime.now()
        self.current_year = today.year
        self.current_month = today.month
        self.month_label.text = f"{calendar.month_name[self.current_month]} {self.current_year}"
        self.generate_calendar(self.current_year, self.current_month)

    def open_student_menu(self, instance):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        layout.add_widget(Label(text="👤 Profile: Student", color=(1, 1, 1, 1)))
        layout.add_widget(Button(text="🌙 Toggle Dark/Light"))
        layout.add_widget(Button(text="📢 Send Feedback"))
        layout.add_widget(Button(text="🚪 Sign Out", on_release=lambda x: setattr(self.manager, 'current', 'login')))

        popup = Popup(title="Menu", content=layout, size_hint=(0.7, 0.6))
        popup.open()

    def open_qr_scanner_popup(self, instance):
        if not self.selected_date:
            return

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        qr_path = f"qrcodes/{self.selected_date}.png"
        if not os.path.exists(qr_path):
            qr_path = "qrcodes/default.png"

    # QR image
        qr_image = KivyImage(source=qr_path, size_hint=(1, 0.7))
        layout.add_widget(qr_image)

    # Manual Code Label (NEW)
        subject_key = self.current_subject_key  # Match the same logic you use in `check_code()`
        key = f"{subject_key}_{self.selected_date}"
        manual_code = code_cache.get(key, "N/A")

        manual_label = Label(
            text=f"[b]Manual Code:[/b] {manual_code}",
            markup=True,
            font_size=16,
            size_hint=(1, 0.1),
            color=(1, 1, 1, 1)
        )
        layout.add_widget(manual_label)

    # Status Label
        status_label = Label(text="Scanning QR code...", size_hint=(1, 0.1), color=(1, 1, 1, 1))
        layout.add_widget(status_label)

        popup = Popup(title="QR Code & Validity Time", content=layout, size_hint=(0.8, 0.6))
        popup.open()

    # Simulate scanning using OpenCV
        def scan_qr_code_from_image(dt):
            img = cv2.imread(qr_path)
            detector = cv2.QRCodeDetector()
            data, bbox, _ = detector.detectAndDecode(img)
            expected = f"QR for {self.selected_date}"

            if data == expected:
                attendance_status_per_subject[subject_key][self.selected_date] = "present"
                status_label.text = "✅ You are marked present!"
                Clock.schedule_once(lambda dt: popup.dismiss(), 1.5)
                self.generate_calendar(self.current_year, self.current_month)
            else:
                status_label.text = "❌ Invalid QR Code"

        Clock.schedule_once(scan_qr_code_from_image, 0.5)

    def open_code_entry_popup(self, instance):
        if not self.selected_date:
            return

        content = BoxLayout(orientation='vertical', padding=20, spacing=10)

        code_input = TextInput(
            hint_text="Enter Code",
            multiline=False,
            font_size=18,
            size_hint_y=None,
            height=50
        )

    # ✅ Add Manual Code Label
        subject_key = self.current_subject_key
        key = f"{subject_key}_{self.selected_date}"
        manual_code = code_cache.get(key, "N/A")

        manual_label = Label(
            text=f"[b]Manual Code:[/b] {manual_code}",
            markup=True,
            font_size=16,
            size_hint_y=None,
            height=30,
            color=(1, 1, 1, 1)
        )

        status_label = Label(
            text="",
            font_size=16,
            size_hint_y=None,
            height=30,
            color=(1, 1, 1, 1)
        )

        submit_btn = Button(
            text="Submit",
            size_hint_y=None,
            height=50,
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1)
        )

        content.add_widget(manual_label)  # ✅ Add this above the code input
        content.add_widget(code_input)
        content.add_widget(status_label)
        content.add_widget(submit_btn)

        popup = Popup(title="Enter QR Code", content=content, size_hint=(0.8, 0.5))
        popup.open()

        def check_code(instance):
            expected_code = code_cache.get(key)
            validity = qr_expiry_cache.get(key)

            if expected_code and validity:
                now = datetime.now()
                start = datetime.strptime(validity["start"], "%Y-%m-%d %H:%M:%S")
                end = datetime.strptime(validity["end"], "%Y-%m-%d %H:%M:%S")

                if code_input.text.strip() == expected_code:
                    if start <= now <= end:
                        attendance_status_per_subject[subject_key][self.selected_date] = "present"
                        status_label.text = "✅ You are marked present!"
                        self.generate_calendar(self.current_year, self.current_month)
                        Clock.schedule_once(lambda dt: popup.dismiss(), 1.5)
                    else:
                        status_label.text = "⏰ Code expired."
                else:
                    status_label.text = "❌ Incorrect code."
            else:
                status_label.text = "❗ No QR generated for this date."

        submit_btn.bind(on_release=check_code)

class PreskoApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(StudentHomeScreen(name="student_home"))
        sm.add_widget(AddSubjectStudentScreen(name="add_subject_student"))
        sm.add_widget(StudentCalendarScreen(name="student_calendar"))
        return sm

if __name__ == '__main__':
    PreskoApp().run()