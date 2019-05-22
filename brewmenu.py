import curses
import random
import time
import images
import sys
import getmenu
import values as val

FIT_SCREEN = True #False
LINE_SPACE = 3
SNOW = True
COLLECT_SNOW = SNOW and False
SNOW_ON_LOGO = SNOW and True
LOOP_SLEEP = 0.15
menu_width = 0
menu_toprow = 0
valid_colspace = 0
menu_rows_fit_error = False

# border_chars = []
# [
#         curses.ACS_LTEE,
#         curses.ACS_RTEE,
#         curses.ACS_HLINE,
#         curses.ACS_BOARD,
#         curses.ACS_ULCORNER,
#         curses.ACS_URCORNER,
#         curses.ACS_SSBB,
#         curses.ACS_VLINE
# ]

def debug_print_dims(win, hgt, wdt):
    ## Print dimensions for debug:
    w_col = 1
    h_col = 5
    win.addstr(1, w_col, "w:")
    for row, char in enumerate(str(wdt), start=2):
        win.addch(row, w_col, char)
    win.addstr(1, h_col, "h:")
    for row, char in enumerate(str(hgt), start=2):
        win.addch(row, h_col, char)

def max_dimensions(window):
    height, width = window.getmaxyx()
    # debug_print_dims(window, height, width)
    return height - 2, width

def divided_col_width(window, ncols):
    return int(max_dimensions(window)[1] / ncols)

def create_panel(window, start_row, start_col, title, content, max_cols=5, content_color=val.color_codes['GREEN'], title_art_font=val.lbls_font): #'wideterm'):
    ## Panel takes parent window, height, width, and the x-y coordinates for its left-upper corner
    global menu_rows_fit_error
    panel = None
    title_art = images.get_art(title_art_font, title, title)
    title_art_lines = len(title_art)
    screen_height = max_dimensions(window)[0]

    panel_h = screen_height - start_row+1 #3  #+6
    while (start_row+panel_h) > (screen_height + 2):
        panel_h-=1

    panel_w = images.longest_str(content)
    if panel_w > divided_col_width(window, max_cols):
        panel_w = divided_col_width(window, max_cols)

    if not FIT_SCREEN:
        trim = max_dimensions(window)[1] // 20
        panel_w -= int(trim)

    panel = window.subwin(panel_h, panel_w, start_row, start_col)
    if panel is None:
        return panel_w

    attribute_list = [
        curses.A_BOLD,
        # curses.A_UNDERLINE,
        # curses.A_STANDOUT,
        # curses.A_BLINK,
        # curses.A_HORIZONTAL,
        # curses.A_LEFT,
        # curses.A_LOW,
        # curses.A_VERTICAL,
    ]
    # panel.attrset(curses.color_pair(images.image_dict['labelbar'].get('color')))
    attr = curses.color_pair(content_color)
    for a in attribute_list:
        attr |= a
    panel.attrset(attr)

    ls=border_chars[0]
    rs=border_chars[1]
    ts=border_chars[2]
    bs=curses.ACS_HLINE #'=' #border_chars[3]
    tl=border_chars[4]
    tr=border_chars[5]
    bl=border_chars[6]
    br=curses.ACS_LRCORNER #border_chars[7]
    panel.border(ls, rs, ts, bs, tl, tr, bl, br)

    inner_text_offset = 3
    row_cnt = 1
    top = title_art[0].strip()
    buff_cnt = 0
    while (len(top)+4) < panel_w:
        top = ' ' + top + ' '
        buff_cnt += 1

    for line in title_art:
        line = line.strip()
        startcol = int(buff_cnt*0.75) + inner_text_offset
        if title.lower() == 'type' and line == title_art[0].strip():
            startcol -= 1
        panel.addstr(row_cnt, startcol, line)
        row_cnt+=1

    panel.addstr(row_cnt, inner_text_offset, '_'*(panel_w-inner_text_offset*2))
    #row_cnt+=1

    ###########################################################################################
    item_cnt = 0
    if not getmenu.SINGLE_REQUEST:
        for row, line in enumerate(content):
            for s in line:
                if s != title:
                    row_cnt+=1
                    if title.lower() == 'cost':
                        s = '${:.2f}'.format(float(s))
                    elif title.lower() == 'abv':
                        s = '{:.1f}%'.format(float(s) * 100)
                    if start_row+row+row_cnt < start_row+panel_h:
                        panel.addstr(row+row_cnt, inner_text_offset, str(s).strip().capitalize())
                    else:
                        menu_rows_fit_error = True
                    row_cnt += (LINE_SPACE-1)
    ###########################################################################################
    else:
        row_cnt+=1
        for row, s in enumerate(content):
            if s != title:
                if str(s).isnumeric():
                    if title.lower() == 'cost':
                        s = '${:.2f}'.format(float(s))
                    elif title.lower() == 'abv':
                        s = '{:.1f}%'.format(float(s) * 100)
                try:
                    panel.addstr(row+row_cnt, inner_text_offset, str(s).strip().capitalize())
                except:
                    from os import system
                    system('echo "addstr ERROR for '+str(s)+' :: --> tile='+title+', row_cnt='+str(row_cnt)+', offset='+str(inner_text_offset)+', panel_w='+str(panel_w)+', panel_h='+str(panel_h)+'" >> debug_gui.log')
    ###########################################################################################

    panel.attrset(curses.color_pair(0))
    return panel_w

def draw_menu(window, menu):
    global menu_width, menu_toprow
    ncols = len(menu.keys())
    next_col_y = len(images.logo['text']) + 1 #2
    next_col_x = 3 #1
    if not FIT_SCREEN:
        if menu_width > 0:
            next_col_x = int((max_dimensions(window)[1] - menu_width) / 2)
    offset = 0
    for k in getmenu.col_lbls:
        offset = create_panel(window, next_col_y, next_col_x, k, menu.get(k), ncols)
        next_col_x += (offset - 1)
    if menu_width == 0:
        menu_width = next_col_x
    if menu_toprow == 0:
        menu_toprow = next_col_y

def draw_image(window, image, attrs=None):
    terminal_width = max_dimensions(window)[1]
    col_offset = image['col_offset']
    start_column = terminal_width - col_offset
    end_column = start_column + image['width']

    if start_column < 0:
        start_column = 10

    attr = curses.color_pair(image['color'])
    if attrs is not None:
        for a in attrs:
            attr |= a
    window.attrset(attr)

    for row, line in enumerate(image['text'], start=1):
        overflow = False
        for column, symbol in enumerate(line, start=start_column):
            if (column < terminal_width):
                window.addch(row+image['row_offset'], column%terminal_width, symbol)

    window.attrset(curses.color_pair(0))

def scroll_title(window, image):
    max_x = max_dimensions(window)[1] - 1
    cur_x = image['col_offset']
    new_x = (cur_x-3) if (cur_x-3) > 0 else max_x
    image.update(col_offset = new_x)

def create_snowflake(window):
    global valid_colspace
    width = max_dimensions(window)[1]
    char = random.choice(['*', '+', '.'])
    column = random.randrange(0, width)
    if not SNOW_ON_LOGO:
        if valid_colspace == 0:
            valid_colspace = (width-menu_width)//2
        if column > (width/2):
            if column < width-valid_colspace:
                try:
                    column = random.randrange(width-valid_colspace,width)
                except ValueError:
                    column = width-1
        else:
            if column > valid_colspace:
                try:
                    column = random.randrange(0,valid_colspace)
                except ValueError:
                    column = 1
    return 0, column, char

def move_snowflakes(prev, window):
    global valid_colspace
    new = {}
    for (row, column), char in prev.items():
        height, width = max_dimensions(window)
        new_row = row + 1
        # For collecting a pile of snow:
        if COLLECT_SNOW:
            if new_row > height or prev.get((new_row, column)):
                new_row -= 1
        if SNOW_ON_LOGO:
            if valid_colspace == 0:
                valid_colspace = (width-menu_width)//2
            if new_row >= menu_toprow:
                if column > (width/2):
                    if column < width-valid_colspace:
                        try:
                            column = random.randrange(width-valid_colspace,width)
                        except ValueError:
                            column = width-1
                        char = ' '
                else:
                    if column > valid_colspace:
                        try:
                            column = random.randrange(0,valid_colspace-1)
                        except ValueError:
                            column = 1
                        char = ' '
        new[(new_row, column)] = char
    return new

def draw_snowflakes(snowflakes, window):
    for (row, column), char in snowflakes.items():
        height, width = max_dimensions(window)
        if row > height or column > width:
            continue
        window.addch(row, column, char)

def main(window):
    global border_chars, menu_rows_fit_error, LINE_SPACE
    border_chars = [
        curses.ACS_LTEE,
        curses.ACS_RTEE,
        curses.ACS_HLINE,
        curses.ACS_BOARD,
        curses.ACS_ULCORNER,
        curses.ACS_URCORNER,
        curses.ACS_SSBB,
        curses.ACS_VLINE
    ]

    curses.init_pair(val.color_codes['YELLOW'], curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(val.color_codes['GREEN'], curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(val.color_codes['RED'], curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(val.color_codes['BLUE'], curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(val.color_codes['CYAN'], curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(val.color_codes['MAGENTA'], curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.curs_set(0)

    logo_img = images.image_dict['logo']
    menu = getmenu.menu_dict()
    # columns = []
    # for (k,v) in menu.items():
    #     columns.append(images.Column(window, k, v))

    prompt_str = val.prompt_str
    prompt_len = len(prompt_str)
    toggle_cursor = False
    toggle_char = '_'

    scroll_cnt = 0
    scroll_speed = 5
    snowflakes = {}

    while True:
        try:
            scroll_cnt %= 100
            window.erase()
            window.addstr(0,1,prompt_str)
            if scroll_cnt % 2 == 0:
                toggle_char = '_' if toggle_cursor else ' '
                toggle_cursor = not toggle_cursor
            window.addch(0,1+prompt_len,toggle_char, curses.color_pair(val.color_codes['WHITE']))# | curses.A_BLINK)

            draw_image(window, logo_img, attrs=[curses.A_BOLD]) #, curses.A_UNDERLINE]) #, curses.A_REVERSE]) #, curses.A_BLINK])
            draw_menu(window, menu)
            if menu_rows_fit_error:
                LINE_SPACE -= 1
                menu_rows_fit_error = False

            if scroll_cnt % scroll_speed == 0:
                scroll_title(window, images.image_dict['logo'])

            if SNOW:
                snowflakes = move_snowflakes(snowflakes, window)
                snowflake = create_snowflake(window)
                snowflakes[(snowflake[0], snowflake[1])] = snowflake[2]
                draw_snowflakes(snowflakes, window)

            window.refresh()

            time.sleep(LOOP_SLEEP)
            scroll_cnt += 1
        except KeyboardInterrupt:
            curses.beep()
            sys.exit(2)

if __name__ == '__main__':
    curses.wrapper(main)
