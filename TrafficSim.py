import os
import sys
from io import StringIO

import osmnx
import yaml
from PyQt6.QtCore import QMetaObject, QRect, QSize, Qt
from PyQt6.QtGui import QFont, QPixmap, QMovie, QIcon
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox, QFormLayout, QFrame, QGridLayout,
                             QLabel, QLayout, QMainWindow, QPlainTextEdit, QPushButton, QTabWidget, QVBoxLayout,
                             QWidget, QFileDialog, QMessageBox, QDialog, QTextEdit)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas, \
    NavigationToolbar2QT as NavigationToolbar
from uxsim import World
from uxsim.OSMImporter import OSMImporter
import ctypes


#TODO refactor imports, check packages
#TODO add feedback to user for example when something is generating or calculating in the backgrounds
#TODO add error handling where there is none
#TODO remove all the comments that are not needed, commented out codes, etc.
#TODO make GUI scalable

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        #self.setObjectName("MainWindow")
        self.setWindowTitle("TrafficSim")
        self.resize(1100, 900)
        self.setFont(QFont("Arial", 10))
        self.setWindowIcon(QIcon("./trsim.png"))
        self.setIconSize(QSize(32, 32))
        self.setTabShape(QTabWidget.TabShape.Rounded)


        self.central_widget=QWidget(self)
        self.vertical_layout=QVBoxLayout(self.central_widget)

        self.canvas_frame = QFrame(parent=self.central_widget)
        self.canvas_layout = QVBoxLayout(self.canvas_frame)
        self.fig = None
        self.ax = None
        self.canvas = None
        self.toolbar = None

        self.setup_canvas_frame()

        self.control_tabs = QTabWidget(parent=self.central_widget)

        self.setup_control_tabs()

        self.world_tab = QWidget()
        self.wo_label = QLabel(parent=self.world_tab)
        self.wo_import_graph_button = QPushButton(parent=self.world_tab)
        self.wp_label = QLabel(parent=self.world_tab)
        self.osmn_button = QPushButton(parent=self.world_tab)
        self.osmn_label = QLabel(parent=self.world_tab)
        self.wp_form_layout = QWidget(parent=self.world_tab)
        self.wp_form = QFormLayout(self.wp_form_layout)
        self.wp_node_merge_threshold_sbox = QDoubleSpinBox(parent=self.wp_form_layout)
        self.wp_node_merge_iteration_label = QLabel(parent=self.wp_form_layout)
        self.wp_node_merge_iteration_sbox = QDoubleSpinBox(parent=self.wp_form_layout)
        self.wp_default_jam_density_label = QLabel(parent=self.wp_form_layout)
        self.wp_default_jam_density_sbox = QDoubleSpinBox(parent=self.wp_form_layout)
        self.wp_enforce_bidirectional_label = QLabel(parent=self.wp_form_layout)
        self.wp_enforce_bidirectional_chbox = QCheckBox(parent=self.wp_form_layout)
        self.wp_node_merge_threshold_label = QLabel(parent=self.wp_form_layout)
        self.osmn_form_layout = QWidget(parent=self.world_tab)
        self.osmn_form = QFormLayout(self.osmn_form_layout)
        self.osmn_figure_size_x_label = QLabel(parent=self.osmn_form_layout)
        self.osmn_figure_size_x_sbox = QDoubleSpinBox(parent=self.osmn_form_layout)
        self.osmn_figure_size_y_label = QLabel(parent=self.osmn_form_layout)
        self.osmn_figure_size_y_sbox = QDoubleSpinBox(parent=self.osmn_form_layout)
        self.osmn_show_link_names_label = QLabel(parent=self.osmn_form_layout)
        self.osmn_show_link_names_chbox = QCheckBox(parent=self.osmn_form_layout)
        self.line_4 = QFrame(parent=self.world_tab)
        self.line_6 = QFrame(parent=self.world_tab)
        self.wo_form_layout = QWidget(parent=self.world_tab)
        self.wo_form = QFormLayout(self.wo_form_layout)
        self.wo_world_name_text = QPlainTextEdit(parent=self.wo_form_layout)
        self.wo_t_max_label = QLabel(parent=self.wo_form_layout)
        self.wo_t_max_automatic_chbox = QCheckBox(parent=self.wo_form_layout)
        self.wo_t_max_sbox = QDoubleSpinBox(parent=self.wo_form_layout)
        self.wo_world_name_label = QLabel(parent=self.wo_form_layout)
        self.wo_delta_n_sbox = QDoubleSpinBox(parent=self.wo_form_layout)
        self.wo_delta_n_label = QLabel(parent=self.wo_form_layout)

        self.setup_world_tab()

        self.simulation_tab = QWidget()
        self.r_add_demand_button = QPushButton(parent=self.simulation_tab)
        self.r_remove_demand_button = QPushButton(parent=self.simulation_tab)
        self.r_label = QLabel(parent=self.simulation_tab)

        self.r_route_tabs = QTabWidget(parent=self.simulation_tab)
        self.r_1 = QWidget()
        self.r_grid_layout_1 = QWidget(parent=self.r_1)
        self.r_grid_1 = QGridLayout(self.r_grid_layout_1)
        self.r_t_end_label_1 = QLabel(parent=self.r_grid_layout_1)
        self.r_y_origin_sbox_1 = QDoubleSpinBox(parent=self.r_grid_layout_1)
        self.r_radius_destination_sbox_1 = QDoubleSpinBox(parent=self.r_grid_layout_1)
        self.r_flow_label_1 = QLabel(parent=self.r_grid_layout_1)
        self.r_x_origin_sbox_1 = QDoubleSpinBox(parent=self.r_grid_layout_1)
        self.r_x_label_1 = QLabel(parent=self.r_grid_layout_1)
        self.r_destination_label_1 = QLabel(parent=self.r_grid_layout_1)
        self.r_x_destination_sbox_1 = QDoubleSpinBox(parent=self.r_grid_layout_1)
        self.r_radius_origin_sbox_1 = QDoubleSpinBox(parent=self.r_grid_layout_1)
        self.r_radius_label_1 = QLabel(parent=self.r_grid_layout_1)
        self.r_y_destination_sbox_1 = QDoubleSpinBox(parent=self.r_grid_layout_1)
        self.r_origin_label_1 = QLabel(parent=self.r_grid_layout_1)
        self.r_t_start_label_1 = QLabel(parent=self.r_grid_layout_1)
        self.r_y_label_1 = QLabel(parent=self.r_grid_layout_1)
        self.r_t_start_sbox_1 = QDoubleSpinBox(parent=self.r_grid_layout_1)
        self.r_t_end_sbox_1 = QDoubleSpinBox(parent=self.r_grid_layout_1)
        self.r_flow_sbox_1 = QDoubleSpinBox(parent=self.r_grid_layout_1)
        self.r_run_simulation_button = QPushButton(parent=self.simulation_tab)

        self.r_index = 1
        self.spin_box_references = {}

        self.setup_simulation_tab()

        self.statistics_tab_1 = QWidget()
        self.wn_label = QLabel(parent=self.statistics_tab_1)
        self.wn_button = QPushButton(parent=self.statistics_tab_1)
        self.mfd_label = QLabel(parent=self.statistics_tab_1)
        self.cc_label = QLabel(parent=self.statistics_tab_1)
        self.mfd_button = QPushButton(parent=self.statistics_tab_1)
        self.cc_button = QPushButton(parent=self.statistics_tab_1)
        self.line_2 = QFrame(parent=self.statistics_tab_1)
        self.line_3 = QFrame(parent=self.statistics_tab_1)
        self.wn_form_layout = QWidget(parent=self.statistics_tab_1)
        self.wn_form = QFormLayout(self.wn_form_layout)
        self.wn_node_size_label = QLabel(parent=self.wn_form_layout)
        self.wn_node_size_sbox = QDoubleSpinBox(parent=self.wn_form_layout)
        self.wn_network_font_size_label = QLabel(parent=self.wn_form_layout)
        self.wn_network_font_size_sbox = QDoubleSpinBox(parent=self.wn_form_layout)
        self.wn_left_handed_label = QLabel(parent=self.wn_form_layout)
        self.wn_left_handed_chbox = QCheckBox(parent=self.wn_form_layout)
        self.wn_figure_size_x_label = QLabel(parent=self.wn_form_layout)
        self.wn_figure_size_x_sbox = QDoubleSpinBox(parent=self.wn_form_layout)
        self.wn_figure_size_y_label = QLabel(parent=self.wn_form_layout)
        self.wn_figure_size_y_sbox = QDoubleSpinBox(parent=self.wn_form_layout)
        self.wn_width_label = QLabel(parent=self.wn_form_layout)
        self.wn_width_sbox = QDoubleSpinBox(parent=self.wn_form_layout)
        self.mfd_form_layout = QWidget(parent=self.statistics_tab_1)
        self.mfd_form = QFormLayout(self.mfd_form_layout)
        self.mfd_kappa_label = QLabel(parent=self.mfd_form_layout)
        self.mfd_kappa_sbox = QDoubleSpinBox(parent=self.mfd_form_layout)
        self.mfd_qmax_label = QLabel(parent=self.mfd_form_layout)
        self.mfd_qmax_sbox = QDoubleSpinBox(parent=self.mfd_form_layout)
        self.mfd_figure_size_x_label = QLabel(parent=self.mfd_form_layout)
        self.mfd_figure_size_x_sbox = QDoubleSpinBox(parent=self.mfd_form_layout)
        self.mfd_figure_size_y_label = QLabel(parent=self.mfd_form_layout)
        self.mfd_figure_size_y_sbox = QDoubleSpinBox(parent=self.mfd_form_layout)
        self.mfd_link_label = QLabel(parent=self.mfd_form_layout)
        self.mfd_link_cobox = QComboBox(parent=self.mfd_form_layout)
        self.cc_form_layout = QWidget(parent=self.statistics_tab_1)
        self.cc_form = QFormLayout(self.cc_form_layout)
        self.cc_figure_size_x_label = QLabel(parent=self.cc_form_layout)
        self.cc_figure_size_x_sbox = QDoubleSpinBox(parent=self.cc_form_layout)
        self.cc_figure_size_y_label = QLabel(parent=self.cc_form_layout)
        self.cc_figure_size_y_sbox = QDoubleSpinBox(parent=self.cc_form_layout)
        self.cc_link_label = QLabel(parent=self.cc_form_layout)
        self.cc_link_cobox = QComboBox(parent=self.cc_form_layout)

        self.setup_statistics_1_tab()

        self.statistics_tab_2 = QWidget()
        self.tsdd_label = QLabel(parent=self.statistics_tab_2)
        self.tsdt_label = QLabel(parent=self.statistics_tab_2)
        self.tsdd_button = QPushButton(parent=self.statistics_tab_2)
        self.tsdt_button = QPushButton(parent=self.statistics_tab_2)
        self.line_5 = QFrame(parent=self.statistics_tab_2)
        self.tsdd_form_layout = QWidget(parent=self.statistics_tab_2)
        self.tsdd_form = QFormLayout(self.tsdd_form_layout)
        self.tsdd_figure_size_x_label = QLabel(parent=self.tsdd_form_layout)
        self.tsdd_figure_size_x_sbox = QDoubleSpinBox(parent=self.tsdd_form_layout)
        self.tsdd_figure_size_y_label = QLabel(parent=self.tsdd_form_layout)
        self.tsdd_figure_size_y_sbox = QDoubleSpinBox(parent=self.tsdd_form_layout)
        self.tsdd_link_label = QLabel(parent=self.tsdd_form_layout)
        self.tsdd_link_cobox = QComboBox(parent=self.tsdd_form_layout)
        self.tsdt_form_layout = QWidget(parent=self.statistics_tab_2)
        self.tsdt_form = QFormLayout(self.tsdt_form_layout)
        self.tsdt_figure_size_x_label = QLabel(parent=self.tsdt_form_layout)
        self.tsdt_figure_size_x_sbox = QDoubleSpinBox(parent=self.tsdt_form_layout)
        self.tsdt_figure_size_y_label = QLabel(parent=self.tsdt_form_layout)
        self.tsdt_figure_size_y_sbox = QDoubleSpinBox(parent=self.tsdt_form_layout)
        self.tsdt_link_label = QLabel(parent=self.tsdt_form_layout)
        self.tsdt_link_cobox = QComboBox(parent=self.tsdt_form_layout)

        self.setup_statistics_2_tab()

        self.animations_tab = QWidget()
        self.sa_label = QLabel(parent=self.animations_tab)
        self.sa_button = QPushButton(parent=self.animations_tab)
        self.fa_button = QPushButton(parent=self.animations_tab)
        self.fa_label = QLabel(parent=self.animations_tab)
        self.line = QFrame(parent=self.animations_tab)
        self.sa_form_layout = QWidget(parent=self.animations_tab)
        self.sa_form = QFormLayout(self.sa_form_layout)
        self.sa_speed_inverse_sbox = QDoubleSpinBox(parent=self.sa_form_layout)
        self.sa_detailed_label = QLabel(parent=self.sa_form_layout)
        self.sa_detailed_chbox = QCheckBox(parent=self.sa_form_layout)
        self.sa_left_handed_label = QLabel(parent=self.sa_form_layout)
        self.sa_left_handed_chbox = QCheckBox(parent=self.sa_form_layout)
        self.sa_figure_size_x_label = QLabel(parent=self.sa_form_layout)
        self.sa_figure_size_x_sbox = QDoubleSpinBox(parent=self.sa_form_layout)
        self.sa_speed_inverse_label = QLabel(parent=self.sa_form_layout)
        self.sa_figure_size_y_label = QLabel(parent=self.sa_form_layout)
        self.sa_figure_size_y_sbox = QDoubleSpinBox(parent=self.sa_form_layout)
        self.sa_node_size_label = QLabel(parent=self.sa_form_layout)
        self.sa_node_size_sbox = QDoubleSpinBox(parent=self.sa_form_layout)
        self.sa_network_font_size_label = QLabel(parent=self.sa_form_layout)
        self.sa_network_font_size_sbox = QDoubleSpinBox(parent=self.sa_form_layout)
        self.sa_timestep_skip_label = QLabel(parent=self.sa_form_layout)
        self.sa_timestep_skip_sbox = QDoubleSpinBox(parent=self.sa_form_layout)
        self.fa_form_layout = QWidget(parent=self.animations_tab)
        self.fa_form = QFormLayout(self.fa_form_layout)
        self.fa_speed_inverse_label = QLabel(parent=self.fa_form_layout)
        self.fa_speed_inverse_sbox = QDoubleSpinBox(parent=self.fa_form_layout)
        self.fa_figure_size_label = QLabel(parent=self.fa_form_layout)
        self.fa_figure_size_sbox = QDoubleSpinBox(parent=self.fa_form_layout)
        self.fa_sample_ratio_label = QLabel(parent=self.fa_form_layout)
        self.fa_sample_ratio_sbox = QDoubleSpinBox(parent=self.fa_form_layout)
        self.fa_interval_label = QLabel(parent=self.fa_form_layout)
        self.fa_interval_sbox = QDoubleSpinBox(parent=self.fa_form_layout)
        self.fa_network_font_size_label = QLabel(parent=self.fa_form_layout)
        self.fa_network_font_size_sbox = QDoubleSpinBox(parent=self.fa_form_layout)
        self.fa_trace_length_label = QLabel(parent=self.fa_form_layout)
        self.fa_trace_length_sbox = QDoubleSpinBox(parent=self.fa_form_layout)
        self.fa_speed_coef_label = QLabel(parent=self.fa_form_layout)
        self.fa_speed_coef_sbox = QDoubleSpinBox(parent=self.fa_form_layout)
        self.fa_antialiasing_label = QLabel(parent=self.fa_form_layout)
        self.fa_antialiasing_chbox = QCheckBox(parent=self.fa_form_layout)

        self.setup_animations_tab()

        self.vertical_layout.addWidget(self.control_tabs)
        self.setCentralWidget(self.central_widget)

        self.control_tabs.setCurrentIndex(0)
        self.r_route_tabs.setCurrentIndex(0)


        #TODO if done remove warning suppressions
        # noinspection PyUnresolvedReferences
        self.wo_import_graph_button.clicked.connect(self.import_graph)
        # noinspection PyUnresolvedReferences
        self.osmn_button.clicked.connect(self.show_osm_network)
        # noinspection PyUnresolvedReferences
        self.r_add_demand_button.clicked.connect(self.add_demand)
        # noinspection PyUnresolvedReferences
        self.r_remove_demand_button.clicked.connect(self.remove_demand)
        # noinspection PyUnresolvedReferences
        self.r_run_simulation_button.clicked.connect(self.run_simulation)
        # noinspection PyUnresolvedReferences
        self.wn_button.clicked.connect(self.show_world_network)
        # noinspection PyUnresolvedReferences
        self.mfd_button.clicked.connect(self.show_mfd)
        # noinspection PyUnresolvedReferences
        self.cc_button.clicked.connect(self.show_cc)
        # noinspection PyUnresolvedReferences
        self.tsdd_button.clicked.connect(self.show_tsdd)
        # noinspection PyUnresolvedReferences
        self.tsdt_button.clicked.connect(self.show_tsdt)
        # noinspection PyUnresolvedReferences
        self.sa_button.clicked.connect(self.show_sa)
        # noinspection PyUnresolvedReferences
        self.fa_button.clicked.connect(self.show_fa)

        QMetaObject.connectSlotsByName(self)

        self.world = None
        self.nodes = None
        self.links = None

        self.graphml_file_path = None


    def setup_canvas_frame(self):
        # TODO write docs
        self.canvas_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.canvas_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.canvas_frame.setLayout(self.canvas_layout)
        self.canvas_frame.setFixedHeight(376)
        self.canvas_frame.setFixedWidth(1082)
        self.vertical_layout.addWidget(self.canvas_frame)

    def setup_control_tabs(self):
        # TODO write docs
        self.control_tabs.setEnabled(True)
        self.control_tabs.setMaximumSize(QSize(1100, 500))
        self.control_tabs.setFont(QFont("Arial", 12))
        self.control_tabs.setTabPosition(QTabWidget.TabPosition.South)
        self.control_tabs.setDocumentMode(False)
        self.control_tabs.setTabsClosable(False)
        self.control_tabs.setTabBarAutoHide(True)
        #self.control_tabs.setObjectName("control_tabs")

    def setup_world_tab(self):
        # TODO write docs

        #self.world_tab.setObjectName("world_tab")
        self.wo_label.setGeometry(QRect(10, -10, 111, 41))
        self.wo_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.wo_label.setText("World Options")
        #self.wo_label.setObjectName("wo_label")

        self.wo_import_graph_button.setGeometry(QRect(70, 30, 210, 40))
        self.wo_import_graph_button.setFont(QFont("Arial", 11, QFont.Weight.Bold, italic=True))
        self.wo_import_graph_button.setAutoDefault(False)
        self.wo_import_graph_button.setDefault(False)
        self.wo_import_graph_button.setFlat(False)
        self.wo_import_graph_button.setText("Import Graph")
        #self.wo_import_graph_button.setObjectName("wo_import_graph_button")

        self.wp_label.setGeometry(QRect(380, -10, 191, 51))
        self.wp_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.wp_label.setText("World Postprocessing")
        #self.wp_label.setObjectName("wp_label")

        self.osmn_button.setGeometry(QRect(780, 420, 210, 40))
        self.osmn_button.setFont(QFont("Arial", 11, italic=True))
        self.osmn_button.setText("Show OSM Network")
        #self.osmn_button.setObjectName("osmn_button")

        self.osmn_label.setGeometry(QRect(730, -10, 111, 41))
        self.osmn_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.osmn_label.setText("OSM Network")
        #self.osmn_label.setObjectName("osmn_label")

        self.wp_form_layout.setGeometry(QRect(400, 60, 303, 321))
        #self.wp_form_layout.setObjectName("wp_form_layout")

        self.wp_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.wp_form.setContentsMargins(0, 0, 0, 0)
        self.wp_form.setHorizontalSpacing(50)
        self.wp_form.setVerticalSpacing(20)
        #self.wp_form.setObjectName("wp_form")

        self.wp_node_merge_threshold_sbox.setFont(QFont("Arial", 13))
        self.wp_node_merge_threshold_sbox.setDecimals(4)
        self.wp_node_merge_threshold_sbox.setSingleStep(0.0005)
        self.wp_node_merge_threshold_sbox.setProperty("value", 0.0011)
        #self.wp_node_merge_threshold_sbox.setObjectName("wp_node_merge_threshold_sbox")

        self.wp_form.setWidget(0, QFormLayout.ItemRole.FieldRole, self.wp_node_merge_threshold_sbox)

        self.wp_node_merge_iteration_label.setFont(QFont("Arial", 12))
        self.wp_node_merge_iteration_label.setText("Node merge iteration")
        #self.wp_node_merge_iteration_label.setObjectName("wp_node_merge_iteration_label")

        self.wp_form.setWidget(1, QFormLayout.ItemRole.LabelRole, self.wp_node_merge_iteration_label)

        self.wp_node_merge_iteration_sbox.setFont(QFont("Arial", 13))
        self.wp_node_merge_iteration_sbox.setDecimals(0)
        self.wp_node_merge_iteration_sbox.setProperty("value", 1.0)
        #self.wp_node_merge_iteration_sbox.setObjectName("wp_node_merge_iteration_sbox")

        self.wp_form.setWidget(1, QFormLayout.ItemRole.FieldRole, self.wp_node_merge_iteration_sbox)

        self.wp_default_jam_density_label.setFont(QFont("Arial", 12))
        self.wp_default_jam_density_label.setText("Default jam density")
        #self.wp_default_jam_density_label.setObjectName("wp_default_jam_density_label")

        self.wp_form.setWidget(2, QFormLayout.ItemRole.LabelRole, self.wp_default_jam_density_label)

        self.wp_default_jam_density_sbox.setFont(QFont("Arial", 13))
        self.wp_default_jam_density_sbox.setDecimals(2)
        self.wp_default_jam_density_sbox.setMinimum(0.01)
        self.wp_default_jam_density_sbox.setSingleStep(0.05)
        self.wp_default_jam_density_sbox.setProperty("value", 0.2)

        #self.wp_default_jam_density_sbox.setObjectName("wp_default_jam_density_sbox")

        self.wp_form.setWidget(2, QFormLayout.ItemRole.FieldRole, self.wp_default_jam_density_sbox)

        self.wp_enforce_bidirectional_label.setFont(QFont("Arial", 12))
        self.wp_enforce_bidirectional_label.setText("Enforce bidirectional")
        #self.wp_enforce_bidirectional_label.setObjectName("wp_enforce_bidirectional_label")

        self.wp_form.setWidget(3, QFormLayout.ItemRole.LabelRole, self.wp_enforce_bidirectional_label)

        #self.wp_enforce_bidirectional_chbox.setFont(QFont("Arial", 9))
        #self.wp_enforce_bidirectional_chbox.setText("")
        self.wp_enforce_bidirectional_chbox.setIconSize(QSize(16, 16))
        self.wp_enforce_bidirectional_chbox.setChecked(False)
        #self.wp_enforce_bidirectional_chbox.setObjectName("wp_enforce_bidirectional_chbox")

        self.wp_form.setWidget(3, QFormLayout.ItemRole.FieldRole, self.wp_enforce_bidirectional_chbox)

        self.wp_node_merge_threshold_label.setFont(QFont("Arial", 12))
        self.wp_node_merge_threshold_label.setText("Node merge threshold")
        #self.wp_node_merge_threshold_label.setObjectName("wp_node_merge_threshold_label")

        self.wp_form.setWidget(0, QFormLayout.ItemRole.LabelRole, self.wp_node_merge_threshold_label)

        self.osmn_form_layout.setGeometry(QRect(750, 50, 301, 301))
        #self.osmn_form_layout.setObjectName("osmn_form_layout")

        self.osmn_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.osmn_form.setContentsMargins(0, 0, 0, 0)
        self.osmn_form.setHorizontalSpacing(50)
        self.osmn_form.setVerticalSpacing(20)
        #self.osmn_form.setObjectName("osmn_form")

        self.osmn_figure_size_x_label.setFont(QFont("Arial", 12))
        self.osmn_figure_size_x_label.setText("Figure size X")
        #self.osmn_figure_size_x_label.setObjectName("osmn_figure_size_x_label")

        self.osmn_form.setWidget(0, QFormLayout.ItemRole.LabelRole, self.osmn_figure_size_x_label)

        self.osmn_figure_size_x_sbox.setFont(QFont("Arial", 13))
        self.osmn_figure_size_x_sbox.setDecimals(0)
        self.osmn_figure_size_x_sbox.setMinimum(1.0)
        self.osmn_figure_size_x_sbox.setProperty("value", 12.0)
        #self.osmn_figure_size_x_sbox.setObjectName("osmn_figure_size_x_sbox")

        self.osmn_form.setWidget(0, QFormLayout.ItemRole.FieldRole, self.osmn_figure_size_x_sbox)

        self.osmn_figure_size_y_label.setFont(QFont("Arial", 12))
        self.osmn_figure_size_y_label.setText("Figure size Y")
        #self.osmn_figure_size_y_label.setObjectName("osmn_figure_size_y_label")

        self.osmn_form.setWidget(1, QFormLayout.ItemRole.LabelRole, self.osmn_figure_size_y_label)

        self.osmn_figure_size_y_sbox.setFont(QFont("Arial", 13))
        self.osmn_figure_size_y_sbox.setDecimals(0)
        self.osmn_figure_size_y_sbox.setProperty("value", 12.0)
        #self.osmn_figure_size_y_sbox.setObjectName("osmn_figure_size_y_sbox")

        self.osmn_form.setWidget(1, QFormLayout.ItemRole.FieldRole, self.osmn_figure_size_y_sbox)

        self.osmn_show_link_names_label.setFont(QFont("Arial", 12))
        self.osmn_show_link_names_label.setText("Show link names")
        #self.osmn_show_link_names_label.setObjectName("osmn_show_link_names_label")

        self.osmn_form.setWidget(2, QFormLayout.ItemRole.LabelRole, self.osmn_show_link_names_label)

        #self.osmn_show_link_names_chbox.setFont(QFont("Arial", 9))
        #self.osmn_show_link_names_chbox.setText("")
        self.osmn_show_link_names_chbox.setIconSize(QSize(16, 16))
        #self.osmn_show_link_names_chbox.setChecked(False)
        #self.osmn_show_link_names_chbox.setObjectName("osmn_show_link_names_chbox")

        self.osmn_form.setWidget(2, QFormLayout.ItemRole.FieldRole, self.osmn_show_link_names_chbox)

        self.line_4.setGeometry(QRect(350, 0, 20, 471))
        self.line_4.setFrameShadow(QFrame.Shadow.Raised)
        self.line_4.setLineWidth(3)
        self.line_4.setMidLineWidth(1)
        self.line_4.setFrameShape(QFrame.Shape.VLine)
        #self.line_4.setObjectName("line_4")

        self.line_6.setGeometry(QRect(700, 0, 20, 471))
        self.line_6.setFrameShadow(QFrame.Shadow.Raised)
        self.line_6.setLineWidth(3)
        self.line_6.setMidLineWidth(1)
        self.line_6.setFrameShape(QFrame.Shape.VLine)
        #self.line_6.setObjectName("line_6")

        self.wo_form_layout.setGeometry(QRect(10, 90, 341, 291))
        #self.wo_form_layout.setObjectName("wo_form_layout")

        self.wo_form.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.wo_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.wo_form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self.wo_form.setFormAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.wo_form.setContentsMargins(0, 0, 0, 0)
        self.wo_form.setHorizontalSpacing(50)
        self.wo_form.setVerticalSpacing(20)
        #self.wo_form.setObjectName("wo_form")

        self.wo_world_name_text.setMaximumSize(QSize(16777215, 40))
        self.wo_world_name_text.setPlainText("")
        self.wo_world_name_text.setPlaceholderText("")
        #self.wo_world_name_text.setObjectName("wo_world_name_text")

        self.wo_form.setWidget(0, QFormLayout.ItemRole.FieldRole, self.wo_world_name_text)

        self.wo_t_max_label.setFont(QFont("Arial", 12))
        self.wo_t_max_label.setText("T max")
        #self.wo_t_max_label.setObjectName("wo_t_max_label")

        self.wo_form.setWidget(1, QFormLayout.ItemRole.LabelRole, self.wo_t_max_label)

        self.wo_t_max_automatic_chbox.setFont(QFont("Arial", 9))
        self.wo_t_max_automatic_chbox.setText("Automatic")
        self.wo_t_max_automatic_chbox.setChecked(True)
        #self.wo_t_max_automatic_chbox.setObjectName("wo_t_max_automatic_chbox")

        self.wo_form.setWidget(1, QFormLayout.ItemRole.FieldRole, self.wo_t_max_automatic_chbox)

        self.wo_t_max_sbox.setEnabled(False)
        self.wo_t_max_sbox.setFont(QFont("Arial", 13))
        self.wo_t_max_sbox.setDecimals(0)
        self.wo_t_max_sbox.setMinimum(1.0)
        self.wo_t_max_sbox.setMaximum(1000000.0)
        self.wo_t_max_sbox.setSingleStep(60.0)
        self.wo_t_max_sbox.setProperty("value", 3600.0)
        #self.wo_t_max_sbox.setObjectName("wo_t_max_sbox")

        self.wo_form.setWidget(2, QFormLayout.ItemRole.FieldRole, self.wo_t_max_sbox)

        self.wo_world_name_label.setFont(QFont("Arial", 12))
        self.wo_world_name_label.setText("World name")
        #self.wo_world_name_label.setObjectName("wo_world_name_label")

        self.wo_form.setWidget(0, QFormLayout.ItemRole.LabelRole, self.wo_world_name_label)

        self.wo_delta_n_sbox.setFont(QFont("Arial", 13))
        self.wo_delta_n_sbox.setDecimals(0)
        self.wo_delta_n_sbox.setMinimum(1.0)
        self.wo_delta_n_sbox.setMaximum(100000.0)
        self.wo_delta_n_sbox.setProperty("value", 5.0)
        #self.wo_delta_n_sbox.setObjectName("wo_delta_n_sbox")

        self.wo_form.setWidget(3, QFormLayout.ItemRole.FieldRole, self.wo_delta_n_sbox)

        self.wo_delta_n_label.setFont(QFont("Arial", 12))
        self.wo_delta_n_label.setText("Delta n")
        #self.wo_delta_n_label.setObjectName("wo_delta_n_label")

        self.wo_form.setWidget(3, QFormLayout.ItemRole.LabelRole, self.wo_delta_n_label)

        self.control_tabs.addTab(self.world_tab, "World")

    def setup_simulation_tab(self):
        # TODO write docs

        #self.simulation_tab.setObjectName("simulation_tab")

        self.r_add_demand_button.setGeometry(QRect(220, 20, 210, 40))
        self.r_add_demand_button.setFont(QFont("Arial", 11, italic=True))
        self.r_add_demand_button.setText("Add Demand")
        #self.r_add_demand_button.setObjectName("r_add_demand_button")

        self.r_remove_demand_button.setGeometry(QRect(630, 20, 210, 40))
        self.r_remove_demand_button.setFont(QFont("Arial", 11, italic=True))
        self.r_remove_demand_button.setText("Remove Demand")
        #self.r_remove_demand_button.setObjectName("r_remove_demand_button")

        self.r_label.setGeometry(QRect(10, -10, 111, 50))
        self.r_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.r_label.setText("Routes")
        #self.r_label.setObjectName("r_label")

        self.r_route_tabs.setGeometry(QRect(20, 90, 771, 371))
        #self.r_route_tab.setObjectName("r_route_tab")

        self.setup_route_tab_i(self.r_index)

        self.r_run_simulation_button.setGeometry(QRect(840, 420, 210, 40))
        self.r_run_simulation_button.setFont(QFont("Arial", 11, italic=True))
        self.r_run_simulation_button.setText("Run Simulation")
        #self.r_run_simulation_button.setObjectName("r_run_simulation_button")

        self.control_tabs.addTab(self.simulation_tab, "Simulation")

    def setup_route_tab_i(self, index):
        """
        Sets up a new route tab with the given index.

        This method creates a new tab and grid layout, adds various widgets to the grid,
        and stores references to the spin boxes in a dictionary.

        Args:
            index (int): The index of the new route tab.
        """
        new_tab = QWidget()
        new_grid = QGridLayout()
        new_grid.setGeometry(QRect(10, 10, 721, 311))
        new_grid.setContentsMargins(0, 0, 0, 0)
        new_grid.setHorizontalSpacing(50)
        new_grid.setVerticalSpacing(20)

        self.spin_box_references[f"r_{index}"] = {}

        #TODO reset values because of testing they are set

        elements = [
            ("r_t_end_label", QLabel("T end"), 6, 2),
            ("r_y_origin_sbox", QDoubleSpinBox(), 2, 2, {"decimals": 5, "minimum": -1000.0, "maximum": 1000.0, "value": 0.00000}),
            ("r_radius_destination_sbox", QDoubleSpinBox(), 3, 3,
            {"decimals": 4, "singleStep": 0.0005, "value": 0.0005}),
            ("r_flow_label", QLabel("Flow"), 6, 3),
            ("r_x_origin_sbox", QDoubleSpinBox(), 2, 1, {"decimals": 5, "minimum": -1000.0, "maximum": 1000.0, "value": 0.00000}),
            ("r_x_label", QLabel("X"), 1, 1),
            ("r_destination_label", QLabel("Destination"), 3, 0),
            ("r_x_destination_sbox", QDoubleSpinBox(), 3, 1, {"decimals": 5, "minimum": -1000.0, "maximum": 1000.0, "value": 0.00000}),
            ("r_radius_origin_sbox", QDoubleSpinBox(), 2, 3, {"decimals": 4, "singleStep": 0.0005, "value": 0.0005}),
            ("r_radius_label", QLabel("Radius"), 1, 3),
            ("r_y_destination_sbox", QDoubleSpinBox(), 3, 2, {"decimals": 5, "minimum": -1000.0, "maximum": 1000.0, "value": 0.00000}),
            ("r_origin_label", QLabel("Origin"), 2, 0),
            ("r_t_start_label", QLabel("T start"), 6, 1),
            ("r_y_label", QLabel("Y"), 1, 2),
            ("r_t_start_sbox", QDoubleSpinBox(), 7, 1, {"decimals": 0, "maximum": 100000.0, "singleStep": 100.0, "value": 200}),
            ("r_t_end_sbox", QDoubleSpinBox(), 7, 2, {"decimals": 0, "maximum": 100000.0, "singleStep": 100.0, "value": 2400}),
            ("r_flow_sbox", QDoubleSpinBox(), 7, 3, {"decimals": 2, "minimum": 0.01, "maximum": 1000.0, "value": 1.0}),
        ]


        for name, widget, row, col, *optional_settings in elements:
            widget.setObjectName(f"{name}_{index}")

            if optional_settings:
                settings = optional_settings[0]
                for attr, value in settings.items():
                    getattr(widget, f"set{attr[0].upper()}{attr[1:]}")(value)

            if isinstance(widget, QLabel):
                widget.setFont(QFont("Arial", 12))
            elif isinstance(widget, QDoubleSpinBox):
                widget.setFont(QFont("Arial", 13))

            new_grid.addWidget(widget, row, col)

            if isinstance(widget, QDoubleSpinBox):
                self.spin_box_references[f"r_{index}"][widget.objectName()] = widget

        new_tab.setLayout(new_grid)

        self.r_route_tabs.addTab(new_tab, f"Route {index}")

    def setup_statistics_1_tab(self):
        # TODO write docs

        self.statistics_tab_1.setEnabled(False)
        #self.statistics_tab_1.setObjectName("statistics_tab_1")

        self.wn_label.setGeometry(QRect(10, -10, 130, 50))
        self.wn_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.wn_label.setText("World Network")
        #self.wn_label.setObjectName("wn_label")

        self.wn_button.setGeometry(QRect(80, 420, 210, 40))
        self.wn_button.setFont(QFont("Arial", 11, italic=True))
        self.wn_button.setText("Show World Network")
        #self.wn_button.setObjectName("wn_button")

        self.mfd_label.setGeometry(QRect(380, -10, 270, 50))
        self.mfd_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.mfd_label.setText("Macroscopic Fundamental Diagram")
        #self.mfd_label.setObjectName("mfd_label")

        self.cc_label.setGeometry(QRect(730, -10, 150, 50))
        self.cc_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.cc_label.setText("Cumulative Curve")
        #self.cc_label.setObjectName("cc_label")

        self.mfd_button.setGeometry(QRect(430, 420, 210, 40))
        self.mfd_button.setFont(QFont("Arial", 11, italic=True))
        self.mfd_button.setText("Show MFD")
        #self.mfd_button.setObjectName("mfd_button")

        self.cc_button.setGeometry(QRect(780, 420, 210, 40))
        self.cc_button.setFont(QFont("Arial", 11, italic=True))
        self.cc_button.setText("Show Cumulative Curve")
        #self.cc_button.setObjectName("cc_button")

        self.line_2.setGeometry(QRect(700, 0, 20, 471))
        self.line_2.setFrameShadow(QFrame.Shadow.Raised)
        self.line_2.setLineWidth(3)
        self.line_2.setMidLineWidth(1)
        self.line_2.setFrameShape(QFrame.Shape.VLine)
        #self.line_2.setObjectName("line_2")

        self.line_3.setGeometry(QRect(350, 0, 20, 471))
        self.line_3.setFrameShadow(QFrame.Shadow.Raised)
        self.line_3.setLineWidth(3)
        self.line_3.setMidLineWidth(1)
        self.line_3.setFrameShape(QFrame.Shape.VLine)
        #self.line_3.setObjectName("line_3")

        self.wn_form_layout.setGeometry(QRect(30, 60, 311, 273))
        #self.wn_form_layout.setObjectName("layoutWidget")

        self.wn_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.wn_form.setContentsMargins(0, 0, 0, 0)
        self.wn_form.setHorizontalSpacing(50)
        self.wn_form.setVerticalSpacing(20)
        #self.wn_form.setObjectName("wn_form")

        self.wn_node_size_label.setFont(QFont("Arial", 12))
        self.wn_node_size_label.setText("Node size")
        #self.wn_node_size_label.setObjectName("wn_node_size_label")

        self.wn_form.setWidget(0, QFormLayout.ItemRole.LabelRole, self.wn_node_size_label)

        self.wn_node_size_sbox.setFont(QFont("Arial", 13))
        self.wn_node_size_sbox.setDecimals(0)
        self.wn_node_size_sbox.setMinimum(0.0)
        self.wn_node_size_sbox.setProperty("value", 6.0)
        #self.wn_node_size_sbox.setObjectName("wn_node_size_sbox")

        self.wn_form.setWidget(0, QFormLayout.ItemRole.FieldRole, self.wn_node_size_sbox)

        self.wn_network_font_size_label.setFont(QFont("Arial", 12))
        self.wn_network_font_size_label.setText("Network font size")
        #self.wn_network_font_size_label.setObjectName("wn_network_font_size_label")

        self.wn_form.setWidget(1, QFormLayout.ItemRole.LabelRole, self.wn_network_font_size_label)

        self.wn_network_font_size_sbox.setFont(QFont("Arial", 13))
        self.wn_network_font_size_sbox.setDecimals(0)
        self.wn_network_font_size_sbox.setMinimum(0.0)
        self.wn_network_font_size_sbox.setMaximum(100.0)
        self.wn_network_font_size_sbox.setProperty("value", 10.0)
        #self.wn_network_font_size_sbox.setObjectName("wn_network_font_size_sbox")

        self.wn_form.setWidget(1, QFormLayout.ItemRole.FieldRole, self.wn_network_font_size_sbox)

        self.wn_left_handed_label.setFont(QFont("Arial", 12))
        self.wn_left_handed_label.setText("Left handed")
        #self.wn_left_handed_label.setObjectName("wn_left_handed_label")

        self.wn_form.setWidget(2, QFormLayout.ItemRole.LabelRole, self.wn_left_handed_label)

        #self.wn_left_handed_chbox.setText("")
        #self.wn_left_handed_chbox.setChecked(False)
        #self.wn_left_handed_chbox.setObjectName("wn_left_handed_chbox")

        self.wn_form.setWidget(2, QFormLayout.ItemRole.FieldRole, self.wn_left_handed_chbox)

        self.wn_figure_size_x_label.setFont(QFont("Arial", 12))
        self.wn_figure_size_x_label.setText("Figure size X")
        #self.wn_figure_size_x_label.setObjectName("wn_figure_size_x_label")

        self.wn_form.setWidget(3, QFormLayout.ItemRole.LabelRole, self.wn_figure_size_x_label)

        self.wn_figure_size_x_sbox.setFont(QFont("Arial", 13))
        self.wn_figure_size_x_sbox.setDecimals(0)
        self.wn_figure_size_x_sbox.setMinimum(1.0)
        self.wn_figure_size_x_sbox.setProperty("value", 6.0)
        #self.wn_figure_size_x_sbox.setObjectName("wn_figure_size_x_sbox")

        self.wn_form.setWidget(3, QFormLayout.ItemRole.FieldRole, self.wn_figure_size_x_sbox)

        self.wn_figure_size_y_label.setFont(QFont("Arial", 12))
        self.wn_figure_size_y_label.setText("Figure size Y")
        #self.wn_figure_size_y_label.setObjectName("wn_figure_size_y_label")

        self.wn_form.setWidget(4, QFormLayout.ItemRole.LabelRole, self.wn_figure_size_y_label)

        self.wn_figure_size_y_sbox.setFont(QFont("Arial", 13))
        self.wn_figure_size_y_sbox.setDecimals(0)
        self.wn_figure_size_y_sbox.setMinimum(1.0)
        self.wn_figure_size_y_sbox.setProperty("value", 6.0)
        #self.wn_figure_size_y_sbox.setObjectName("wn_figure_size_y_sbox")

        self.wn_form.setWidget(4, QFormLayout.ItemRole.FieldRole, self.wn_figure_size_y_sbox)

        self.wn_width_label.setFont(QFont("Arial", 12))
        self.wn_width_label.setText("Width")
        #self.wn_width_label.setObjectName("wn_width_label")

        self.wn_form.setWidget(5, QFormLayout.ItemRole.LabelRole, self.wn_width_label)

        self.wn_width_sbox.setFont(QFont("Arial", 13))
        self.wn_width_sbox.setDecimals(0)
        self.wn_width_sbox.setMinimum(0.0)
        self.wn_width_sbox.setProperty("value", 1.0)
        #self.wn_width_sbox.setObjectName("wn_width_sbox")

        self.wn_form.setWidget(5, QFormLayout.ItemRole.FieldRole, self.wn_width_sbox)

        self.mfd_form_layout.setGeometry(QRect(400, 60, 301, 281))
        #self.mfd_form_layout.setObjectName("mfd_form_layout")

        self.mfd_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.mfd_form.setContentsMargins(0, 0, 0, 0)
        self.mfd_form.setHorizontalSpacing(50)
        self.mfd_form.setVerticalSpacing(20)
        #self.mfd_form.setObjectName("mfd_form")

        self.mfd_kappa_label.setFont(QFont("Arial", 12))
        self.mfd_kappa_label.setText("Kappa")
        #self.mfd_kappa_label.setObjectName("mfd_kappa_label")

        self.mfd_form.setWidget(0, QFormLayout.ItemRole.LabelRole, self.mfd_kappa_label)

        self.mfd_kappa_sbox.setFont(QFont("Arial", 13))
        self.mfd_kappa_sbox.setDecimals(2)
        self.mfd_kappa_sbox.setMinimum(0.05)
        self.mfd_kappa_sbox.setSingleStep(0.05)
        self.mfd_kappa_sbox.setProperty("value", 0.2)
        #self.mfd_kappa_sbox.setObjectName("mfd_kappa_sbox")

        self.mfd_form.setWidget(0, QFormLayout.ItemRole.FieldRole, self.mfd_kappa_sbox)

        self.mfd_qmax_label.setFont(QFont("Arial", 12))
        self.mfd_qmax_label.setText("Q max")
        #self.mfd_qmax_label.setObjectName("mfd_qmax_label")

        self.mfd_form.setWidget(1, QFormLayout.ItemRole.LabelRole, self.mfd_qmax_label)

        self.mfd_qmax_sbox.setFont(QFont("Arial", 13))
        self.mfd_qmax_sbox.setDecimals(2)
        self.mfd_qmax_sbox.setMinimum(0.05)
        self.mfd_qmax_sbox.setSingleStep(0.05)
        self.mfd_qmax_sbox.setProperty("value", 1.0)
        #self.mfd_qmax_sbox.setObjectName("mfd_qmax_sbox")

        self.mfd_form.setWidget(1, QFormLayout.ItemRole.FieldRole, self.mfd_qmax_sbox)

        self.mfd_figure_size_x_label.setFont(QFont("Arial", 12))
        self.mfd_figure_size_x_label.setText("Figure size X")
        #self.mfd_figure_size_x_label.setObjectName("mfd_figure_size_x_label")

        self.mfd_form.setWidget(2, QFormLayout.ItemRole.LabelRole, self.mfd_figure_size_x_label)

        self.mfd_figure_size_x_sbox.setFont(QFont("Arial", 13))
        self.mfd_figure_size_x_sbox.setDecimals(0)
        self.mfd_figure_size_x_sbox.setMinimum(1.0)
        self.mfd_figure_size_x_sbox.setProperty("value", 4.0)
        #self.mfd_figure_size_x_sbox.setObjectName("mfd_figure_size_x_sbox")

        self.mfd_form.setWidget(2, QFormLayout.ItemRole.FieldRole, self.mfd_figure_size_x_sbox)

        self.mfd_figure_size_y_label.setFont(QFont("Arial", 12))
        self.mfd_figure_size_y_label.setText("Figure size Y")
        #self.mfd_figure_size_y_label.setObjectName("mfd_figure_size_y_label")

        self.mfd_form.setWidget(3, QFormLayout.ItemRole.LabelRole, self.mfd_figure_size_y_label)

        self.mfd_figure_size_y_sbox.setFont(QFont("Arial", 13))
        self.mfd_figure_size_y_sbox.setDecimals(0)
        self.mfd_figure_size_y_sbox.setMinimum(1.0)
        self.mfd_figure_size_y_sbox.setProperty("value", 4.0)
        #self.mfd_figure_size_y_sbox.setObjectName("mfd_figure_size_y_sbox")

        self.mfd_form.setWidget(3, QFormLayout.ItemRole.FieldRole, self.mfd_figure_size_y_sbox)

        self.mfd_link_label.setFont(QFont("Arial", 12))
        self.mfd_link_label.setText("Link")
        #self.mfd_link_label.setObjectName("mfd_link_label")

        self.mfd_form.setWidget(4, QFormLayout.ItemRole.LabelRole, self.mfd_link_label)

        self.mfd_link_cobox.setFont(QFont("Arial", 10))
        #self.mfd_link_cobox.setObjectName("mfd_link_cobox")

        self.mfd_form.setWidget(4, QFormLayout.ItemRole.FieldRole, self.mfd_link_cobox)

        self.cc_form_layout.setGeometry(QRect(750, 60, 321, 281))
        #self.cc_form_layout.setObjectName("cc_form_layout")

        self.cc_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.cc_form.setContentsMargins(0, 0, 0, 0)
        self.cc_form.setHorizontalSpacing(50)
        self.cc_form.setVerticalSpacing(20)
        #self.cc_form.setObjectName("cc_form")

        self.cc_figure_size_x_label.setFont(QFont("Arial", 12))
        self.cc_figure_size_x_label.setText("Figure size X")
        #self.cc_figure_size_x_label.setObjectName("cc_figure_size_x_label")

        self.cc_form.setWidget(0, QFormLayout.ItemRole.LabelRole, self.cc_figure_size_x_label)

        self.cc_figure_size_x_sbox.setFont(QFont("Arial", 13))
        self.cc_figure_size_x_sbox.setDecimals(0)
        self.cc_figure_size_x_sbox.setMinimum(1.0)
        self.cc_figure_size_x_sbox.setProperty("value", 6.0)
        #self.cc_figure_size_x_sbox.setObjectName("cc_figure_size_x_sbox")

        self.cc_form.setWidget(0, QFormLayout.ItemRole.FieldRole, self.cc_figure_size_x_sbox)

        self.cc_figure_size_y_label.setFont(QFont("Arial", 12))
        self.cc_figure_size_y_label.setText("Figure size Y")
        #self.cc_figure_size_y_label.setObjectName("cc_figure_size_y_label")

        self.cc_form.setWidget(1, QFormLayout.ItemRole.LabelRole, self.cc_figure_size_y_label)

        self.cc_figure_size_y_sbox.setFont(QFont("Arial", 13))
        self.cc_figure_size_y_sbox.setDecimals(0)
        self.cc_figure_size_y_sbox.setMinimum(1.0)
        self.cc_figure_size_y_sbox.setProperty("value", 4.0)
        #self.cc_figure_size_y_sbox.setObjectName("cc_figure_size_y_sbox")

        self.cc_form.setWidget(1, QFormLayout.ItemRole.FieldRole, self.cc_figure_size_y_sbox)

        self.cc_link_label.setFont(QFont("Arial", 12))
        self.cc_link_label.setText("Link")
        #self.cc_link_label.setObjectName("cc_link_label")

        self.cc_form.setWidget(2, QFormLayout.ItemRole.LabelRole, self.cc_link_label)

        self.cc_link_cobox.setFont(QFont("Arial", 10))
        #self.cc_link_cobox.setObjectName("cc_link_cobox")

        self.cc_form.setWidget(2, QFormLayout.ItemRole.FieldRole, self.cc_link_cobox)

        self.control_tabs.addTab(self.statistics_tab_1, "Statistics 1")

    def setup_statistics_2_tab(self):
        # TODO write docs

        self.statistics_tab_2.setEnabled(False)
        #self.statistics_tab_2.setObjectName("statistics_tab_2")

        self.tsdd_label.setGeometry(QRect(10, -10, 260, 50))
        self.tsdd_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.tsdd_label.setText("Time Space Diagram Density")
        #self.tsdd_label.setObjectName("tsdd_label")

        self.tsdt_label.setGeometry(QRect(560, -10, 270, 50))
        self.tsdt_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.tsdt_label.setText("Time Space Diagram Trajectory")
        #self.tsdt_label.setObjectName("tsdt_label")

        self.tsdd_button.setGeometry(QRect(160, 420, 210, 40))
        self.tsdd_button.setFont(QFont("Arial", 11, italic=True))
        self.tsdd_button.setText("Show TSD Density")
        #self.tsdd_button.setObjectName("tsdd_button")

        self.tsdt_button.setGeometry(QRect(690, 420, 210, 40))
        self.tsdt_button.setFont(QFont("Arial", 11, italic=True))
        self.tsdt_button.setText("Show TSD Trajectory")
        #self.tsdt_button.setObjectName("tsdt_button")

        self.line_5.setGeometry(QRect(530, 0, 20, 471))
        self.line_5.setFrameShadow(QFrame.Shadow.Raised)
        self.line_5.setLineWidth(3)
        self.line_5.setMidLineWidth(1)
        self.line_5.setFrameShape(QFrame.Shape.VLine)
        #self.line_5.setObjectName("line_5")

        self.tsdd_form_layout.setGeometry(QRect(30, 60, 501, 271))
        #self.tsdd_form_layout.setObjectName("tsdd_form_layout")

        self.tsdd_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.tsdd_form.setContentsMargins(0, 0, 0, 0)
        self.tsdd_form.setHorizontalSpacing(50)
        self.tsdd_form.setVerticalSpacing(20)
        #self.tsdd_form.setObjectName("tsdd_form")

        self.tsdd_figure_size_x_label.setFont(QFont("Arial", 12))
        self.tsdd_figure_size_x_label.setText("Figure size X")
        #self.tsdd_figure_size_x_label.setObjectName("tsdd_figure_size_x_label")

        self.tsdd_form.setWidget(0, QFormLayout.ItemRole.LabelRole, self.tsdd_figure_size_x_label)

        self.tsdd_figure_size_x_sbox.setFont(QFont("Arial", 13))
        self.tsdd_figure_size_x_sbox.setDecimals(0)
        self.tsdd_figure_size_x_sbox.setMinimum(1.0)
        self.tsdd_figure_size_x_sbox.setProperty("value", 12.0)
        #self.tsdd_figure_size_x_sbox.setObjectName("tsdd_figure_size_x_sbox")

        self.tsdd_form.setWidget(0, QFormLayout.ItemRole.FieldRole, self.tsdd_figure_size_x_sbox)

        self.tsdd_figure_size_y_label.setFont(QFont("Arial", 12))
        self.tsdd_figure_size_y_label.setText("Figure size Y")
        #self.tsdd_figure_size_y_label.setObjectName("tsdd_figure_size_y_label")

        self.tsdd_form.setWidget(1, QFormLayout.ItemRole.LabelRole, self.tsdd_figure_size_y_label)

        self.tsdd_figure_size_y_sbox.setFont(QFont("Arial", 13))
        self.tsdd_figure_size_y_sbox.setDecimals(0)
        self.tsdd_figure_size_y_sbox.setMinimum(1.0)
        self.tsdd_figure_size_y_sbox.setProperty("value", 4.0)
        #self.tsdd_figure_size_y_sbox.setObjectName("tsdd_figure_size_y_sbox")

        self.tsdd_form.setWidget(1, QFormLayout.ItemRole.FieldRole, self.tsdd_figure_size_y_sbox)

        self.tsdd_link_label.setFont(QFont("Arial", 12))
        self.tsdd_link_label.setText("Link")
        #self.tsdd_link_label.setObjectName("tsdd_link_label")

        self.tsdd_form.setWidget(2, QFormLayout.ItemRole.LabelRole, self.tsdd_link_label)

        self.tsdd_link_cobox.setFont(QFont("Arial", 10))
        #self.tsdd_link_cobox.setObjectName("tsdd_link_cobox")

        self.tsdd_form.setWidget(2, QFormLayout.ItemRole.FieldRole, self.tsdd_link_cobox)

        self.tsdt_form_layout.setGeometry(QRect(580, 60, 481, 271))
        #self.tsdt_form_layout.setObjectName("tsdt_form_layout")

        self.tsdt_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.tsdt_form.setContentsMargins(0, 0, 0, 0)
        self.tsdt_form.setHorizontalSpacing(50)
        self.tsdt_form.setVerticalSpacing(20)
        #self.tsdt_form.setObjectName("tsdt_form")

        self.tsdt_figure_size_x_label.setFont(QFont("Arial", 12))
        self.tsdt_figure_size_x_label.setText("Figure size X")
        #self.tsdt_figure_size_x_label.setObjectName("tsdt_figure_size_x_label")

        self.tsdt_form.setWidget(0, QFormLayout.ItemRole.LabelRole, self.tsdt_figure_size_x_label)

        self.tsdt_figure_size_x_sbox.setFont(QFont("Arial", 13))
        self.tsdt_figure_size_x_sbox.setDecimals(0)
        self.tsdt_figure_size_x_sbox.setMinimum(1.0)
        self.tsdt_figure_size_x_sbox.setProperty("value", 12.0)
        #self.tsdt_figure_size_x_sbox.setObjectName("tsdt_figure_size_x_sbox")

        self.tsdt_form.setWidget(0, QFormLayout.ItemRole.FieldRole, self.tsdt_figure_size_x_sbox)

        self.tsdt_figure_size_y_label.setFont(QFont("Arial", 12))
        self.tsdt_figure_size_y_label.setText("Figure size Y")
        #self.tsdt_figure_size_y_label.setObjectName("tsdt_figure_size_y_label")

        self.tsdt_form.setWidget(1, QFormLayout.ItemRole.LabelRole, self.tsdt_figure_size_y_label)

        self.tsdt_figure_size_y_sbox.setFont(QFont("Arial", 13))
        self.tsdt_figure_size_y_sbox.setDecimals(0)
        self.tsdt_figure_size_y_sbox.setMinimum(1.0)
        self.tsdt_figure_size_y_sbox.setProperty("value", 4.0)
        #self.tsdt_figure_size_y_sbox.setObjectName("tsdt_figure_size_y_sbox")

        self.tsdt_form.setWidget(1, QFormLayout.ItemRole.FieldRole, self.tsdt_figure_size_y_sbox)

        self.tsdt_link_label.setFont(QFont("Arial", 12))
        self.tsdt_link_label.setText("Link")
        #self.tsdt_link_label.setObjectName("tsdt_link_label")

        self.tsdt_form.setWidget(2, QFormLayout.ItemRole.LabelRole, self.tsdt_link_label)

        self.tsdt_link_cobox.setFont(QFont("Arial", 10))
        #self.tsdt_link_cobox.setObjectName("tsdt_link_cobox")

        self.tsdt_form.setWidget(2, QFormLayout.ItemRole.FieldRole, self.tsdt_link_cobox)

        self.control_tabs.addTab(self.statistics_tab_2, "Statistics 2")

    def setup_animations_tab(self):
        # TODO write docs

        self.animations_tab.setEnabled(False)
        #self.animations_tab.setObjectName("animations_tab")

        self.sa_label.setGeometry(QRect(10, -10, 160, 50))
        self.sa_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.sa_label.setText("Simple Animation")
        #self.sa_label.setObjectName("sa_label")

        self.sa_button.setGeometry(QRect(160, 420, 210, 40))
        self.sa_button.setFont(QFont("Arial", 11, italic=True))
        self.sa_button.setText("Show Simple Animation")
        #self.sa_button.setObjectName("sa_button")

        self.fa_button.setGeometry(QRect(690, 420, 210, 40))
        self.fa_button.setFont(QFont("Arial", 11, italic=True))
        self.fa_button.setText("Show Fancy Animation")
        #self.fa_button.setObjectName("fa_button")

        self.fa_label.setGeometry(QRect(560, -10, 160, 50))
        self.fa_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.fa_label.setText("Fancy Animation")
        #self.fa_label.setObjectName("fa_label")

        self.line.setGeometry(QRect(530, 0, 20, 471))
        self.line.setFrameShadow(QFrame.Shadow.Raised)
        self.line.setLineWidth(3)
        self.line.setMidLineWidth(1)
        self.line.setFrameShape(QFrame.Shape.VLine)
        #self.line.setObjectName("line")

        self.sa_form_layout.setGeometry(QRect(130, 30, 281, 391))
        #self.sa_form_layout.setObjectName("formLayoutWidget")

        self.sa_form.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.sa_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.sa_form.setContentsMargins(0, 0, 0, 0)
        self.sa_form.setHorizontalSpacing(50)
        self.sa_form.setVerticalSpacing(20)
        #self.sa_form.setObjectName("sa_form")

        self.sa_speed_inverse_sbox.setFont(QFont("Arial", 13))
        self.sa_speed_inverse_sbox.setDecimals(0)
        self.sa_speed_inverse_sbox.setMinimum(1.0)
        self.sa_speed_inverse_sbox.setMaximum(100.0)
        self.sa_speed_inverse_sbox.setProperty("value", 10.0)
        #self.sa_speed_inverse_sbox.setObjectName("sa_speed_inverse_sbox")

        self.sa_form.setWidget(0, QFormLayout.ItemRole.FieldRole, self.sa_speed_inverse_sbox)

        self.sa_detailed_label.setFont(QFont("Arial", 12))
        self.sa_detailed_label.setText("Detailed")
        #self.sa_detailed_label.setObjectName("sa_detailed_label")

        self.sa_form.setWidget(1, QFormLayout.ItemRole.LabelRole, self.sa_detailed_label)

        #self.sa_detailed_chbox.setText("")
        #self.sa_detailed_chbox.setChecked(False)
        #self.sa_detailed_chbox.setObjectName("sa_detailed_chbox")

        self.sa_form.setWidget(1, QFormLayout.ItemRole.FieldRole, self.sa_detailed_chbox)

        self.sa_left_handed_label.setFont(QFont("Arial", 12))
        self.sa_left_handed_label.setText("Left handed")
        #self.sa_left_handed_label.setObjectName("sa_left_handed_label")

        self.sa_form.setWidget(2, QFormLayout.ItemRole.LabelRole, self.sa_left_handed_label)

        #self.sa_left_handed_chbox.setText("")
        #self.sa_left_handed_chbox.setChecked(False)
        #self.sa_left_handed_chbox.setObjectName("sa_left_handed_chbox")

        self.sa_form.setWidget(2, QFormLayout.ItemRole.FieldRole, self.sa_left_handed_chbox)

        self.sa_figure_size_x_label.setFont(QFont("Arial", 12))
        self.sa_figure_size_x_label.setText("Figure size X")
        #self.sa_figure_size_x_label.setObjectName("sa_figure_size_x_label")

        self.sa_form.setWidget(3, QFormLayout.ItemRole.LabelRole, self.sa_figure_size_x_label)

        self.sa_figure_size_x_sbox.setFont(QFont("Arial", 13))
        self.sa_figure_size_x_sbox.setDecimals(0)
        self.sa_figure_size_x_sbox.setMinimum(1.0)
        self.sa_figure_size_x_sbox.setProperty("value", 6.0)
        #self.sa_figure_size_x_sbox.setObjectName("sa_figure_size_x_sbox")

        self.sa_form.setWidget(3, QFormLayout.ItemRole.FieldRole, self.sa_figure_size_x_sbox)

        self.sa_speed_inverse_label.setFont(QFont("Arial", 12))
        self.sa_speed_inverse_label.setText("Animation speed inverse")
        #self.sa_speed_inverse_label.setObjectName("sa_speed_inverse_label")

        self.sa_form.setWidget(0, QFormLayout.ItemRole.LabelRole, self.sa_speed_inverse_label)

        self.sa_figure_size_y_label.setFont(QFont("Arial", 12))
        self.sa_figure_size_y_label.setText("Figure size Y")
        #self.sa_figure_size_y_label.setObjectName("sa_figure_size_y_label")

        self.sa_form.setWidget(4, QFormLayout.ItemRole.LabelRole, self.sa_figure_size_y_label)

        self.sa_figure_size_y_sbox.setFont(QFont("Arial", 13))
        self.sa_figure_size_y_sbox.setDecimals(0)
        self.sa_figure_size_y_sbox.setMinimum(1.0)
        self.sa_figure_size_y_sbox.setProperty("value", 12.0)
        #self.sa_figure_size_y_sbox.setObjectName("sa_figure_size_y_sbox")

        self.sa_form.setWidget(4, QFormLayout.ItemRole.FieldRole, self.sa_figure_size_y_sbox)

        self.sa_node_size_label.setFont(QFont("Arial", 12))
        self.sa_node_size_label.setText("Node size")
        #self.sa_node_size_label.setObjectName("sa_node_size_label")

        self.sa_form.setWidget(5, QFormLayout.ItemRole.LabelRole, self.sa_node_size_label)

        self.sa_node_size_sbox.setFont(QFont("Arial", 13))
        self.sa_node_size_sbox.setDecimals(0)
        self.sa_node_size_sbox.setMinimum(0.0)
        self.sa_node_size_sbox.setMaximum(100.0)
        self.sa_node_size_sbox.setProperty("value", 2.0)
        #self.sa_node_size_sbox.setObjectName("sa_node_size_sbox")

        self.sa_form.setWidget(5, QFormLayout.ItemRole.FieldRole, self.sa_node_size_sbox)

        self.sa_network_font_size_label.setFont(QFont("Arial", 12))
        self.sa_network_font_size_label.setText("Network font size")
        #self.sa_network_font_size_label.setObjectName("sa_network_font_size_label")

        self.sa_form.setWidget(6, QFormLayout.ItemRole.LabelRole, self.sa_network_font_size_label)

        self.sa_network_font_size_sbox.setFont(QFont("Arial", 13))
        self.sa_network_font_size_sbox.setDecimals(0)
        self.sa_network_font_size_sbox.setMinimum(0.0)
        self.sa_network_font_size_sbox.setMaximum(100.0)
        self.sa_network_font_size_sbox.setProperty("value", 20.0)
        #self.sa_network_font_size_sbox.setObjectName("sa_network_font_size_sbox")

        self.sa_form.setWidget(6, QFormLayout.ItemRole.FieldRole, self.sa_network_font_size_sbox)

        self.sa_timestep_skip_label.setFont(QFont("Arial", 12))
        self.sa_timestep_skip_label.setText("Timestep skip")
        #self.sa_timestep_skip_label.setObjectName("sa_timestep_skip_label")

        self.sa_form.setWidget(7, QFormLayout.ItemRole.LabelRole, self.sa_timestep_skip_label)

        self.sa_timestep_skip_sbox.setFont(QFont("Arial", 13))
        self.sa_timestep_skip_sbox.setDecimals(0)
        self.sa_timestep_skip_sbox.setMinimum(1.0)
        self.sa_timestep_skip_sbox.setMaximum(100.0)
        self.sa_timestep_skip_sbox.setProperty("value", 8.0)
        #self.sa_timestep_skip_sbox.setObjectName("sa_timestep_skip_sbox")

        self.sa_form.setWidget(7, QFormLayout.ItemRole.FieldRole, self.sa_timestep_skip_sbox)

        self.fa_form_layout.setGeometry(QRect(660, 30, 297, 391))
        #self.fa_form_layout.setObjectName("layoutWidget1")

        self.fa_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.fa_form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self.fa_form.setContentsMargins(0, 0, 0, 0)
        self.fa_form.setHorizontalSpacing(50)
        self.fa_form.setVerticalSpacing(20)
        #self.fa_form.setObjectName("f_anim_form")

        self.fa_speed_inverse_label.setFont(QFont("Arial", 12))
        self.fa_speed_inverse_label.setText("Animation speed inverse")
        #self.fa_speed_inverse_label.setObjectName("fa_speed_inverse_label")

        self.fa_form.setWidget(0, QFormLayout.ItemRole.LabelRole, self.fa_speed_inverse_label)

        self.fa_speed_inverse_sbox.setFont(QFont("Arial", 13))
        self.fa_speed_inverse_sbox.setDecimals(0)
        self.fa_speed_inverse_sbox.setMinimum(1.0)
        self.fa_speed_inverse_sbox.setMaximum(100.0)
        self.fa_speed_inverse_sbox.setProperty("value", 10.0)
        #self.fa_speed_inverse_sbox.setObjectName("fa_speed_inverse_sbox")

        self.fa_form.setWidget(0, QFormLayout.ItemRole.FieldRole, self.fa_speed_inverse_sbox)

        self.fa_figure_size_label.setFont(QFont("Arial", 12))
        self.fa_figure_size_label.setText("Figure size")
        #self.fa_figure_size_label.setObjectName("fa_figure_size_label")

        self.fa_form.setWidget(1, QFormLayout.ItemRole.LabelRole, self.fa_figure_size_label)

        self.fa_figure_size_sbox.setFont(QFont("Arial", 13))
        self.fa_figure_size_sbox.setDecimals(0)
        self.fa_figure_size_sbox.setMinimum(1.0)
        self.fa_figure_size_sbox.setMaximum(100.0)
        self.fa_figure_size_sbox.setProperty("value", 6.0)
        #self.fa_figure_size_sbox.setObjectName("fa_figure_size_sbox")

        self.fa_form.setWidget(1, QFormLayout.ItemRole.FieldRole, self.fa_figure_size_sbox)

        self.fa_sample_ratio_label.setFont(QFont("Arial", 12))
        self.fa_sample_ratio_label.setText("Sample ratio")
        #self.fa_sample_ratio_label.setObjectName("fa_sample_ratio_label")

        self.fa_form.setWidget(2, QFormLayout.ItemRole.LabelRole, self.fa_sample_ratio_label)

        self.fa_sample_ratio_sbox.setFont(QFont("Arial", 13))
        self.fa_sample_ratio_sbox.setDecimals(2)
        self.fa_sample_ratio_sbox.setMinimum(0.01)
        self.fa_sample_ratio_sbox.setMaximum(1.0)
        self.fa_sample_ratio_sbox.setSingleStep(0.05)
        self.fa_sample_ratio_sbox.setProperty("value", 0.3)
        #self.fa_sample_ratio_sbox.setObjectName("fa_sample_ratio_sbox")

        self.fa_form.setWidget(2, QFormLayout.ItemRole.FieldRole, self.fa_sample_ratio_sbox)

        self.fa_interval_label.setFont(QFont("Arial", 12))
        self.fa_interval_label.setText("Interval")
        #self.fa_interval_label.setObjectName("fa_interval_label")

        self.fa_form.setWidget(3, QFormLayout.ItemRole.LabelRole, self.fa_interval_label)

        self.fa_interval_sbox.setFont(QFont("Arial", 13))
        self.fa_interval_sbox.setDecimals(0)
        self.fa_interval_sbox.setMinimum(1.0)
        self.fa_interval_sbox.setMaximum(100.0)
        self.fa_interval_sbox.setProperty("value", 5.0)
        #self.fa_interval_sbox.setObjectName("fa_interval_sbox")

        self.fa_form.setWidget(3, QFormLayout.ItemRole.FieldRole, self.fa_interval_sbox)

        self.fa_network_font_size_label.setFont(QFont("Arial", 12))
        self.fa_network_font_size_label.setText("Network font size")
        #self.fa_network_font_size_label.setObjectName("fa_network_font_size_label")

        self.fa_form.setWidget(4, QFormLayout.ItemRole.LabelRole, self.fa_network_font_size_label)

        self.fa_network_font_size_sbox.setFont(QFont("Arial", 13))
        self.fa_network_font_size_sbox.setDecimals(0)
        self.fa_network_font_size_sbox.setMinimum(0.0)
        self.fa_network_font_size_sbox.setMaximum(100.0)
        self.fa_network_font_size_sbox.setProperty("value", 0.0)
        #self.fa_network_font_size_sbox.setObjectName("fa_network_font_size_sbox")

        self.fa_form.setWidget(4, QFormLayout.ItemRole.FieldRole, self.fa_network_font_size_sbox)

        self.fa_trace_length_label.setFont(QFont("Arial", 12))
        self.fa_trace_length_label.setText("Trace length")
        #self.fa_trace_length_label.setObjectName("fa_trace_length_label")

        self.fa_form.setWidget(5, QFormLayout.ItemRole.LabelRole, self.fa_trace_length_label)

        self.fa_trace_length_sbox.setFont(QFont("Arial", 13))
        self.fa_trace_length_sbox.setDecimals(0)
        self.fa_trace_length_sbox.setMinimum(0.0)
        self.fa_trace_length_sbox.setMaximum(100.0)
        self.fa_trace_length_sbox.setProperty("value", 3.0)
        #self.fa_trace_length_sbox.setObjectName("fa_trace_length_sbox")

        self.fa_form.setWidget(5, QFormLayout.ItemRole.FieldRole, self.fa_trace_length_sbox)

        self.fa_speed_coef_label.setFont(QFont("Arial", 12))
        self.fa_speed_coef_label.setText("Speed coefficient")
        #self.fa_speed_coef_label.setObjectName("fa_speed_coef_label")

        self.fa_form.setWidget(6, QFormLayout.ItemRole.LabelRole, self.fa_speed_coef_label)

        self.fa_speed_coef_sbox.setFont(QFont("Arial", 13))
        self.fa_speed_coef_sbox.setDecimals(0)
        self.fa_speed_coef_sbox.setMinimum(0.0)
        self.fa_speed_coef_sbox.setMaximum(100.0)
        self.fa_speed_coef_sbox.setProperty("value", 2.0)
        #self.fa_speed_coef_sbox.setObjectName("fa_speed_coef_sbox")

        self.fa_form.setWidget(6, QFormLayout.ItemRole.FieldRole, self.fa_speed_coef_sbox)

        self.fa_antialiasing_label.setFont(QFont("Arial", 12))
        self.fa_antialiasing_label.setText("Antialiasing")
        #self.fa_antialiasing_label.setObjectName("fa_antialiasing_label")

        self.fa_form.setWidget(7, QFormLayout.ItemRole.LabelRole, self.fa_antialiasing_label)

        #self.fa_antialiasing_chbox.setText("")
        self.fa_antialiasing_chbox.setChecked(True)
        #self.fa_antialiasing_chbox.setObjectName("fa_antialiasing_chbox")

        self.fa_form.setWidget(7, QFormLayout.ItemRole.FieldRole, self.fa_antialiasing_chbox)

        self.control_tabs.addTab(self.animations_tab, "Animations")

    def import_graph(self):
        """
        Imports a graph from a .graphml file and applies a style from a corresponding .yaml file.

        This function opens a file dialog for the user to select a .graphml file, loads the graph using osmnx,
        and then attempts to load a style file with the same name but with a .yaml extension. The graph is then
        plotted with the specified style and displayed on the canvas. Then it disables the tabs in the user interface.

        Raises:
            FileNotFoundError: If the style file is not found.
            yaml.YAMLError: If there is an error in the YAML file.
            Exception: For any other unexpected errors.
        """
        #TODO rewrite  docs

        self.graphml_file_path = QFileDialog.getOpenFileName(
            parent=self,
            caption="Select a .graphml file",
            directory=os.getcwd(),
            filter="GraphML Files (*.graphml)",
            initialFilter="GraphML Files (*.graphml)"
        )[0]

        if self.graphml_file_path == "":
            return

        print(self.graphml_file_path)

        graph = osmnx.load_graphml(self.graphml_file_path)
        style_file_path = self.graphml_file_path.replace(".graphml", "_style.yaml")

        self.wo_world_name_text.setPlainText(self.graphml_file_path.split("/")[-1].split(".")[0])

        style_data = self.load_style_file(style_file_path)
        self.fig, self.ax = self.plot_graph_with_style(graph, style_data)

        self.update_canvas(self.fig, self.ax)

        self.enable_tabs(False)

    def load_style_file(self, style_file_path):
        """
        Loads the style data from a YAML file.

        Args:
            style_file_path (str): The path to the style YAML file.

        Returns:
            dict: The style data.

        Raises:
            FileNotFoundError: If the style file is not found.
            yaml.YAMLError: If there is an error in the YAML file.
            Exception: For any other unexpected errors.
        """
        try:
            with open(style_file_path, "r") as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"File not found: {style_file_path}")
            raise
        except yaml.YAMLError as exc:
            print(f"Error in YAML file: {exc}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise

    def plot_graph_with_style(self, graph, style_data):
        """
        Plots the graph with the specified style.

        Args:
            graph: The graph to plot.
            style_data (dict): The style data.

        Returns:
            tuple: The figure and axis of the plot.
        """
        fig, ax = osmnx.plot_graph(graph, node_size=int(style_data["node_size"]),
                                   node_color=style_data["node_color"],
                                   edge_color=style_data["edge_color"],
                                   bgcolor=style_data["bgcolor"],
                                   edge_linewidth=style_data["edge_linewidth"],
                                   show=False)
        fig.tight_layout()
        ax.set_aspect('equal')
        return fig, ax

    def update_canvas(self, fig, ax):
        """
        Updates the canvas with the new plot.

        Args:
            fig: The figure of the plot.
            ax: The axis of the plot.
        """
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

    def enable_tabs(self, enable):
        """
        Enables or disables the tabs in the user interface.

        Args:
            enable (bool): If True, enables the tabs; if False, disables them.
        """
        self.statistics_tab_1.setEnabled(enable)
        self.statistics_tab_2.setEnabled(enable)
        self.animations_tab.setEnabled(enable)

    def show_osm_network(self):
        #TODO write docs

        try:
            self.generate_nodes_and_links()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating nodes and links: {e}", QMessageBox.StandardButton.Ok)
            print(f"Error generating nodes and links: {e}")
            return

        if not os.path.exists(f"./out{self.world.name}"):
            os.makedirs(f"./out{self.world.name}")


        fig_size = (self.osmn_figure_size_x_sbox.value(), self.osmn_figure_size_y_sbox.value())
        link_names = self.osmn_show_link_names_chbox.isChecked()
        image_path = f"./out{self.world.name}/osm_network.png"

        try:
            OSMImporter.osm_network_visualize(nodes=self.nodes, links=self.links, figsize=fig_size, show_link_name=link_names, save_mode=1, show_mode=0,
                                              save_fname=image_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error visualizing the OSM network: {e}", QMessageBox.StandardButton.Ok)
            print(f"Error visualizing the OSM network: {e}")

        image_dialog = QDialog(self)
        image_dialog.setWindowTitle("OSM Network Visualization")
        image_dialog.setMinimumSize(600, 400)  # Minimum size for the dialog

        # Create a label to display the image
        image_label = QLabel(image_dialog)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setScaledContents(True)  # Enable automatic scaling of image contents

        # Load the image and set it to the label
        pixmap = QPixmap(image_path)
        image_label.setPixmap(pixmap)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(image_label)
        image_dialog.setLayout(layout)

        # Show the dialog
        image_dialog.exec()

        self.update_canvas(self.fig, self.ax)

    def add_demand(self):
        """
        Adds a new demand route tab.

        This method increments the route index and sets up a new route tab
        with the updated index.
        """
        self.r_index += 1
        self.setup_route_tab_i(self.r_index)

    def remove_demand(self):
        """
        Removes the most recently added demand route tab.

        This method checks if there is more than one route tab. If so, it removes the last tab
        and deletes its references from the spin box dictionary. The route index is then decremented.
        """
        if self.r_index > 1:
            tab_name = f"r_{self.r_index}"

            self.r_route_tabs.removeTab(self.r_index - 1)

            if tab_name in self.spin_box_references:
                del self.spin_box_references[tab_name]

            self.r_index -= 1

    def run_simulation(self):
        # TODO write docs
        try:
            self.generate_nodes_and_links()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating nodes and links: {e}", QMessageBox.StandardButton.Ok)
            print(f"Error generating nodes and links: {e}")
            return


        tab_index = 0
        for tab_name, spin_boxes in self.spin_box_references.items():
            tab_index += 1
            x_orig = self.spin_box_references[tab_name]["r_x_origin_sbox_" + str(tab_index)].value()
            y_orig = self.spin_box_references[tab_name]["r_y_origin_sbox_" + str(tab_index)].value()
            radius_orig = self.spin_box_references[tab_name]["r_radius_origin_sbox_" + str(tab_index)].value()
            x_dest = self.spin_box_references[tab_name]["r_x_destination_sbox_" + str(tab_index)].value()
            y_dest = self.spin_box_references[tab_name]["r_y_destination_sbox_" + str(tab_index)].value()
            radius_dest = self.spin_box_references[tab_name]["r_radius_destination_sbox_" + str(tab_index)].value()
            t_start = self.spin_box_references[tab_name]["r_t_start_sbox_" + str(tab_index)].value()
            t_end = self.spin_box_references[tab_name]["r_t_end_sbox_" + str(tab_index)].value()
            flow = self.spin_box_references[tab_name]["r_flow_sbox_" + str(tab_index)].value()

            self.world.adddemand_area2area(
                x_orig=x_orig, y_orig=y_orig, radious_orig=radius_orig,
                x_dest=x_dest, y_dest=y_dest, radious_dest=radius_dest,
                t_start=t_start, t_end=t_end, flow=flow
            )

        output_dialog = QDialog(self)
        output_dialog.setWindowTitle("Simulation Output")
        output_dialog.resize(400, 300)

        output_text = QTextEdit(output_dialog)
        output_text.setReadOnly(True)

        layout = QVBoxLayout(output_dialog)
        layout.addWidget(output_text)

        original_stdout = sys.stdout
        sys.stdout = StringIO()

        self.world.exec_simulation()

        self.world.analyzer.print_simple_stats()

        sys.stdout.seek(0)
        output_text.setText(sys.stdout.read())
        sys.stdout = original_stdout

        with open(f"./out{self.world.name}/simulation_output.txt", "w") as f:
            f.write(output_text.toPlainText())


        output_dialog.exec()

        self.enable_tabs(True)

        self.mfd_link_cobox.clear()
        self.cc_link_cobox.clear()
        self.tsdd_link_cobox.clear()
        self.tsdt_link_cobox.clear()

        #TODO only populate comboboxes with links that have data / used after postprocessing
        #TODO make comboboxes searchable
        #TODO make comboboxes display links in aplhabetical order
        active_links = [link for link in self.world.LINKS if self.world.K_AREA[link] is not None]
        for link in active_links:
            link_name = str(link).split("<Link ")[1][:-1]
            self.mfd_link_cobox.addItem(link_name, link)
            self.cc_link_cobox.addItem(link_name, link)
            self.tsdd_link_cobox.addItem(link_name, link)
            self.tsdt_link_cobox.addItem(link_name, link)

    def generate_nodes_and_links(self):
        """
        Generates nodes and links for the world.

        This method loads world data from a YAML file, imports OSM data based on the bounding box and custom filter,
        processes the network, and converts it to the World format.

        Raises:
            FileNotFoundError: If the world YAML file is not found.
            yaml.YAMLError: If there is an error in the YAML file.
            Exception: For any other unexpected errors.
        """
        # TODO rewrite docs

        if self.graphml_file_path is None:
            QMessageBox.critical(self, "Error", "Please import an OSM network first.", QMessageBox.StandardButton.Ok)
            return

        world_name = self.wo_world_name_text.toPlainText()

        if world_name == "":
            QMessageBox.critical(self, "Error", "Please enter a world name.", QMessageBox.StandardButton.Ok)
            return

        delta_n = int(self.wo_delta_n_sbox.value())
        tmax = None if self.wo_t_max_automatic_chbox.isChecked() else int(self.wo_t_max_sbox.value())

        self.world = World(
            name=world_name,
            deltan=delta_n,
            tmax=tmax,
            print_mode=1,
            save_mode=1,
            show_mode=1
        )


        world_data = self.load_style_file(self.graphml_file_path.replace(".graphml", "_style.yaml"))

        bbox = list((
                    world_data["bounding_box_north"], world_data["bounding_box_south"], world_data["bounding_box_east"],
                    world_data["bounding_box_west"]))
        custom_filter = world_data["custom_filter"]

        self.nodes, self.links = OSMImporter.import_osm_data(bbox=bbox, custom_filter=custom_filter)

        node_merge_threshold = float(self.wp_node_merge_threshold_sbox.value())
        node_merge_iteration = int(self.wp_node_merge_iteration_sbox.value())
        enforce_bidirectional = self.wp_enforce_bidirectional_chbox.isChecked()

        try:
            self.nodes, self.links = OSMImporter.osm_network_postprocessing(nodes=self.nodes, links=self.links, node_merge_threshold=node_merge_threshold,
                                                                    node_merge_iteration=node_merge_iteration, enforce_bidirectional=enforce_bidirectional)
        except Exception as e:
            print(f"Error postprocessing nodes and links: {e}")


        default_jam_density = float(self.wp_default_jam_density_sbox.value())

        try:
            OSMImporter.osm_network_to_World(W=self.world, nodes=self.nodes, links=self.links,
                                             default_jam_density=default_jam_density)
        except KeyError as e:
            print(f"Error converting OSM network to World: {e}")

    def show_world_network(self):
        """
        Visualizes the world network with the given parameters.

        This function retrieves the width, left-handedness, figure size, network font size,
        and node size from the UI elements and calls the `show_network` method of the `world` object
        to visualize the network.

        Args:
            self: The instance of the class.
        """
        width = self.wn_width_sbox.value()
        left_handed = 1 if self.wn_left_handed_chbox.isChecked() else 0
        fig_size = (self.wn_figure_size_x_sbox.value(), self.wn_figure_size_y_sbox.value())
        network_font_size = self.wn_network_font_size_sbox.value()
        node_size = self.wn_node_size_sbox.value()

        self.world.show_network(width=width,
                                left_handed=left_handed,
                                figsize=fig_size,
                                network_font_size=network_font_size,
                                node_size=node_size)

        self.update_canvas(self.fig, self.ax)


    def show_mfd(self):
        """
        Visualizes the Macroscopic Fundamental Diagram (MFD) for the selected link.

        This function retrieves the kappa value, maximum flow (q_max), selected link,
        and figure size from the UI elements. It then calls the `show_mfd` method
        of the `world` object to visualize the MFD.

        Args:
            self: The instance of the class.
        """
        kappa = float(self.mfd_kappa_sbox.value())
        q_max = float(self.mfd_qmax_sbox.value())
        link = self.mfd_link_cobox.currentData()
        links = [link]
        fname = f"_{str(link).split('<Link ')[1][:-1]}"
        fig_size = (int(self.mfd_figure_size_x_sbox.value()), int(self.mfd_figure_size_y_sbox.value()))

        self.world.analyzer.macroscopic_fundamental_diagram(kappa=kappa,
                                                            qmax=q_max,
                                                            links=links,
                                                            fname=fname,
                                                            figsize=fig_size)

        self.update_canvas(self.fig, self.ax)

    def show_cc(self):
        """
        Visualizes the Cumulative Curve (CC) for the selected link.

        This function retrieves the selected link and figure size from the UI elements.
        It then calls the `cumulative_curves` method of the `analyzer` object in the `world`
        to visualize the CC.

        Args:
            self: The instance of the class.
        """
        link = self.cc_link_cobox.currentData()
        fig_size = (self.cc_figure_size_x_sbox.value(), self.cc_figure_size_y_sbox.value())

        self.world.analyzer.cumulative_curves(links=link, figsize=fig_size)

        self.update_canvas(self.fig, self.ax)


    def show_tsdd(self):
        """
        Visualizes the Time Space Diagram Density (TSDD) for the selected link.

        This function retrieves the selected link and figure size from the UI elements.
        It then calls the `time_space_diagram_density` method of the `analyzer` object in the `world`
        to visualize the TSDD.

        Args:
            self: The instance of the class.
        """
        link = self.tsdd_link_cobox.currentData()
        fig_size = (self.tsdd_figure_size_x_sbox.value(), self.tsdd_figure_size_y_sbox.value())

        self.world.analyzer.time_space_diagram_density(links=link, figsize=fig_size)

        self.update_canvas(self.fig, self.ax)


    def show_tsdt(self):
        """
        Visualizes the Time Space Diagram Trajectory (TSDT) for the selected link.

        This function retrieves the selected link and figure size from the UI elements.
        It then calls the `time_space_diagram_traj` method of the `analyzer` object in the `world`
        to visualize the TSDT.

        Args:
            self: The instance of the class.
        """
        link = self.tsdt_link_cobox.currentData()
        fig_size = (self.tsdt_figure_size_x_sbox.value(), self.tsdt_figure_size_y_sbox.value())

        self.world.analyzer.time_space_diagram_traj(links=link, figsize=fig_size)

        self.update_canvas(self.fig, self.ax)


    def show_sa(self):
        """
        Visualizes a simple animation of the network.

        This function retrieves various parameters from the UI elements, such as animation speed,
        detailed view, figure size, node size, network font size, and timestep skip. It then calls
        the `network_anim` method of the `analyzer` object in the `world` to visualize the animation.

        Args:
            self: The instance of the class.
        """
        animation_speed_inverse = int(self.sa_speed_inverse_sbox.value())
        detailed = 1 if self.sa_detailed_chbox.isChecked() else 0
        minwidth = float(0.5)
        maxwidth = float(8.0)
        left_handed = 1 if self.sa_left_handed_chbox.isChecked() else 0
        fig_size = (int(self.sa_figure_size_x_sbox.value()), int(self.sa_figure_size_y_sbox.value()))
        node_size = int(self.sa_node_size_sbox.value())
        network_font_size = int(self.sa_network_font_size_sbox.value())
        timestep_skip = int(self.sa_timestep_skip_sbox.value())

        self.world.analyzer.network_anim(animation_speed_inverse=animation_speed_inverse,
                                         detailed=detailed,
                                         minwidth=minwidth,
                                         maxwidth=maxwidth,
                                         left_handed=left_handed,
                                         figsize=fig_size,
                                         node_size=node_size,
                                         network_font_size=network_font_size,
                                         timestep_skip=timestep_skip)

        if detailed:
            self.show_gif_popup(f"./out{self.world.name}/anim_network1.gif")
        else:
            self.show_gif_popup(f"./out{self.world.name}/anim_network0.gif")

        self.update_canvas(self.fig, self.ax)

    def show_fa(self):
        """
        Visualizes a fancy animation of the network.

        This function retrieves various parameters from the UI elements, such as animation speed,
        figure size, sample ratio, interval, network font size, trace length, speed coefficient,
        and antialiasing. It then calls the `network_fancy` method of the `analyzer` object in the `world`
        to visualize the animation.

        Args:
            self: The instance of the class.
        """

        animation_speed_inverse = int(self.fa_speed_inverse_sbox.value())
        fig_size = int(self.fa_figure_size_sbox.value())
        sample_ratio = float(self.fa_sample_ratio_sbox.value())
        interval = int(self.fa_interval_sbox.value())
        network_font_size = int(self.fa_network_font_size_sbox.value())
        trace_length = int(self.fa_trace_length_sbox.value())
        speed_coef = int(self.fa_speed_coef_sbox.value())
        antialiasing = self.fa_antialiasing_chbox.isChecked()

        self.world.analyzer.network_fancy(animation_speed_inverse=animation_speed_inverse,
                                          figsize=fig_size,
                                          sample_ratio=sample_ratio,
                                          interval=interval,
                                          network_font_size=network_font_size,
                                          trace_length=trace_length,
                                          speed_coef=speed_coef,
                                          antialiasing=antialiasing)

        self.show_gif_popup(f"./out{self.world.name}/anim_network_fancy.gif")

        self.update_canvas(self.fig, self.ax)


    def show_gif_popup(self, gif_path):
        #TODO write docs
        dialog = QDialog(self)
        dialog.setWindowTitle("Simulation Animation")
        dialog.setMinimumSize(600, 400)

        gif_label = QLabel(dialog)
        gif_label.setScaledContents(True)

        movie = QMovie(gif_path)
        gif_label.setMovie(movie)
        movie.start()

        layout = QVBoxLayout()
        layout.addWidget(gif_label)
        dialog.setLayout(layout)

        dialog.exec()




if __name__ == "__main__":
    myappid = 'mycompany.myproduct.subproduct.version'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    osmnx.settings.use_cache = False
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
