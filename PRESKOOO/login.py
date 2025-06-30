Window.fullscreen = 'auto'
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.popup import Popup
from datetime import datetime
from kivy.clock import Clock

class ImageButton(ButtonBehavior, Image):
    pass

temporary_users = {
    "student": {"password": "1234", "role": "Student"},
    "professor": {"password": "abcd", "role": "Professor"}
}
# Welcome Screen
class WelcomeScreen(Screen):
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

        self.layout.add_widget(Image(source='preskokooko-letter.png', size_hint=(None, None), size=(200, 200), pos_hint={"center_x": 0.5, "top": 1}))

        logo = Image(source='ISKODE2.png', size_hint=(0.1, 0.075),pos_hint={'center_x': 0.5, 'center_y': 0.75})
        self.layout.add_widget(logo)

        greeting = Label(text="[color=ffffff]Greetings, Iskolar ng Bayan![/color]",markup=True, font_size='18sp',pos_hint={'center_x': 0.5, 'center_y': 0.68})
        
        menu_btn = ImageButton(
            source='menu.png',
            size_hint=(None, None),
            size=(45, 45),
            pos_hint={"top": 0.98, "right": 0.98}
        )   
        menu_btn.bind(on_release=self.open_menu)
        self.layout.add_widget(menu_btn)

        student_btn = Button(text="STUDENT", size_hint=(0.4, 0.08),pos_hint={'center_x': 0.5, 'center_y': 0.50})
        faculty_btn = Button(text="FACULTY", size_hint=(0.4, 0.08),pos_hint={'center_x': 0.5, 'center_y': 0.40})
        signup_btn = Button(text="Sign Up", size_hint=(0.4, 0.08),pos_hint={'center_x': 0.5, 'center_y': 0.30})

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

        # Assign logic to prepare login screen based on role
        student_btn.bind(on_press=self.go_student)
        faculty_btn.bind(on_press=self.go_faculty)
        signup_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'signup'))

        self.layout.add_widget(greeting)
        self.layout.add_widget(student_btn)
        self.layout.add_widget(faculty_btn)
        self.layout.add_widget(signup_btn)
        self.add_widget(self.layout)

    def go_student(self, instance):
        self.manager.get_screen('login').set_user_type('Student')
        self.manager.current = 'login'

    def go_faculty(self, instance):
        self.manager.get_screen('login').set_user_type('Professor')
        self.manager.current = 'login'

    def open_menu(self, instance):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        layout.add_widget(Label(text="👤 Options Menu", color=(1, 1, 1, 1)))
        layout.add_widget(Button(text="🌙 Toggle Dark/Light"))
        layout.add_widget(Button(text="📢 Send Feedback"))
        layout.add_widget(Button(text="🚪 Sign Out", on_release=lambda x: setattr(self.manager, 'current', 'welcome')))

        popup = Popup(title="Menu", content=layout, size_hint=(0.7, 0.6))
        popup.open()

    def update_datetime(self, dt):
        now = datetime.now()
        self.datetime_label.text = now.strftime("%A, %B %d, %Y | %I:%M:%S %p")

# Sign-Up Screen
class SignUpScreen(Screen): 
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

        logo = Image(source='ISKODE2.png', size_hint=(0.1, 0.075),pos_hint={'center_x': 0.5, 'center_y': 0.85})
        self.layout.add_widget(logo)

        self.layout.add_widget(Image(source='preskokooko-letter.png', size_hint=(None, None), size=(200, 200), pos_hint={"center_x": 0.5, "top": 1}))

        menu_btn = ImageButton(
            source='menu.png',
            size_hint=(None, None),
            size=(45, 45),
            pos_hint={"top": 0.98, "right": 0.98}
        )   
        menu_btn.bind(on_release=self.open_menu)
        self.layout.add_widget(menu_btn)

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

        content = BoxLayout(orientation='vertical', spacing=12,size_hint=(0.85, 0.65), pos_hint={'center_x': 0.75, 'center_y': 0.40})

        # 🔹 Full Name Field (New)
        self.name_input = TextInput(hint_text="Full Name", multiline=False,background_color=(1, 1, 1, 1), foreground_color=(0, 0, 0, 1),size_hint=(0.4, 0.08), padding=[10, 10])
        self.id_input = TextInput(hint_text="PUP ID Number", multiline=False,background_color=(1, 1, 1, 1), foreground_color=(0, 0, 0, 1),size_hint=(0.4, 0.08), padding=[10, 10])
        self.password_input = TextInput(hint_text="Password", password=True, multiline=False,background_color=(1, 1, 1, 1), foreground_color=(0, 0, 0, 1),size_hint=(0.4, 0.08), padding=[10, 10])
        self.confirm_input = TextInput(hint_text="Re-enter Password", password=True, multiline=False,background_color=(1, 1, 1, 1), foreground_color=(0, 0, 0, 1),size_hint=(0.4, 0.08), padding=[10, 10])
        self.role_spinner = Spinner(text="Select Role", values=('Student', 'Professor'),size_hint=(0.4, 0.08))
        self.msg = Label(size_hint=(1, 0.1), color=(1, 1, 1, 1),pos_hint={'center_x': 0.20, 'center_y': 0.40})

        # Update input list for tab key handling
        self.inputs = [self.name_input, self.id_input, self.password_input, self.confirm_input]
        for field in self.inputs:
            field.write_tab = False  # Allow tab key to propagate

        Window.bind(on_key_down=self.on_tab_key)

        signup_btn = Button(text="SIGN UP", size_hint=(0.4, 0.08), background_color=(1, 1, 1, 1), color=(1, 1, 1, 1))
        signup_btn.bind(on_press=self.register_user)


        back_btn = ImageButton(
            source='back-button.png',
            size_hint=(None, None),
            size=(45, 45),
            pos_hint={"top": 0.98, "x": 0.01}
        )
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'welcome'))
        self.layout.add_widget(back_btn)

        # Add all fields
        content.add_widget(self.name_input)
        content.add_widget(self.id_input)
        content.add_widget(self.password_input)
        content.add_widget(self.confirm_input)
        content.add_widget(self.role_spinner)
        content.add_widget(signup_btn)
        content.add_widget(self.msg)

        self.layout.add_widget(content)
        self.add_widget(self.layout)

    def register_user(self, instance):
        name = self.name_input.text.strip()
        uname = self.id_input.text.strip()
        pword = self.password_input.text.strip()
        confirm = self.confirm_input.text.strip()
        role = self.role_spinner.text.strip()
        key = f"{role.lower()}_{uname}"

        if not name or not uname or not pword or not confirm or role not in ['Student', 'Professor']:
            self.msg.text = "All fields are required."
            return

        if pword != confirm:
            self.msg.text = "Passwords do not match."
            return

        if key in temporary_users:  # 👈 Change this check
            self.msg.text = "User already exists."
            return

        temporary_users[key] = {  # 👈 Save using the unique role-based key
            "name": name,
            "password": pword,
            "role": role
        }

        self.msg.text = "Registered successfully!"

        def go_to_login(dt):
            self.manager.get_screen('login').set_user_type(None)
            self.manager.current = 'login'

        Clock.schedule_once(go_to_login, 1.5)

    def on_pre_enter(self):
        self.name_input.text = ""
        self.id_input.text = ""
        self.password_input.text = ""
        self.confirm_input.text = ""
        self.role_spinner.text = "Select Role"
        self.msg.text = ""

    def on_tab_key(self, window, key, scancode, codepoint, modifiers):
        if key == 9:  # Tab key
            for i, field in enumerate(self.inputs):
                if field.focus:
                    next_index = (i + 1) % len(self.inputs)
                    self.inputs[next_index].focus = True
                    return True
        return False
    
    def open_menu(self, instance):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        layout.add_widget(Label(text="👤 Options Menu", color=(1, 1, 1, 1)))
        layout.add_widget(Button(text="🌙 Toggle Dark/Light"))
        layout.add_widget(Button(text="📢 Send Feedback"))
        layout.add_widget(Button(text="🚪 Sign Out", on_release=lambda x: setattr(self.manager, 'current', 'welcome')))

        popup = Popup(title="Menu", content=layout, size_hint=(0.7, 0.6))
        popup.open()

    def update_datetime(self, dt):
        now = datetime.now()
        self.datetime_label.text = now.strftime("%A, %B %d, %Y | %I:%M:%S %p")

      
# Login Screen
class LoginScreen(Screen):
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

        logo = Image(source='ISKODE2.png', size_hint=(0.1, 0.075),pos_hint={'center_x': 0.5, 'center_y': 0.85})
        self.layout.add_widget(logo)

        self.layout.add_widget(Image(source='preskokooko-letter.png', size_hint=(None, None), size=(200, 200), pos_hint={"center_x": 0.5, "top": 1}))

        greeting = Label(text="Greetings, Iskolar ng Bayan!",markup=True, font_size='16sp',pos_hint={'center_x': 0.5, 'top': 1.25})
        self.layout.add_widget(greeting)
        
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

        # Menu Button
        menu_btn = ImageButton(
            source='menu.png',
            size_hint=(None, None),
            size=(45, 45),
            pos_hint={"top": 0.98, "right": 0.98}
        )
        menu_btn.bind(on_release=self.open_menu)
        self.layout.add_widget(menu_btn)

        self.content = BoxLayout(orientation='vertical', spacing=12,size_hint=(0.85, 0.45), pos_hint={'center_x': 0.5, 'center_y': 0.45})

        self.username = TextInput(hint_text="PUP ID Number", multiline=False,background_color=(1, 1, 1, 1), foreground_color=(0, 0, 0, 1),size_hint=(0.4, 0.08), padding=[10, 10],pos_hint={'center_x': 0.5, 'center_y': 0.45})
        self.password = TextInput(hint_text="Password", password=True, multiline=False,background_color=(1, 1, 1, 1), foreground_color=(0, 0, 0, 1),size_hint=(0.4, 0.08), padding=[10, 10],pos_hint={'center_x': 0.5, 'center_y': 0.45})
        self.role_spinner = Spinner(text="Select Role", values=('Student', 'Professor'),size_hint=(0.4, 0.08),pos_hint={'center_x': 0.5, 'center_y': 0.45})
        self.msg = Label(size_hint=(1, 0.1), color=(1, 1, 1, 1))

        login_btn = Button(text="LOG IN", size_hint=(0.4, 0.08), background_color=(1, 1, 1, 1),pos_hint={'center_x': 0.5, 'center_y': 0.45})
        login_btn.bind(on_press=self.login_user)

        self.inputs = [self.username, self.password]
        for field in self.inputs:
            field.write_tab = False

        Window.bind(on_key_down=self.on_tab_key)

        back_btn = ImageButton(
            source='back-button.png',
            size_hint=(None, None),
            size=(45, 45),
            pos_hint={"top": 0.98, "x": 0.01}
        )
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'welcome'))
        self.layout.add_widget(back_btn)

        self.content.add_widget(self.username)
        self.content.add_widget(self.password)
        self.content.add_widget(self.role_spinner)
        self.content.add_widget(login_btn)
        self.content.add_widget(self.msg)

        self.layout.add_widget(self.content)
        self.add_widget(self.layout)

    def login_user(self, instance):
        uname = self.username.text.strip()
        pword = self.password.text.strip()
        role = self.role_spinner.text.strip()

        key = f"{role.lower()}_{uname}"
        if key in temporary_users:
                user = temporary_users[key]
                if user["password"] == pword and user["role"] == role:
                    self.msg.text = f"Login successful! ({role})"
                    return

        self.msg.text = "Invalid login or role."

    def set_user_type(self, user_type):
        if user_type == "Student":
            self.username.hint_text = "STUDENT NO:"
            self.role_spinner.text = "Student"
        elif user_type == "Professor":
            self.username.hint_text = "PROFESSOR NO:"
            self.role_spinner.text = "Professor"
        else:
            self.username.hint_text = "PUP ID Number"
            self.role_spinner.text = "Select Role"

    def on_pre_enter(self):
        self.username.text = ""
        self.password.text = ""
        self.msg.text = ""

    def on_tab_key(self, window, key, scancode, codepoint, modifiers):
        if key == 9:  # Tab
            for i, field in enumerate(self.inputs):
                if field.focus:
                    next_index = (i + 1) % len(self.inputs)
                    self.inputs[next_index].focus = True
                    return True
        return False
    
    def open_menu(self, instance):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        layout.add_widget(Label(text="👤 Options Menu", color=(1, 1, 1, 1)))
        layout.add_widget(Button(text="🌙 Toggle Dark/Light"))
        layout.add_widget(Button(text="📢 Send Feedback"))
        layout.add_widget(Button(text="🚪 Sign Out", on_release=lambda x: setattr(self.manager, 'current', 'welcome')))

        popup = Popup(title="Menu", content=layout, size_hint=(0.7, 0.6))
        popup.open()

    def update_datetime(self, dt):
        now = datetime.now()
        self.datetime_label.text = now.strftime("%A, %B %d, %Y | %I:%M:%S %p")

class PreskoApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(WelcomeScreen(name="welcome"))
        sm.add_widget(SignUpScreen(name="signup"))
        sm.add_widget(LoginScreen(name="login"))
        return sm

if __name__ == '__main__':
    PreskoApp().run()