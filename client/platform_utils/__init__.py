import os, platform as sys_platform


class Platform(object):
    def __init__(self, font_path):
        self.font_path = font_path

    def configure_paths(self):
        import client
        os.environ["PYSDL2_DLL_PATH"] = os.path.join(os.path.dirname(os.path.realpath(client.__file__)), "lib")

    def get_font_path(self, fontname):
        return os.path.join(self.font_path, "%s.ttf" % fontname)

    @staticmethod
    def get_platform():
        platform_string = sys_platform.platform().lower()
        if "windows" in platform_string:
            return WindowsPlatform()
        elif "darwin" in platform_string:
            return MacPlatform()


class WindowsPlatform(Platform):
    def __init__(self):
        super().__init__("C:/Windows/Fonts")


class MacPlatform(Platform):
    def __init__(self):
        super().__init__("/Library/Fonts/")


platform = Platform.get_platform()


