import os, platform


class Platform(object):
    def __init__(self, font_path):
        self.font_path = font_path
        self.configure_paths()

    def configure_paths(self):
        os.environ["PYSDL2_DLL_PATH"] = os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib")

    def get_font_path(self, fontname):
        return os.path.join(self.font_path, "%s.ttf" % fontname)


class WindowsPlatform(Platform):
    def __init__(self):
        super().__init__("C:/Windows/Fonts")


class MacPlatform(Platform):
    def __init__(self):
        super().__init__("/Library/Fonts/")


p_str = platform.platform().lower()
_p = None
if "windows" in p_str:
    _p = WindowsPlatform()
elif "darwin" in p_str:
    _p = MacPlatform()


def get_font_path(fontname):
    return _p.get_font_path(fontname)

