from kivy.core.window import Window
Window.fullscreen = 'auto'

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
import qrcode
import random
import string

def create_menu_icon(callback):
    return ImageButton(
        source="menu.png",
        size_hint=(None, None),
        size=(45, 45),  # Match the same as other screens
        pos_hint={"top": .99, "right": .99},
        on_release=callback
    )

valid_until = "2025-05-14 12:19:34"
current_time = datetime.now()

if current_time > datetime.strptime(valid_until, "%Y-%m-%d %H:%M:%S"):
    print("QR Code expired!")  # ⛔ BLOCK attendance
else:
    print("Valid QR")  # ✅ ALLOW attendance

qr_expiry_cache = {}

code_cache = {}

def generate_fixed_code(subject_key, date_str):
        key = f"{subject_key}_{date_str}"
        if key not in code_cache:
            code_cache[key] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return code_cache[key]
Window.clearcolor = (1, 1, 1, 1)

class ImageButton(ButtonBehavior, KivyImage):
    pass

class ProfessorHomeScreen(Screen):
    subject_data = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()

        background = Image(source='bg_app.jpg', allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(background)

        header_bar = BoxLayout(size_hint=(1, None), height=120, pos_hint={"top": 1})
        with header_bar.canvas.before:
            Color(0.6, 0.6, 0.6, 1)  # RGBA: dark semi-transparent maroon
            header_bar.bg_rect = Rectangle(size=header_bar.size, pos=header_bar.pos)

        def update_header_rect(instance, value):
            header_bar.bg_rect.size = instance.size
            header_bar.bg_rect.pos = instance.pos

        header_bar.bind(size=update_header_rect, pos=update_header_rect)
        self.layout.add_widget(header_bar)

        self.datetime_label = Label(text="", size_hint=(.2, .1), pos_hint={"top": 1, "center_x": 0.50}, font_size=18, color=(1,1,1,1))
        self.layout.add_widget(self.datetime_label)

        Clock.schedule_interval(self.update_datetime, 1)

        menu_icon = ImageButton(
            source="menu.png",
            size_hint=(None, None),
            size=(45, 45),              
            pos_hint={"top": .99, "right": .99}
        )

        menu_icon.bind(on_release=self.open_professor_menu)
        self.layout.add_widget(menu_icon)

        # Little white header bar above "PROFESSOR

        self.layout.add_widget(Image(source='preskokooko-letter.png', size_hint=(None, None), size=(200, 200), pos_hint={"center_x": 0.5, "top": 1}))
        
        professor_label = Label(
            text="[b]PROFESSOR[/b]",
            markup=True,
            font_size='24sp',
            size_hint=(0.1, 0.08),
            pos_hint={"center_x": 0.5, "top": 0.88},
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle'
        )
        professor_label.bind(size=professor_label.setter('text_size'))

        with professor_label.canvas.before:
            Color(0.5, 0.5, 0.5, 1)  # white
            professor_bg = Rectangle(size=professor_label.size, pos=professor_label.pos)

        professor_label.bind(pos=lambda instance, value: setattr(professor_bg, 'pos', value))
        professor_label.bind(size=lambda instance, value: setattr(professor_bg, 'size', value))

        self.layout.add_widget(professor_label)

        self.subject_box = BoxLayout(orientation='vertical', spacing=10, size_hint=(.9, .5), pos_hint={"center_x": 0.5, "top": 0.68})
        self.layout.add_widget(self.subject_box)

        add_btn = Button(
            background_normal='plus_sign.png',  # your circular + image
            background_down='plus_sign.png',
            size_hint=(None, None),
            size=(50, 50),
            pos_hint={"center_x": 0.5, "y": 0.02},
            border=(0, 0, 0, 0)
        )
        add_btn.bind(on_release=self.go_to_add_subject)
        self.layout.add_widget(add_btn)

        self.add_widget(self.layout)
        self.update_subject_cards()

    def go_to_add_subject(self, instance):
        self.manager.current = "add_subject"

    def on_subject_data(self, instance, value):
        self.update_subject_cards()

    def go_to_calendar(self, subject_info):
        calendar_screen = self.manager.get_screen("calendar")
        calendar_screen.subject_info = subject_info
        self.manager.current = "calendar"

    def update_datetime(self, dt):
        now = datetime.now()
        self.datetime_label.text = now.strftime("%A, %B %d, %Y | %I:%M:%S %p")

    def update_subject_cards(self):
        self.subject_box.clear_widgets()

        for data in self.subject_data[-7:]:
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
            card.bind(on_release=lambda btn, d=data: self.go_to_calendar(d))
            card.bind(size=lambda instance, value: setattr(instance, 'text_size', (instance.width - 40, None)))
            self.subject_box.add_widget(card)

        for _ in range(7 - len(self.subject_data)):
            self.subject_box.add_widget(Button(
                background_normal='',
                background_color=(1, 1, 1, 0.3),
                size_hint_y=None,
                height=80
            ))

    def open_professor_menu(self, instance):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        layout.add_widget(Label(text="👤 Profile: Professor 003", color=(1,1,1,1)))
        layout.add_widget(Button(text="🌙 Toggle Dark/Light"))
        layout.add_widget(Button(text="📢 Send Feedback"))
        layout.add_widget(Button(text="🚪 Sign Out", on_release=lambda x: self.manager.current == "login"))

        popup = Popup(title="Menu", content=layout, size_hint=(0.7, 0.6))
        popup.open()

#  ADD SUBJECT SCREEN
class AddSubjectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()

        background = Image(source='bg_app.jpg', allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(background)

        header_bar = BoxLayout(size_hint=(1, None), height=120, pos_hint={"top": 1})
        with header_bar.canvas.before:
            Color(0.6, 0.6, 0.6, 1)  # Light gray
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
        back_btn.bind(on_release=self.go_back)
        self.layout.add_widget(back_btn)  # ✅ Add to FloatLayout

        menu_icon = ImageButton(
            source="menu.png",
            size_hint=(None, None),
            size=(45, 45),
            pos_hint={"top": .99, "right": .99}
        )
        menu_icon.bind(on_release=self.open_professor_menu)
        self.layout.add_widget(menu_icon)

        self.layout.add_widget(Image(source='preskokooko-letter.png',size_hint=(None, None),size=(200, 200), pos_hint={"center_x": 0.5, "top": 1}))

        professor_label = Label(
            text="[b]PROFESSOR[/b]",
            markup=True,
            font_size='24sp',
            size_hint=(0.1, 0.08),
            pos_hint={"center_x": 0.5, "top": 0.88},
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle'
        )
        professor_label.bind(size=professor_label.setter('text_size'))

        with professor_label.canvas.before:
            Color(0.5, 0.5, 0.5, 1)  # white
            professor_bg = Rectangle(size=professor_label.size, pos=professor_label.pos)

        professor_label.bind(pos=lambda instance, value: setattr(professor_bg, 'pos', value))
        professor_label.bind(size=lambda instance, value: setattr(professor_bg, 'size', value))

        self.layout.add_widget(professor_label)

        self.datetime_label = Label(text="",size_hint=(.2, .1),pos_hint={"top": 1, "center_x": 0.5},font_size=18,color=(1, 1, 1, 1))
        self.layout.add_widget(self.datetime_label)
        Clock.schedule_interval(self.update_datetime, 1)

        form = BoxLayout(
            orientation='vertical',
            spacing=15,
            padding=[50, 10, 50, 150],  # [left, top, right, bottom]
            size_hint=(None, None),
            size=(750, 750),
            pos_hint={"center_x": 0.5, "center_y": 0.75}
        )

        self.inputs = {
            'Subject Code': TextInput(hint_text='Insert Subject Code:', font_size=18, size_hint=(1, None), height=45),
            'Subject Name': TextInput(hint_text='Insert Subject Name:', font_size=18, size_hint=(1, None), height=45),
            'Professor Name': TextInput(hint_text="Professor's Name:", font_size=18, size_hint=(1, None), height=45),
            'Schedule': TextInput(hint_text='Time & Day Schedule:', font_size=18, size_hint=(1, None), height=45),
            'Section': TextInput(hint_text='Course, Year & Section:', font_size=18, size_hint=(1, None), height=45)
        }

        for field in self.inputs.values():
            form.add_widget(field)

        submit_btn = Button(
            text='Submit',
            font_size=18,
            size_hint=(1, None),
            height=45,
            background_normal='',
            background_color=(0.2, 0.2, 0.2, 1),  # dark gray
            color=(1, 1, 1, 1)  # white text
        )
        submit_btn.bind(on_release=self.submit)
        form.add_widget(submit_btn)

        form_container = BigRoundedCard()
        form_container.add_widget(form)
        self.layout.add_widget(form_container)
        self.add_widget(self.layout)

        self.text_inputs = list(self.inputs.values())
        for field in self.text_inputs:
            field.multiline = False
            field.bind(on_text_validate=self.focus_next_field)
            Window.bind(on_key_down=self.override_keyboard)

    def submit(self, instance):
        values = [i.text.strip() for i in self.inputs.values()]
        if all(values):
            home = self.manager.get_screen("professor_home")
            home.subject_data.append(values)
            home.update_subject_cards()
            self.manager.current = "professor_home"
            for field in self.inputs.values():
                field.text = ""

    def go_back(self, instance):
        self.manager.current = "professor_home"

    def on_pre_enter(self):
        for field in self.inputs.values():
            field.text = ""

    def focus_next_field(self, instance):
        index = self.text_inputs.index(instance)
        if index + 1 < len(self.text_inputs):
            self.text_inputs[index + 1].focus = True

    def override_keyboard(self, window, keycode, scancode, codepoint, modifiers):
        if keycode == 9:  # Tab key
            focused = [field for field in self.text_inputs if field.focus]
            if focused:
                self.focus_next_field(focused[0])
            return True
        return False
    
    def update_datetime(self, dt):
        now = datetime.now()
        self.datetime_label.text = now.strftime("%A, %B %d, %Y | %I:%M:%S %p")

    def open_professor_menu(self, instance):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        layout.add_widget(Label(text="👤 Profile: Professor 003", color=(1,1,1,1)))
        layout.add_widget(Button(text="🌙 Toggle Dark/Light"))
        layout.add_widget(Button(text="📢 Send Feedback"))
        layout.add_widget(Button(text="🚪 Sign Out", on_release=lambda x: self.manager.current == "login"))

        popup = Popup(title="Menu", content=layout, size_hint=(0.7, 0.6))
        popup.open()

class BigRoundedCard(BoxLayout):  # ⬅️ Put it here
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
    
    def update_bg(self, *args):  # 👈 THIS must be included
        self.bg.pos = self.pos
        self.bg.size = self.size

#CALENDAR SCREEN
class CalendarScreen(Screen):
    subject_info = ListProperty([])
    marked_dates_per_subject = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()

        self.current_year = datetime.now().year
        self.current_month = datetime.now().month

        bg = Image(source='bg_app.jpg', allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(bg)

        # Gray header bar
        header_bar = BoxLayout(size_hint=(1, None), height=120, pos_hint={"top": 1})
        with header_bar.canvas.before:
            Color(0.6, 0.6, 0.6, 1)
            header_bar.bg_rect = Rectangle(size=header_bar.size, pos=header_bar.pos)

        header_bar.bind(
        size=lambda instance, value: setattr(header_bar.bg_rect, 'size', instance.size),
        pos=lambda instance, value: setattr(header_bar.bg_rect, 'pos', instance.pos)
        )
        self.layout.add_widget(header_bar)

        menu_icon = create_menu_icon(self.open_professor_menu)
        self.layout.add_widget(menu_icon)

        self.month_label = Label(
        text=f"{calendar.month_name[self.current_month]} {self.current_year}",font_size=18,color=(0.5, 0, 0, 1), bold=True,size_hint=(0.6, 1),halign='center',valign='middle')
        self.month_label.bind(size=lambda s, *a: setattr(s, 'text_size', s.size))

        nav_buttons = BoxLayout(size_hint=(1, 0.08), spacing=10)
        prev_btn = Button(
            text="<",
            font_size=20,
            size_hint=(0.2, 1),
            background_normal='',
            background_color=(0.2, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        next_btn = Button(
            text=">",
            font_size=20,
            size_hint=(0.2, 1),
            background_normal='',
            background_color=(0.2, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        prev_btn.bind(on_release=self.go_to_prev_month)
        next_btn.bind(on_release=self.go_to_next_month)
        nav_buttons.add_widget(prev_btn)
        nav_buttons.add_widget(self.month_label)
        nav_buttons.add_widget(next_btn)

        self.calendar_grid = GridLayout(cols=7, spacing=5, size_hint=(1, 0.65))
        self.generate_qr_btn = Button(
            text="Generate QR Code",
            size_hint=(1, 0.1),
            background_color=(0.7, 0.7, 0.7, 1),
            disabled=True
        )
        self.generate_qr_btn.bind(on_release=self.show_or_generate_qr)
        self.view_attendance_btn = Button(
            text="View Attendance List",
            size_hint=(1, 0.1),
            background_color=(0.7, 0.7, 0.7, 1),
            disabled=True
        )
        self.view_attendance_btn.bind(on_release=self.view_attendance_for_selected)

        back_btn = ImageButton(
            source='back-button.png',
            size_hint=(None, None),
            size=(45, 45),
            pos_hint={"top": .99, "x": 0.01}
        )
        back_btn.bind(on_release=self.go_back)
        self.layout.add_widget(back_btn)

    # ✅ Now safe to add all widgets
        rounded_container = BigRoundedCard()
        rounded_container.add_widget(nav_buttons)
        rounded_container.add_widget(self.calendar_grid)
        rounded_container.add_widget(self.generate_qr_btn)
        rounded_container.add_widget(self.view_attendance_btn)
        self.layout.add_widget(rounded_container)

        self.layout.add_widget(Image(source='preskokooko-letter.png',size_hint=(None, None),size=(200, 200), pos_hint={"center_x": 0.5, "top": 1}))

        professor_label = Label(
            text="[b]PROFESSOR[/b]",
            markup=True,
            font_size='24sp',
            size_hint=(0.1, 0.08),
            pos_hint={"center_x": 0.5, "top": 0.88},
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle'
        )
        professor_label.bind(size=professor_label.setter('text_size'))

        with professor_label.canvas.before:
            Color(0.5, 0.5, 0.5, 1)  # white
            professor_bg = Rectangle(size=professor_label.size, pos=professor_label.pos)

        professor_label.bind(pos=lambda instance, value: setattr(professor_bg, 'pos', value))
        professor_label.bind(size=lambda instance, value: setattr(professor_bg, 'size', value))

        self.layout.add_widget(professor_label)

        self.datetime_label = Label(text="",size_hint=(.2, .1),pos_hint={"top": 1, "center_x": 0.5},font_size=18,color=(1, 1, 1, 1))
        self.layout.add_widget(self.datetime_label)
        Clock.schedule_interval(self.update_datetime, 1)
        self.add_widget(self.layout)
        self.selected_day = None

    def on_subject_info(self, instance, value):
        if value:
            self.current_subject_key = f"{value[0]}_{value[1]}"
            self.month_label.text = f"{self.subject_info[1]}  –  {calendar.month_name[self.current_month]} {self.current_year}"
            if self.current_subject_key not in self.marked_dates_per_subject:
                self.marked_dates_per_subject[self.current_subject_key] = set()
            self.generate_calendar(self.current_year, self.current_month)

    def go_back(self, instance):
        self.manager.current = "professor_home"

    def generate_calendar(self, year, month):
        self.calendar_grid.clear_widgets()
        self.selected_day_btn = None
        calendar.setfirstweekday(calendar.SUNDAY)
        for day in ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]:
            self.calendar_grid.add_widget(Label(text=day, color=(0.5, 0, 0, 1), bold=True))

        self.selected_day = None
        self.generate_qr_btn.disabled = True

        self.generate_qr_btn.background_color = (1, 1, 1, 1)
        self.view_attendance_btn.disabled = True

        self.view_attendance_btn.background_color = (1, 1, 1, 1)
        month_days = calendar.monthcalendar(year, month)
        marked_dates = self.marked_dates_per_subject.get(self.current_subject_key, set())

        for week in month_days:
            for day in week:
                if day == 0:
                    self.calendar_grid.add_widget(Label(text=""))
                else:
                    date_str = datetime(year, month, day).strftime("%Y-%m-%d")
                    is_marked = date_str in marked_dates
                    btn = Button(
                    text=str(day),
                    background_normal='',
                    background_color=(0.2, 0.8, 0.2, 1) if is_marked else (1, 1, 1, 0.8),
                    color=(0, 0, 0, 1)
                    )
                    btn.bind(on_release=lambda btn_instance, d=day, b=btn: self.select_day(d, b))
                    self.calendar_grid.add_widget(btn)

    def select_day(self, day, btn):
        if self.selected_day_btn and self.selected_day is not None:
            previous_date = datetime(self.current_year, self.current_month, self.selected_day).strftime("%Y-%m-%d")
            if previous_date in self.marked_dates_per_subject.get(self.current_subject_key, set()):
                self.selected_day_btn.background_color = (0.2, 0.8, 0.2, 1)  # Green
            else:
                self.selected_day_btn.background_color = (1, 1, 1, 0.8)  # Default

        self.selected_day = day
        self.selected_day_btn = btn

        date_str = datetime(self.current_year, self.current_month, self.selected_day).strftime("%Y-%m-%d")
        if date_str in self.marked_dates_per_subject.get(self.current_subject_key, set()):
            btn.background_color = (0.2, 0.8, 0.2, 1)
            self.generate_qr_btn.text = "Show QR Code"
        else:
            btn.background_color = (1, 0, 0, 1)
            self.generate_qr_btn.text = "Generate QR Code"

        self.generate_qr_btn.disabled = False
        self.view_attendance_btn.disabled = False
        self.generate_qr_btn.background_color = (0.1, 0.5, 0.9, 1)
        self.view_attendance_btn.background_color = (0.1, 0.5, 0.9, 1)

    def show_or_generate_qr(self, instance):
        if self.selected_day is None:
            return

        selected_date = datetime(self.current_year, self.current_month, self.selected_day).strftime("%Y-%m-%d")
        subject_key = self.current_subject_key
        key = f"{subject_key}_{selected_date}"

    # Check if QR already exists
        if key in qr_expiry_cache:
        # ✅ Just show existing QR
            self.show_final_qr(selected_date)
        else:
        # ❓ Ask for start & end time first
            self.generate_qr_popup(selected_date)

    def generate_qr_popup(self, date_str):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        start_input = TextInput(hint_text="Start Time (HH:MM, 24hr)", multiline=False)
        end_input = TextInput(hint_text="End Time (HH:MM, 24hr)", multiline=False)

        submit_btn = Button(text="Generate QR", size_hint=(1, 0.2))
        cancel_btn = Button(text="Cancel", size_hint=(1, 0.2))

        layout.add_widget(start_input)
        layout.add_widget(end_input)
        layout.add_widget(submit_btn)
        layout.add_widget(cancel_btn)

        popup = Popup(title="Set QR Validity Time", content=layout, size_hint=(0.8, 0.6))
        popup.open()

        def on_submit(instance):
            try:
                start_time = datetime.strptime(start_input.text.strip(), "%H:%M").time()
                end_time = datetime.strptime(end_input.text.strip(), "%H:%M").time()

                now = datetime.now().replace(second=0, microsecond=0)
                start_dt = datetime.combine(now.date(), start_time)
                end_dt = datetime.combine(now.date(), end_time)

                if end_dt <= start_dt:
                    raise ValueError("End time must be after start time.")

                key = f"{self.current_subject_key}_{date_str}"
                qr_expiry_cache[key] = {
                    "start": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "end": end_dt.strftime("%Y-%m-%d %H:%M:%S")
                }

        # ✅ Mark the date AFTER successful QR time entry
                self.marked_dates_per_subject.setdefault(self.current_subject_key, set()).add(date_str)

        # ✅ Turn the selected day button green AFTER marking
                if self.selected_day_btn:
                    self.selected_day_btn.background_color = (0.2, 0.8, 0.2, 1)

                popup.dismiss()
                self.show_final_qr(date_str)
                self.generate_calendar(self.current_year, self.current_month)  # update color

            except ValueError:
                start_input.text = ""
                end_input.text = ""
                start_input.hint_text = "❗ Invalid time format"
                end_input.hint_text = "Use HH:MM (24hr)"

        submit_btn.bind(on_release=on_submit)
        cancel_btn.bind(on_release=popup.dismiss)

    def view_attendance_for_selected(self, instance):
        if self.selected_day is None:
            return

        date_str = datetime(datetime.now().year, datetime.now().month, self.selected_day).strftime("%Y-%m-%d")
        subject_key = self.current_subject_key
        record_key = f"{subject_key}_{date_str}"

    # ✅ Check if QR was generated for this date
        if date_str not in self.marked_dates_per_subject.get(subject_key, set()):
            popup = Popup(
                title="No Attendance",
                content=Label(text="No QR was generated for this date.", color=(1,1,1,1)),
                size_hint=(0.7, 0.4)
            )
            popup.open()
            return

    # Dummy student data (to be replaced later)
        students = {
            f"{subject_key}_{date_str}": ["Angel Hernandez", "Ryan Cruz", "Jane Doe"]
        }.get(record_key, [])

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

    # Header Row
        header = GridLayout(cols=3, size_hint_y=None, height=40)
        header.add_widget(Label(text='[b]Name[/b]', markup=True, color=(1, 1, 1, 1)))
        header.add_widget(Label(text='[b]Present[/b]', markup=True, color=(1, 1, 1, 1)))
        header.add_widget(Label(text='[b]Absent[/b]', markup=True, color=(1, 1, 1, 1)))
        layout.add_widget(header)

        scroll = ScrollView(size_hint=(1, 0.8))
        grid = GridLayout(cols=3, spacing=5, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        if students:
            for student in students:
                grid.add_widget(Label(text=student, size_hint_y=None, height=30, color=(1, 1, 1, 1)))
                grid.add_widget(Label(text='✔️', size_hint_y=None, height=30))
                grid.add_widget(Label(text='❌', size_hint_y=None, height=30))
        else:
            grid.add_widget(Label(text="No attendance found.", color=(1, 1, 1, 1), size_hint_y=None, height=30))

        scroll.add_widget(grid)
        layout.add_widget(scroll)

        close_btn = Button(text="Close", size_hint=(1, 0.15))
        layout.add_widget(close_btn)

        popup = Popup(title=f"Attendance – {date_str}", content=layout, size_hint=(0.9, 0.9))
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    # Disable buttons again after viewing
        self.selected_day = None
        self.generate_qr_btn.disabled = True
        self.generate_qr_btn.background_color = (0.7, 0.7, 0.7, 1)
        self.view_attendance_btn.disabled = True
        self.view_attendance_btn.background_color = (0.7, 0.7, 0.7, 1)
 
    def go_back(self, instance):
        self.selected_day = None  # Reset selection
        self.generate_qr_btn.disabled = True
        self.generate_qr_btn.background_color = (0.7, 0.7, 0.7, 1)

        self.view_attendance_btn.disabled = True
        self.view_attendance_btn.background_color = (0.7, 0.7, 0.7, 1)

        self.manager.current = "professor_home"

    def go_to_prev_month(self, instance):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1

        self.month_label.text = f"{calendar.month_name[self.current_month]} {self.current_year}"

        self.generate_calendar(self.current_year, self.current_month)

    def go_to_next_month(self, instance):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1

        self.month_label.text = f"{calendar.month_name[self.current_month]} {self.current_year}"

        self.generate_calendar(self.current_year, self.current_month)

    def on_pre_enter(self):
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.selected_day = None  # Reset selected day
        self.month_label.text = f"{calendar.month_name[self.current_month]} {self.current_year}"

        self.generate_calendar(self.current_year, self.current_month)

    def show_final_qr(self, date_str):
        key = f"{self.current_subject_key}_{date_str}"
        validity = qr_expiry_cache.get(key, {})
        start_time = validity.get("start", "N/A")
        end_time = validity.get("end", "N/A")

        manual_code = generate_fixed_code(self.current_subject_key, date_str)

        qr_content = (
            f"Subject: {self.subject_info[1]}\n"
            f"Date: {date_str}\n"
            f"Valid From: {start_time}\n"
            f"Valid Until: {end_time}\n"
            f"Manual Code: {manual_code}"
        )

        qr = qrcode.make(qr_content)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        buffer.seek(0)
        qr_texture = CoreImage(buffer, ext='png').texture

        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        qr_image = KivyImage(texture=qr_texture)
        popup_layout.add_widget(qr_image)

        popup_layout.add_widget(Label(text=f"[b]Manual Code:[/b] {manual_code}", markup=True, color=(1, 1, 1, 1)))

        close_btn = Button(text="Close", size_hint=(1, 0.2))
        popup_layout.add_widget(close_btn)

        popup = Popup(title="QR Code & Validity Time", content=popup_layout, size_hint=(0.8, 0.9))
        close_btn.bind(on_release=popup.dismiss)
        popup.open()
    
    def update_datetime(self, dt):
        now = datetime.now()
        self.datetime_label.text = now.strftime("%A, %B %d, %Y | %I:%M:%S %p")

    def open_professor_menu(self, instance):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        layout.add_widget(Label(text="👤 Profile: Professor 003", color=(1,1,1,1)))
        layout.add_widget(Button(text="🌙 Toggle Dark/Light"))
        layout.add_widget(Button(text="📢 Send Feedback"))
        layout.add_widget(Button(text="🚪 Sign Out", on_release=lambda x: self.manager.current == "login"))

        popup = Popup(title="Menu", content=layout, size_hint=(0.7, 0.6))
        popup.open()

class PreskoApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(ProfessorHomeScreen(name="professor_home"))
        sm.add_widget(AddSubjectScreen(name="add_subject"))
        sm.add_widget(CalendarScreen(name="calendar"))
        return sm

if __name__ == "__main__":
    PreskoApp().run()