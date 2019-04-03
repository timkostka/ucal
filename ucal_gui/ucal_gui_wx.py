"""
This is a class derived from CalculatorWindowBase.

"""

import os
import ctypes
import platform
import decimal
import sys

import wx

import ucal

from BaseCalculatorWindow import BaseCalculatorWindow


# Windows default DPI
default_dpi = 96

# DPI setting for this system
system_dpi = default_dpi


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
        #self.scrolled_window_history.SetDoubleBuffered(True)
        self.SetDoubleBuffered(True)
        self.text_ctrl_input.SetFocus()
        self.text_ctrl_input.SetInsertionPoint(-1)

        # set the program icon
        icon_filename = find_file('ucal.ico')
        if icon_filename:
            self.SetIcon(wx.Icon(icon_filename))
        else:
            print('ERROR: could not find icon file')

        # delete last two items in history and save their styles
        #input_element, result_element = self.scrolled_window_history.GetChildren()
        #self.history_input_style = input_element.GetWindowStyle()
        #self.history_input_font = input_element.GetFont()
        #self.history_input_sizer_style = input_element.GetContainingSizer().GetWindowStyle()
        #print(self.history_input_style, self.history_input_font, self.history_input_sizer_style)
        #self.history_result_style = result_element.GetWindowStyle()

        self.clear_history()


    # Virtual event handlers, overide them in your derived class
    def event_on_size(self, event):
        event.Skip()
        return
        client_size = self.m_scrolledWindow1.GetClientSize()
        print('\nclient_size =', client_size)
        print('getscrollpos(H) =', self.m_scrolledWindow1.GetScrollPos(wx.HORIZONTAL))
        print('getscrollpos(V) =', self.m_scrolledWindow1.GetScrollPos(wx.VERTICAL))
        print('getscrollrange(H) =', self.m_scrolledWindow1.GetScrollRange(wx.HORIZONTAL))
        print('getscrollrange(V) =', self.m_scrolledWindow1.GetScrollRange(wx.VERTICAL))
        print(wx.SystemSettings.GetMetric(wx.SYS_VSCROLL_X))
        print(wx.SystemSettings.GetMetric(wx.SYS_HSCROLL_Y))
        event.Skip()

    def event_button_hide_description_click(self, event):
        self.panel_description.Hide()
        self.Layout()
        #event.Skip()

    def event_text_ctrl_on_char(self, event):
        key = event.GetKeyCode()
        if key == 13:
            # enter key was pressed
            self.calculate_input()
        else:
            event.Skip()

    def event_text_ctrl_input_enter(self, event):
        event.Skip()

    def event_button_calculate_click(self, event):
        self.calculate_input()
        # event.Skip()

    def event_menu_file_exit_selected(self, event):
        self.Close()
        #event.Skip()

    def calculate_input(self):
        # reset history position
        history_position = 0
        # try to parse new value
        this_input = self.text_ctrl_input.GetValue()
        if not this_input:
            return
        try:
            this_answer = ucal.interpret(this_input)
        except (ucal.ParserError, ucal.QuantityError) as e:
            this_answer = e.args[0]
        except decimal.DecimalException:
            this_answer = 'Undefined'
        # add new value
        self.add_history(this_input, this_answer)
        #self.scroll_to_bottom()

    def add_history(self, input_text="Input", result_text="Result"):
        """Add an input and output to the window."""
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
        sizer_history.Add(result_element, 0, wx.BOTTOM | wx.RIGHT | wx.EXPAND, 10)
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
        print('\n')
        best_size = self.m_staticText1.GetBestSize()
        print('best_size =', best_size)
        min_size = self.m_staticText1.GetMinSize()
        print('min_size =', min_size)
        size = self.m_staticText1.GetSize()
        print('size =', size)
        size = self.m_staticText1.GetBestHeight(size[0])
        print('size =', size)
        GetMaxSize = self.m_staticText1.GetMaxSize()
        print('GetMaxSize =', GetMaxSize)
        GetMaxClientSize = self.m_staticText1.GetMaxClientSize()
        print('GetMaxClientSize =', GetMaxSize)
        self.panel_description.Fit()
        event.Skip()


    def clear_history(self):
        """Clear the history list."""
        sizer = self.scrolled_window_history.GetSizer()
        for i in reversed(range(1, sizer.GetItemCount())):
            sizer.Hide(i)
            sizer.Remove(i)
        self.scrolled_window_history.Fit()


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
    window.clear_history()
    history_count = 5
    for i in range(history_count):
        window.add_history("History %d" % i, 'Result %d' % i)
    # add sizer to scrolled window
    print(window.GetBestSize())
    # window.SetMinSize(window.GetBestSize())
    window.Show()
    app.MainLoop()


if __name__ == "__main__":
    run_gui()
