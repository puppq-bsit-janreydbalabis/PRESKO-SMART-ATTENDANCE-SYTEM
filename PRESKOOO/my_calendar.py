from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp, sp
from kivy.properties import StringProperty, NumericProperty
from kivy.config import Config
from kivy.graphics import Color, Rectangle
from datetime import datetime
import calendar

# Set window size to simulate mobile geometry
Config.set("graphics", "width", "360")
Config.set("graphics", "height", "640")
Config.set("graphics", "resizable", False)


class CalendarWidget(BoxLayout):
    current_month = NumericProperty(datetime.now().month)
    current_year = NumericProperty(datetime.now().year)
    selected_date = StringProperty(datetime.now().strftime("%Y-%m-%d"))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(8)
        self.spacing = dp(4)

        # Header: Month/Year and Navigation
        self.header = BoxLayout(size_hint=(1, 0.12))
        self.prev_button = Button(
            text="<",
            size_hint=(0.15, 1),
            font_size=sp(20),
            background_color=(0.1, 0.1, 0.1, 1),
        )
        self.prev_button.bind(on_press=self.prev_month)
        self.month_label = Label(
            text=self.get_month_year(),
            size_hint=(0.7, 1),
            font_size=sp(18),
            bold=True,
        )
        self.next_button = Button(
            text=">",
            size_hint=(0.15, 1),
            font_size=sp(20),
            background_color=(0.1, 0.1, 0.1, 1),
        )
        self.next_button.bind(on_press=self.next_month)
        self.header.add_widget(self.prev_button)
        self.header.add_widget(self.month_label)
        self.header.add_widget(self.next_button)

        # Weekday Headers
        self.weekdays = GridLayout(cols=7, size_hint=(1, 0.08))
        for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
            self.weekdays.add_widget(
                Label(
                    text=day,
                    font_size=sp(12),
                    color=(0.9, 0.9, 0.9, 1),
                )
            )

        # Calendar Grid
        # Total size_hint_y: 1 - (0.12 + 0.08 + 0.1) = 0.72
        self.grid = GridLayout(
            cols=7,
            size_hint=(1, 0.72),  # Fills remaining space
            spacing=dp(2),
        )

        # Bottom Buttons
        self.button_layout = BoxLayout(
            size_hint=(1, 0.1), spacing=dp(8), padding=(dp(8), dp(4))
        )
        self.scan_qr_button = Button(
            text="Scan QR",
            font_size=sp(16),
            background_color=(0.1, 0.5, 0.8, 1),
            background_normal="",
        )
        self.scan_qr_button.bind(on_press=self.on_scan_qr_press)
        self.enter_code_button = Button(
            text="Enter Code",
            font_size=sp(16),
            background_color=(0.1, 0.5, 0.8, 1),
            background_normal="",
        )
        self.enter_code_button.bind(on_press=self.on_enter_code_press)
        self.button_layout.add_widget(self.scan_qr_button)
        self.button_layout.add_widget(self.enter_code_button)

        # Add all widgets to main layout
        self.add_widget(self.header)
        self.add_widget(self.weekdays)
        self.add_widget(self.grid)
        self.add_widget(self.button_layout)
        self.update_calendar()

    def get_month_year(self):
        return f"{calendar.month_name[self.current_month]} {self.current_year}"

    def update_calendar(self):
        self.grid.clear_widgets()
        self.month_label.text = self.get_month_year()

        cal = calendar.monthcalendar(self.current_year, self.current_month)
        today = datetime.now()

        first_weekday = calendar.monthrange(self.current_year, self.current_month)[0]
        for _ in range(first_weekday):
            self.grid.add_widget(Label(text="", size_hint=(1, 1)))

        for week in cal:
            for day in week:
                if day == 0:
                    self.grid.add_widget(Label(text="", size_hint=(1, 1)))
                else:
                    btn = Button(
                        text=str(day),
                        font_size=sp(16),
                        size_hint=(1, 1),
                        background_color=(0.15, 0.15, 0.15, 1),
                        background_normal="",
                    )
                    if (
                        day == today.day
                        and self.current_month == today.month
                        and self.current_year == today.year
                    ):
                        btn.background_color = (0, 0.7, 0.3, 1)
                    btn.bind(on_press=self.on_day_press)
                    self.grid.add_widget(btn)

    def prev_month(self, instance):
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self.update_calendar()

    def next_month(self, instance):
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        self.update_calendar()

    def on_day_press(self, instance):
        self.selected_date = (
            f"{self.current_year}-{self.current_month:02d}-{int(instance.text):02d}"
        )
        print(f"Selected date: {self.selected_date}")

    def on_scan_qr_press(self, instance):
        print("Scan QR button pressed")

    def on_enter_code_press(self, instance):
        print("Enter Code button pressed")


class CalendarApp(App):
    def build(self):
        return CalendarWidget()


if __name__ == "__main__":
    CalendarApp().run()
