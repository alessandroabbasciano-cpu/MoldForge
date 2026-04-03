import os
import json
import urllib.request
import urllib.error
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
                               QPushButton, QLabel, QMessageBox, QApplication, QListWidgetItem)
from PySide6.QtCore import Qt

class CommunityBrowserDialog(QDialog):
    def __init__(self, parent=None, local_shapes_dir="shapes_library"):
        super().__init__(parent)
        self.setWindowTitle("Community Shapes Store")
        self.resize(450, 350)
        self.local_shapes_dir = local_shapes_dir
        
        # GitHub API URL
        self.api_url = "https://api.github.com/repos/alessandroabbasciano-cpu/MoldForge/contents/community_shapes?ref=edge"
        
        self.shapes_data = []
        self.downloaded_something = False
        
        self.init_ui()
        self.fetch_shapes_list()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.lbl_status = QLabel("Connecting to GitHub...")
        layout.addWidget(self.lbl_status)
        
        self.list_widget = QListWidget()
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.list_widget)
        
        btn_layout = QHBoxLayout()
        self.btn_download = QPushButton("Download and Install")
        self.btn_download.setEnabled(False)
        self.btn_download.clicked.connect(self.download_selected_shape)
        
        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.close)
        
        btn_layout.addWidget(self.btn_download)
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)

    def fetch_shapes_list(self):
        # Keep UI responsive during fetch
        QApplication.processEvents()
        
        req = urllib.request.Request(self.api_url)
        req.add_header('User-Agent', 'MoldForge-App') 
        
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                
                # Filter for .dxf files only
                self.shapes_data = [item for item in data if item['name'].lower().endswith('.dxf')]
                self.populate_list()
                
        except urllib.error.HTTPError as e:
            self.lbl_status.setText(f"GitHub API Error: {e.code}")
        except urllib.error.URLError:
            self.lbl_status.setText("Network error. Check your internet connection.")
        except Exception as e:
            self.lbl_status.setText(f"Unknown error: {str(e)}")

    def populate_list(self):
        self.list_widget.clear()
        
        if not self.shapes_data:
            self.lbl_status.setText("No shapes found in the community repository.")
            return
            
        self.lbl_status.setText(f"Found {len(self.shapes_data)} official community shapes!")
        
        # Ensure local directory exists
        os.makedirs(self.local_shapes_dir, exist_ok=True)
        local_files = os.listdir(self.local_shapes_dir)
        
        for shape in self.shapes_data:
            file_name = shape['name']
            item = QListWidgetItem(file_name)
            
            # Check if file is already installed
            if file_name in local_files:
                item.setText(f"{file_name} (Already Installed)")
                item.setForeground(Qt.gray)
                item.setData(Qt.UserRole, "installed")
            else:
                item.setData(Qt.UserRole, "available")
                
            # Store the download URL
            item.setData(Qt.UserRole + 1, shape['download_url'])
            self.list_widget.addItem(item)

    def on_selection_changed(self):
        items = self.list_widget.selectedItems()
        if not items:
            self.btn_download.setEnabled(False)
            return
            
        item = items[0]
        if item.data(Qt.UserRole) == "installed":
            self.btn_download.setEnabled(False)
            self.btn_download.setText("Already Installed")
        else:
            self.btn_download.setEnabled(True)
            self.btn_download.setText("Download and Install")

    def download_selected_shape(self):
        items = self.list_widget.selectedItems()
        if not items: return
        item = items[0]
        
        file_name = item.text()
        download_url = item.data(Qt.UserRole + 1)
        save_path = os.path.join(self.local_shapes_dir, file_name)
        
        self.btn_download.setEnabled(False)
        self.lbl_status.setText(f"Downloading {file_name}...")
        QApplication.processEvents()
        
        try:
            urllib.request.urlretrieve(download_url, save_path)
            self.lbl_status.setText(f"{file_name} installed successfully!")
            self.downloaded_something = True
            
            item.setText(f"{file_name} (Already Installed)")
            item.setForeground(Qt.gray)
            item.setData(Qt.UserRole, "installed")
            
        except Exception as e:
            QMessageBox.critical(self, "Download Error", f"Unable to download file:\n{str(e)}")
            self.lbl_status.setText("Error during download.")
        finally:
            self.on_selection_changed()