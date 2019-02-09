"""Unit definitions for use by ucal.py."""

# unit and constant definitions
units = dict()

# length
units['mm'] = '1e-3 m'
units['km'] = '1e3 m'
units['cm'] = '1e-2 m'
units['um'] = '1e-6 m'
units['nm'] = '1e-9 m'
units['ft'] = '0.3048 m'
units['feet'] = 'ft'
units['in'] = '1 / 12 ft'
units['inch'] = 'in'
units['mil'] = '0.001 in'
units['inches'] = 'in'
units['yd'] = '3 ft'
units['cubit'] = '18 in'
units['mi'] = '5280 ft'
units['mile'] = 'mi'
units['miles'] = 'mi'

# area
units['acre'] = '1 / 640 * mi^2'

# speed
units['mph'] = 'mile/hour'
units['mps'] = 'm/s'
units['fps'] = 'ft/sec'
units['kph'] = 'km/hr'
units['knot'] = '1.852 mph'

# volume
units['cc'] = 'cm^3'
units['floz'] = '1 / 20 pint'
units['pint'] = '2 cup'
units['cup'] = '1 / 16 gallon'
units['quart'] = '2 pint'
units['gallon'] = 'gal'
units['gal'] = '231 in^3'
units['L'] = '1e-3 m^3'
units['mL'] = '1e-3 L'

# mass
units['lb'] = '0.45359237 kg'
units['lbs'] = 'lb'
units['lbm'] = 'lb'
units['gm'] = '0.001 kg'
units['oz'] = '1/16 lb'
units['ton'] = '2000 lb'

# force
units['N'] = '1 kg * m / s^2'
units['kN'] = '1e3 N'
units['lbf'] = 'lb * g'

# energy
units['J'] = '1 N * m'
units['mJ'] = '1e-3 J'
units['kJ'] = '1e3 J'
units['MJ'] = '1e6 J'
units['GJ'] = '1e9 J'
units['Btu'] = '1055.06 J'
units['btu'] = 'Btu'
units['BTU'] = 'Btu'

# power
units['W'] = '1 J / s'
units['mW'] = '1e-3 W'
units['kW'] = '1e3 W'
units['MW'] = '1e6 W'
units['GW'] = '1e9 W'
# metric horsepower
units['hp'] = '75 kg * g * 1m / (1s)'

# pressure
units['Pa'] = 'N / m^2'
units['kPa'] = '1e3 Pa'
units['MPa'] = '1e6 Pa'
units['GPa'] = '1e9 Pa'
units['psi'] = 'lbf / in^2'
units['ksi'] = '1e3 psi'
units['atm'] = '101325 Pa'
units['cmHg'] = '10 mmHg'
units['mmHg'] = '133.322387415 Pa'
units['Torr'] = '1 / 760 atm'
units['bar'] = '100 kPa'
units['mbar'] = '0.001 bar'

# charge
units['C'] = 'A * s'

# electrical storage
units['F'] = 'C / V'
units['mF'] = '1e-3 F'
units['uF'] = '1e-6 F'
units['nF'] = '1e-9 F'
units['pF'] = '1e-12 F'

# electrical resistance
units['Ohm'] = 'V / A'
units['uOhm'] = '1e-6 Ohm'
units['mOhm'] = '1e-3 Ohm'
units['kOhm'] = '1e3 Ohm'
units['MOhm'] = '1e6 Ohm'

# electrical inductance
units['H'] = 'Ohm * s'
units['mH'] = '1e-3 H'
units['uH'] = '1e-6 H'
units['nH'] = '1e-9 H'

# current
units['mA'] = '1e-3 A'
units['uA'] = '1e-6 A'
units['nA'] = '1e-9 A'
units['pA'] = '1e-12 A'

# voltage
units['V'] = 'W / A'
units['kV'] = '1e3 V'
units['MV'] = '1e6 V'
units['mV'] = '1e-3 V'
units['uV'] = '1e-6 V'
units['nV'] = '1e-9 V'
units['pV'] = '1e-12 V'

# density
units['pcf'] = 'lb / ft^3'

# frequency
units['Hz'] = '1 / s'
units['kHz'] = '1e3 Hz'
units['MHz'] = '1e6 Hz'
units['GHz'] = '1e9 Hz'

# time
units['sec'] = 's'
units['ms'] = '1e-3 s'
units['us'] = '1e-6 s'
units['ns'] = '1e-9 s'
units['ps'] = '1e-12 s'
units['min'] = '60 s'
units['hr'] = 'hour'
units['hour'] = '60 min'
units['day'] = '24 hour'
units['week'] = '7 day'
units['year'] = '365.2425 day'
units['month'] = '(1 year) / 12'

# data
units['bytes'] = 'byte'
units['bit'] = '(1 / 8) byte'
units['bits'] = 'bit'
units['kB'] = '1e3 byte'
units['MB'] = '1e6 byte'
units['GB'] = '1e9 byte'
units['TB'] = '1e12 byte'
units['kbit'] = '1e3 bit'
units['Mbit'] = '1e6 bit'
units['Gbit'] = '1e9 bit'
units['Tbit'] = '1e12 bit'

# data rate
units['bps'] = 'bit / s'
units['kbps'] = 'kbit / s'
units['Mbps'] = 'Mbit / s'
units['Gbps'] = 'Gbit / s'
units['Tbps'] = 'Tbit / s'
units['Bps'] = 'byte / s'
units['kBps'] = 'kB / s'
units['MBps'] = 'MB / s'
units['GBps'] = 'GB / s'
units['TBps'] = 'TB / s'

# constants
units['c'] = '299792458 m/s'
units['g'] = '9.80665 m/s^2'
units['pi'] = '3.141592653589793238462643383279502884197169399375105820974'
units['e'] = '2.7182818284590452353602874713526624977572470936999595749669'
