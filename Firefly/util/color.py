"""Color util methods. From Home Assistant"""
import colorsys
import math
from typing import Tuple

from colour import Color

from Firefly import logging

# Official CSS3 colors from w3.org:
# https://www.w3.org/TR/2010/PR-css3-color-20101028/#html4
# names do not have spaces in them so that we can compare against
# requests more easily (by removing spaces from the requests as well).
# This lets "dark seagreen" and "dark sea green" both match the same
# color "darkseagreen".
COLORS = {
  'aliceblue':            (240, 248, 255),
  'antiquewhite':         (250, 235, 215),
  'aqua':                 (0, 255, 255),
  'aquamarine':           (127, 255, 212),
  'azure':                (240, 255, 255),
  'beige':                (245, 245, 220),
  'bisque':               (255, 228, 196),
  'black':                (0, 0, 0),
  'blanchedalmond':       (255, 235, 205),
  'blue':                 (0, 0, 255),
  'blueviolet':           (138, 43, 226),
  'brown':                (165, 42, 42),
  'burlywood':            (222, 184, 135),
  'cadetblue':            (95, 158, 160),
  'chartreuse':           (127, 255, 0),
  'chocolate':            (210, 105, 30),
  'coral':                (255, 127, 80),
  'cornflowerblue':       (100, 149, 237),
  'cornsilk':             (255, 248, 220),
  'crimson':              (220, 20, 60),
  'cyan':                 (0, 255, 255),
  'darkblue':             (0, 0, 139),
  'darkcyan':             (0, 139, 139),
  'darkgoldenrod':        (184, 134, 11),
  'darkgray':             (169, 169, 169),
  'darkgreen':            (0, 100, 0),
  'darkgrey':             (169, 169, 169),
  'darkkhaki':            (189, 183, 107),
  'darkmagenta':          (139, 0, 139),
  'darkolivegreen':       (85, 107, 47),
  'darkorange':           (255, 140, 0),
  'darkorchid':           (153, 50, 204),
  'darkred':              (139, 0, 0),
  'darksalmon':           (233, 150, 122),
  'darkseagreen':         (143, 188, 143),
  'darkslateblue':        (72, 61, 139),
  'darkslategray':        (47, 79, 79),
  'darkslategrey':        (47, 79, 79),
  'darkturquoise':        (0, 206, 209),
  'darkviolet':           (148, 0, 211),
  'deeppink':             (255, 20, 147),
  'deepskyblue':          (0, 191, 255),
  'dimgray':              (105, 105, 105),
  'dimgrey':              (105, 105, 105),
  'dodgerblue':           (30, 144, 255),
  'firebrick':            (178, 34, 34),
  'floralwhite':          (255, 250, 240),
  'forestgreen':          (34, 139, 34),
  'fuchsia':              (255, 0, 255),
  'gainsboro':            (220, 220, 220),
  'ghostwhite':           (248, 248, 255),
  'gold':                 (255, 215, 0),
  'goldenrod':            (218, 165, 32),
  'gray':                 (128, 128, 128),
  'green':                (0, 128, 0),
  'greenyellow':          (173, 255, 47),
  'grey':                 (128, 128, 128),
  'honeydew':             (240, 255, 240),
  'hotpink':              (255, 105, 180),
  'indianred':            (205, 92, 92),
  'indigo':               (75, 0, 130),
  'ivory':                (255, 255, 240),
  'khaki':                (240, 230, 140),
  'lavender':             (230, 230, 250),
  'lavenderblush':        (255, 240, 245),
  'lawngreen':            (124, 252, 0),
  'lemonchiffon':         (255, 250, 205),
  'lightblue':            (173, 216, 230),
  'lightcoral':           (240, 128, 128),
  'lightcyan':            (224, 255, 255),
  'lightgoldenrodyellow': (250, 250, 210),
  'lightgray':            (211, 211, 211),
  'lightgreen':           (144, 238, 144),
  'lightgrey':            (211, 211, 211),
  'lightpink':            (255, 182, 193),
  'lightsalmon':          (255, 160, 122),
  'lightseagreen':        (32, 178, 170),
  'lightskyblue':         (135, 206, 250),
  'lightslategray':       (119, 136, 153),
  'lightslategrey':       (119, 136, 153),
  'lightsteelblue':       (176, 196, 222),
  'lightyellow':          (255, 255, 224),
  'lime':                 (0, 255, 0),
  'limegreen':            (50, 205, 50),
  'linen':                (250, 240, 230),
  'magenta':              (255, 0, 255),
  'maroon':               (128, 0, 0),
  'mediumaquamarine':     (102, 205, 170),
  'mediumblue':           (0, 0, 205),
  'mediumorchid':         (186, 85, 211),
  'mediumpurple':         (147, 112, 219),
  'mediumseagreen':       (60, 179, 113),
  'mediumslateblue':      (123, 104, 238),
  'mediumspringgreen':    (0, 250, 154),
  'mediumturquoise':      (72, 209, 204),
  'mediumvioletredred':   (199, 21, 133),
  'midnightblue':         (25, 25, 112),
  'mintcream':            (245, 255, 250),
  'mistyrose':            (255, 228, 225),
  'moccasin':             (255, 228, 181),
  'navajowhite':          (255, 222, 173),
  'navy':                 (0, 0, 128),
  'navyblue':             (0, 0, 128),
  'oldlace':              (253, 245, 230),
  'olive':                (128, 128, 0),
  'olivedrab':            (107, 142, 35),
  'orange':               (255, 165, 0),
  'orangered':            (255, 69, 0),
  'orchid':               (218, 112, 214),
  'palegoldenrod':        (238, 232, 170),
  'palegreen':            (152, 251, 152),
  'paleturquoise':        (175, 238, 238),
  'palevioletred':        (219, 112, 147),
  'papayawhip':           (255, 239, 213),
  'peachpuff':            (255, 218, 185),
  'peru':                 (205, 133, 63),
  'pink':                 (255, 192, 203),
  'plum':                 (221, 160, 221),
  'powderblue':           (176, 224, 230),
  'purple':               (128, 0, 128),
  'red':                  (255, 0, 0),
  'rosybrown':            (188, 143, 143),
  'royalblue':            (65, 105, 225),
  'saddlebrown':          (139, 69, 19),
  'salmon':               (250, 128, 114),
  'sandybrown':           (244, 164, 96),
  'seagreen':             (46, 139, 87),
  'seashell':             (255, 245, 238),
  'sienna':               (160, 82, 45),
  'silver':               (192, 192, 192),
  'skyblue':              (135, 206, 235),
  'slateblue':            (106, 90, 205),
  'slategray':            (112, 128, 144),
  'slategrey':            (112, 128, 144),
  'snow':                 (255, 250, 250),
  'springgreen':          (0, 255, 127),
  'steelblue':            (70, 130, 180),
  'tan':                  (210, 180, 140),
  'teal':                 (0, 128, 128),
  'thistle':              (216, 191, 216),
  'tomato':               (255, 99, 71),
  'turquoise':            (64, 224, 208),
  'violet':               (238, 130, 238),
  'wheat':                (245, 222, 179),
  'white':                (255, 255, 255),
  'whitesmoke':           (245, 245, 245),
  'yellow':               (255, 255, 0),
  'yellowgreen':          (154, 205, 50),
}


def color_name_to_rgb(color_name):
  """Convert color name to RGB hex value."""
  # COLORS map has no spaces in it, so make the color_name have no
  # spaces in it as well for matching purposes
  hex_value = COLORS.get(color_name.replace(' ', '').lower())
  if not hex_value:
    logging.error('unknown color supplied %s default to white', color_name)
    hex_value = COLORS['white']

  return hex_value


# Taken from:
# http://www.developers.meethue.com/documentation/color-conversions-rgb-xy
# License: Code is given as is. Use at your own risk and discretion.
# pylint: disable=invalid-name, invalid-sequence-index
def color_RGB_to_xy(iR: int, iG: int, iB: int) -> Tuple[float, float, int]:
  """Convert from RGB color to XY color."""
  if iR + iG + iB == 0:
    return 0.0, 0.0, 0

  R = iR / 255
  B = iB / 255
  G = iG / 255

  # Gamma correction
  R = pow((R + 0.055) / (1.0 + 0.055),
          2.4) if (R > 0.04045) else (R / 12.92)
  G = pow((G + 0.055) / (1.0 + 0.055),
          2.4) if (G > 0.04045) else (G / 12.92)
  B = pow((B + 0.055) / (1.0 + 0.055),
          2.4) if (B > 0.04045) else (B / 12.92)

  # Wide RGB D65 conversion formula
  X = R * 0.664511 + G * 0.154324 + B * 0.162028
  Y = R * 0.313881 + G * 0.668433 + B * 0.047685
  Z = R * 0.000088 + G * 0.072310 + B * 0.986039

  # Convert XYZ to xy
  x = X / (X + Y + Z)
  y = Y / (X + Y + Z)

  # Brightness
  Y = 1 if Y > 1 else Y
  brightness = round(Y * 255)

  return round(x, 3), round(y, 3), brightness


# Converted to Python from Obj-C, original source from:
# http://www.developers.meethue.com/documentation/color-conversions-rgb-xy
# pylint: disable=invalid-sequence-index
def color_xy_brightness_to_RGB(vX: float, vY: float,
                               ibrightness: int) -> Tuple[int, int, int]:
  """Convert from XYZ to RGB."""
  brightness = ibrightness / 255.
  if brightness == 0:
    return (0, 0, 0)

  Y = brightness

  if vY == 0:
    vY += 0.00000000001

  X = (Y / vY) * vX
  Z = (Y / vY) * (1 - vX - vY)

  # Convert to RGB using Wide RGB D65 conversion.
  r = X * 1.656492 - Y * 0.354851 - Z * 0.255038
  g = -X * 0.707196 + Y * 1.655397 + Z * 0.036152
  b = X * 0.051713 - Y * 0.121364 + Z * 1.011530

  # Apply reverse gamma correction.
  r, g, b = map(
      lambda x: (12.92 * x) if (x <= 0.0031308) else
      ((1.0 + 0.055) * pow(x, (1.0 / 2.4)) - 0.055),
      [r, g, b]
  )

  # Bring all negative components to zero.
  r, g, b = map(lambda x: max(0, x), [r, g, b])

  # If one component is greater than 1, weight components by that value.
  max_component = max(r, g, b)
  if max_component > 1:
    r, g, b = map(lambda x: x / max_component, [r, g, b])

  ir, ig, ib = map(lambda x: int(x * 255), [r, g, b])

  return (ir, ig, ib)


# pylint: disable=invalid-sequence-index
def color_RGB_to_hsv(iR: int, iG: int, iB: int) -> Tuple[int, int, int]:
  """Convert an rgb color to its hsv representation."""
  fHSV = colorsys.rgb_to_hsv(iR / 255.0, iG / 255.0, iB / 255.0)
  return (int(fHSV[0] * 65536), int(fHSV[1] * 255), int(fHSV[2] * 255))


# pylint: disable=invalid-sequence-index
def color_hsv_to_RGB(iH: int, iS: int, iV: int) -> Tuple[int, int, int]:
  """Convert an hsv color into its rgb representation."""
  fRGB = colorsys.hsv_to_rgb(iH / 65536, iS / 255, iV / 255)
  return (int(fRGB[0] * 255), int(fRGB[1] * 255), int(fRGB[2] * 255))


# pylint: disable=invalid-sequence-index
def color_xy_to_hs(vX: float, vY: float) -> Tuple[int, int]:
  """Convert an xy color to its hs representation."""
  h, s, _ = color_RGB_to_hsv(*color_xy_brightness_to_RGB(vX, vY, 255))
  return (h, s)


# pylint: disable=invalid-sequence-index
def _match_max_scale(input_colors: Tuple[int, ...],
                     output_colors: Tuple[int, ...]) -> Tuple[int, ...]:
  """Match the maximum value of the output to the input."""
  max_in = max(input_colors)
  max_out = max(output_colors)
  if max_out == 0:
    factor = 0.0
  else:
    factor = max_in / max_out
  return tuple(int(round(i * factor)) for i in output_colors)


def color_rgb_to_rgbw(r, g, b):
  """Convert an rgb color to an rgbw representation."""
  # Calculate the white channel as the minimum of input rgb channels.
  # Subtract the white portion from the remaining rgb channels.
  w = min(r, g, b)
  rgbw = (r - w, g - w, b - w, w)

  # Match the output maximum value to the input. This ensures the full
  # channel range is used.
  return _match_max_scale((r, g, b), rgbw)


def color_rgbw_to_rgb(r, g, b, w):
  """Convert an rgbw color to an rgb representation."""
  # Add the white channel back into the rgb channels.
  rgb = (r + w, g + w, b + w)

  # Match the output maximum value to the input. This ensures the
  # output doesn't overflow.
  return _match_max_scale((r, g, b, w), rgb)


def color_rgb_to_hex(r, g, b):
  """Return a RGB color from a hex color string."""
  return '{0:02x}{1:02x}{2:02x}'.format(r, g, b)


def rgb_hex_to_rgb_list(hex_string):
  """Return an RGB color value list from a hex color string."""
  return [int(hex_string[i:i + len(hex_string) // 3], 16)
          for i in range(0,
                         len(hex_string),
                         len(hex_string) // 3)]


def color_temperature_to_rgb(color_temperature_kelvin):
  """
  Return an RGB color from a color temperature in Kelvin.

  This is a rough approximation based on the formula provided by T. Helland
  http://www.tannerhelland.com/4435/convert-temperature-rgb-algorithm-code/
  """
  # range check
  if color_temperature_kelvin < 1000:
    color_temperature_kelvin = 1000
  elif color_temperature_kelvin > 40000:
    color_temperature_kelvin = 40000

  tmp_internal = color_temperature_kelvin / 100.0

  red = _get_red(tmp_internal)

  green = _get_green(tmp_internal)

  blue = _get_blue(tmp_internal)

  return (red, green, blue)


def _bound(color_component: float, minimum: float = 0,
           maximum: float = 255) -> float:
  """
  Bound the given color component value between the given min and max values.

  The minimum and maximum values will be included in the valid output.
  i.e. Given a color_component of 0 and a minimum of 10, the returned value
  will be 10.
  """
  color_component_out = max(color_component, minimum)
  return min(color_component_out, maximum)


def _get_red(temperature: float) -> float:
  """Get the red component of the temperature in RGB space."""
  if temperature <= 66:
    return 255
  tmp_red = 329.698727446 * math.pow(temperature - 60, -0.1332047592)
  return _bound(tmp_red)


def _get_green(temperature: float) -> float:
  """Get the green component of the given color temp in RGB space."""
  if temperature <= 66:
    green = 99.4708025861 * math.log(temperature) - 161.1195681661
  else:
    green = 288.1221695283 * math.pow(temperature - 60, -0.0755148492)
  return _bound(green)


def _get_blue(temperature: float) -> float:
  """Get the blue component of the given color temperature in RGB space."""
  if temperature >= 66:
    return 255
  if temperature <= 19:
    return 0
  blue = 138.5177312231 * math.log(temperature - 10) - 305.0447927307
  return _bound(blue)


def color_temperature_mired_to_kelvin(mired_temperature):
  """Convert absolute mired shift to degrees kelvin."""
  return 1000000 / mired_temperature


def color_temperature_kelvin_to_mired(kelvin_temperature):
  """Convert degrees kelvin to mired shift."""
  return 1000000 / kelvin_temperature


def average_rgb(r=[], g=[], b=[]):
  """ Average multiple RGB Colros

  Args:
    r: list of red values
    g: list of green values
    b: list of blue values

  Returns:(R,G,B) Average

  """
  # https://medium.com/@kevinsimper/how-to-average-rgb-colors-together-6cd3ef1ff1e5
  if not(len(r) == len(g) == len(b)):
    return (0,0,0)

  size = len(r)
  r_sum = 0
  g_sum = 0
  b_sum = 0
  for i in range(size):
    r_sum += (r[i] * 255)
    g_sum += (g[i] * 255)
    b_sum += (b[i] * 255)

  r_squared = r_sum/size
  g_squared = g_sum/size
  b_squared = b_sum/size

  r_avg = int(math.sqrt(r_squared))
  g_avg = int(math.sqrt(g_squared))
  b_avg = int(math.sqrt(b_squared))

  return (r_avg, g_avg, b_avg)



def check_ct(ct, kelvin=True, min_ct=2200, max_ct=6500):
  if type(ct) is str:
    if 'K' in ct.upper():
      ct = ct.upper().replace('K', '')
    try:
      ct = int(ct)
    except:
      if kelvin:
        return min_ct
      return color_temperature_kelvin_to_mired(min_ct)

  if ct < 500:
    ct = color_temperature_mired_to_kelvin(ct)

  ct = max(min_ct, ct)
  ct = min(max_ct, ct)
  if kelvin:
    return int(ct)
  return int(color_temperature_kelvin_to_mired(ct))



class Colors(object):
  def __init__(self):
    self.hue = None
    self.sat = None
    self.bri = None
    self.hex = None
    self.r = None
    self.g = None
    self.b = None
    self.color_string = None
    self.is_set = False

  def set(self, hue, sat, bri, hex, r, g, b, color_string):
    self.hue = hue
    self.sat = sat
    self.bri = bri
    self.hex = hex
    self.r = r
    self.g = g
    self.b = b
    self.color_string = color_string
    self.is_set = True

  @property
  def rgb(self):
    return (self.r, self.g, self.b)

  @property
  def hue_expanded(self):
    return int(self.hue * 65535)

  @property
  def sat_expanded(self):
    return int(self.sat*255)




def populate_colors(**kwargs) -> Colors:
  """ Generates a Colors object by calculating all the missing colors.

  Args:
    **kwargs:
      rgb: RGB tuple for color
      r: R of RGB (Requires all 3 of RGB)
      g: G of RGB (Requires all 3 of RGB)
      b: B of RGB (Requires all 3 of RGB)
      hue: hue of HSL (Requires all 3 of HSL)
      sat: sat of HSL (Requires all 3 of HSL)
      bri: bri of HSL (Requires all 3 of HSL)
      hex: hex color
      color: color name string

  Returns:Colors Object

  """
  colors = Colors()
  color = None

  if 'rgb' in kwargs:
    rgb_in = kwargs['rgb']
    r = rgb_in[0] / 255 if rgb_in[0] != 0 else rgb_in[0]
    g = rgb_in[1] / 255 if rgb_in[1] != 0 else rgb_in[1]
    b = rgb_in[2] / 255 if rgb_in[2] != 0 else rgb_in[2]
    color = Color(rgb=(r, g, b))

  if 'hex' in kwargs:
    hex_in = kwargs['hex']
    if '#' not in hex_in:
      hex_in = '#%s' % hex_in
    color = Color(hex=hex_in)

  if 'r' in kwargs and 'g' in kwargs and 'b' in kwargs:
    try:
      rgb_in = (kwargs['r'], kwargs['g'], kwargs['b'])
      r = int(rgb_in[0])
      g = int(rgb_in[1])
      b = int(rgb_in[2])
      r = r / 255.0 if r != 0 else r
      g = g / 255.0 if g != 0 else g
      b = b / 255.0 if b != 0 else b
      color = Color(rgb=(r, g, b))
    except:
      pass

  if 'hue' in kwargs and 'sat' in kwargs and 'bri' in kwargs:
    hue_in = float(kwargs['hue'])
    sat_in = float(kwargs['sat'])
    bri_in = float(kwargs['bri'])

    if hue_in <= 1.0:
      hue_in = hue_in * 65536
    if sat_in <= 1.0:
      sat_in = sat_in * 255
    if bri_in <= 1.0:
      bri_in = bri_in * 255

    hue_in = int(hue_in)
    sat_in = int(sat_in)
    bri_in = int(bri_in)

    rgb_in = color_hsv_to_RGB(hue_in, sat_in, bri_in)

    r = int(rgb_in[0])
    g = int(rgb_in[1])
    b = int(rgb_in[2])
    r = r / 255.0 if r != 0 else r
    g = g / 255.0 if g != 0 else g
    b = b / 255.0 if b != 0 else b
    color = Color(rgb=(r, g, b))

  if 'color' in kwargs:
    color = Color(color=kwargs['color'])

  if color is None:
    return colors

  rgb_out = color.get_rgb()
  r = int(rgb_out[0] * 255)
  g = int(rgb_out[1] * 255)
  b = int(rgb_out[2] * 255)

  if 'hue' in kwargs and 'sat' in kwargs and 'bri' in kwargs:
    colors.set(hue_in, sat_in, bri_in, color.get_hex(), r, g, b, color.get_web())
  else:
    colors.set(color.get_hue(), color.get_saturation(), color.get_luminance(), color.get_hex(), r, g, b, color.get_web())

  return colors
