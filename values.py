# import curses

### BREWMENU CONSTANTS ###
# For curses color_pairs
color_codes = {
    'WHITE': 0,
    'BLACK': 1,
    'YELLOW': 2,
    'GREEN': 3,
    'RED': 4,
    'BLUE': 5,
    'CYAN': 6,
    'MAGENTA': 7,
}

# Toilet fonts are listed as .tlf files in /usr/share/figlet/ (for Linux)
# else /usr/local/Cellar/toilet/0.3/share/figlet/ (if installed via Brew on Mac)
toilet_fonts = [
    'ascii12',
    'ascii9',
    'bigascii12',
    'bigascii9',
    'bigmono12',
    'bigmono9',
    'circle',
    'emboss2',
    'emboss',
    'future',
    'letter',
    'mono12',
    'mono9',
    'pagga',
    'smascii12',
    'smascii9',
    'smblock',
    'smbraille',
    'smmono12',
    'smmono9',
    'wideterm'
]


### CHANGEABLE VALUES ###
sheet_cell_range = 'Sheet1!A2:E17'
COL1_RANGE = 'A2:A17'
COL2_RANGE = 'B2:B17'
COL3_RANGE = 'C2:C17'
COL4_RANGE = 'D2:D17'
COL5_RANGE = 'E2:E17'
sheet_url = "https://docs.google.com/spreadsheets/d/13AHRFbjuJ1F6LEDU5o2949DCyCFtPAxXZgHg2fLH_jc/edit?ts=5c8913ff#gid=0"

# For changin' whenever:
logo_title = 'Halfway Crooks'
# Good logo fonts: pagga, mono9, ascii9, emboss, emboss2, future, smblock (meh)
logo_font = 'mono9' #'emboss' #'pagga' #'ascii9'  #'bigascii9'  #'emboss2' #'future'
# logo_offset = 250  # should range from ~100 to ~290
logo_color = color_codes['GREEN']

IMGFROMFILE = True
LOGOFILE = 'ascii_art/Halfway_slant_art.txt' #'fig.img'

col_lbls = ['Name', 'Type', 'ABV', 'Pour', 'Cost']
lbls_font = 'bubble' #'pagga' #'wideterm' #'smbraille' # 'smmono9' # 'smblock' # 'emboss2' # 'future'
lbls_color = color_codes['GREEN']

prompt_str = "sh-v4.4$ ./halfway_crooks.sh"

### CURSES CONSTANTS ###
# ls = curses.ACS_LTEE #curses.ACS_CKBOARD #curses.ACS_PLMINUS
# rs =  curses.ACS_RTEE
# ts = curses.ACS_HLINE #TTEE #curses.ACS_GEQUAL #curses.ACS_BOARD #curses.ACS_S3 #curses.ACS_HLINE #curses.ACS_TTEE #curses.ACS_NEQUAL #curses.ACS_CKBOARD
# bs = curses.ACS_BOARD #BTEE #curses.ACS_CKBOARD #curses.ACS_S7 #curses.ACS_HLINE #curses.ACS_BTEE
# tl = curses.ACS_ULCORNER #curses.ACS_RTEE #curses.ACS_DEGREE
# tr = curses.ACS_URCORNER
# bl = curses.ACS_SSBB #curses.ACS_DIAMOND
# br = curses.ACS_VLINE  #CKBOARD #SBBS
"""
Window type constants for border chars:
    ACS_BBSS        alternate name for upper right corner
    ACS_BLOCK       solid square block
    ACS_BOARD       board of squares
    ACS_BSBS        alternate name for horizontal line
    ACS_BSSB        alternate name for upper left corner
    ACS_BSSS        alternate name for top tee
    ACS_BTEE        bottom tee
    ACS_BULLET      bullet
    ACS_CKBOARD     checker board (stipple)
    ACS_DARROW      arrow pointing down
    ACS_DEGREE      degree symbol
    ACS_DIAMOND     diamond
    ACS_GEQUAL      greater-than-or-equal-to
    ACS_HLINE       horizontal line
    ACS_LANTERN     lantern symbol
    ACS_LARROW      left arrow
    ACS_LEQUAL      less-than-or-equal-to
    ACS_LLCORNER    lower left-hand corner
    ACS_LRCORNER    lower right-hand corner
    ACS_LTEE        left tee
    ACS_NEQUAL      not-equal sign
    ACS_PI          letter pi
    ACS_PLMINUS     plus-or-minus sign
    ACS_PLUS        big plus sign
    ACS_RARROW      right arrow
    ACS_RTEE        right tee
    ACS_S1          scan line 1
    ACS_S3          scan line 3
    ACS_S7          scan line 7
    ACS_S9          scan line 9
    ACS_SBBS        alternate name for lower right corner
    ACS_SBSB        alternate name for vertical line
    ACS_SBSS        alternate name for right tee
    ACS_SSBB        alternate name for lower left corner
    ACS_SSBS        alternate name for bottom tee
    ACS_SSSB        alternate name for left tee
    ACS_SSSS        alternate name for crossover or big plus
    ACS_STERLING    pound sterling
    ACS_TTEE        top tee
    ACS_UARROW      up arrow
    ACS_ULCORNER    upper left corner
    ACS_URCORNER    upper right corner
    ACS_VLINE       vertical line
"""

# menu_attribute_list = [
#         curses.A_BOLD,
#         # curses.A_UNDERLINE,
#         # curses.A_STANDOUT,
#         # curses.A_BLINK,
#         # curses.A_HORIZONTAL,
#         # curses.A_LEFT,
#         # curses.A_LOW,
#         # curses.A_VERTICAL,
#     ]
"""
Attributes:
    A_ALTCHARSET    Alternate character set mode
    A_BLINK         Blink mode
    A_BOLD          Bold mode
    A_DIM           Dim mode
    A_INVIS         Invisible or blank mode
    A_ITALIC        Italic mode
    A_NORMAL        Normal attribute
    A_PROTECT       Protected mode
    A_REVERSE       Reverse background and foreground colors
    A_STANDOUT      Standout mode
    A_UNDERLINE     Underline mode
    A_HORIZONTAL    Horizontal highlight
    A_LEFT          Left highlight
    A_LOW           Low highlight
    A_RIGHT         Right highlight
    A_TOP           Top highlight
    A_VERTICAL      Vertical highlight
    A_CHARTEXT      Bit-mask to extract a character
"""


"""
Predefined curses color constants:
    COLOR_BLACK, COLOR_BLUE, COLOR_CYAN, COLOR_GREEN, COLOR_MAGENTA, COLOR_RED, COLOR_WHITE, COLOR_YELLOW
"""
