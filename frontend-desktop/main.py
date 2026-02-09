import sys
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QFileDialog, QTableWidget,
                             QTableWidgetItem, QMessageBox, QTabWidget, QListWidget, QGroupBox, QScrollArea)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

API_URL = "http://localhost:8000/api/"

class LoginDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")
        self.resize(300, 150)

        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.handle_login)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # Test credentials
        try:
            response = requests.get(API_URL + "history/", auth=(username, password))
            if response.status_code == 200:
                self.parent().on_login_success(username, password)
                self.close()
            else:
                QMessageBox.warning(self, "Error", "Invalid credentials")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection failed: {str(e)}")

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chemical Equipment Visualizer")
        self.resize(1200, 800)

        self.auth = None
        self.current_upload_id = None

        self.login_widget = LoginDialog(self)
        self.setCentralWidget(self.login_widget)

    def on_login_success(self, username, password):
        self.auth = (username, password)
        self.init_ui()
        self.load_history()
        self.load_dashboard()

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout()

        # Left Panel: History & Actions
        left_panel = QVBoxLayout()

        self.upload_btn = QPushButton("Upload CSV")
        self.upload_btn.clicked.connect(self.upload_file)
        left_panel.addWidget(self.upload_btn)

        left_panel.addWidget(QLabel("History:"))
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.on_history_select)
        left_panel.addWidget(self.history_list)

        main_layout.addLayout(left_panel, 1)

        # Right Panel: Dashboard
        right_panel = QVBoxLayout()

        # Summary Stats
        stats_group = QGroupBox("Summary Statistics")
        stats_layout = QHBoxLayout()
        self.lbl_count = QLabel("Count: -")
        self.lbl_flow = QLabel("Avg Flow: -")
        self.lbl_press = QLabel("Avg Press: -")
        self.lbl_temp = QLabel("Avg Temp: -")
        stats_layout.addWidget(self.lbl_count)
        stats_layout.addWidget(self.lbl_flow)
        stats_layout.addWidget(self.lbl_press)
        stats_layout.addWidget(self.lbl_temp)
        stats_group.setLayout(stats_layout)
        right_panel.addWidget(stats_group)

        # Charts Area
        charts_layout = QHBoxLayout()
        self.canvas_type = MplCanvas(self, width=5, height=4, dpi=100)
        self.canvas_params = MplCanvas(self, width=5, height=4, dpi=100)
        charts_layout.addWidget(self.canvas_type)
        charts_layout.addWidget(self.canvas_params)
        right_panel.addLayout(charts_layout, 2)

        # Table & PDF Button
        right_panel.addWidget(QLabel("Equipment Data:"))
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Name", "Type", "Flowrate", "Pressure", "Temperature"])
        right_panel.addWidget(self.table, 2)

        self.pdf_btn = QPushButton("Download PDF Report")
        self.pdf_btn.clicked.connect(self.download_pdf)
        right_panel.addWidget(self.pdf_btn)

        main_layout.addLayout(right_panel, 3)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def load_history(self):
        try:
            response = requests.get(API_URL + "history/", auth=self.auth)
            if response.status_code == 200:
                self.history_list.clear()
                uploads = response.json()
                for upload in uploads:
                    item = f"Upload {upload['id']} ({upload['uploaded_at']})"
                    self.history_list.addItem(item)
                    # Store ID in item data? simpler to just parse or store list
                    self.history_list.item(self.history_list.count()-1).setData(Qt.UserRole, upload['id'])
        except Exception as e:
            print(f"Error loading history: {e}")

    def on_history_select(self, item):
        upload_id = item.data(Qt.UserRole)
        self.load_dashboard(upload_id)

    def upload_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open CSV', '.', "CSV Files (*.csv)")
        if fname:
            try:
                files = {'file': open(fname, 'rb')}
                response = requests.post(API_URL + "upload/", files=files, auth=self.auth)
                if response.status_code == 201:
                    QMessageBox.information(self, "Success", "Upload successful")
                    self.load_history()
                    self.load_dashboard(response.json()['id'])
                else:
                    QMessageBox.warning(self, "Error", f"Upload failed: {response.text}")
            except Exception as e:
                 QMessageBox.critical(self, "Error", f"Upload error: {e}")

    def load_dashboard(self, upload_id=None):
        url = API_URL + ("dashboard/" if not upload_id else f"dashboard/{upload_id}/")
        try:
            response = requests.get(url, auth=self.auth)
            if response.status_code == 200:
                data = response.json()
                self.current_upload_id = data['upload_id']
                self.update_ui(data)
            else:
                print(f"Error loading dashboard: {response.text}")
        except Exception as e:
            print(f"Connection error: {e}")

    def update_ui(self, data):
        summary = data['summary']
        self.lbl_count.setText(f"Count: {summary['count']}")
        self.lbl_flow.setText(f"Avg Flow: {summary.get('avg_flowrate', 0):.2f}")
        self.lbl_press.setText(f"Avg Press: {summary.get('avg_pressure', 0):.2f}")
        self.lbl_temp.setText(f"Avg Temp: {summary.get('avg_temperature', 0):.2f}")

        # Update Table
        rows = data['data']
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(row['equipment_name'])))
            self.table.setItem(i, 1, QTableWidgetItem(str(row['equipment_type'])))
            self.table.setItem(i, 2, QTableWidgetItem(str(row['flowrate'])))
            self.table.setItem(i, 3, QTableWidgetItem(str(row['pressure'])))
            self.table.setItem(i, 4, QTableWidgetItem(str(row['temperature'])))

        # Update Charts
        # 1. Bar Chart (Type Distribution)
        self.canvas_type.figure.clf()
        ax1 = self.canvas_type.figure.add_subplot(111)
        types = [d['equipment_type'] for d in summary['type_distribution']]
        counts = [d['count'] for d in summary['type_distribution']]
        ax1.bar(types, counts)
        ax1.set_title("Equipment Types")
        ax1.set_ylabel("Count")
        self.canvas_type.draw()

        # 2. Line Chart (Parameters)
        self.canvas_params.figure.clf()
        ax2 = self.canvas_params.figure.add_subplot(111)
        names = [d['equipment_name'] for d in rows] # Might be too crowded
        # Just use index
        x = range(len(rows))
        ax2.plot(x, [d['flowrate'] for d in rows], label='Flowrate')
        ax2.plot(x, [d['pressure'] for d in rows], label='Pressure')
        ax2.plot(x, [d['temperature'] for d in rows], label='Temperature')
        ax2.legend()
        ax2.set_title("Parameters Overview")
        self.canvas_params.draw()

    def download_pdf(self):
        if not self.current_upload_id:
            return
        try:
            response = requests.get(API_URL + f"report/{self.current_upload_id}/", auth=self.auth)
            if response.status_code == 200:
                fname, _ = QFileDialog.getSaveFileName(self, 'Save PDF', f"report_{self.current_upload_id}.pdf", "PDF Files (*.pdf)")
                if fname:
                    with open(fname, 'wb') as f:
                        f.write(response.content)
                    QMessageBox.information(self, "Success", "PDF saved successfully")
            else:
                 QMessageBox.warning(self, "Error", "Failed to download PDF")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Download error: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
