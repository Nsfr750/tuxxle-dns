
import os
import sys

# Set Qt plugin path
if hasattr(sys, 'frozen'):
    # We are running in a PyInstaller bundle
    os.environ['QT_PLUGIN_PATH'] = os.path.join(sys._MEIPASS, 'PySide6', 'plugins')

# Disable Qt WebEngine components if not needed
os.environ['QTWEBENGINE_DISABLE_SANDBOX'] = '1'
