import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.properties import StringProperty, NumericProperty

# Set the app window size for demonstration
Window.size = (360, 640)

# --- KV Language String ---
# This string contains the UI design rules, similar to CSS for web.
# It's cleaner to keep the design separate from the application logic.
# NOTE: All indentation has been corrected to use standard spaces.
KV = """
#<-- Custom Widget Definitions -->
<RoundedButton@Button>:
    # A custom button with a solid background and rounded corners
    background_color: (0, 0, 0, 0) # Make Kivy's default background transparent
    canvas.before:
        Color:
            rgba: (34/255, 142/255, 222/255, 1) # Accent color
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [24,] # All corners rounded

<SignOutButton@Button>:
    # A custom button with an outline/border and rounded corners
    background_color: (0, 0, 0, 0)
    canvas.before:
        Color:
            rgba: (0.7, 0.7, 0.7, 1) # Gray color for the outline
        Line:
            width: 1.2
            rounded_rectangle: (self.x, self.y, self.width, self.height, 24)

#<-- Main Screen Layout -->
<ProfileScreen>:
    orientation: 'vertical'
    padding: '20dp'
    spacing: '15dp'

    canvas.before:
        Color:
            rgba: (25/255, 25/255, 25/255, 1) # Dark background color
        Rectangle:
            pos: self.pos
            size: self.size

    # --- Top Section: Profile Picture and Name ---
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: self.minimum_height
        spacing: '10dp'
        pos_hint: {'top': 1}

        # This FloatLayout is used to create a circular profile picture
        FloatLayout:
            size_hint_y: None
            height: '120dp'
            # --- Image and details changed to Elon Musk ---
            AsyncImage:
                id: profile_pic
                source: 'https://upload.wikimedia.org/wikipedia/commons/8/85/Elon_Musk_Royal_Society_%28crop1%29.jpg'
                size_hint: None, None
                size: '110dp', '110dp'
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                # --- This canvas code clips the image into a circle ---
                canvas.before:
                    StencilPush
                    Ellipse:
                        pos: self.pos
                        size: self.size
                    StencilUse
                canvas.after:
                    StencilPop

        Label:
            text: 'Elon Musk'
            font_size: '28sp'
            bold: True
            size_hint_y: None
            height: self.texture_size[1]

        Label:
            text: '@elonmusk'
            font_size: '16sp'
            color: (0.7, 0.7, 0.7, 1) # Lighter gray for subtext
            size_hint_y: None
            height: self.texture_size[1]

    # --- Bio Section ---
    Label:
        text: "Full-Stack Developer | Python, JavaScript, & Rust | Building the future, one line of code at a time. #OpenSource #Tech"
        font_size: '15sp'
        color: (0.85, 0.85, 0.85, 1)
        text_size: self.width, None # Allows for text wrapping
        size_hint_y: None
        height: self.texture_size[1]
        halign: 'center'
        valign: 'top'
        
    # --- Edit Profile Button ---
    RoundedButton:
        text: 'Edit Profile'
        size_hint_y: None
        height: '48dp'
        on_press: app.edit_profile()

    # --- Spacer Widget ---
    # This widget will expand to push the bottom buttons down
    Widget:
        size_hint_y: 1

    # --- Bottom Section: Action Buttons ---
    # <-- NEW WIDGET ADDED HERE -->
    SignOutButton:
        text: 'Send Feedback'
        size_hint_y: None
        height: '48dp'
        on_press: app.send_feedback()

    SignOutButton:
        text: 'Sign Out'
        size_hint_y: None
        height: '48dp'
        on_press: app.sign_out()

"""

# --- Python Class Definitions ---


# This is the root widget of our application.
class ProfileScreen(BoxLayout):
    pass


# This is the main App class.
class ProfileApp(App):
    def build(self):
        # Load the KV string
        Builder.load_string(KV)
        # Return the root widget
        return ProfileScreen()

    # --- App Logic/Functions ---
    # These methods are called when the buttons are pressed (defined in the KV string)

    def edit_profile(self):
        """Placeholder function for 'Edit Profile' button press."""
        print("The 'Edit Profile' button has been pressed.")

    # <-- NEW FUNCTION ADDED HERE -->
    def send_feedback(self):
        """Placeholder function for 'Send Feedback' button press."""
        print("The 'Send Feedback' button has been pressed.")

    def sign_out(self):
        """Placeholder function for 'Sign Out' button press."""
        print("The 'Sign Out' button has been pressed. Signing out...")
        # In a real app, you would add logic here to clear user session and change screens.
        # For this example, we can just close the app.
        App.get_running_app().stop()


# --- Main Execution ---
if __name__ == "__main__":
    ProfileApp().run()
