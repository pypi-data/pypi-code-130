from PyQt5 import QtWidgets, QtCore
from optimeed.visualize.graphs import Widget_graphsVisualLite
from optimeed.core import Graphs, Data, SHOW_WARNING, printIfShown, SHOW_INFO
from optimeed.visualize.widgets import Widget_listWithSearch


class Widget_SAChaosTuner(QtWidgets.QWidget):
    """Class to tune a OpenTURNS Chaos fit (in consolidate)."""
    def __init__(self):
        super().__init__()
        main_vertical_layout = QtWidgets.QVBoxLayout(self)
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)

        # Widget slider
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(10)
        self.slider.setValue(2)
        self.slider.valueChanged.connect(self.slider_changed)
        self.slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.slider.setTickInterval(1)

        self.label_degree = QtWidgets.QLabel("Order: NA")
        self.label_Q2 = QtWidgets.QLabel("Q2: {:.5f} %".format(1.0*100))

        self.button = QtWidgets.QPushButton("Copy")
        self.button.clicked.connect(self._copy_metamodel)

        horizontalLayout = QtWidgets.QHBoxLayout()
        horizontalLayout.addWidget(self.slider)
        horizontalLayout.addWidget(self.label_degree)
        horizontalLayout.addWidget(self.label_Q2)
        horizontalLayout.addWidget(self.button)

        main_vertical_layout.addLayout(horizontalLayout)

        theGraphs = Graphs()
        g1 = theGraphs.add_graph(updateChildren=False)
        self.data_ideal = Data([], [], x_label='model', y_label='metamodel', legend='Ideal', is_scattered=False)
        self.data_comparison = Data([], [], x_label='model', y_label='metamodel', legend='Predicted', is_scattered=True, symbolsize=5, outlinesymbol=1)
        theGraphs.add_trace(g1, self.data_ideal, updateChildren=False)
        theGraphs.add_trace(g1, self.data_comparison, updateChildren=False)

        self.wg_graphs = Widget_graphsVisualLite(theGraphs, refresh_time=-1)
        main_vertical_layout.addWidget(self.wg_graphs)

        self.updateMethods = set()

        self.SA_chaos = None
        self.theObjectives = None
        self.theSensitivityParameters = None
        self.add_update_method(self.wg_graphs.update_graphs)
        self.show()

    def _update_children(self):
        for updateMethod in self.updateMethods:
            updateMethod()

    def _copy_metamodel(self):
        theStr = self.SA_chaos.get_metamodel_as_python_method(self.theSensitivityParameters, self.theObjectives)
        cb = QtWidgets.QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(theStr, mode=cb.Clipboard)
        printIfShown("{}\nCopied to clipboard!".format(theStr), SHOW_INFO)

    def add_update_method(self, childObject):
        self.updateMethods.add(childObject)

    def set_SA(self, SA_chaos, theSensitivityParameters, theObjectives):
        """Set sensitivity analysis to fit.

        :param SA_chaos: SensitivityAnalysis_OpenTURNS_Chaos
        :param theSensitivityParameters: Sensitivity parameters used for the analysis
        :param theObjectives: Objectives to fit
        """
        self.SA_chaos = SA_chaos
        self.theSensitivityParameters = theSensitivityParameters
        self.theObjectives = theObjectives
        self.update()

    def slider_changed(self):
        self.SA_chaos.set_fit_degree(self.slider.value())
        self.update()

    def update(self):
        if self.SA_chaos is None:
            printIfShown("Please use method set_SA before!", SHOW_WARNING)
            return
        Q2, outputs_real, outputs_model = self.SA_chaos.check_goodness_of_fit(self.theSensitivityParameters, self.theObjectives)
        min_value = min(list(outputs_real) + list(outputs_model))
        max_value = max(list(outputs_real) + list(outputs_model))
        self.data_ideal.set_data([min_value, max_value], [min_value, max_value])
        self.data_comparison.set_data(outputs_real, outputs_model)
        self.label_Q2.setText("Q2: {:.5f} %".format(Q2*100))
        self.label_degree.setText("Order: {}".format(self.SA_chaos.degree_fitted))
        self._update_children()


class Widget_LiveChaosTuner(QtWidgets.QWidget):
    def __init__(self, theLiveChaos):
        super().__init__()
        main_vertical_layout = QtWidgets.QVBoxLayout(self)

        self.theLiveChaos = theLiveChaos

        self.listWithSearch = Widget_listWithSearch()
        self.SAChaosTuner = Widget_SAChaosTuner()

        self.theLiveChaos.add_update_method(self.update_available_attributes)
        self.listWithSearch.myListWidget.currentItemChanged.connect(self.update_tune_window)

        main_vertical_layout.addWidget(self.listWithSearch)
        main_vertical_layout.addWidget(self.SAChaosTuner)
        self.update_available_attributes()

    def update_available_attributes(self):
        self.listWithSearch.set_list(list(self.theLiveChaos.fitted_chaos.keys()))

    def update_tune_window(self):
        try:
            attribute_name = self.listWithSearch.get_name_selected()
        except AttributeError:
            return
        self.SAChaosTuner.set_SA(self.theLiveChaos.get_chaos(attribute_name), self.theLiveChaos.theSensitivityParameters, self.theLiveChaos.theCollection.get_list_attributes(attribute_name))
