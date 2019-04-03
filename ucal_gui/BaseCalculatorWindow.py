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

class BaseCalculatorWindow ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Unit Calculator", pos = wx.DefaultPosition, size = wx.Size( 453,440 ), style = wx.DEFAULT_FRAME_STYLE|wx.CLIP_CHILDREN|wx.NO_FULL_REPAINT_ON_RESIZE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		self.panel_description = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.CLIP_CHILDREN|wx.TAB_TRAVERSAL )
		self.panel_description.Hide()

		sizerDescription = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText1 = wx.StaticText( self.panel_description, wx.ID_ANY, u"Unit Calculator is a calculator\nwith built in unit conversions.", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1.Wrap( -1 )

		sizerDescription.Add( self.m_staticText1, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )

		self.button_hide_description = wx.Button( self.panel_description, wx.ID_ANY, u"Hide", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizerDescription.Add( self.button_hide_description, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )


		self.panel_description.SetSizer( sizerDescription )
		self.panel_description.Layout()
		sizerDescription.Fit( self.panel_description )
		bSizer1.Add( self.panel_description, 0, wx.EXPAND |wx.ALL, 0 )

		self.scrolled_window_history = wx.ScrolledWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.CLIP_CHILDREN|wx.NO_FULL_REPAINT_ON_RESIZE )
		self.scrolled_window_history.SetScrollRate( 5, 5 )
		sizer_history = wx.BoxSizer( wx.VERTICAL )


		sizer_history.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_staticText2 = wx.StaticText( self.scrolled_window_history, wx.ID_ANY, u"Input", wx.DefaultPosition, wx.DefaultSize, wx.ST_ELLIPSIZE_END )
		self.m_staticText2.Wrap( -1 )

		self.m_staticText2.SetFont( wx.Font( 9, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL, False, "Consolas" ) )

		sizer_history.Add( self.m_staticText2, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_staticText3 = wx.StaticText( self.scrolled_window_history, wx.ID_ANY, u"Result", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT|wx.ST_ELLIPSIZE_START )
		self.m_staticText3.Wrap( -1 )

		self.m_staticText3.SetFont( wx.Font( 12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Consolas" ) )

		sizer_history.Add( self.m_staticText3, 0, wx.ALL|wx.EXPAND, 5 )


		self.scrolled_window_history.SetSizer( sizer_history )
		self.scrolled_window_history.Layout()
		sizer_history.Fit( self.scrolled_window_history )
		bSizer1.Add( self.scrolled_window_history, 1, wx.EXPAND |wx.ALL, 5 )

		bSizer4 = wx.BoxSizer( wx.HORIZONTAL )

		self.text_ctrl_input = wx.TextCtrl( self, wx.ID_ANY, u"sqrt(2*g*30ft)", wx.DefaultPosition, wx.DefaultSize, 0|wx.WANTS_CHARS )
		self.text_ctrl_input.SetFont( wx.Font( 9, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Consolas" ) )

		bSizer4.Add( self.text_ctrl_input, 1, wx.ALL|wx.EXPAND, 5 )


		bSizer1.Add( bSizer4, 0, wx.EXPAND, 5 )

		self.panel_buttons = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.panel_buttons.Hide()

		bSizer5 = wx.BoxSizer( wx.HORIZONTAL )

		self.button_calculate = wx.Button( self.panel_buttons, wx.ID_ANY, u"Calculate", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer5.Add( self.button_calculate, 0, wx.ALL, 5 )

		self.m_button3 = wx.Button( self.panel_buttons, wx.ID_ANY, u"Copy to Clipboard", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer5.Add( self.m_button3, 0, wx.ALL, 5 )


		bSizer5.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.button_exit = wx.Button( self.panel_buttons, wx.ID_ANY, u"Exit", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer5.Add( self.button_exit, 0, wx.ALL, 5 )


		self.panel_buttons.SetSizer( bSizer5 )
		self.panel_buttons.Layout()
		bSizer5.Fit( self.panel_buttons )
		bSizer1.Add( self.panel_buttons, 0, wx.EXPAND |wx.ALL, 0 )


		self.SetSizer( bSizer1 )
		self.Layout()
		self.status_bar = self.CreateStatusBar( 1, wx.STB_DEFAULT_STYLE, wx.ID_ANY )
		self.m_menubar1 = wx.MenuBar( 0 )
		self.m_menu1 = wx.Menu()
		self.m_menuItem1 = wx.MenuItem( self.m_menu1, wx.ID_EXIT, u"E&xit", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu1.Append( self.m_menuItem1 )

		self.m_menubar1.Append( self.m_menu1, u"&File" )

		self.SetMenuBar( self.m_menubar1 )


		self.Centre( wx.BOTH )

		# Connect Events
		self.Bind( wx.EVT_SIZE, self.event_window_on_size )
		self.button_hide_description.Bind( wx.EVT_BUTTON, self.event_button_hide_description_click )
		self.text_ctrl_input.Bind( wx.EVT_CHAR, self.event_text_ctrl_on_char )
		self.text_ctrl_input.Bind( wx.EVT_TEXT_ENTER, self.event_text_ctrl_input_on_text_enter )
		self.button_calculate.Bind( wx.EVT_BUTTON, self.event_button_calculate_click )
		self.Bind( wx.EVT_MENU, self.event_menu_file_exit_selected, id = self.m_menuItem1.GetId() )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def event_window_on_size( self, event ):
		event.Skip()

	def event_button_hide_description_click( self, event ):
		event.Skip()

	def event_text_ctrl_on_char( self, event ):
		event.Skip()

	def event_text_ctrl_input_on_text_enter( self, event ):
		event.Skip()

	def event_button_calculate_click( self, event ):
		event.Skip()

	def event_menu_file_exit_selected( self, event ):
		event.Skip()


