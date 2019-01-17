"""
GUI implementation of the functionality in ucal.py.

Usage:
>>> import ucal_gui
>>> ucal_gui.run()

"""


import time
import os
import ctypes
import sys
import platform
import inspect
import textwrap
import math
import decimal
import subprocess

import PySimpleGUI as sg

from ucal_units import units


def run():
    """Start the GUI to begin processing user input."""
    print('Starting GUI...')
    # hold the index of the next answer variable
    # next_answer_index = 0
    history_position = 0
    # hold answer variables ad the input for them
    answer_history = []
    input_history = []
    # set DPI awareness on
    # this DLL only exists on Win8 and newer
    if int(platform.release()) >= 8:
        print('Registering DPI awareness.')
        ctypes.windll.shcore.SetProcessDpiAwareness(True)
    # set user model to something unique so this isn't grouped under Python
    # icons on the taskbar
    myappid = 'unit.calculator'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    # change look and feel
    sg.ChangeLookAndFeel('SandyBeach')
    set_colors(sg)
    sg.SetOptions(element_padding=(0, 0))
    # sg.SetOptions(font=('Helvetica', 12))
    sg.SetOptions(font=get_default_windows_font())
    # window top of layout
    layout = []
    layout.append([sg.Text('Unit Calculator performs calculations taking into '
                           'account units.\nEnter "help" for general help and '
                           '"units" for a list of known units.',
                           size=(56, 2))])
    layout.append([sg.Text(' ', font=('Consolas', 4))])
    # add history entries
    starting_history_index = len(layout)
    for _ in range(displayed_history_length):
        layout.append([sg.Text('',
                               justification='left',
                               font=history_font,
                               size=(int(history_width / history_font[1] +
                                         0.5),
                                     1))])
        layout.append([sg.Text('',
                               justification='right',
                               font=result_font,
                               size=(int(history_width / result_font[1] + 0.5),
                                     1))])
        layout.append([sg.Text(' ', font=('Consolas', 4))])
    # add input field
    layout.append([sg.Text(' ', font=('Consolas', 4))])
    input_width = int(history_width / input_font[1] + 0.5)
    input_element = sg.InputText(font=input_font,
                                 justification='left',
                                 size=(input_width, 1))
    layout.append([input_element])
    # add buttons
    layout.append([sg.Text(' ', font=('Consolas', 4))])
    buttons = dict()
    buttons['calculate'] = sg.Button('Calculate', bind_return_key=True)
    layout.append([buttons['calculate'],
                   sg.Text('  ' * 1),
                   sg.ReadButton('Copy to Clipboard'),
                   sg.Text(' ' * 71),
                   sg.ReadButton('Exit')])
    layout.append([sg.Text(' ', font=('Consolas', 4))])
    icon_filename = r'ucal.ico'
    icon_path = os.path.join(base_path, icon_filename)
    if os.path.isfile(icon_path):
        print('Using icon at %s.' % (icon_path))
    else:
        icon_path = os.path.join(os.path.dirname(__file__), icon_filename)
        if not os.path.isfile(icon_path):
            print('Icon file "%s" not found.' % (icon_path))
            icon_path = None
        else:
            print('Using icon at %s.' % (icon_path))
    window = sg.Window('Unit Calculator',
                       return_keyboard_events=True,
                       icon=icon_path)
    # pady=0, relief='flat'
    # buttons['calculate'].TKroot
    window.Layout(layout)
    # input_element.SetFocus()
    window.Show(layout)
    window.TKroot.focus_force()
    # first_loop = True
    while True:
        # read current state
        button, value = window.Read()
        # if first_loop:
        #    first_loop = False
        #    input_element.SetFocus()
        # detect window X button pressed to close window
        if value is None:
            break
        # loop until something is pressed
        if button is None:
            continue
        # print(type(button), button)
        # if button:
        #    print(button, [ord(c) for c in button])
        # if we enter an infix operator, insert the previous answer first
        if button and input_element.Get() == button and input_history:
            if button in infix_operators:
                input_element.Update('(%s)%s' % (answer_history[-1], button))
                input_element.TKEntry.icursor('end')
        # process keyboard shortcuts into button names
        if button == chr(3) and value[0] == '':
            button = 'Copy to Clipboard'
        if button == chr(13):
            button = 'Calculate'
        if button == chr(27):
            button = 'Exit'
        # handle up
        if button == 'Up:38' and history_position < len(input_history):
            history_position += 1
            new_text = input_history[-history_position]
            input_element.Update(new_text)
            # layout[input_index][0].TKEntry.mark_set('insert',
            #                                        '1.%d' % len(new_text))
            # layout[input_index][0].TKEntry.select_range(0, 'end')
            input_element.TKEntry.selection_clear()
            input_element.TKEntry.icursor('end')
            # layout[input_index][0].TKEntry.tag_add('sel',
            #                                       '1.1',
            #                                       '1.%d' % (len(new_text)))
            # layout[input_index][0].TKEntry.selection_range(0, 'end')
        if button == 'Down:40' and history_position > 0:
            history_position -= 1
            if history_position > 0:
                new_text = input_history[-history_position]
            else:
                new_text = ''
            input_element.Update(new_text)
            input_element.TKEntry.selection_clear()
            input_element.TKEntry.icursor('end')
        # copy to clipboard
        if button == 'Copy to Clipboard' and answer_history and not value[0]:
            # print('<Ctrl+C>')
            new_text = answer_history[-1]
            set_clipboard_text(new_text)
            history_position = 0
            input_element.Update(new_text)
            input_element.TKEntry.select_range(0, 'end')
            input_element.TKEntry.icursor('end')
            pass
        # if "exit" was entered, then exit
        if button == 'Calculate' and value[0].lower() == 'exit':
            button = 'Exit'
        # if "units" was entered, show units
        if button == 'Calculate' and value[0].lower() == 'units':
            button = 'Units'
            input_element.Update('')
        if button == 'Units':
            # window.TKroot.grab_set_global()
            # window.Disable()
            show_units_gui()
            # window.self.TKroot.grab_release()
        # exit
        if button == 'Exit':
            break
        # calculate values if requested
        if button == 'Calculate' and value[0]:
            # reset history position
            history_position = 0
            # try to parse new value
            this_input = value[0]
            this_answer = None
            # error = False
            try:
                this_answer = process_user_equation(this_input)
            except (ParserError, QuantityError) as e:
                # error = True
                this_answer = e.args[0]
            except (decimal.DecimalException) as e:
                this_answer = 'Undefined'
            # shift history values up one
            i = starting_history_index
            for _ in range(displayed_history_length - 1):
                layout[i][0].Update(layout[i + 3][0].DisplayText)
                i += 1
                layout[i][0].Update(layout[i + 3][0].DisplayText)
                i += 2
            answer_history.append(this_answer)
            input_history.append(this_input)
            layout[i][0].Update(this_input)
            layout[i + 1][0].Update('%s' % (this_answer))
            # add new answer variable
            # next_answer_index += 1
            # clear input field
            input_element.Update('')
    # print(button)
    window.CloseNonBlockingForm()


# if this is run as a script, start the gui
if __name__ == "__main__":
    run()
