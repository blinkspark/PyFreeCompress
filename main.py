from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QWidget, QGridLayout, QMessageBox, QListWidget, QListWidgetItem, QTreeWidgetItem, QStyle
from PySide6.QtCore import Qt, QCoreApplication, QSize
from PySide6.QtGui import QPixmap, QIcon, QCloseEvent
import sys, os
from PIL import ImageQt, Image


class MyApp(QMainWindow):

  def __init__(self):
    super().__init__()

    self.setWindowTitle(self.tr('MyApp'))
    self.currentDir = os.getcwd()
    self.filelistViewItems: list[QListWidgetItem] = []

    self.initGUI()

  def initGUI(self):
    self.mainWidget = QWidget()
    self.setCentralWidget(self.mainWidget)
    self.mainLayout = QGridLayout()
    self.mainWidget.setLayout(self.mainLayout)
    self.resize(800, 600)

    self.fileMenu = self.menuBar().addMenu(self.tr('File'))
    self.createMenu = self.fileMenu.addMenu(self.tr('Create'))
    self.createMenu.addAction(self.tr('Zip'))
    self.fileMenu.addAction(self.tr('Exit'), self.exit)

    self.fileListView = QListWidget()
    self.fileListView.setSelectionMode(QListWidget.ExtendedSelection)
    self.mainLayout.addWidget(self.fileListView, 0, 0)
    self.updateFileList()

    btn = QPushButton(self.tr('Open'), self)
    btn.clicked.connect(self.debugClicked)
    self.mainLayout.addWidget(btn, 1, 0)

    # self.label.setContextMenuPolicy(Qt.CustomContextMenu)
  def debugClicked(self):
    si = self.fileListView.selectedItems()
    print(si)

  def updateFileList(self):
    self.fileListView.clear()
    for file in os.listdir(self.currentDir):
      icon = None
      if os.path.isdir(os.path.join(self.currentDir, file)):
        icon = QStyle.SP_DirIcon
      else:
        icon = QStyle.SP_FileIcon
      icon = self.style().standardIcon(icon)
      print(icon)
      item = QListWidgetItem(icon, file, self.fileListView)
      item.setIcon(icon)
      # item.setSizeHint(QSize(100, 100))
      # self.fileListView.addItem(file)
      self.filelistViewItems.append(item)

  def closeEvent(self, event: QCloseEvent) -> None:
    mb = QMessageBox()
    mb.setText(self.tr('Are you sure you want to quit?'))
    mb.setIcon(QMessageBox.Question)
    mb.setStandardButtons(QMessageBox.Ok.Yes | QMessageBox.No)
    mb.setDefaultButton(QMessageBox.No)
    ret = mb.exec()
    if ret == QMessageBox.Yes:
      # event.accept()
      super().closeEvent(event)
    else:
      event.ignore()

  def exit(self):
    QApplication.instance().quit()


def main():
  app = QApplication(sys.argv)
  mainWindow = MyApp()
  mainWindow.show()

  sys.exit(app.exec())


if __name__ == '__main__':
  main()