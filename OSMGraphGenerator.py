import os

import osmnx
import osmnx.graph
import osmnx.settings
from PyQt6 import QtGui, QtCore, QtWidgets
from PyQt6.QtWidgets import QMainWindow
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import ctypes

# TODO generate docs to methods
CUSTOM_FILTER_MAPPING = {
    "Select a custom filter . . .": None,
    "All roads": None,
    "Motorways only": '["highway"~"motorway"]',
    "Primary and secondary roads": '["highway"~"primary|secondary"]',
    "Residential roads only": '["highway"~"residential"]',
    "Primary, secondary, and residential roads": '["highway"~"primary|secondary|residential"]'
}



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setObjectName("MainWindow")
        self.setWindowTitle("OSM Graph Generator")
        self.resize(1100, 900)
        self.setFont(QtGui.QFont("Arial", 10))
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        self.setWindowIcon(QtGui.QIcon("./logos/osmgraphgenerator.png"))
        self.setIconSize(QtCore.QSize(32, 32))
        self.setTabShape(QtWidgets.QTabWidget.TabShape.Rounded)

        self.central_widget = QtWidgets.QWidget(self)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.central_widget)

        self.controls_frame = QtWidgets.QFrame(self.central_widget)
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.controls_frame)

        self.osm_controls_frame = QtWidgets.QFrame(self.controls_frame)
        self.locations_combo_box = QtWidgets.QComboBox(self.osm_controls_frame)
        self.network_combo_box = QtWidgets.QComboBox(self.osm_controls_frame)
        self.custom_filter_combo_box = QtWidgets.QComboBox(self.osm_controls_frame)
        self.simplify_box = QtWidgets.QCheckBox("Simplify Graph", self.osm_controls_frame)
        self.retain_box = QtWidgets.QCheckBox("Retain All", self.osm_controls_frame)
        self.truncate_box = QtWidgets.QCheckBox("Truncate By Edge", self.osm_controls_frame)
        self.osm_label = QtWidgets.QLabel("OSM Controls", self.osm_controls_frame)
        self.custom_location_text = QtWidgets.QPlainTextEdit(self.osm_controls_frame)

        self.graph_controls_frame = QtWidgets.QFrame(self.controls_frame)
        self.graph_label = QtWidgets.QLabel("Graph Controls", self.graph_controls_frame)
        self.node_size_spin_box = QtWidgets.QDoubleSpinBox(self.graph_controls_frame)
        self.node_color_combo_box = QtWidgets.QComboBox(self.graph_controls_frame)
        self.edge_color_combo_box = QtWidgets.QComboBox(self.graph_controls_frame)
        self.background_color_combo_box = QtWidgets.QComboBox(self.graph_controls_frame)
        self.edge_linewidht_spin_box = QtWidgets.QDoubleSpinBox(self.graph_controls_frame)
        self.color_label = QtWidgets.QLabel("Color", self.graph_controls_frame)
        self.size_label = QtWidgets.QLabel("Size", self.graph_controls_frame)
        self.background_label = QtWidgets.QLabel("Background", self.graph_controls_frame)
        self.nodes_label = QtWidgets.QLabel("Nodes", self.graph_controls_frame)
        self.edges_label = QtWidgets.QLabel("Edges", self.graph_controls_frame)
        self.bounding_box_label = QtWidgets.QLabel("BoundingBox", self.graph_controls_frame)
        self.bounding_box_west = QtWidgets.QPlainTextEdit(self.graph_controls_frame)
        self.bounding_box_north = QtWidgets.QPlainTextEdit(self.graph_controls_frame)
        self.bounding_box_east = QtWidgets.QPlainTextEdit(self.graph_controls_frame)
        self.bounding_box_south = QtWidgets.QPlainTextEdit(self.graph_controls_frame)

        self.setup_controls_frame()

        self.buttons_frame = QtWidgets.QFrame(self.central_widget)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.buttons_frame)
        self.visualize_button_frame = QtWidgets.QFrame(self.buttons_frame)
        self.visualize_button = QtWidgets.QPushButton("Visualize", self.visualize_button_frame)
        self.save_button_frame = QtWidgets.QFrame(self.buttons_frame)
        self.saved_file_name = QtWidgets.QPlainTextEdit(self.save_button_frame)
        self.save_button = QtWidgets.QPushButton("Save", self.save_button_frame)
        self.format_label = QtWidgets.QLabel(".graphml", self.save_button_frame)

        self.setup_buttons_frame()

        self.canvas_frame = QtWidgets.QFrame(self.central_widget)
        self.canvas_layout = QtWidgets.QVBoxLayout(self.canvas_frame)
        self.fig = None
        self.canvas = None
        self.toolbar = None

        self.setup_canvas_frame()

        self.setCentralWidget(self.central_widget)
        self.setStatusBar(QtWidgets.QStatusBar(self))

        self.G = None

        self.visualize_button.clicked.connect(self.run_visualization)
        self.save_button.clicked.connect(self.save_graph)

        QtCore.QMetaObject.connectSlotsByName(self)

    def setup_controls_frame(self):
        self.controls_frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.controls_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)

        self.setup_osm_controls()
        self.setup_graph_controls()

        self.verticalLayout.addWidget(self.controls_frame)

    def setup_osm_controls(self):
        self.osm_controls_frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.osm_controls_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)

        self.locations_combo_box.setGeometry(QtCore.QRect(20, 30, 440, 40))
        self.locations_combo_box.setFont(QtGui.QFont("Arial", 11))
        self.locations_combo_box.addItems([
            "Select a location . . .", "Piedmont, California, USA", "Manhattan, New York, USA",
            "Debrecen, Hungary", "Paris, France", "Berlin, Germany", "London, UK"
        ])

        self.network_combo_box.setGeometry(QtCore.QRect(20, 160, 440, 40))
        self.network_combo_box.setFont(QtGui.QFont("Arial", 11))
        self.network_combo_box.addItems([
            "Select a network type . . .", "all", "all_public", "bike", "drive", "walk"
        ])

        self.custom_filter_combo_box.setGeometry(QtCore.QRect(20, 225, 440, 40))
        self.custom_filter_combo_box.setFont(QtGui.QFont("Arial", 11))
        self.custom_filter_combo_box.addItems([
            "Select a custom filter . . .", "All roads", "Motorways only", "Primary and secondary roads",
            "Residential roads only", "Primary, secondary, and residential roads"
        ])

        self.simplify_box.setGeometry(QtCore.QRect(20, 280, 130, 50))
        self.simplify_box.setFont(QtGui.QFont("Arial", 11))
        self.simplify_box.setChecked(True)

        self.retain_box.setGeometry(QtCore.QRect(190, 280, 130, 50))
        self.retain_box.setFont(QtGui.QFont("Arial", 11))

        self.truncate_box.setGeometry(QtCore.QRect(340, 280, 135, 50))
        self.truncate_box.setFont(QtGui.QFont("Arial", 11))

        self.osm_label.setGeometry(QtCore.QRect(10, 0, 121, 21))
        self.osm_label.setFont(QtGui.QFont("Arial", 13))

        self.custom_location_text.setGeometry(QtCore.QRect(20, 95, 440, 40))
        self.custom_location_text.setFont(QtGui.QFont("Arial", 11))
        self.custom_location_text.setPlainText("Or enter a custom location . . .")

        self.horizontalLayout.addWidget(self.osm_controls_frame)

    def setup_graph_controls(self):
        self.graph_controls_frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.graph_controls_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)

        self.graph_label.setGeometry(QtCore.QRect(0, 0, 141, 21))
        self.graph_label.setFont(QtGui.QFont("Arial", 13))

        self.node_size_spin_box.setGeometry(QtCore.QRect(200, 120, 61, 31))
        self.node_size_spin_box.setFont(QtGui.QFont("Arial", 11))
        self.node_size_spin_box.setDecimals(0)
        self.node_size_spin_box.setSingleStep(1)
        self.node_size_spin_box.setValue(8)

        self.node_color_combo_box.setGeometry(QtCore.QRect(340, 120, 101, 31))
        self.node_color_combo_box.setFont(QtGui.QFont("Arial", 11))
        self.node_color_combo_box.addItems([
            "black", "white", "gray", "red", "blue", "green", "yellow", "orange", "pink"
        ])

        self.edge_color_combo_box.setGeometry(QtCore.QRect(340, 180, 101, 31))
        self.edge_color_combo_box.setFont(QtGui.QFont("Arial", 11))
        self.edge_color_combo_box.addItems([
            "gray", "white", "black", "red", "blue", "green", "yellow", "orange", "pink"
        ])

        self.background_color_combo_box.setGeometry(QtCore.QRect(340, 60, 101, 31))
        self.background_color_combo_box.setFont(QtGui.QFont("Arial", 11))
        self.background_color_combo_box.addItems([
            "white", "black", "gray", "red", "blue", "green", "yellow", "orange", "pink"
        ])

        self.edge_linewidht_spin_box.setGeometry(QtCore.QRect(200, 180, 61, 31))
        self.edge_linewidht_spin_box.setFont(QtGui.QFont("Arial", 11))
        self.edge_linewidht_spin_box.setDecimals(1)
        self.edge_linewidht_spin_box.setSingleStep(0.5)
        self.edge_linewidht_spin_box.setValue(1.0)

        self.color_label.setGeometry(QtCore.QRect(340, 0, 81, 31))
        self.color_label.setFont(QtGui.QFont("Arial", 12))

        self.size_label.setGeometry(QtCore.QRect(200, 0, 81, 31))
        self.size_label.setFont(QtGui.QFont("Arial", 12))

        self.background_label.setGeometry(QtCore.QRect(60, 60, 91, 31))
        self.background_label.setFont(QtGui.QFont("Arial", 12))

        self.nodes_label.setGeometry(QtCore.QRect(60, 120, 91, 31))
        self.nodes_label.setFont(QtGui.QFont("Arial", 12))

        self.edges_label.setGeometry(QtCore.QRect(60, 180, 91, 31))
        self.edges_label.setFont(QtGui.QFont("Arial", 12))

        self.bounding_box_label.setGeometry(QtCore.QRect(220, 260, 101, 41))
        self.bounding_box_label.setFont(QtGui.QFont("Arial", 11))

        self.bounding_box_west.setGeometry(QtCore.QRect(110, 270, 90, 30))
        self.bounding_box_west.setFont(QtGui.QFont("Arial", 10))

        self.bounding_box_north.setGeometry(QtCore.QRect(220, 230, 90, 30))
        self.bounding_box_north.setFont(QtGui.QFont("Arial", 10))

        self.bounding_box_east.setGeometry(QtCore.QRect(330, 270, 90, 30))
        self.bounding_box_east.setFont(QtGui.QFont("Arial", 10))

        self.bounding_box_south.setGeometry(QtCore.QRect(220, 300, 90, 30))
        self.bounding_box_south.setFont(QtGui.QFont("Arial", 10))

        self.horizontalLayout.addWidget(self.graph_controls_frame)

    def setup_buttons_frame(self):
        self.buttons_frame.setMaximumSize(QtCore.QSize(16777215, 100))
        self.buttons_frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.buttons_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)

        self.visualize_button.setGeometry(QtCore.QRect(110, 10, 241, 51))
        self.visualize_button.setFont(QtGui.QFont("Arial", 16))

        self.horizontalLayout_2.addWidget(self.visualize_button_frame)

        self.saved_file_name.setGeometry(QtCore.QRect(10, 30, 191, 30))
        self.saved_file_name.setMaximumSize(QtCore.QSize(200, 30))

        self.save_button.setGeometry(QtCore.QRect(310, 20, 131, 51))
        self.save_button.setFont(QtGui.QFont("Arial", 16))

        self.format_label.setGeometry(QtCore.QRect(210, 20, 91, 41))
        self.format_label.setFont(QtGui.QFont("Arial", 12))

        self.horizontalLayout_2.addWidget(self.save_button_frame)
        self.verticalLayout.addWidget(self.buttons_frame)

    def setup_canvas_frame(self):
        #TODO make it clickable for bounding box selection
        self.canvas_frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.canvas_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.canvas_frame.setFixedHeight(374)
        self.canvas_frame.setFixedWidth(1082)
        self.canvas_frame.setLayout(self.canvas_layout)
        self.verticalLayout.addWidget(self.canvas_frame)

    def run_visualization(self):
        location = self.locations_combo_box.currentText()
        network_type = self.network_combo_box.currentText()
        custom_filter = CUSTOM_FILTER_MAPPING[self.custom_filter_combo_box.currentText()]
        simplify = self.simplify_box.isChecked()
        retain_all = self.retain_box.isChecked()
        truncate_by_edge = self.truncate_box.isChecked()

        if (location == "Select a location . . ." and
                self.custom_location_text.toPlainText() == "Or enter a custom location . . ." and
                (self.bounding_box_west.toPlainText() == "" or self.bounding_box_north.toPlainText() == "" or
                 self.bounding_box_east.toPlainText() == "" or self.bounding_box_south.toPlainText() == "")):
            QtWidgets.QMessageBox.critical(None, "Error", "Please provide a valid location.",
                                           QtWidgets.QMessageBox.StandardButton.Ok)
            return

        if network_type == "Select a network type . . .":
            QtWidgets.QMessageBox.critical(None, "Error", "Please select a network type.",
                                           QtWidgets.QMessageBox.StandardButton.Ok)
            return

        bounding_box = None
        if (self.bounding_box_west.toPlainText() and self.bounding_box_north.toPlainText() and
                self.bounding_box_east.toPlainText() and self.bounding_box_south.toPlainText()):
            bounding_box = (float(self.bounding_box_north.toPlainText()), float(self.bounding_box_south.toPlainText()),
                            float(self.bounding_box_east.toPlainText()), float(self.bounding_box_west.toPlainText()))

        self.generate_graph(bounding_box, custom_filter, location, network_type, retain_all, simplify, truncate_by_edge)

        ax, fig = self.plot_graph()

        self.draw_graph(fig, ax)

        return

    def generate_graph(self, bounding_box, custom_filter, location, network_type, retain_all, simplify,
                       truncate_by_edge):
        if bounding_box:
            self.G = osmnx.graph.graph_from_bbox(bbox=bounding_box, network_type=network_type, simplify=simplify,
                                                 retain_all=retain_all, truncate_by_edge=truncate_by_edge,
                                                 custom_filter=custom_filter)
        elif self.custom_location_text.toPlainText() != "Or enter a custom location . . .":
            try:
                self.G = osmnx.graph.graph_from_place(self.custom_location_text.toPlainText(),
                                                      network_type=network_type,
                                                      simplify=simplify, retain_all=retain_all,
                                                      truncate_by_edge=truncate_by_edge,
                                                      custom_filter=custom_filter)
            except Exception as e:
                QtWidgets.QMessageBox.critical(None, "Error",
                                               f"Error generating graph for custom location: {e}",
                                               QtWidgets.QMessageBox.StandardButton.Ok)
                return
        else:
            self.G = osmnx.graph.graph_from_place(location, network_type=network_type, simplify=simplify,
                                                  retain_all=retain_all, truncate_by_edge=truncate_by_edge,
                                                  custom_filter=custom_filter)

    def plot_graph(self):
        (fig, ax) = osmnx.plot_graph(self.G, node_size=int(self.node_size_spin_box.value()),
                                     node_color=self.node_color_combo_box.currentText(),
                                     edge_color=self.edge_color_combo_box.currentText(),
                                     bgcolor=self.background_color_combo_box.currentText(),
                                     edge_linewidth=self.edge_linewidht_spin_box.value(),
                                     show=False)
        return ax, fig

    def draw_graph(self, fig, ax):
        # TODO: fix figure size inside canvas
        # fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        # fig.set_size_inches(self.canvas_frame.width() / fig.dpi, self.canvas_frame.height() / fig.dpi)
        fig.tight_layout()
        ax.set_aspect('equal')
        if self.canvas is not None:
            self.canvas_layout.removeWidget(self.canvas)
            self.canvas.close()
            self.canvas = None
            self.toolbar.close()
            self.toolbar = None
        self.canvas = FigureCanvas(fig)
        self.toolbar = NavigationToolbar(self.canvas, self.canvas_frame)
        self.canvas_layout.addWidget(self.toolbar)
        self.canvas_layout.addWidget(self.canvas)

    def save_graph(self):
        if not os.path.exists("graphs"):
            os.mkdir("graphs")

        filename = self.saved_file_name.toPlainText()
        if filename == "":
            filename = "graph"

        #create directory inside graphs named after the filename
        directory = f"{filename}_graph"
        if not os.path.exists(f"graphs/{directory}"):
            os.mkdir(f"graphs/{directory}")


        if self.G is not None:
            # TODO: notify user that the graph is succesfully saved
            osmnx.save_graphml(self.G, f"graphs/{directory}/{filename}.graphml")

            gdf_nodes, gdf_edges = osmnx.graph_to_gdfs(self.G)
            bounds = gdf_nodes.total_bounds  # [west, south, east, north]

            with open(f"graphs/{directory}/{filename}_style.yaml", "w") as f:
                f.write(f"node_size: {self.node_size_spin_box.value()}\n")
                f.write(f"node_color: {self.node_color_combo_box.currentText()}\n")
                f.write(f"edge_linewidth: {self.edge_linewidht_spin_box.value()}\n")
                f.write(f"edge_color: {self.edge_color_combo_box.currentText()}\n")
                f.write(f"bgcolor: {self.background_color_combo_box.currentText()}\n")
                f.write(f"bounding_box_west: {bounds[0]}\n")
                f.write(f"bounding_box_south: {bounds[1]}\n")
                f.write(f"bounding_box_east: {bounds[2]}\n")
                f.write(f"bounding_box_north: {bounds[3]}\n")
                f.write(f"custom_filter: '{CUSTOM_FILTER_MAPPING[self.custom_filter_combo_box.currentText()]}'\n")


        else:
            QtWidgets.QMessageBox.critical(None, "Error", "No graph to save",
                                           QtWidgets.QMessageBox.StandardButton.Ok)


if __name__ == "__main__":
    myappid = 'mycompany.myproduct.subproduct.version'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    osmnx.settings.use_cache = False
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
