from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QWidget, QGridLayout, QMessageBox, QListWidget, QListWidgetItem, QTreeWidgetItem, QStyle, QMenu, QFileDialog
from PySide6.QtCore import Qt, QCoreApplication, QSize, Slot, Signal
from PySide6.QtGui import QPixmap, QIcon, QCloseEvent
import sys, os
from PIL import ImageQt, Image
import zipfile as zf

class MyApp(QMainWindow):
  updateFileListSignal = Signal()

  def __init__(self):
    super().__init__()

    self.setWindowTitle(self.tr('MyApp'))
    self.currentDir = os.getcwd()

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
    self.fileListView.setContextMenuPolicy(Qt.CustomContextMenu)
    self.fileListView.customContextMenuRequested.connect(
        self.onFileListViewContextMenu)
    self.fileListView.itemDoubleClicked.connect(self.onItemDoubleClicked)
    self.fileListView.setSelectionMode(QListWidget.ExtendedSelection)
    self.mainLayout.addWidget(self.fileListView, 0, 0)
    self.updateFileListSignal.connect(self.updateFileList)
    self.updateFileListSignal.emit()

    menu = QMenu()
    menu.addAction(self.tr('Extract'))
    menu.addAction(self.tr('Create zip file'), self.onCreateZip)
    menu.addAction(self.tr('Create 7z file'))
    menu.addAction(self.tr('Create tar.gz file'))
    menu.addAction(self.tr('Create tar.xz file'))
    self.fileListViewContextMenu = menu

    btn = QPushButton(self.tr('Open'), self)
    btn.clicked.connect(self.debugClicked)
    self.mainLayout.addWidget(btn, 1, 0)

  def onCreateZip(self):
    fpath = QFileDialog.getSaveFileName(self, self.tr('Select zip file path'),
                                        self.currentDir,
                                        self.tr('Zip file (*.zip)'))
    self.makeZip(fpath)

  def makeZip(self, fpath, comporessionType=zf.ZIP_DEFLATED, compressLevel=9):
    zipFile = zf.ZipFile(fpath[0], 'w', comporessionType, compresslevel=compressLevel)
    for item in self.fileListView.selectedItems():
      data = item.data(Qt.UserRole)
      fname = data['path']
      if data['isDir']:
        self.writeZipDir(fname, os.path.basename(fname), zipFile)
      else:
        zipFile.write(fname, os.path.join(os.path.basename(fname)))
    zipFile.close()
    print('zip file created')

  def writeZipDir(self, dirPath, dirName, zipFile):
    for fname in os.listdir(dirPath):
      fpath = os.path.join(dirPath, fname)
      if os.path.isdir(fpath):
        self.writeZipDir(fpath, os.path.join(dirName, fname), zipFile)
      else:
        zipFile.write(fpath, os.path.join(dirName, fname))

    # self.label.setContextMenuPolicy(Qt.CustomContextMenu)
  def debugClicked(self):
    si = self.fileListView.selectedItems()
    print(si)

  def onFileListViewContextMenu(self, pos):
    items = self.fileListView.selectedItems()
    for item in items:
      print(item.data(Qt.UserRole))
    menu = self.fileListViewContextMenu
    menu.exec(self.fileListView.mapToGlobal(pos))

  def updateFileList(self):
    self.fileListView.clear()
    icon = None
    isDir = False
    fpath = ""
    dirList = ['..']
    dirList.extend(os.listdir(self.currentDir))
    for file in dirList:
      if file == '..':
        fpath = os.path.abspath(os.path.join(self.currentDir, os.pardir))
        isDir = True
      else:
        fpath = os.path.join(self.currentDir, file)
        isDir = os.path.isdir(fpath)

      if isDir:
        icon = QStyle.SP_DirIcon
      else:
        icon = QStyle.SP_FileIcon
      icon = self.style().standardIcon(icon)
      item = QListWidgetItem(icon, file, self.fileListView)
      item.setData(Qt.UserRole, {"isDir": isDir, "path": fpath})
      item.setIcon(icon)
      # item.setSizeHint(QSize(100, 100))
      # self.fileListView.addItem(file)

  @Slot(QListWidgetItem)
  def onItemDoubleClicked(self, item: QListWidgetItem):
    data = item.data(Qt.UserRole)
    if data is None:
      return
    if data["isDir"]:
      self.currentDir = data["path"]
      # self.updateFileList()
      self.updateFileListSignal.emit()

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