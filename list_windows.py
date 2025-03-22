import win32gui

def list_windows():
    def callback(hwnd, hwnds):
        title = win32gui.GetWindowText(hwnd)
        if title:
            hwnds[title] = hwnd
        return True

    hwnds = {}
    win32gui.EnumWindows(callback, hwnds)
    return hwnds

if __name__ == "__main__":
    windows = list_windows()
    for title, hwnd in windows.items():
        print(f"Title: {title}, HWND: {hwnd}")
