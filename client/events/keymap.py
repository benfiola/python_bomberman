import sdl2


class KeyMap(object):
    A = 0
    B = 1
    C = 2
    D = 3
    E = 4
    F = 5
    G = 6
    H = 7
    I = 8
    J = 9
    K = 10
    L = 11
    M = 12
    N = 13
    O = 14
    P = 15
    Q = 16
    R = 17
    S = 18
    T = 19
    U = 20
    V = 21
    W = 22
    X = 23
    Y = 24
    Z = 25
    K_0 = 26
    K_1 = 27
    K_2 = 28
    K_3 = 29
    K_4 = 30
    K_5 = 31
    K_6 = 32
    K_7 = 33
    K_8 = 34
    K_9 = 35
    N_0 = 36
    N_1 = 37
    N_2 = 38
    N_3 = 39
    N_4 = 40
    N_5 = 41
    N_6 = 42
    N_7 = 43
    N_8 = 44
    N_9 = 45
    N_RETURN = 46
    ESC = 47
    TILDE = 48
    TAB = 49
    CAPS_LOCK = 50
    LEFT_SHIFT = 51
    LEFT_CONTROL = 52
    LEFT_ALT = 53
    LEFT_META = 54
    SPACE = 55
    RIGHT_META = 56
    RIGHT_ALT = 57
    RIGHT_CONTROL = 58
    RIGHT_SHIFT = 59
    RETURN = 60
    BACKSPACE = 61
    LEFT_BRACKET = 62
    RIGHT_BRACKET = 63
    COLON = 64
    QUOTE = 65
    COMMA = 66
    PERIOD = 67
    SLASH = 68
    BACKSLASH = 69
    MINUS = 70
    PLUS = 71
    UP = 72
    LEFT = 73
    RIGHT = 74
    DOWN = 75

class SDL2KeyMap(object):
    MAP = {
        sdl2.SDLK_a: KeyMap.A,
        sdl2.SDLK_b: KeyMap.B,
        sdl2.SDLK_c: KeyMap.C,
        sdl2.SDLK_d: KeyMap.D,
        sdl2.SDLK_e: KeyMap.E,
        sdl2.SDLK_f: KeyMap.F,
        sdl2.SDLK_g: KeyMap.G,
        sdl2.SDLK_h: KeyMap.H,
        sdl2.SDLK_i: KeyMap.I,
        sdl2.SDLK_j: KeyMap.J,
        sdl2.SDLK_k: KeyMap.K,
        sdl2.SDLK_l: KeyMap.L,
        sdl2.SDLK_m: KeyMap.M,
        sdl2.SDLK_n: KeyMap.N,
        sdl2.SDLK_o: KeyMap.O,
        sdl2.SDLK_p: KeyMap.P,
        sdl2.SDLK_q: KeyMap.Q,
        sdl2.SDLK_r: KeyMap.R,
        sdl2.SDLK_s: KeyMap.S,
        sdl2.SDLK_t: KeyMap.T,
        sdl2.SDLK_u: KeyMap.U,
        sdl2.SDLK_v: KeyMap.V,
        sdl2.SDLK_w: KeyMap.W,
        sdl2.SDLK_x: KeyMap.X,
        sdl2.SDLK_y: KeyMap.Y,
        sdl2.SDLK_z: KeyMap.Z,
        sdl2.SDLK_0: KeyMap.K_0,
        sdl2.SDLK_1: KeyMap.K_1,
        sdl2.SDLK_2: KeyMap.K_2,
        sdl2.SDLK_3: KeyMap.K_3,
        sdl2.SDLK_4: KeyMap.K_4,
        sdl2.SDLK_5: KeyMap.K_5,
        sdl2.SDLK_6: KeyMap.K_6,
        sdl2.SDLK_7: KeyMap.K_7,
        sdl2.SDLK_8: KeyMap.K_8,
        sdl2.SDLK_9: KeyMap.K_9,
        sdl2.SDLK_KP_0: KeyMap.N_0,
        sdl2.SDLK_KP_1: KeyMap.N_1,
        sdl2.SDLK_KP_2: KeyMap.N_2,
        sdl2.SDLK_KP_3: KeyMap.N_3,
        sdl2.SDLK_KP_4: KeyMap.N_4,
        sdl2.SDLK_KP_5: KeyMap.N_5,
        sdl2.SDLK_KP_6: KeyMap.N_6,
        sdl2.SDLK_KP_7: KeyMap.N_7,
        sdl2.SDLK_KP_8: KeyMap.N_8,
        sdl2.SDLK_KP_9: KeyMap.N_9,
        sdl2.SDLK_RETURN2: KeyMap.N_RETURN,
        sdl2.SDLK_ESCAPE: KeyMap.ESC,
        sdl2.SDLK_BACKQUOTE: KeyMap.TILDE,
        sdl2.SDLK_TAB: KeyMap.TAB,
        sdl2.SDLK_CAPSLOCK: KeyMap.CAPS_LOCK,
        sdl2.SDLK_LSHIFT: KeyMap.LEFT_SHIFT,
        sdl2.SDLK_LCTRL: KeyMap.LEFT_CONTROL,
        sdl2.SDLK_LALT: KeyMap.LEFT_ALT,
        sdl2.SDLK_LGUI: KeyMap.LEFT_META,
        sdl2.SDLK_SPACE: KeyMap.SPACE,
        sdl2.SDLK_RGUI: KeyMap.RIGHT_META,
        sdl2.SDLK_RALT: KeyMap.RIGHT_ALT,
        sdl2.SDLK_RCTRL: KeyMap.RIGHT_CONTROL,
        sdl2.SDLK_RSHIFT: KeyMap.RIGHT_SHIFT,
        sdl2.SDLK_RETURN: KeyMap.RETURN,
        sdl2.SDLK_BACKSPACE: KeyMap.BACKSPACE,
        sdl2.SDLK_LEFTBRACKET: KeyMap.LEFT_BRACKET,
        sdl2.SDLK_RIGHTBRACKET: KeyMap.RIGHT_BRACKET,
        sdl2.SDLK_COLON: KeyMap.COLON,
        sdl2.SDLK_QUOTE: KeyMap.QUOTE,
        sdl2.SDLK_COMMA: KeyMap.COMMA,
        sdl2.SDLK_PERIOD: KeyMap.PERIOD,
        sdl2.SDLK_SLASH: KeyMap.SLASH,
        sdl2.SDLK_BACKSLASH: KeyMap.BACKSLASH,
        sdl2.SDLK_MINUS: KeyMap.MINUS,
        sdl2.SDLK_PLUS: KeyMap.PLUS,
        sdl2.SDLK_UP: KeyMap.UP,
        sdl2.SDLK_LEFT: KeyMap.LEFT,
        sdl2.SDLK_RIGHT: KeyMap.RIGHT,
        sdl2.SDLK_DOWN: KeyMap.DOWN,
    }

    @staticmethod
    def convert_from_sdl2(key_code):
        if key_code in SDL2KeyMap.MAP:
            return SDL2KeyMap.MAP[key_code]
        return None
