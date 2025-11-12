
# Parameters that specify the template grid configuration
img_padding = 20            # # empty space on image edges, in pixels
dot_size = 7                # width and height of 'dot', in pixels
dot_gap = 1                 # space between 'dots', in pixels
line_gap = 32               # vertical space between lines, in pixels
line_dots_x = 128           # line width in 'dots'
line_dots_y = 8             # line height in 'dots'
lines = 4                   # how many lines there are

color_bg = '#000000'        # image background color
color_off = '#3f3f3f'       # 'empty' dot color
color_on = '#00ffff'        # 'active' dot color

# Below are the variables derived from the previous ones
dot_full_size = dot_size + dot_gap
line_width = dot_full_size * line_dots_x
line_height = dot_full_size * line_dots_y
lines_height = line_height*lines + line_gap*(lines-1)
img_width = img_padding*2 + line_width
img_height = img_padding*2 + lines_height

# Shorthand to get single 'dot' coordinates
def dot_coord(line, dot_x, dot_y):
    x = img_padding + dot_full_size*dot_x
    y = img_padding + dot_full_size*dot_y + (line_height+line_gap)*line
    return x, y
