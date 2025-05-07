import os
import mss
import mss.tools
import datetime

def take_and_save_screenshot(screen_geometry=None):
    date = datetime.date.today()
    output_dir = os.getcwd() + f"/{date}"
    os.makedirs(output_dir, exist_ok=True)

    now = datetime.datetime.now().strftime("%H-%M-%S")

    sct = mss.mss()

    
    if screen_geometry:
        # Create a monitor dict for the specific screen
        monitor = {
            "left": screen_geometry.x(),
            "top": screen_geometry.y(),
            "width": screen_geometry.width(),
            "height": screen_geometry.height()
        }
        screenshot = sct.grab(monitor)
        output_path = os.path.join(output_dir, f"{now}.png")
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=output_path)
    else:
        # Fallback to capturing all monitors if no geometry provided
        for monitor_number, monitor in enumerate(sct.monitors[1:], 1):
            screenshot = sct.grab(monitor)
            output_path = os.path.join(output_dir, f"{now}_monitor_{monitor_number}.png")
            mss.tools.to_png(screenshot.rgb, screenshot.size, output=output_path)
    
    sct.close()