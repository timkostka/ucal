"""
The ucal module evaluates expressions with automatic unit conversions.

Typically, this module is used from ucal_gui.py to perform calculations,
however it can also be used as a standalone module.

Usage:
>>> import ucal
>>> ucal.evaluate("5km in mi")
'3.10686 mi'
>>> ucal.evaluate("sqrt(2 * g * 30ft) in fps")
'43.9367 fps'
>>> ucal.evaluate("5V * 500mA")
'2.5 W'
>>> ucal.evaluate("1mi + 10km")
'11609.344 m'

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

"""
def get_clipboard_text():
    CF_TEXT = 1
    text = ''
    if ctypes.windll.user32.OpenClipboard(ctypes.c_int(0)):
        h_clip_mem = ctypes.windll.user32.GetClipboardData(CF_TEXT)
        ctypes.windll.kernel32.GlobalLock.restype = ctypes.c_char_p
        #text = ctypes.wstring_at(ctypes.windll.kernel32.GlobalLock(h_clip_mem))
        text = ctypes.windll.kernel32.GlobalLock(ctypes.c_int(h_clip_mem))
        #ctypes.windll.kernel32.GlobalUnlock(h_clip_mem)
        ctypes.windll.kernel32.GlobalUnlock(ctypes.c_int(h_clip_mem))
        ctypes.windll.user32.CloseClipboard()
        text = text.decode('utf-8')
    return text
"""


def set_clipboard_text(text):
    os.system('echo | set /p="' + text + '" | clip')
    return
    subprocess.Popen(['clip'],
                     stdin=subprocess.PIPE,
                     encoding='utf8').communicate(text)
    return
    CF_UNICODETEXT = 13
    GMEM_DDESHARE = 0x2000
    if not isinstance(text, str):
        text = text.decode('mbcs')
    ctypes.windll.user32.OpenClipboard(None)
    ctypes.windll.user32.EmptyClipboard()
    hCd = ctypes.windll.kernel32.GlobalAlloc(GMEM_DDESHARE,
                                             2 * (len(text) + 1))
    pchData = ctypes.windll.kernel32.GlobalLock(hCd)
    text = ctypes.c_wchar_p(text)
    print(type(text))
    print(type(pchData))
    print(pchData)
    print([c for c in pchData])
    # print(type(ctypes.c_wchar_p(pchData)))
    # ctypes.cdll.msvcrt.wcscpy(pchData, text)
    ctypes.c_wchar_p(pchData)
    ctypes.cdll.msvcrt.wcscpy(ctypes.c_wchar_p(pchData), text)
    ctypes.windll.kernel32.GlobalUnlock(hCd)
    ctypes.windll.user32.SetClipboardData(CF_UNICODETEXT, hCd)
    # ctypes.windll.user32.SetClipboardText(CF_UNICODETEXT, hCd)
    ctypes.windll.user32.CloseClipboard()


if False:
    print(get_clipboard_text())
    set_clipboard_text('hello world!')
    print(get_clipboard_text())
    set_clipboard_text('goodbye world!')
    print(get_clipboard_text())

# working precision in base-10 decimal units
working_precision_digits = 32

# output precision in base-10 decimal units
output_precision_digits = 16

# if True, will replace non-infix % with (1/100)
allow_percent = True

# if True, show some timing information
show_timings = False

# if True, will show debug output
debug_output = False

# if True, unit tests will be run
run_unit_tests = True

# displayed history length
displayed_history_length = 8

# font for history input
history_font = ('Consolas Italic', 10)

# font for history results
result_font = ('Consolas', 13)

# font for current input
input_font = ('Consolas', 16)

# width of history lines in character points
history_width = 60 * 10

##################
# END OF OPTIONS #
##################

print('Unit calculator starting...')
print('We are at %s.' % (os.getcwd()))

try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    base_path = sys._MEIPASS
except Exception:
    base_path = os.path.abspath(".")
print('Local files are at %s.' % (base_path))

print('Windows release is %s.' % (platform.release()))

# def set_clipboard(text):
#    """Set the clipboard to the given text."""
#    subprocess.Popen(['clip'],
#                     stdin=subprocess.PIPE,
#                     encoding='utf8').communicate(text)
#    #os.system('echo | set /p="' + text + '" | clip')


def show_units_gui():
    """Show a window with all units defined."""
    layout = []
    global units
    layout.append([sg.Text('The following units and variables are defined.')])
    layout.append([sg.Text(' ', font=('Consolas', 4))])
    unit_names = sorted(unit_def.keys())
    # target line length in characters
    max_line_length = 50
    i = 0
    while i < len(unit_names) - 1:
        if i >= len(unit_names) - 1:
            continue
        if len(unit_names[i]) + 2 + len(unit_names[i + 1]) <= max_line_length:
            unit_names[i] += ', ' + unit_names[i + 1]
            del unit_names[i + 1]
        else:
            i += 1
    unit_names = '\n'.join(unit_names)
    # print(unit_names)
    layout.append([sg.Text(unit_names)])
    layout.append([sg.Text(' ', font=('Consolas', 4))])
    layout.append([sg.OK(), sg.Text(' ', font=('Consolas', 4)), sg.Cancel()])
    layout.append([sg.Text(' ', font=('Consolas', 4))])
    window = sg.Window('Units defined')
    window.Layout(layout)
    window.Read(timeout=0)
    window.TKroot.grab_set()
    window.Read()
    window.TKroot.grab_release()
    window.Close()


def set_colors(sg):
    """Set the color scheme."""
    # this scheme is similar to Windows default colors
    sg.SetOptions(background_color='#F0F0F0',
                  text_element_background_color='#F0F0F0',
                  element_background_color='#F0F0F0',
                  text_color='#000000',
                  input_elements_background_color='#FFFFFF',
                  button_color=('#000000', '#E1E1E1'))


def run_gui():
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


class QuantityError(Exception):
    """
    This is a custom Exception for the Quantity class.

    The arguments should be [title, message, optional_value].

    """
    pass


class ParserError(Exception):
    """This is a custom Exception for the parser module."""
    pass


def framed_message(messages, width=79):
    """Print out a formatted message which fits in a specified width."""
    # format messages
    if not isinstance(messages, list):
        messages = [messages]
    for i in range(len(messages)):
        if not isinstance(messages[i], tuple):
            messages[i] = ('', messages[i])
    # store the message width
    max_header_width = max(len(x[0]) for x in messages)
    width = max(width, max_header_width + 20 + 6)
    # print the top frame after a blank line
    print('')
    print('*' * width)
    print('*' + (' ' * (width - 2)) + '*')
    # process each message
    # *  Header: Text             *
    for message in messages:
        header = message[0]
        # format text into broken lines
        text = ''
        for line in message[1].split('\n'):
            text += textwrap.fill(
                line,
                width=width - 6 - len(header))
            text += '\n'
        # remove trailing newlines
        while text and text[-1] == '\n':
            text = text[:-1]
        # break into a list
        text = text.split('\n')
        # process each line
        for i in range(len(text)):
            if i == 0:
                line = '%s%s' % (header, text[i])
            else:
                line = '%s%s' % (' ' * len(header), text[i])
            if len(line) < width - 6:
                line += ' ' * (width - 6 - len(line))
            print('*  %s  *' % (line))
        print('*' + (' ' * (width - 2)) + '*')
    # print the bottom frame
    print('*' * width)


def get_trace(omitted_frames=1):
    """Return a compressed stack trace."""
    last_file = ''
    message = ''
    for frame in inspect.stack()[omitted_frames:]:
        this_file = frame[1].split('/')[-1]
        if this_file != last_file:
            message += this_file + ':'
            last_file = this_file
        else:
            message += ' ' * len(last_file) + ' '
        message += frame[3] + ':' + str(frame[2])
        message += '\n'
    return message


def error_message(title, message):
    """Print out a formatted error message and return."""
    framed_message([title, message])
    print(get_trace())


class Quantity:
    """A Quantity represents a physical quantity--a number with units."""

    def __init__(self, text='', value=decimal.Decimal(0), units=None):
        """Initialize."""
        if not text:
            self.value = value
            if units is not None:
                self.units = units
            else:
                self.units = [0.0] * unit_count
        else:
            self = Quantity.evaluate(text)

    def __str__(self):
        """Convert to a human-readable string."""
        upper_units = []
        for x, y in zip(self.units, base_units):
            if x == int(x):
                x = int(x)
            if x == 0.0:
                continue
            elif x == 1.0:
                upper_units.append(y)
            elif x == -1.0:
                upper_units.append('%s^-1' % y)
            elif x > 0:
                upper_units.append('%s^%s' % (y, x))
            else:
                upper_units.append('%s^%s' % (y, x))
        value_str = '0' if self.value == 0 else str(self.value)
        if 'E' in value_str:
            base, exponent = value_str.split('E')
            exponent = str(int(exponent))
            if '.' in base:
                base = base.rstrip('0').rstrip('.')
            value_str = base + 'e' + exponent
        elif '.' in value_str:
            value_str = value_str.rstrip('0').rstrip('.')
        if upper_units:
            return value_str + ' ' + ' '.join(upper_units)
        else:
            return value_str

    def __repr__(self):
        return 'Quantity(' + str(self) + ')'

    def __add__(self, other):
        if self.units != other.units:
            raise QuantityError('Inconsistent units', self, other)
        return Quantity(value=self.value + other.value, units=list(self.units))

    def __sub__(self, other):
        if self.units != other.units:
            raise QuantityError('Inconsistent units', self, other)
        return Quantity(value=self.value - other.value, units=list(self.units))

    def __mul__(self, other):
        return Quantity(value=self.value * other.value,
                        units=[x + y for x, y in zip(self.units, other.units)])

    def __div__(self, other):
        return Quantity(value=self.value / other.value,
                        units=[x - y for x, y in zip(self.units, other.units)])

    def __neg__(self):
        return Quantity(value=-self.value, units=self.units)

    def __pos__(self):
        return Quantity(value=+self.value, units=self.units)

    def __mod__(self, other):
        if self.units != other.units:
            raise QuantityError('Inconsistent units', self, other)
        return Quantity(value=self.value % other.value,
                        units=[0.0] * unit_count)

    def __pow__(self, other):
        if other.units != [0.0] * unit_count:
            raise QuantityError('Inconsistent units',
                                'Values in the exponent must be unitless.',
                                self)
        return Quantity(value=self.value ** other.value,
                        units=[x * float(other.value) for x in self.units])

    def factorial(self):
        if self.units != [0.0] * unit_count:
            raise QuantityError('Inconsistent units', self)
        if self.value.to_integral_value() != self.value or self.value < 0:
            raise QuantityError('Invalid value', self)
        new_value = decimal.Decimal('1')
        while self.value > 1:
            new_value *= self.value
            self.value -= 1
        return Quantity(value=new_value,
                        units=[0.0] * unit_count)

    # function are given with the prefix "function_"
    # for example, "sqrt(value)" would call "value.function_sqrt()"
    def function_sqrt(self):
        return Quantity(value=self.value.sqrt(),
                        units=[x / 2.0 for x in self.units])

    def function_exp(self):
        if self.units != [0.0] * unit_count:
            raise QuantityError('Inconsistent units',
                                'Exponent values must be unitless.',
                                self)
        return Quantity(value=self.value.exp(),
                        units=self.units)

    def function_abs(self):
        return Quantity(value=abs(self.value),
                        units=self.units)

    def function_ln(self):
        if self.units != [0.0] * unit_count:
            raise QuantityError('Inconsistent units', self)
        return Quantity(value=self.value.ln(),
                        units=self.units)

    def function_log(self):
        return self.function_ln()

    def function_log10(self):
        if self.units != [0.0] * unit_count:
            raise QuantityError('Inconsistent units', self)
        return Quantity(value=self.value.log10(),
                        units=self.units)

    def function_atan2(self, other):
        if self.units != [0.0] * unit_count:
            raise QuantityError('Inconsistent units', self, other)
        if other.units != [0.0] * unit_count:
            raise QuantityError('Inconsistent units', self, other)
        return Quantity(value=math.atan2(self.value, other.value))


class Token:
    """The Token class defines various token types."""
    opening_parenthesis = '('
    closing_parenthesis = ')'
    function = 'function'
    variable = 'variable'
    value = 'value'
    infix_operator = 'infix_op'
    prefix_operator = 'prefix_op'
    postfix_operator = 'postfix_op'


# syntax rules for what can follow
token_can_follow = dict()
token_can_follow[Token.opening_parenthesis] = {Token.function,
                                               Token.variable,
                                               Token.value,
                                               Token.prefix_operator,
                                               Token.opening_parenthesis}
token_can_follow[Token.closing_parenthesis] = {Token.closing_parenthesis,
                                               Token.infix_operator,
                                               Token.postfix_operator,
                                               Token.closing_parenthesis}
token_can_follow[Token.function] = {Token.opening_parenthesis}
token_can_follow[Token.variable] = {Token.closing_parenthesis,
                                    Token.infix_operator,
                                    Token.postfix_operator}
token_can_follow[Token.value] = token_can_follow[Token.variable]
token_can_follow[Token.infix_operator] = {Token.opening_parenthesis,
                                          Token.function,
                                          Token.variable,
                                          Token.value,
                                          Token.prefix_operator}
token_can_follow[Token.prefix_operator] = {Token.opening_parenthesis,
                                           Token.function,
                                           Token.variable,
                                           Token.value}
token_can_follow[Token.postfix_operator] = {Token.closing_parenthesis,
                                            Token.infix_operator}

# allowable tokens at the start of an equation
token_can_start = token_can_follow[Token.infix_operator]

# allowable tokens at the end of an equation
token_can_end = {Token.closing_parenthesis,
                 Token.variable,
                 Token.value,
                 Token.postfix_operator}

# define temperature unit conversion
# temperature_units = dict()
# temperature_units['degC'] = ['(K * 1 - 273.15)']
# temperature_units['degF'] = ['((K * 1 - 273.15 + 40) * 9 / 5 - 40)']

# default unit systems
unit_systems = dict()
unit_systems['SI'] = ['kg', 'm', 's', 'A', 'K', 'mol', 'cd', 'byte']

# unit measures
unit_measure = dict()
unit_measure['N'] = 'force'
unit_measure['W'] = 'power'
unit_measure['J'] = 'energy'
unit_measure['m'] = 'length'
unit_measure['kg'] = 'mass'
unit_measure['s'] = 'time'
unit_measure['A'] = 'current'
unit_measure['K'] = 'temperature'
unit_measure['mol'] = 'amount'
unit_measure['cd'] = 'intensity'
unit_measure['m^2'] = 'area'
unit_measure['m^3'] = 'volume'
unit_measure['m/s'] = 'velocity'
unit_measure['m/s^2'] = 'acceleration'
unit_measure['kg/m^3'] = 'mass density'
unit_measure['Pa'] = 'stress'
unit_measure['V'] = 'electric potential'
unit_measure['F'] = 'capacitance'
unit_measure['Ohm'] = 'electric resistance'
unit_measure['H'] = 'inductance'
unit_measure['Mbps'] = 'data rate'
unit_measure['byte'] = 'data'

# get a set of all units
all_units = set()
all_units.update(units.keys())
for x in unit_systems.values():
    all_units.update(x)

# target base unit system
base_units = unit_systems['SI']

# get number of units
unit_count = len(base_units)

# prefix operators and their corresponding precedence and functions
prefix_operators = dict()

prefix_operators['-'] = (2, Quantity.__neg__)
prefix_operators['+'] = (2, Quantity.__pos__)

# infix operators and their corresponding precedence and functions
infix_operators = dict()

infix_operators['+'] = (4, Quantity.__add__)
infix_operators['-'] = (4, Quantity.__sub__)
infix_operators['/'] = (3, Quantity.__div__)
infix_operators['*'] = (3, Quantity.__mul__)
infix_operators['%'] = (3, Quantity.__mod__)
infix_operators['^'] = (1, Quantity.__pow__)

# postfix operators and their corresponding precedence and functions
postfix_operators = dict()

postfix_operators['!'] = (1, Quantity.factorial)

# valid starting characters for variables and functions
starting_variable_characters = ('abcdefghijklmnopqrstuvwxyz'
                                'ABCDEFGHIJKLMNOPQRSTUVWXYZ')

# valid following characters for variables and functions
following_variable_characters = starting_variable_characters + '0123456789'

# determine functions and how many arguments each of them take
# functions['sqrt'] -> (Quantity.function_sqrt, arg_count)
functions = dict()
prefix = 'function_'
# print(inspect.getmembers(Quantity, predicate=inspect.isfunction))
names = inspect.getmembers(Quantity, predicate=inspect.isfunction(x))
names = [x for x in names if x[0].startswith(prefix)]
print('Adding %d functions.' % (len(names)))
for f in names:
    name = f[0][len(prefix):]
    functions[f[0][len(prefix):]] = (len(inspect.getargspec(f[1])[0]), f[1])


def parse_value_at_start(text):
    """Return the string of the value at the start, or None if not found."""
    i = 0
    # skip sign if present
    if i >= len(text):
        return None
    if text[i] in '-+':
        i += 1
        if i >= len(text):
            return None
    # get digits before decimal point, if any
    found_digit = False
    while text[i].isdigit():
        found_digit = True
        i += 1
        if i >= len(text):
            if found_digit:
                return text[:i]
            else:
                return None
    # skip decimal point if present
    if text[i] == '.':
        i += 1
        if i >= len(text):
            if found_digit:
                return text[:i]
            else:
                return None
    # get digits after decimal point if any
    while text[i].isdigit():
        found_digit = True
        i += 1
        if i >= len(text):
            if found_digit:
                return text[:i]
            else:
                return None
    # if no value found so far, we're done
    if not found_digit:
        return None
    # try to parse an exponent
    if text[i] != 'e':
        return text[:i]
    start_index = i
    i += 1
    if i >= len(text):
        return text[:start_index]
    # parse sign if any
    if text[i] in '+-':
        i += 1
        if i >= len(text):
            return text[:start_index]
    # parse digits
    found_digit = False
    while i < len(text) and text[i].isdigit():
        found_digit = True
        i += 1
    if found_digit:
        return text[:i]
    else:
        return text[:start_index]


def parse_variable_at_start(text):
    """Return the string of the variable at the start, or None if not found."""
    if not text or not text[0] in starting_variable_characters:
        return None
    i = 1
    while i < len(text) and text[i] in following_variable_characters:
        i += 1
    return text[:i]


def add_implicit_multiplication(tokens):
    """
    Add implicit multiplication between tokens where necessary.

    implicit parenthesis rules:
    1) between a value and a variable:
       7 mm -> 7 * mm
    2) between a variable and a variable:
       in lbs -> in * lbs
    3) between a closing parenthesis and a variable
       (2 * 12) mm -> (2 * 12) * mm
    4) between parentheses
       (8)(9) -> (8) * (9)

    """
    added_any = False
    i = 0
    while i < len(tokens) - 1:
        add_it = False
        # between value/variable and variable
        if ((tokens[i][0] == Token.value or tokens[i][0] == Token.variable) and
                tokens[i + 1][0] == Token.variable):
            add_it = True
        # between closing parenthesis and a variable
        elif (tokens[i][0] == Token.closing_parenthesis and
                tokens[i + 1][0] == Token.variable):
            add_it = True
        # between parenthesis
        elif (tokens[i][0] == Token.opening_parenthesis and
                tokens[i + 1][0] == Token.closing_parenthesis):
            add_it = True
        if add_it:
            if debug_output and not added_any:
                print('Adding implicit parentheses:')
            added_any = True
            if debug_output:
                print('- adding implicit * between %s and %s'
                      % (tokens[i], tokens[i + 1]))
            tokens.insert(i + 1, ['infix_op', '*'])
        i += 1
    if debug_output and added_any:
        print('- we now have %d tokens' % len(tokens))
        print('  ' + ' '.join(x[1] for x in tokens))
        print('  ' + ' '.join('^' * len(x[1]) for x in tokens))


def parse_to_tokens(equation):
    """Take the equation and parse it into tokens."""
    if debug_output:
        print('\nParsing equation "%s"' % (equation))
    # set to true if a value immediately preceded the current character
    parsed_values = []
    value_before = False
    found_operator = False
    while equation:
        # print '-->', equation, parsed_values
        # trim equation if necessary
        if equation != equation.strip():
            equation = equation.strip()
            continue
        # see if a value immediately preceeded this position
        if not parsed_values:
            value_before = False
        else:
            if (parsed_values[-1][0] == Token.closing_parenthesis or
                    parsed_values[-1][0] == Token.variable or
                    parsed_values[-1][0] == Token.value or
                    parsed_values[-1][0] == Token.postfix_operator):
                value_before = True
            else:
                value_before = False
        # look for parenthesis
        if equation.startswith('('):
            parsed_values.append([Token.opening_parenthesis, '('])
            equation = equation[1:]
            continue
        if equation.startswith(')'):
            parsed_values.append([Token.closing_parenthesis, ')'])
            equation = equation[1:]
            continue
        # look for prefix operators if value was not immediately preceeding
        if not value_before:
            found_operator = False
            for operator in prefix_operators.keys():
                if equation.startswith(operator):
                    found_operator = True
                    parsed_values.append([Token.prefix_operator,
                                          operator])
                    equation = equation[len(operator):]
                    break
            if found_operator:
                continue
        # look for infix operator if value was preceeding
        if value_before:
            for operator in infix_operators.keys():
                if equation.startswith(operator):
                    found_operator = True
                    parsed_values.append([Token.infix_operator,
                                          operator])
                    equation = equation[len(operator):]
                    break
            if found_operator:
                continue
        # look for postfix operator if value was preceeding
        if value_before:
            for operator in postfix_operators.keys():
                if equation.startswith(operator):
                    found_operator = True
                    parsed_values.append([Token.postfix_operator,
                                          operator])
                    equation = equation[len(operator):]
                    break
            if found_operator:
                continue
        # try to parse a variable or function
        result = parse_variable_at_start(equation)
        if result is not None:
            equation = equation[len(result):]
            if equation and equation[0] == '(':
                parsed_values.append([Token.function, result])
            else:
                parsed_values.append([Token.variable, result])
            continue
        # try to parse a value
        result = parse_value_at_start(equation)
        if result is not None:
            parsed_values.append([Token.value, result])
            equation = equation[len(result):]
            continue
        # we don't know what to do here
        message = 'Symbol "%s" is not recognized' % equation[0]
        raise ParserError(message, equation)
        # raise ParserError('Unrecognized symbol', equation)
    if debug_output:
        print('- found %d tokens' % (len(parsed_values)))
        print('- ' + ' '.join(x[1] for x in parsed_values))
        print('- ' + ' '.join('^' * len(x[1]) for x in parsed_values))
    return parsed_values


def evaluate_flat_tokens(tokens):
    """Evaluate the given tokens that do not contain parentheses."""
    if debug_output:
        print('Evaluating tokens ', tokens)
    tokens = list(tokens)
    # ensure no parenthesis are present
    assert not any(x[0] == Token.opening_parenthesis for x in tokens)
    assert not any(x[0] == Token.closing_parenthesis for x in tokens)
    # evaluate functions
    function_indices = [i
                        for i, x in enumerate(tokens)
                        if x[0] == Token.function]
    for i in reversed(function_indices):
        if tokens[i][1] not in functions:
            message = 'Function "%s" not recognized' % (tokens[i][1])
            raise ParserError(message)  # 'Unrecognized function', message)
        this_function = functions[tokens[i][1]]
        if this_function[0] != 1:
            message = 'Functions with 2+ arguments not supported'
            raise ParserError(message)  # 'Invalid function', message)
        this_value = this_function[1](tokens[i + 1][1])
        del tokens[i + 1]
        tokens[i] = [Token.value, this_value]
    # evaluate exponentiation from right to left
    for i in reversed(range(1, len(tokens))):
        if (tokens[i][0] == Token.infix_operator and
                tokens[i][1][-1] == Quantity.__pow__):
            assert tokens[i - 1][0] == Token.value
            assert tokens[i + 1][0] == Token.value
            tokens[i - 1: i + 2] = [[Token.value,
                                     tokens[i][1][-1](tokens[i - 1][1],
                                                      tokens[i + 1][1])]]
        elif (tokens[i][0] == Token.postfix_operator and
                tokens[i][1][-1] == Quantity.factorial):
            assert tokens[i - 1][0] == Token.value
            tokens[i - 1: i + 1] = [[Token.value,
                                     tokens[i][1][-1](tokens[i - 1][1])]]
    # evaluate everything else left to right
    while len(tokens) > 1:
        # get the lowest order of operations present in the equation and
        # evaluate them
        this_order = min(x[1][0]
                         for x in tokens
                         if (x[0] == Token.infix_operator or
                             x[0] == Token.prefix_operator))
        i = 0
        while i < len(tokens):
            if (tokens[i][0] == Token.prefix_operator and
                    tokens[i][1][0] == this_order):
                assert tokens[i + 1][0] == Token.value
                tokens[i: i + 2] = [[Token.value,
                                     tokens[i][1][-1](tokens[i + 1][1])]]
            elif (tokens[i][0] == Token.infix_operator and
                  tokens[i][1][0] == this_order):
                assert tokens[i - 1][0] == Token.value
                assert tokens[i + 1][0] == Token.value
                tokens[i - 1: i + 2] = [[Token.value,
                                         tokens[i][1][-1](tokens[i - 1][1],
                                                          tokens[i + 1][1])]]
                i -= 1
            i += 1
    # at this point, it should be a single value
    assert len(tokens) == 1
    assert tokens[0][0] == Token.value
    return tokens[0]


def evaluate_tokens(tokens):
    """
    Return the result of the given equation.

    """
    if debug_output:
        print('\nstart of calculate2:')
        for x in tokens:
            print(x)
    # eliminate any parenthesis
    tokens = list(tokens)
    opening_index = []
    found = True
    while found:
        found = False
        # print tokens
        for i, x in enumerate(tokens):
            if x[0] == Token.opening_parenthesis:
                opening_index.append(i)
                found = True
            elif x[1] == Token.closing_parenthesis:
                # eliminate this parenthesis level
                # print 'before ->', tokens
                value = evaluate_flat_tokens(tokens[opening_index[-1] + 1:i])
                tokens[opening_index[-1]:i + 1] = [value]
                # print 'after ->', tokens
                opening_index = opening_index[:-1]
                break
    # print tokens
    return evaluate_flat_tokens(tokens)
    # print 'end of calculate2:'
    # for x in tokens:
    #    print x
    # print
    # assert False


def check_token_syntax(tokens):
    """Check the syntax of the tokens and report any error found."""
    if debug_output:
        print('\nChecking token syntax')
    # check for empty token list
    if not tokens:
        raise ParserError('Empty expression')
    # check for balanced parenthesis
    level = 0
    for x in tokens:
        if x[0] == Token.opening_parenthesis:
            level += 1
        if x[0] == Token.closing_parenthesis:
            level -= 1
            if level < 0:
                raise ParserError('Unbalanced parentheses')
    if level != 0:
        raise ParserError('Unbalanced parentheses')
    # check for correct starting token
    if tokens[0][0] not in token_can_start:
        raise ParserError('Invalid starting token "%s"' % (tokens[-1][-1]),
                          tokens[0])
    # check for correct starting token
    if tokens[-1][0] not in token_can_end:
        raise ParserError('Invalid ending token "%s"' % (tokens[-1][-1]),
                          tokens[-1])
    # check for valid token sequence
    for i in range(1, len(tokens)):
        if tokens[i][0] not in token_can_follow[tokens[i - 1][0]]:
            raise ParserError('Invalid syntax')
    if debug_output:
        print('- passed')


def interpret_percent_sign(tokens):
    """
    Interpret the % symbol as a percent sign or as an infix operator.

    """
    # if we don't allow the percent sign, nothing to change
    if not allow_percent:
        return
    # the percent sign is allowed immediately following a number and must be
    # followed by an infix operator, or be the last token
    i = 1
    while i < len(tokens):
        if tokens[i - 1][0] == Token.value and tokens[i][1] == '%':
            if debug_output:
                print(i, tokens)
            if (i == len(tokens) - 1 or
                    (tokens[i + 1][0] == Token.infix_operator or
                     tokens[i + 1][0] == Token.closing_parenthesis)):
                if debug_output:
                    print('Interpreted %% as percent sign at index %d' % i)
                tokens[i][0] = Token.value
                tokens[i][1] = '0.01'
                tokens.insert(i, [Token.infix_operator, '*'])
                if debug_output:
                    print(tokens)
                i += 1
        i += 1


def calculate(equation):
    """
    Evaluate the string equation and return the result.

    """
    # store units used by the equation
    units_in_equation = []
    # replace all constants with their actual values
    # tokenize the equation
    tokens = parse_to_tokens(equation)
    # process % as a percent sign or as an infix operator
    interpret_percent_sign(tokens)
    # add implicit multiplication where necessary
    add_implicit_multiplication(tokens)
    # ensure syntax is valid
    check_token_syntax(tokens)
    # replace operators with their function info
    for x in tokens:
        if x[0] == Token.prefix_operator:
            x[1] = prefix_operators[x[1]]
        elif x[0] == Token.infix_operator:
            x[1] = infix_operators[x[1]]
        elif x[0] == Token.postfix_operator:
            x[1] = postfix_operators[x[1]]
    # convert each value to a Quantity
    for x in tokens:
        if x[0] == Token.value:
            x[1] = Quantity(value=decimal.Decimal(x[1]))
    # replace all variables and units with proper values
    for x in tokens:
        if x[0] == Token.variable:
            # see if it's a unit
            if x[1] in unit_def:
                units_in_equation.append(x[1])
                x[1] = unit_def[x[1]]
                x[0] = Token.value
            else:
                # variable not recognized
                message = 'Variable "%s" is undefined.' % x[1]
                raise ParserError(message, equation)
    return evaluate_tokens(tokens)[1]


# hold dictionary mapping unit name to a Quantity()
unit_def = dict()

#if allow_percent:
#    unit_def['%'] = Quantity(value=decimal.Decimal('0.01'))

# add base unit definitions
for i, unit_name in enumerate(base_units):
    unit_def[unit_name] = Quantity(value=decimal.Decimal('1'),
                                   units=[0.0] * unit_count)
    unit_def[unit_name].units[i] = 1.0

# convert each unit to a Quantity
while units:
    # print units.keys()
    decoded_something = False
    for key in list(units.keys()):
        value = units[key]
        tokens = parse_to_tokens(value)
        add_implicit_multiplication(tokens)
        # print key, value, tokens
        # check to see if all variables are defined units
        this_units = [x[1] in unit_def
                      for x in tokens
                      if x[0] == Token.variable]
        # if not all units are defined, skip it for now
        if this_units:
            if not all(this_units):
                continue
        # evaluate it and add this unit definition
        unit_def[key] = calculate(value)
        decoded_something = True
        del units[key]
    # if we couldn't decode anything else, the remaining units are ill-defined
    if not decoded_something:
        print('ERROR: could not decode all units')
        for x in sorted(units.keys()):
            print('* %s: %s' % (x, units[x]))
        raise ValueError
if False:
    print('Unit conversions:')
    for key, value in sorted(unit_def.items()):
        print('* %s --> %s' % (key, value))

# form a dictionary of all unit types
# we want: unit_measure[tuple(Quantity.units)] = 'length'
for key in sorted(unit_measure.keys()):
    value = calculate(key)
    unit_measure[tuple(value.units)] = [unit_measure[key], key, calculate(key)]

# verify that all unit definitions match units
for key, value in unit_def.items():
    left = calculate(key)
    assert left.units == value.units


def matching_units(value1, value2):
    """Return True if the units of the two values match."""
    if type(value1) is str:
        value1 = calculate(value1)
    if type(value2) is str:
        value2 = calculate(value2)
    return value1.units == value2.units


# attempt to find the unit of measure of the given quantity
def get_measure(quantity):
    """
    Return the measure of the units of the given quantity, or None.

    For example, get_measure('m') should return 'length'.

    """
    check = tuple(quantity.units)
    if check in unit_measure:
        return unit_measure[check][0]
    return None


def formatted_tokens(tokens):
    """Return the tokens formatted as a string with standard spacing."""
    assert all(x[1] is str for x in tokens)
    pass


# output units, in order of precedence
# if the units match one of these exactly, display it in those units
# else, display it in base units
def to_string(quantity, output_units=None, include_measure=False):
    if debug_output:
        print('Converting "%s" with output_units=%s'
              % (quantity, output_units))
    # round exponents to the nearest 1e-5 to
    # get rid of roundoff errors
    quantity.units = [math.floor(x * 1.0e5 + 0.5) / 1.0e5
                      for x in quantity.units]
    if include_measure:
        measure = get_measure(quantity)
        if measure:
            measure = ' [%s]' % measure
        else:
            measure = ''
    else:
        measure = ''
    # see if the output units match
    if (output_units in unit_def and
            quantity.units == unit_def[output_units].units):
        if debug_output:
            print('- found match in unit definitions')
        quantity.value /= unit_def[output_units].value
        quantity.value *= decimal.Decimal(
            '1.' + '0' * decimal.getcontext().prec)
        value_str = str(quantity.value)
        if '.' in value_str:
            value_str = value_str.rstrip('0').rstrip('.')
        return "%s %s%s" % (value_str, output_units, measure)
    elif type(output_units) is str:
        units_quantity = calculate(output_units)
        if matching_units(quantity, units_quantity):
            if debug_output:
                print('- found match to derived output units')
            quantity.value /= units_quantity.value
            quantity.value *= decimal.Decimal(
                '1.' + '0' * decimal.getcontext().prec)
            value_str = str(quantity.value)
            if '.' in value_str:
                value_str = value_str.rstrip('0').rstrip('.')
            return '%s %s%s' % (value_str, output_units, measure)
    # otherwise look for the default units for this type
    key = tuple(quantity.units)
    if key in unit_measure:
        if debug_output:
            print('- found match in unit_measure')
        quantity.value /= unit_measure[key][2].value
        quantity.value *= decimal.Decimal(
            '1.' + '0' * decimal.getcontext().prec)
        value_str = str(quantity.value)
        if '.' in value_str:
            value_str = value_str.rstrip('0').rstrip('.')
        return "%s %s%s" % (value_str, unit_measure[key][1], measure)
    # or output in base SI units
    quantity.value *= decimal.Decimal('1.' + '0' * decimal.getcontext().prec)
    if debug_output:
        print('- no match found, using base units')
    return '%s%s' % (str(quantity), measure)


def process_user_equation(equation):
    """Return the result of the equation which may include unit specifiers."""
    # set high working precision
    decimal.getcontext().prec = working_precision_digits
    # see if string has desired units
    # if "in" is used, see if the equation is written in the form "x in y"
    if ' to ' in equation:
        equation, target_units = equation.rsplit(' to ', 1)
        result = calculate(equation)
    elif ' as ' in equation:
        equation, target_units = equation.rsplit(' as ', 1)
        result = calculate(equation)
    elif ' in ' in equation:
        possible_equation, possible_units = equation.rsplit(' in ', 1)
        try:
            result = calculate(possible_equation)
            target_units = possible_units
            assert matching_units(result, target_units)
        except (AssertionError, QuantityError, ParserError):
            result = calculate(equation)
            target_units = None
    else:
        target_units = None
        result = calculate(equation)
    # save answer as "Ans"
    unit_def['Ans'] = result
    # round results for output
    decimal.getcontext().prec = output_precision_digits
    return to_string(+result, target_units)


def get_default_windows_font():
    """Return the default font used by Windows on forms."""
    return ('Segoe UI', 9)


# evaluating these should give the desired result
valid_expressions = []
valid_expressions.append('1 ^ 1 + 1 - 1 * 1 / 1 % 1')
valid_expressions.append('-(1)')
valid_expressions.append('+(1)')
valid_expressions.append('((1))')

# evaluating these expressions should cause a QuantityError or a ParserError
invalid_expressions = []

# unbalanced parentheses
invalid_expressions.append('(1 + 1')
invalid_expressions.append('1 + 1)')
invalid_expressions.append('1) + (1')
invalid_expressions.append('(((1))')
invalid_expressions.append('((1)))')

# invalid expression
invalid_expressions.append('1 * ()')

# invalid implicit multiplication stuff
invalid_expressions.append('1 2')
invalid_expressions.append('m 2')
invalid_expressions.append('1 m 1')

# if this is run as a script, then do some basic calculations
if __name__ == "__main__":
    if run_unit_tests:
        if debug_output:
            print('Running unit tests')
        all_passed = True
        # run valid expressions
        for eq in valid_expressions:
            if debug_output:
                print('- Checking "%s" for validity' % (eq))
            valid = True
            try:
                result = process_user_equation(eq)
            except (QuantityError, ParserError):
                valid = False
            if not valid:
                all_passed = False
                print('ERROR: the expression "%s" failed to evaluate' % (eq))
        # run invalid expressions
        for eq in invalid_expressions:
            if debug_output:
                print('- Checking "%s" for failure' % (eq))
            valid = True
            try:
                result = process_user_equation(eq)
            except (QuantityError, ParserError):
                valid = False
            if valid:
                all_passed = False
                print('ERROR: the expression "%s" did not fail' % (eq))
        assert all_passed
        if debug_output:
            print('- completed')
    run_gui()
