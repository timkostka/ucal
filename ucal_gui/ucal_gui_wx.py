"""
This is a class derived from CalculatorWindowBase.

"""

import os
import ctypes
import platform
import decimal
import sys
import configparser

import wx

import ucal

from BaseCalculatorWindow import BaseCalculatorWindow


#######################
# START OF OF OPTIONS #
#######################

# Windows default DPI
default_dpi = 96

# DPI setting for this system
system_dpi = default_dpi

# history items, each as a (input, output) tuple
history = []

# index of selected history item (0 = last)
history_index = None

##################
# END OF OPTIONS #
##################


# default INI file options
default_configuration = configparser.ConfigParser()
default_configuration["Settings"] = {
    "ViewOptions": "no",
    "SaveHistory": "yes",
    "RememberWindowSettings": "yes",
    "MaxHistoryEntries": "1000",
}

# INI file location
ini_file_path = os.path.join(
    os.path.join(os.environ["LOCALAPPDATA"], "uCal"), "ucal.ini"
)


def read_configuration():
    """Attempt to read the INI configuration file."""
    if not os.path.isfile(ini_file_path):
        print("INI file not found")
        print("Configuration file not found")
        return default_configuration
    print("Reading INI file")
    config = configparser.ConfigParser()
    config.read(ini_file_path)
    return config


def store_configuration(config):
    """Store the configuration to an INI file."""
    print("Writing INI file")
    # create path if it doesn't exist
    try:
        os.makedirs(os.path.dirname(ini_file_path), exist_ok=True)
        with open(ini_file_path, "w") as f:
            config.write(f)
    except:
        print('ERROR: error while saving INI file')


def find_file(filename):
    """Search and return the path to the given filename, or None."""
    directories = [".", os.path.dirname(__file__)]
    directories.append(getattr(sys, "_MEIPASS", "."))
    for this_dir in directories:
        path = os.path.join(os.path.abspath(this_dir), filename)
        if os.path.isfile(path):
            print("Found file: %s" % path)
            return path
    print("Unable to find file %s" % filename)
    return None


def get_system_dpi():
    """Return the DPI currently in use."""
    import ctypes

    dc = ctypes.windll.user32.GetDC(0)
    dpi = ctypes.windll.gdi32.GetDeviceCaps(dc, 88)
    ctypes.windll.user32.ReleaseDC(0, dc)
    return dpi


def adjusted_size(size):
    """Return a size adjusted for the current DPI setting."""
    if isinstance(size, int):
        return int(size * system_dpi / 96.0 + 0.5)
    if isinstance(size, wx.Size):
        return wx.Size(adjusted_size(size[0]), adjusted_size(size[1]))
    raise ValueError


class CalculatorWindow(BaseCalculatorWindow):
    def __init__(self, parent):
        super(CalculatorWindow, self).__init__(parent)
        new_size = adjusted_size(self.GetSize())
        if new_size != self.GetSize():
            self.SetSize(new_size)
        self.Centre()
        # self.scrolled_window_history.SetDoubleBuffered(True)
        self.SetDoubleBuffered(True)
        # move focus to the input text box
        self.text_ctrl_input.SetFocus()
        self.text_ctrl_input.SetInsertionPoint(-1)
        # set the program icon
        icon_filename = find_file("ucal.ico")
        if icon_filename:
            self.SetIcon(wx.Icon(icon_filename))
        else:
            print("ERROR: could not find icon file")
        # clear history
        self.clear_history()

    def apply_configuration(self, config):
        """Apply the given INI configuration."""
        self.panel_options.Show(
            show=config.getboolean("Settings", "ViewOptions")
        )
        self.menu_file_view_options.Check(
            config.getboolean("Settings", "ViewOptions")
        )
        self.checkbox_remember_window_position.SetValue(
            config.getboolean("Settings", "RememberWindowSettings")
        )
        self.checkbox_save_history.SetValue(
            config.getboolean("Settings", "SaveHistory")
        )
        self.spin_ctrl_history_capacity.SetValue(
            config.get("Settings", "MaxHistoryEntries")
        )
        # apply window size/position if requested
        if self.checkbox_remember_window_position.GetValue():
            # set size
            target_size = config.get("Settings", "WindowSize").lower()
            print("WindowSize=%s" % target_size)
            if "x" in target_size:
                size = target_size.split("x")
                if len(size) == 2 and all(x.isdigit() for x in size):
                    size = [int(x) for x in size]
                    self.SetSize(*size)
            # set position
            position = config.get("Settings", "WindowPosition").split(",")
            if len(position) == 2 and all(x.isdigit() for x in position):
                position = [int(x) for x in position]
                print("WindowPosition=%s" % position)
                self.SetPosition(position)
        # load history if requested
        if self.checkbox_save_history.GetValue():
            count = int(config.get("History", "Entries"))
            for i in range(1, count + 1):
                input_text = config.get("History", "Input%d" % i)
                result = config.get("History", "Result%d" % i)
                self.add_history(input_text, result)

    def get_configuration(self):
        """Return the current configuration."""
        config = configparser.ConfigParser()
        config.add_section("Settings")
        config.set(
            "Settings",
            "ViewOptions",
            "yes" if self.panel_options.IsShown() else "no",
        )
        config.set(
            "Settings",
            "RememberWindowSettings",
            "yes" if self.checkbox_remember_window_position.IsChecked() else "no",
        )
        config.set(
            "Settings", "SaveHistory",
            "yes" if self.checkbox_save_history.IsChecked() else "no",
        )
        config.set(
            "Settings",
            "MaxHistoryEntries",
            str(self.spin_ctrl_history_capacity.GetValue()),
        )
        config.set(
            "Settings", "WindowSize", "x".join(str(x) for x in self.GetSize())
        )
        config.set(
            "Settings",
            "WindowPosition",
            ",".join(str(x) for x in self.GetPosition()),
        )
        # store the history if necessary
        if self.checkbox_save_history.IsChecked():
            config.add_section("History")
            config.set("History", "Entries", str(len(history)))
            for i, (input_text, result_text) in enumerate(history, 1):
                config.set('History', 'Input%d' % i, input_text)
                config.set('History', 'Result%d' % i, input_text)
        return config

    # Virtual event handlers, overide them in your derived class
    def event_on_size(self, event):
        event.Skip()
        return
        client_size = self.m_scrolledWindow1.GetClientSize()
        print("\nclient_size =", client_size)
        print(
            "getscrollpos(H) =",
            self.m_scrolledWindow1.GetScrollPos(wx.HORIZONTAL),
        )
        print(
            "getscrollpos(V) =",
            self.m_scrolledWindow1.GetScrollPos(wx.VERTICAL),
        )
        print(
            "getscrollrange(H) =",
            self.m_scrolledWindow1.GetScrollRange(wx.HORIZONTAL),
        )
        print(
            "getscrollrange(V) =",
            self.m_scrolledWindow1.GetScrollRange(wx.VERTICAL),
        )
        print(wx.SystemSettings.GetMetric(wx.SYS_VSCROLL_X))
        print(wx.SystemSettings.GetMetric(wx.SYS_HSCROLL_Y))
        event.Skip()

    def event_button_hide_description_click(self, event):
        self.panel_description.Hide()
        self.Layout()

    def event_text_ctrl_on_char(self, event):
        # handle up/down events on
        key = event.GetKeyCode()
        print("key %s pressed" % key)
        global history
        global history_index
        print("history_index =", history_index)
        if key == 315:
            # up key pressed
            if history:
                if history_index is None:
                    history_index = len(history) - 1
                elif history_index > 0:
                    history_index -= 1
                self.text_ctrl_input.SetValue(history[history_index][0])
                self.text_ctrl_input.SetSelection(-1, -1)
        elif key == 317:
            # down key pressed
            if history:
                if history_index < len(history) - 1:
                    history_index += 1
                elif history_index is not None:
                    history_index = len(history) - 1
                self.text_ctrl_input.SetValue(history[history_index][0])
                self.text_ctrl_input.SetSelection(-1, -1)
        elif (
            chr(key) in ucal.infix_operators
            and not self.text_ctrl_input.GetValue()
            and history
        ):
            # an infix operator was pressed and the current text is empty
            value = "(" + history[-1][0] + ")" + chr(key)
            self.text_ctrl_input.SetValue(value)
            self.text_ctrl_input.SetInsertionPoint(-1)
        else:
            # find another handler for this key
            event.Skip()

    def event_button_hide_options_click(self, event):
        self.panel_options.Hide()
        self.menu_file_view_options.Check(False)
        self.Layout()

    def event_menu_file_view_options_selected(self, event):
        if self.menu_file_view_options.IsChecked():
            self.panel_options.Show()
        else:
            self.panel_options.Hide()
        self.Layout()

    def event_text_ctrl_input_on_text_enter(self, event):
        self.calculate_input()

    def event_button_calculate_click(self, event):
        self.calculate_input()

    def event_menu_file_exit_selected(self, event):
        self.Close()

    def calculate_input(self):
        # try to parse new value
        this_input = self.text_ctrl_input.GetValue()
        if not this_input:
            return
        try:
            this_answer = ucal.interpret(this_input)
        except (ucal.ParserError, ucal.QuantityError) as e:
            this_answer = e.args[0]
        except decimal.DecimalException:
            this_answer = "Undefined"
        # add new value
        self.add_history(this_input, this_answer)
        # delete input
        self.text_ctrl_input.SetValue("")

    def clear_history(self):
        """Clear all history."""
        global history_index
        global history
        history_index = None
        history = []
        # remove all elements from the history panel
        sizer_history = self.scrolled_window_history.GetSizer()
        for i in reversed(range(1, sizer_history.GetItemCount())):
            sizer_history.Hide(i)
            sizer_history.Remove(i)
        self.scrolled_window_history.Fit()
        self.scrolled_window_history.Refresh()

    def event_menu_file_clear_selected(self, _event):
        self.clear_history()

    def add_history(self, input_text="Input", result_text="Result"):
        """Add an input and output to the window."""
        global history_index
        global history
        # we're no longer scrolling through the history
        history_index = None
        # add to the local history variable
        history.append((input_text, result_text))
        sizer_history = self.scrolled_window_history.GetSizer()
        # add the input element
        input_element = wx.StaticText(
            self.scrolled_window_history,
            wx.ID_ANY,
            input_text,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.ST_ELLIPSIZE_END,
        )
        input_element.Wrap(-1)
        input_element.SetFont(
            wx.Font(
                9,
                wx.FONTFAMILY_MODERN,
                wx.FONTSTYLE_ITALIC,
                wx.FONTWEIGHT_NORMAL,
                False,
                "Consolas",
            )
        )
        sizer_history.Add(input_element, 0, wx.TOP | wx.LEFT | wx.EXPAND, 10)
        # add the result element
        result_element = wx.StaticText(
            self.scrolled_window_history,
            wx.ID_ANY,
            result_text,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_RIGHT | wx.ST_ELLIPSIZE_START,
        )
        result_element.Wrap(-1)
        result_element.SetFont(
            wx.Font(
                12,
                wx.FONTFAMILY_MODERN,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                False,
                "Consolas",
            )
        )
        sizer_history.Add(
            result_element, 0, wx.BOTTOM | wx.RIGHT | wx.EXPAND, 10
        )
        # refit the window
        self.Layout()
        height = self.scrolled_window_history.GetVirtualSize()[1]
        self.scrolled_window_history.Scroll(0, height)

    # scroll to the bottom of the history window
    def scroll_to_bottom(self):
        height = self.scrolled_window_history.GetVirtualSize()[1]
        self.scrolled_window_history.Scroll(0, height)

    # Virtual event handlers, overide them in your derived class
    def event_window_on_size(self, event):
        event.Skip()
        return
        # set min height of label
        print("\n")
        best_size = self.m_staticText1.GetBestSize()
        print("best_size =", best_size)
        min_size = self.m_staticText1.GetMinSize()
        print("min_size =", min_size)
        size = self.m_staticText1.GetSize()
        print("size =", size)
        size = self.m_staticText1.GetBestHeight(size[0])
        print("size =", size)
        GetMaxSize = self.m_staticText1.GetMaxSize()
        print("GetMaxSize =", GetMaxSize)
        GetMaxClientSize = self.m_staticText1.GetMaxClientSize()
        print("GetMaxClientSize =", GetMaxSize)
        self.panel_description.Fit()
        event.Skip()

    def event_close(self, event):
        store_configuration(self.get_configuration())
        event.Skip()

    def event_key_down(self, event):
        """If Alt was pressed, show the menubar."""
        print('Key %s was prssed.' % event.GetKeyCode())
        event.Skip()


def set_dpi_aware():
    """Make the application DPI aware."""
    print("Registering DPI awareness.")
    if platform.release() == "7":
        ctypes.windll.user32.SetProcessDPIAware()
    elif platform.release() == "8" or platform.release() == "10":
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    else:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)


def run_gui():
    set_dpi_aware()
    # store the system DPI
    global system_dpi
    system_dpi = get_system_dpi()
    app = wx.App()
    window = CalculatorWindow(None)
    # hide the buttons
    window.panel_buttons.Hide()
    window.Layout()
    window.Refresh()
    window.clear_history()
    # apply configuration settings
    try:
        window.apply_configuration(read_configuration())
        print("INI file loaded")
    except configparser.NoOptionError:
        print("Error loading INI file")
        window.apply_configuration(default_configuration)
        print("Default INI file restored")
    # window.SetMinSize(window.GetBestSize())
    window.Show()
    app.MainLoop()


if __name__ == "__main__":
    run_gui()
