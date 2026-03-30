import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStyleFactory
from BldgAuditToolPackage.GUI_Functionality import MyMainWindow
from PyQt5.QtCore import Qt
if __name__ == "__main__":
    import sys
    
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    # Use high DPI icons
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication([])
    app.setStyle(QStyleFactory.create("Fusion"))
    MainWindow = MyMainWindow()
    MainWindow.show()
    sys.exit(app.exec_())