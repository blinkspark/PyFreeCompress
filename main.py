from tracemalloc import take_snapshot
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QWidget, QGridLayout, QMessageBox, QListWidget, QListWidgetItem, QTreeWidgetItem, QStyle, QMenu, QFileDialog, QProgressDialog
from PySide6.QtCore import Qt, QCoreApplication, QSize, Slot, Signal
from PySide6.QtGui import QPixmap, QIcon, QCloseEvent
import sys, os
from os import path
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

    btn = QPushButton(self.tr('Debug'), self)
    btn.clicked.connect(self.debugClicked)
    self.mainLayout.addWidget(btn, 1, 0)

  def walkDir(self, dirPath: str) -> list[tuple[str, str]]:
    parDir: str = path.abspath(path.join(dirPath, os.pardir))
    dirList = []
    for root, _, files in os.walk(dirPath):
      for file in files:
        fpath = path.join(root, file)
        dirList.append((fpath, path.relpath(fpath, parDir)))
    return dirList

  def getTaskData(self) -> list[tuple[str, str]]:
    taskData: list[tuple[str, str]] = []
    for item in self.fileListView.selectedItems():
      data = item.data(Qt.UserRole)
      fname = data['path']
      if data['isDir']:
        # self.writeZipDir(fname, path.basename(fname), zipFile)
        tds = self.walkDir(fname)
        taskData.extend(tds)
      else:
        # zipFile.write(fname, path.basename(fname))
        td = (fname, path.basename(fname))
        taskData.append(td)
    return taskData

  def onCreateZip(self):
    fpath = QFileDialog.getSaveFileName(self, self.tr('Select zip file path'),
                                        self.currentDir,
                                        self.tr('Zip file (*.zip)'))
    self.makeZip(fpath[0])

  def makeZip(self,
              fpath: str,
              comporessionType=zf.ZIP_DEFLATED,
              compressLevel=6):
    zipFile = zf.ZipFile(fpath,
                         'w',
                         comporessionType,
                         compresslevel=compressLevel)
    taskData = self.getTaskData()
    taskCount = len(taskData)
    progressDialog = QProgressDialog(self.tr('Compressing...'),
                                     self.tr('Cancel'), 0, taskCount)
    progressDialog.setWindowModality(Qt.ApplicationModal)
    progressDialog.setMinimumDuration(1)
    progressDialog.can
    # progressDialog.setValue(0)
    progressDialog.show()
    for (i, td) in enumerate(taskData):
      print(i + 1, taskCount, td)
      progressDialog.setValue(i + 1)
      progressDialog.setLabelText(path.basename(td[1]))
      zipFile.write(td[0], td[1])
      # time.sleep(0.1)
    zipFile.close()

  def writeZipDir(self, dirPath, dirName, zipFile):
    for fname in os.listdir(dirPath):
      fpath = path.join(dirPath, fname)
      if path.isdir(fpath):
        self.writeZipDir(fpath, path.join(dirName, fname), zipFile)
      else:
        zipFile.write(fpath, path.join(dirName, fname))

    # self.label.setContextMenuPolicy(Qt.CustomContextMenu)
  def debugClicked(self):
    for item in self.fileListView.selectedItems():
      data = item.data(Qt.UserRole)
      fpath = data['path']
      if data['isDir']:
        pardir = path.abspath(path.join(fpath, os.pardir))
        print(f'pardir:{pardir}')
        for f in self.walkDir(fpath):
          print(f)

  def onFileListViewContextMenu(self, pos):
    items = self.fileListView.selectedItems()
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
        fpath = path.abspath(path.join(self.currentDir, os.pardir))
        isDir = True
      else:
        fpath = path.join(self.currentDir, file)
        isDir = path.isdir(fpath)

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
    pass
    # mb = QMessageBox()
    # mb.setText(self.tr('Are you sure you want to quit?'))
    # mb.setIcon(QMessageBox.Question)
    # mb.setStandardButtons(QMessageBox.Ok.Yes | QMessageBox.No)
    # mb.setDefaultButton(QMessageBox.No)
    # ret = mb.exec()
    # if ret == QMessageBox.Yes:
    #   # event.accept()
    #   super().closeEvent(event)
    # else:
    #   event.ignore()

  def exit(self):
    QApplication.instance().quit()


def main():
  app = QApplication(sys.argv)
  mainWindow = MyApp()
  mainWindow.show()
  sys.exit(app.exec())


if __name__ == '__main__':
  main()