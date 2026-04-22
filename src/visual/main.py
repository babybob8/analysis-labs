import sys
import pyqtgraph as pg
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget



"""
діаграми розкиду - 168стр
паралельні координати - 170стр
теплова карта - 173стр
бульбашкова діаграма - 174стр
"""




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.plot = pg.PlotWidget()
        layout.addWidget(self.plot)
        
        self.plot.plot([1, 2, 3, 4], [10, 20, 15, 30])




# // Debug
def main():
    app = QApplication(sys.argv)
    wnd = MainWindow()
    wnd.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()