# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Oct 26 2018)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class BaseCalculatorWindow
###########################################################################


class BaseCalculatorWindow(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            title=u"Unit Calculator",
            pos=wx.DefaultPosition,
            size=wx.Size(475, 494),
            style=wx.DEFAULT_FRAME_STYLE
            | wx.CLIP_CHILDREN
            | wx.NO_FULL_REPAINT_ON_RESIZE
            | wx.TAB_TRAVERSAL,
        )

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(
            wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE)
        )

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        self.panel_description = wx.Panel(
            self,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.CLIP_CHILDREN | wx.TAB_TRAVERSAL,
        )
        self.panel_description.Hide()

        sizerDescription = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText1 = wx.StaticText(
            self.panel_description,
            wx.ID_ANY,
            u'Unit Calculator performs calculations taking into account units.\nEnter "help" for general help and "units" for a list of defined units.',
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.ST_ELLIPSIZE_END,
        )
        self.m_staticText1.Wrap(-1)

        sizerDescription.Add(
            self.m_staticText1,
            1,
            wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND,
            5,
        )

        self.button_hide_description = wx.Button(
            self.panel_description,
            wx.ID_ANY,
            u"Hide",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        sizerDescription.Add(
            self.button_hide_description,
            0,
            wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL,
            5,
        )

        self.panel_description.SetSizer(sizerDescription)
        self.panel_description.Layout()
        sizerDescription.Fit(self.panel_description)
        bSizer1.Add(self.panel_description, 0, wx.EXPAND | wx.ALL, 0)

        self.scrolled_window_history = wx.ScrolledWindow(
            self,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.CLIP_CHILDREN | wx.NO_FULL_REPAINT_ON_RESIZE,
        )
        self.scrolled_window_history.SetScrollRate(5, 5)
        sizer_history = wx.BoxSizer(wx.VERTICAL)

        sizer_history.Add((0, 0), 1, wx.EXPAND, 5)

        self.m_staticText2 = wx.StaticText(
            self.scrolled_window_history,
            wx.ID_ANY,
            u"Input",
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.ST_ELLIPSIZE_END,
        )
        self.m_staticText2.Wrap(-1)

        self.m_staticText2.SetFont(
            wx.Font(
                9,
                wx.FONTFAMILY_MODERN,
                wx.FONTSTYLE_ITALIC,
                wx.FONTWEIGHT_NORMAL,
                False,
                "Consolas",
            )
        )

        sizer_history.Add(self.m_staticText2, 0, wx.ALL | wx.EXPAND, 5)

        self.m_staticText3 = wx.StaticText(
            self.scrolled_window_history,
            wx.ID_ANY,
            u"Result",
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_RIGHT | wx.ST_ELLIPSIZE_START,
        )
        self.m_staticText3.Wrap(-1)

        self.m_staticText3.SetFont(
            wx.Font(
                12,
                wx.FONTFAMILY_MODERN,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                False,
                "Consolas",
            )
        )

        sizer_history.Add(self.m_staticText3, 0, wx.ALL | wx.EXPAND, 5)

        self.scrolled_window_history.SetSizer(sizer_history)
        self.scrolled_window_history.Layout()
        sizer_history.Fit(self.scrolled_window_history)
        bSizer1.Add(self.scrolled_window_history, 1, wx.EXPAND | wx.ALL, 5)

        bSizer4 = wx.BoxSizer(wx.HORIZONTAL)

        self.text_ctrl_input = wx.TextCtrl(
            self,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            0 | wx.WANTS_CHARS,
        )
        self.text_ctrl_input.SetFont(
            wx.Font(
                12,
                wx.FONTFAMILY_MODERN,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                False,
                "Consolas",
            )
        )

        bSizer4.Add(self.text_ctrl_input, 1, wx.ALL | wx.EXPAND, 10)

        bSizer1.Add(bSizer4, 0, wx.EXPAND, 5)

        self.panel_options = wx.Panel(
            self,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TAB_TRAVERSAL,
        )
        sbSizer1 = wx.StaticBoxSizer(
            wx.StaticBox(self.panel_options, wx.ID_ANY, u"Options"),
            wx.VERTICAL,
        )

        self.checkbox_remember_window_position = wx.CheckBox(
            sbSizer1.GetStaticBox(),
            wx.ID_ANY,
            u"Save window size and position",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.checkbox_remember_window_position.SetValue(True)
        sbSizer1.Add(self.checkbox_remember_window_position, 0, wx.ALL, 5)

        self.checkbox_save_history = wx.CheckBox(
            sbSizer1.GetStaticBox(),
            wx.ID_ANY,
            u"Save history between sessions",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.checkbox_save_history.SetValue(True)
        sbSizer1.Add(self.checkbox_save_history, 0, wx.ALL, 5)

        bSizer9 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText21 = wx.StaticText(
            sbSizer1.GetStaticBox(),
            wx.ID_ANY,
            u"Limit history to",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.m_staticText21.Wrap(-1)

        bSizer9.Add(self.m_staticText21, 0, wx.ALL, 5)

        self.spin_ctrl_history_capacity = wx.SpinCtrl(
            sbSizer1.GetStaticBox(),
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.SP_ARROW_KEYS,
            0,
            10000,
            1000,
        )
        bSizer9.Add(self.spin_ctrl_history_capacity, 0, wx.ALL, 5)

        self.m_staticText22 = wx.StaticText(
            sbSizer1.GetStaticBox(),
            wx.ID_ANY,
            u"entries.",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.m_staticText22.Wrap(-1)

        bSizer9.Add(self.m_staticText22, 0, wx.ALL, 5)

        bSizer9.Add((0, 0), 1, wx.EXPAND, 5)

        sbSizer1.Add(bSizer9, 1, wx.EXPAND, 5)

        self.checkbox_hide_menu_bar = wx.CheckBox(
            sbSizer1.GetStaticBox(),
            wx.ID_ANY,
            u"Hide menu bar until Alt is pressed",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.checkbox_hide_menu_bar.SetValue(True)
        self.checkbox_hide_menu_bar.Hide()

        sbSizer1.Add(self.checkbox_hide_menu_bar, 0, wx.ALL, 5)

        self.button_hide_options = wx.Button(
            sbSizer1.GetStaticBox(),
            wx.ID_ANY,
            u"Hide options",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        sbSizer1.Add(self.button_hide_options, 0, wx.ALL, 5)

        self.panel_options.SetSizer(sbSizer1)
        self.panel_options.Layout()
        sbSizer1.Fit(self.panel_options)
        bSizer1.Add(self.panel_options, 0, wx.ALL | wx.EXPAND, 0)

        self.panel_buttons = wx.Panel(
            self,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TAB_TRAVERSAL,
        )
        self.panel_buttons.Hide()

        bSizer5 = wx.BoxSizer(wx.HORIZONTAL)

        self.button_calculate = wx.Button(
            self.panel_buttons,
            wx.ID_ANY,
            u"Calculate",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        bSizer5.Add(self.button_calculate, 0, wx.ALL, 5)

        self.m_button3 = wx.Button(
            self.panel_buttons,
            wx.ID_ANY,
            u"Copy to Clipboard",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        bSizer5.Add(self.m_button3, 0, wx.ALL, 5)

        bSizer5.Add((0, 0), 1, wx.EXPAND, 5)

        self.button_exit = wx.Button(
            self.panel_buttons,
            wx.ID_ANY,
            u"Exit",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        bSizer5.Add(self.button_exit, 0, wx.ALL, 5)

        self.panel_buttons.SetSizer(bSizer5)
        self.panel_buttons.Layout()
        bSizer5.Fit(self.panel_buttons)
        bSizer1.Add(self.panel_buttons, 0, wx.EXPAND | wx.ALL, 0)

        self.SetSizer(bSizer1)
        self.Layout()
        self.status_bar = self.CreateStatusBar(
            1, wx.STB_DEFAULT_STYLE, wx.ID_ANY
        )
        self.status_bar.Hide()

        self.menubar = wx.MenuBar(0)
        self.menu_file = wx.Menu()
        self.menu_file_clear = wx.MenuItem(
            self.menu_file,
            wx.ID_ANY,
            u"&Clear",
            wx.EmptyString,
            wx.ITEM_NORMAL,
        )
        self.menu_file.Append(self.menu_file_clear)

        self.menu_file_view_options = wx.MenuItem(
            self.menu_file,
            wx.ID_ANY,
            u"&View options",
            wx.EmptyString,
            wx.ITEM_CHECK,
        )
        self.menu_file.Append(self.menu_file_view_options)

        self.menu_file.AppendSeparator()

        self.menu_file_exit = wx.MenuItem(
            self.menu_file,
            wx.ID_EXIT,
            u"E&xit",
            wx.EmptyString,
            wx.ITEM_NORMAL,
        )
        self.menu_file.Append(self.menu_file_exit)

        self.menubar.Append(self.menu_file, u"&File")

        self.SetMenuBar(self.menubar)

        self.Centre(wx.BOTH)

        # Connect Events
        self.Bind(wx.EVT_CLOSE, self.event_close)
        self.Bind(wx.EVT_KEY_DOWN, self.event_key_down)
        self.Bind(wx.EVT_SIZE, self.event_window_on_size)
        self.button_hide_description.Bind(
            wx.EVT_BUTTON, self.event_button_hide_description_click
        )
        self.text_ctrl_input.Bind(wx.EVT_CHAR, self.event_text_ctrl_on_char)
        self.text_ctrl_input.Bind(
            wx.EVT_TEXT_ENTER, self.event_text_ctrl_input_on_text_enter
        )
        self.button_hide_options.Bind(
            wx.EVT_BUTTON, self.event_button_hide_options_click
        )
        self.button_calculate.Bind(
            wx.EVT_BUTTON, self.event_button_calculate_click
        )
        self.button_exit.Bind(wx.EVT_BUTTON, self.event_button_exit_click)
        self.menubar.Bind(wx.EVT_KILL_FOCUS, self.event_menubar_kill_focus)
        self.menubar.Bind(wx.EVT_SET_FOCUS, self.event_menubar_set_focus)
        self.Bind(
            wx.EVT_MENU,
            self.event_menu_file_clear_selected,
            id=self.menu_file_clear.GetId(),
        )
        self.Bind(
            wx.EVT_MENU,
            self.event_menu_file_view_options_selected,
            id=self.menu_file_view_options.GetId(),
        )
        self.Bind(
            wx.EVT_MENU,
            self.event_menu_file_exit_selected,
            id=self.menu_file_exit.GetId(),
        )

    def __del__(self):
        pass

        # Virtual event handlers, overide them in your derived class

    def event_close(self, event):
        event.Skip()

    def event_key_down(self, event):
        event.Skip()

    def event_window_on_size(self, event):
        event.Skip()

    def event_button_hide_description_click(self, event):
        event.Skip()

    def event_text_ctrl_on_char(self, event):
        event.Skip()

    def event_text_ctrl_input_on_text_enter(self, event):
        event.Skip()

    def event_button_hide_options_click(self, event):
        event.Skip()

    def event_button_calculate_click(self, event):
        event.Skip()

    def event_button_exit_click(self, event):
        event.Skip()

    def event_menubar_kill_focus(self, event):
        event.Skip()

    def event_menubar_set_focus(self, event):
        event.Skip()

    def event_menu_file_clear_selected(self, event):
        event.Skip()

    def event_menu_file_view_options_selected(self, event):
        event.Skip()

    def event_menu_file_exit_selected(self, event):
        event.Skip()
