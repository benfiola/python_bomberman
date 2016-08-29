import os, platform


def init():
    os.environ["PYSDL2_DLL_PATH"] = os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib")


def base_font_path():
    p_str = platform.platform().lower()
    if "windows" in p_str:
        return "C:/Windows/Fonts"
    elif "darwin" in p_str:
        return "/Library/Fonts/"


def get_font_path(fontname):
    return os.path.join(base_font_path(), "%s.ttf" % fontname)

init()

