from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.window import Window
from kivy.utils import platform
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
import calendar
from datetime import datetime
from threading import Thread
from pyzbar.pyzbar import decode

import cv2

Window.fullscreen = 'auto'

class ClickableImage(ButtonBehavior, Image):
    pass

class RoundedCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

class BigRoundedCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = [30, 30, 30, 30]
        self.spacing = 20
        self.size_hint = (None, None)
        self.size = (900, 650)
        self.pos_hint = {"center_x": 0.5, "center_y": 0.43}
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg = RoundedRectangle(radius=[30], pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)
    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

class MaroonBar(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = 38
        with self.canvas.before:
            Color(0.5, 0, 0, 1)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)
    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        self.add_widget(layout)

        background = Image(source='bg_app.jpg', allow_stretch=True, keep_ratio=False)
        layout.add_widget(background)

        header_bar = BoxLayout(size_hint=(1, None), height=120, pos_hint={"top": 1})
        with header_bar.canvas.before:
            Color(0.6, 0.6, 0.6, 1)  # Light gray like professor tab
            header_bar.bg_rect = Rectangle(size=header_bar.size, pos=header_bar.pos)

        header_bar.bind(
        size=lambda instance, value: setattr(header_bar.bg_rect, 'size', instance.size),
        pos=lambda instance, value: setattr(header_bar.bg_rect, 'pos', instance.pos)
        )
        layout.add_widget(header_bar)

        self.date_time_label = Label(text="[b]DATE | TIME[/b]", markup=True,
                                font_size='12sp', color=(1, 1, 1, 1), halign='center',
                                valign='middle', size_hint=(1, 1))
        self.date_time_label.bind(size=self.date_time_label.setter('text_size'))
        header_bar.add_widget(self.date_time_label)

        menu_btn = ClickableImage(
            source="menu.png",
            size_hint=(None, None),
            size=(40, 40),
        )
        
        menu_btn.bind(on_press=lambda x: print("Menu Button Pressed!"))
        header_bar.add_widget(menu_btn)

        layout.add_widget(Image(source='PUP Logo.png',size_hint=(None, None), size=(24, 24),pos_hint={"center_x": 0.5, "top": 0.94}))
        
        layout.add_widget(Image(source='preskokooko-letter.png',size_hint=(None, None), size=(150, 150),pos_hint={"center_x": 0.50, "top": 0.97}))

        student_label = Label(text="[b]STUDENT[/b]",
                              markup=True,
                              size_hint=(.4, .06),
                              pos_hint={"center_x": 0.50, "top": 0.80},
                              color=(1, 0, 0, 1),
                              font_size='16sp',
                              halign='center',
                              valign='middle')
        student_label.bind(size=student_label.setter('text_size'))
        with student_label.canvas.before:
            Color(1, 1, 1, 1)
            student_bg = Rectangle(size=student_label.size, pos=student_label.pos)
        student_label.bind(pos=lambda instance, value: setattr(student_bg, 'pos', value))
        student_label.bind(size=lambda instance, value: setattr(student_bg, 'size', value))
        layout.add_widget(student_label)

        self.subject_data = [
            ("COMP 003", "Computer Programming", "Prof. Brian De Vivar"),
        ]

        self.subject_box = BoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint=(.9, .35),
            pos_hint={"x": 0.05, "top": 0.6}
        )
        layout.add_widget(self.subject_box)
        self.update_subject_cards()

        qr_btn = ClickableImage(source="qr-black.png", size_hint=(None, None),
                                size=(64, 64), pos_hint={"center_x": 0.5, "y": 0.02})
        qr_btn.bind(on_press=self.on_qr_press)
        layout.add_widget(qr_btn)

        Clock.schedule_interval(self.update_datetime, 1)

    def update_subject_cards(self):
        self.subject_box.clear_widgets()
        for data in self.subject_data:
            card = RoundedCard(size_hint_y=None, height=100)

            hbox = BoxLayout(
                orientation='horizontal',
                spacing=10,
                size_hint_y=None,
                height=92
            )

            subject_img = Image(
                source='compbg.png',
                size_hint=(None, None),
                size=(70, 70),
                allow_stretch=True,
                keep_ratio=True,
                pos_hint={'center_y': 0.5}
            )
            hbox.add_widget(subject_img)

            vbox = BoxLayout(orientation='vertical', spacing=3, padding=[0, 8, 0, 8])

            code_label = Label(
                text=f"[b]{data[0]}[/b]",
                markup=True,
                halign="left",
                valign="middle",
                color=(0.5, 0, 0, 1),
                font_size=20,
                size_hint_y=None,
                height=28
            )
            code_label.bind(size=code_label.setter('text_size'))
            vbox.add_widget(code_label)

            class LineWidget(BoxLayout):
                def __init__(self, **kwargs):
                    super().__init__(**kwargs)
                    with self.canvas:
                        Color(0.5, 0, 0, 1)
                        self.line = Rectangle(size=(0, 2), pos=self.pos)
                    self.bind(pos=self.update_line, size=self.update_line)
                def update_line(self, *args):
                    self.line.pos = self.pos
                    self.line.size = (self.width, 2)
            vbox.add_widget(LineWidget(size_hint_y=None, height=3))

            info_label = Label(
                text=f"{data[1]}\n{data[2]}",
                halign="left",
                valign="middle",
                color=(0, 0, 0, 1),
                font_size=15,
                padding=(0, 0)
            )
            info_label.bind(size=info_label.setter('text_size'))
            vbox.add_widget(info_label)

            hbox.add_widget(vbox)
            card.add_widget(hbox)
            card.bind(on_touch_down=lambda instance, touch: self.go_to_calendar() if card.collide_point(*touch.pos) else None)
            self.subject_box.add_widget(card)

        for _ in range(3 - len(self.subject_data)):
            empty_card = RoundedCard(size_hint_y=None, height=100)
            self.subject_box.add_widget(empty_card)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def on_qr_press(self, instance):
        self.manager.transition.direction = 'left'
        self.manager.current = 'qr'

    def go_to_calendar(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'calendar'

    def update_datetime(self, dt):
        now = datetime.now()
        self.date_time_label.text = now.strftime("[b]%A, %B %d, %Y | %I:%M:%S %p[/b]")

class QRScannerWidget(FloatLayout):
    def __init__(self, **kwargs):
        super(QRScannerWidget, self).__init__(**kwargs)

        self.loading_label = Label(
            text="Loading camera...",
            font_size='16sp',
            color=(0.5, 0, 0, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.75}
        )
        self.add_widget(self.loading_label)

        self.camera_index = 0
        self.capture = None
        self.camera_event = None

        self.bg_container = FloatLayout(
            size_hint=(0.65, 0.55),
            pos_hint={"center_x": 0.5, "center_y": 0.55}
        )
        with self.bg_container.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle()
        self.bg_container.bind(size=self.update_bg_rect, pos=self.update_bg_rect)

        self.image = Image(size_hint=(0.95, 0.65), pos_hint={"center_x": 0.5, "top": 1})
        self.bg_container.add_widget(self.image)

        scan_button = Button(
            text="SCAN QR CODE",
            size_hint=(0.7, 0.18),
            pos_hint={"center_x": 0.5, "y": 0.05},
            background_color=(0.6, 0.6, 0.6, 1),
            color=(1, 1, 1, 1)
        )
        self.bg_container.add_widget(scan_button)

        self.add_widget(self.bg_container)

        enter_button = Button(
            text="ENTER CODE",
            size_hint=(0.4, 0.08),
            pos_hint={"center_x": 0.5, "center_y": 0.22},
            background_color=(0.6, 0.6, 0.6, 1)
        )
        enter_button.bind(on_press=self.go_to_entercode)
        self.add_widget(enter_button)

        flip_button = Button(
            text="FLIP CAMERA",
            size_hint=(0.4, 0.08),
            pos_hint={"center_x": 0.5, "center_y": 0.14},
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        flip_button.bind(on_press=self.flip_camera)
        self.add_widget(flip_button)


    def update_bg_rect(self, *args):
        self.bg_rect.pos = self.bg_container.pos
        self.bg_rect.size = self.bg_container.size

    def update_camera(self, dt):
        ret, frame = self.capture.read()
        if not ret:
            return  # Skip update if no frame yet

    # Remove loading label if it exists
        if hasattr(self, 'loading_label') and self.loading_label:
            self.remove_widget(self.loading_label)
            self.loading_label = None

    # Flip and render
        frame = cv2.flip(frame, 0)
        buf = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
        texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
        self.image.texture = texture


    def on_stop(self):
        if hasattr(self, 'camera_event'):
            Clock.unschedule(self.camera_event)
            self.camera_event = None

        if hasattr(self, 'capture') and self.capture and self.capture.isOpened():
            self.capture.release()
            self.capture = None

    def flip_camera(self, instance):
        if self.capture:
            self.capture.release()
            self.capture = None
            if self.camera_event:
                Clock.unschedule(self.camera_event)

        self.camera_index = 1 - self.camera_index  # toggle
        Clock.schedule_once(self._start_new_camera, 1.0)  # wait 1 second before starting

    def go_to_entercode(self, instance):
        app = App.get_running_app()
        app.root.current = 'entercode'

class QRScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        self.add_widget(layout)

        layout.add_widget(Image(source="bg_app.jpg",allow_stretch=True,keep_ratio=False,size_hint=(1, 1),pos_hint={"x": 0, "y": 0}))

        header = BoxLayout(size_hint=(1, None), height=120, pos_hint={"top": 1})
        with header.canvas.before:
            Color(0.6, 0.6, 0.6, 1)
            header.bg_rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(
            size=lambda instance, value: setattr(header.bg_rect, 'size', instance.size),
            pos=lambda instance, value: setattr(header.bg_rect, 'pos', instance.pos)
        )

        back_btn_container = RelativeLayout(size_hint=(None, None), size=(50, 50))
        with back_btn_container.canvas.before:
            Color(0.5, 0, 0, 1)
            RoundedRectangle(pos=back_btn_container.pos, size=back_btn_container.size, radius=[25])
        back_btn_container.bind(pos=lambda instance, value: setattr(instance.children[0], 'pos', value))
        back_btn_container.bind(size=lambda instance, value: setattr(instance.children[0], 'size', value))

        back_btn = ClickableImage(
            source="back-button.png",
            size_hint=(None, None),
            size=(50, 50),
            pos_hint={"top": 2, "right": 2},
        )
        back_btn.bind(on_press=self.animate_back_to_home)
        back_btn_container.add_widget(back_btn)
        header.add_widget(back_btn_container)

        header.add_widget(Label(size_hint_x=None, width=40))

        self.date_time_label = Label(
            text=self.get_current_time(),
            markup=True,
            font_size='12sp', color=(1, 1, 1, 1),
            halign='center', valign='middle', size_hint=(1, 1)
        )

        self.date_time_label.bind(size=self.date_time_label.setter('text_size'))
        header.add_widget(self.date_time_label)

        menu_btn = ClickableImage(
            source="menu.png",
            size_hint=(None, None),
            size=(40, 40),
        )
        menu_btn.bind(on_press=lambda x: print("Menu Button Pressed!"))
        header.add_widget(menu_btn)

        layout.add_widget(header)


        self.scanner = QRScannerWidget()
        layout.add_widget(self.scanner)

        top_logo = Image(
            source="PUP Logo.png",
            size_hint=(None, None),
            size=(24, 24),
            pos_hint={"center_x": 0.5, "top": 0.91}
        )
        layout.add_widget(top_logo)

        logo = Image(source="preskokooko-letter.png",
                     size_hint=(None, None),
                     size=(150, 150),
                     pos_hint={"center_x": 0.5, "top": 0.95})
        layout.add_widget(logo)

        Clock.schedule_interval(self.update_datetime, 1)

    def get_current_time(self):
        return datetime.now().strftime("[b]%A, %B %d, %Y | %I:%M:%S %p[/b]")

    def on_enter(self):
        def start_camera():
            self.scanner.capture = cv2.VideoCapture(0)
            if self.scanner.capture.isOpened():
                Clock.schedule_once(lambda dt: self.start_camera_loop(), 0)
            else:
                Clock.schedule_once(lambda dt: self.show_camera_error(), 0)

        Thread(target=start_camera).start()

    def start_camera_loop(self):
        self.scanner.camera_event = Clock.schedule_interval(self.scanner.update_camera, 1.0 / 30)

    def show_camera_error(self):
        self.scanner.image.source = ''
        error_label = Label(
            text="Unable to access camera",
            pos_hint={"center_x": 0.5, "center_y": 0.65},
            color=(1, 1, 1, 1)
        )
        self.scanner.bg_container.add_widget(error_label)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def update_datetime(self, dt):
        self.date_time_label.text = self.get_current_time()


    def on_leave(self):
        self.scanner.on_stop()

    def animate_back_to_home(self, instance):
        sm = self.manager
        sm.transition.direction = 'right'
        sm.current = 'home'

class CalendarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_month = 1
        self.current_year = 2025

        layout = FloatLayout()
        self.add_widget(layout)

        layout.add_widget(Image(source='bg_app.jpg', allow_stretch=True, keep_ratio=False))

        header = BoxLayout(size_hint=(1, None), height=120, pos_hint={"top": 1})
        with header.canvas.before:
            Color(0.6, 0.6, 0.6, 1)
            header.bg_rect = Rectangle(size=header.size, pos=header.pos)

        header.bind(
            size=lambda instance, value: setattr(header.bg_rect, 'size', instance.size),
            pos=lambda instance, value: setattr(header.bg_rect, 'pos', instance.pos)
        )

        back_btn_container = RelativeLayout(size_hint=(None, None), size=(50, 50))
        with back_btn_container.canvas.before:
            Color(0.5, 0, 0, 1)
            RoundedRectangle(pos=back_btn_container.pos, size=back_btn_container.size, radius=[25])
        back_btn_container.bind(pos=lambda instance, value: setattr(instance.children[0], 'pos', value))
        back_btn_container.bind(size=lambda instance, value: setattr(instance.children[0], 'size', value))

        back_btn = ClickableImage(
            source="back-button.png",
            size_hint=(None, None),
            size=(50, 50),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        back_btn.bind(on_press=self.animate_back_to_home)
        back_btn_container.add_widget(back_btn)
        header.add_widget(back_btn_container)

        header.add_widget(Label(size_hint_x=None, width=40))

        self.date_time_label = Label(
            text=self.get_current_time(),
            markup=True,
            font_size='12sp',
            color=(0.5, 0, 0, 1),
            halign='center',
            valign='middle',
            size_hint=(1, 1)
        )
        self.date_time_label.bind(size=self.date_time_label.setter('text_size'))
        header.add_widget(self.date_time_label)

        menu_btn = ClickableImage(
            source="menu.png",
            size_hint=(None, None),
            size=(40, 40),
        )
        menu_btn.bind(on_press=lambda x: print("Menu Button Pressed!"))
        header.add_widget(menu_btn)

        layout.add_widget(header)

        layout.add_widget(Image(source='PUP Logo.png',
                                size_hint=(None, None), size=(24, 24),
                                pos_hint={"center_x": 0.5, "top": 0.91}))
        layout.add_widget(Image(source='preskokooko-letter.png',
                                size_hint=(None, None), size=(150, 150),
                                pos_hint={"center_x": 0.50, "top": 0.95}))

        big_card = BigRoundedCard()

        subject_row = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=60)

        subject_code_box = BoxLayout(orientation='vertical', size_hint=(None, 1), width=140)
        subject_code = Label(
            text="[b]COMP 003[/b]", markup=True, color=(0.5, 0, 0, 1),
            font_size=28, halign='center', valign='middle', size_hint=(1, 1)
        )
        subject_code.bind(size=subject_code.setter('text_size'))
        subject_code_box.add_widget(Widget(size_hint_y=1))
        subject_code_box.add_widget(subject_code)
        subject_code_box.add_widget(Widget(size_hint_y=1))
        subject_row.add_widget(subject_code_box)

        class VerticalLine(Widget):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.size_hint_x = None
                self.width = 2
                with self.canvas:
                    Color(0.5, 0, 0, 1)
                    self.line = Rectangle(pos=self.pos, size=(2, 50))
                self.bind(pos=self.update_line, size=self.update_line)
            def update_line(self, *args):
                self.line.pos = self.pos
                self.line.size = (2, self.height)

        subject_row.add_widget(VerticalLine(size_hint_y=None, height=50))

        right_col = BoxLayout(orientation='vertical', spacing=2, size_hint_y=None, height=50)
        subject_name = Label(
            text="Computer Programming II", color=(0, 0, 0, 1),
            font_size=15, halign='left', valign='middle', size_hint_y=None, height=28
        )
        subject_name.bind(size=subject_name.setter('text_size'))
        right_col.add_widget(subject_name)

        prof_label = Label(
            text="Prof. Brian De Vivar",
            color=(0, 0, 0, 1),
            font_size=15,
            halign='left',
            valign='middle',
            size_hint_y=None,
            height=18
        )
        prof_label.bind(size=prof_label.setter('text_size'))
        right_col.add_widget(prof_label)

        subject_row.add_widget(right_col)

        big_card.add_widget(subject_row)

        nav_row = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)

        prev_btn = Button(
            text="<",
            size_hint=(None, None),
            size=(40, 36),
            background_color=(0.5, 0, 0, 1),
            color=(1, 1, 1, 1)
        )
        next_btn = Button(
            text=">",
            size_hint=(None, None),
            size=(40, 36),
            background_color=(0.5, 0, 0, 1),
            color=(1, 1, 1, 1)
        )
        self.month_label = Label(
            text=f"[b]{calendar.month_name[self.current_month]} {self.current_year}[/b]",
            markup=True,
            font_size=18,
            color=(0.5, 0, 0, 1),
            halign='center',
            valign='middle'
        )

        nav_row.add_widget(prev_btn)
        nav_row.add_widget(self.month_label)
        nav_row.add_widget(next_btn)

        days_row = BoxLayout(orientation='horizontal', spacing=2, size_hint_y=None, height=36)
        days = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
        for day in days:
            day_label = Label(
                text=f"[b]{day}[/b]",
                markup=True,
                color=(0.5, 0, 0, 1),
                font_size=14,
                halign='center',
                valign='middle'
            )
            day_label.bind(size=day_label.setter('text_size'))
            days_row.add_widget(day_label)

        calendar_grid = GridLayout(rows=6, cols=7, spacing=0, size_hint_y=1)

        calendar_section = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            spacing=0
        )
        calendar_section.add_widget(nav_row)
        calendar_section.add_widget(days_row)
        calendar_section.add_widget(calendar_grid)

        big_card.add_widget(calendar_section)

        def update_calendar_grid():
            self.month_label.text = f"[b]{calendar.month_name[self.current_month]} {self.current_year}[/b]"
            calendar_grid.clear_widgets()
            cal = calendar.Calendar(firstweekday=6)
            month_days = cal.monthdayscalendar(self.current_year, self.current_month)
            while len(month_days) < 6:
                month_days.append([0]*7)
            for week in month_days:
                for day in week:
                    text = str(day) if day > 0 else ""
                    cell = GridCell(
                        text=text,
                        color=(0, 0, 0, 1),
                        font_size=13,
                        halign='center',
                        valign='middle'
                    )
                    cell.bind(size=cell.setter('text_size'))
                    calendar_grid.add_widget(cell)

        def prev_month(instance):
            if self.current_month == 1:
                self.current_month = 12
                self.current_year -= 1
            else:
                self.current_month -= 1
            update_calendar_grid()

        def next_month(instance):
            if self.current_month == 12:
                self.current_month = 1
                self.current_year += 1
            else:
                self.current_month += 1
            update_calendar_grid()

        prev_btn.bind(on_press=prev_month)
        next_btn.bind(on_press=next_month)

        update_calendar_grid()

        layout.add_widget(big_card)

        Clock.schedule_interval(self.update_datetime, 1)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def update_datetime(self, dt):
        now = datetime.now()
        self.date_time_label.text = now.strftime("[b]%A, %B %d, %Y | %I:%M:%S %p[/b]")

    def animate_back_to_home(self, instance):
        sm = self.manager
        sm.transition.direction = 'right'
        sm.current = 'home'

    def get_current_time(self):
        return datetime.now().strftime("[b]%A, %B %d, %Y | %I:%M:%S %p[/b]")

class GridCell(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.after:
            Color(0.7, 0.7, 0.7, 1)
            self.line_right = Rectangle(size=(1, self.height), pos=(self.right-1, self.y))
            self.line_bottom = Rectangle(size=(self.width, 1), pos=(self.x, self.y))
        self.bind(pos=self.update_lines, size=self.update_lines)
    def update_lines(self, *args):
        self.line_right.pos = (self.right-1, self.y)
        self.line_right.size = (1, self.height)
        self.line_bottom.pos = (self.x, self.y)
        self.line_bottom.size = (self.width, 1)

class EnterCodeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        self.add_widget(layout)

        layout.add_widget(Image(source="bg_app.jpg",
                                allow_stretch=True,
                                keep_ratio=False,
                                size_hint=(1, 1),
                                pos_hint={"x": 0, "y": 0}))

        # Header (light gray like professor screen)
        header = BoxLayout(size_hint=(1, None), height=120, pos_hint={"top": 1})
        with header.canvas.before:
            Color(0.6, 0.6, 0.6, 1)  # Light gray
            self.rect = Rectangle(size=header.size, pos=header.pos)

        header.bind(pos=self.update_rect, size=self.update_rect)

# Back Button
        back_btn_container = RelativeLayout(size_hint=(None, None), size=(50, 50))
        with back_btn_container.canvas.before:
            Color(0.5, 0, 0, 1)
            RoundedRectangle(pos=back_btn_container.pos, size=back_btn_container.size, radius=[25])
        back_btn_container.bind(pos=lambda instance, value: setattr(instance.children[0], 'pos', value))
        back_btn_container.bind(size=lambda instance, value: setattr(instance.children[0], 'size', value))

        back_btn = ClickableImage(
            source="back-button.png",
            size_hint=(None, None),
            size=(50, 50),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        back_btn.bind(on_press=self.animate_back_to_home)
        back_btn_container.add_widget(back_btn)
        header.add_widget(back_btn_container)

        header.add_widget(Label(size_hint_x=None, width=40))

        self.date_time_label = Label(
            text=self.get_current_time(),
            markup=True,
            font_size='12sp',
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle',
            size_hint=(1, 1)
        )   
        self.date_time_label.bind(size=self.date_time_label.setter('text_size'))
        header.add_widget(self.date_time_label)

# Menu Button
        menu_btn = ClickableImage(
            source="menu.png",
            size_hint=(None, None),
            size=(40, 40),
        )
        menu_btn.bind(on_press=lambda x: print("Menu Button Pressed!"))
        header.add_widget(menu_btn)
        layout.add_widget(header)


        top_logo = Image(
            source="PUP Logo.png",
            size_hint=(None, None),
            size=(24, 24),
            pos_hint={"center_x": 0.5, "top": 0.91}
        )
        layout.add_widget(top_logo)

        logo = Image(source="preskokooko-letter.png",
                     size_hint=(None, None),
                     size=(150, 150),
                     pos_hint={"center_x": 0.5, "top": 0.95})
        layout.add_widget(logo)

        card = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            size=(400, 220),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            padding=[30, 30, 30, 30],
            spacing=20
        )
        with card.canvas.before:
            Color(1, 1, 1, 1)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        card.bind(pos=lambda instance, value: setattr(self.bg, 'pos', value))
        card.bind(size=lambda instance, value: setattr(self.bg, 'size', value))

        code_label = Label(
            text="[b]Enter Code[/b]",
            markup=True,
            font_size=20,
            color=(0.5, 0, 0, 1),
            size_hint=(1, None),
            height=40
        )
        card.add_widget(code_label)

        self.code_input = TextInput(
            hint_text="Type code here...",
            multiline=False,
            font_size=18,
            size_hint=(1, None),
            height=48,
            background_color=(0.95, 0.95, 0.95, 1),
            foreground_color=(0, 0, 0, 1),
            padding=[10, 10, 10, 10]
        )
        card.add_widget(self.code_input)

        submit_btn = Button(
            text="SUBMIT",
            size_hint=(1, None),
            height=44,
            background_color=(0.5, 0, 0, 1),
            color=(1, 1, 1, 1)
        )
        card.add_widget(submit_btn)

        layout.add_widget(card)

        Clock.schedule_interval(self.update_datetime, 1)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def update_datetime(self, dt):
        now = datetime.now()
        self.date_time_label.text = now.strftime("[b]%A, %B %d, %Y | %I:%M:%S %p[/b]")

    def get_current_time(self):
        return datetime.now().strftime("[b]%A, %B %d, %Y | %I:%M:%S %p[/b]")

    def animate_back_to_home(self, instance):
        sm = self.manager
        sm.transition.direction = 'right'
        sm.current = 'home'

class PreskoApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.current = 'home' 
        sm.add_widget(QRScreen(name='qr'))
        sm.add_widget(CalendarScreen(name='calendar'))
        sm.add_widget(EnterCodeScreen(name='entercode'))
        return sm

if __name__ == '__main__':
    PreskoApp().run()