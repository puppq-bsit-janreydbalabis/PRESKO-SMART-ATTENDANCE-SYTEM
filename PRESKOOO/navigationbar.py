# main.py (or navigationbar.py as per your execution path)
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel  # Make sure this line is present!
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.utils import get_color_from_hex
from kivy.metrics import dp  # For density-independent pixels
from kivy.core.window import Window  # Import Window to control window properties
from kivy.utils import platform  # To check the operating platform


class NavigationItem(MDBoxLayout):
    """
    A custom KivyMD widget representing a single item in the navigation bar,
    consisting only of an icon.
    """

    icon_name = StringProperty()  # Kivy property to set the icon
    item_name = StringProperty()  # Kivy property to uniquely identify the item
    is_active = BooleanProperty(False)  # Kivy property to control active state
    # Reference to the parent NavigationBar to call its methods
    parent_bar = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"  # Keep vertical to center the icon if needed
        self.spacing = 0  # No spacing needed between icon and non-existent label
        self.padding = (0, dp(8), 0, dp(8))  # Adjust padding for icon-only display
        self.size_hint_y = None
        self.height = dp(
            40
        )  # A reasonable height for just an icon, less than dp(56) total bar height minus padding
        self.ripple_behavior = True

        # Create MDIconButton
        self.icon_button = MDIconButton(
            icon=self.icon_name,
            halign="center",
            valign="center",  # Ensure icon is vertically centered within its space
            size_hint=(1, 1),  # Make the icon button fill its parent (NavigationItem)
            theme_text_color="Custom",
        )
        self.icon_button.bind(icon=self._update_icon)  # Bind icon property
        self.icon_button.bind(on_release=self._on_button_release)  # Bind release event

        self.add_widget(self.icon_button)

        # Bind the is_active property to update colors
        self.bind(is_active=self._update_colors)
        self.bind(icon_name=self._update_icon)

        # Call _update_colors initially to set the correct color on startup
        self._update_colors(self, self.is_active)

    def _update_icon(self, instance, value):
        """Callback to update icon if icon_name changes."""
        self.icon_button.icon = value

    def _update_colors(self, instance, value):
        """Updates the colors of the icon based on is_active."""
        if value:  # if is_active is True
            # --- MODIFICATION START ---
            # Set the icon color to red when active
            self.icon_button.text_color = get_color_from_hex("#FF0000")
            # --- MODIFICATION END ---
        else:  # if is_active is False
            # Set the icon color to gray when inactive
            self.icon_button.text_color = get_color_from_hex("#808080")

    def _on_button_release(self, instance):
        """Handles the button release event and informs the parent bar."""
        if self.parent_bar:
            self.parent_bar.set_active_item(self.item_name)


class NavigationBar(MDBoxLayout):
    """
    A custom KivyMD widget representing the entire bottom navigation bar.
    It manages the active state of its child NavigationItem widgets.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(56)  # Standard height for bottom navigation bars
        self.md_bg_color = (1, 1, 1, 1)  # White background
        self.elevation = 4  # Shadow effect
        self.padding = (dp(8), 0, dp(8), 0)  # Horizontal padding for items
        self.active_item = "Home"  # Set initial active item to "Home"

        # Create NavigationItem widgets with new icons and names
        self.home_item = NavigationItem(
            icon_name="home", item_name="Home", is_active=True, parent_bar=self
        )
        self.add_item = NavigationItem(
            icon_name="plus",  # Icon for 'Add'
            item_name="Add",  # Item name is still used for logic, even if not displayed
            is_active=False,
            parent_bar=self,
        )
        self.menu_item = NavigationItem(
            icon_name="menu",  # Icon for 'Menu'
            item_name="Menu",  # Item name is still used for logic, even if not displayed
            is_active=False,
            parent_bar=self,
        )

        # Add them to the layout in the desired order
        self.add_widget(self.home_item)
        self.add_widget(self.add_item)
        self.add_widget(self.menu_item)

    def set_active_item(self, item_name):
        """
        Updates the active item in the navigation bar.
        This method is called when a NavigationItem is pressed.
        """
        if self.active_item == item_name:
            # If the same item is pressed, do nothing
            return

        # Deactivate the previously active item
        for item in self.children:
            if isinstance(item, NavigationItem) and item.item_name == self.active_item:
                item.is_active = False
                break

        # Activate the newly selected item
        for item in self.children:
            if isinstance(item, NavigationItem) and item.item_name == item_name:
                item.is_active = True
                self.active_item = item_name
                # print(f"Active item changed to: {self.active_item}") # Removed for cleaner mobile output
                break


class MainApp(MDApp):
    """
    The main KivyMD application class.
    """

    def build(self):
        """
        Builds the application UI programmatically.
        """
        # --- Mobile Geometry Simulation (for desktop testing) ---
        if platform == "win" or platform == "macosx" or platform == "linux":
            # Set a common mobile resolution (e.g., iPhone SE/Android Small)
            # You can adjust these values for other common mobile resolutions
            Window.size = (360, 640)
            # Optionally make the window borderless for an app-like feel
            # Window.borderless = True
        # --------------------------------------------------------

        self.theme_cls.primary_palette = (
            "Teal"  # This no longer affects the active icon color
        )
        self.theme_cls.theme_style = "Light"  # Use light theme

        # Create the root layout
        root_layout = MDBoxLayout(orientation="vertical")

        # Create the main content area (placeholder)
        content_label = MDLabel(  # This is where MDLabel is used
            text="Main Content Area",
            halign="center",
            valign="middle",
            font_style="H5",
            size_hint_y=1,
        )
        root_layout.add_widget(content_label)

        # Create the navigation bar
        navigation_bar = NavigationBar()
        root_layout.add_widget(navigation_bar)

        return root_layout

    def on_start(self):
        """
        Called when the application starts.
        Ensures the correct initial active state is set based on the `NavigationBar`'s default.
        """
        pass  # No changes needed here


if __name__ == "__main__":
    MainApp().run()
