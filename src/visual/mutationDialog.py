import logging
from collections.abc import Sequence

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QDialog, QListWidget, QListWidgetItem

from ..compui.mutation_widget import Ui_MutationWidget
from ..mutations import MutationRequest


def make_feature_item(name: str) -> QListWidgetItem:
    item = QListWidgetItem(name)
    item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
    item.setCheckState(Qt.CheckState.Unchecked)
    return item


def checked_rows(list_widget: QListWidget) -> tuple[int, ...]:
    items = (list_widget.item(row) for row in range(list_widget.count()))
    return tuple(
        row
        for row, item in enumerate(items)
        if item is not None and item.checkState() == Qt.CheckState.Checked
    )


class MutationDialog(QDialog):
    mutations_submitted = pyqtSignal(object)

    def __init__(
        self,
        /,
        features: Sequence[str] | None = None,
        minimal: list[float] | float | None = None,
    ):
        super().__init__()
        if not features:
            logging.error("Features cant be empty")
            raise ValueError("Features cant be empty")

        self.ui = Ui_MutationWidget()
        self.ui.setupUi(self)

        self.ui.featuresListWidget.clear()
        for name in features:
            self.ui.featuresListWidget.addItem(make_feature_item(name))
        if isinstance(minimal, list):
            self.minimal = min(minimal)
        elif minimal is not None:
            self.minimal = minimal
        else:
            self.minimal = 0

        if self.minimal < 0:
            self.minimal *= -1
        else:
            self.minimal = 0
        self.ui.additionSpinBox.setRange(-1_000_000, 1_000_000)
        self.ui.additionSpinBox.setValue(self.minimal)
        self.ui.multiplicationSpinBox.setRange(-1_000_000, 1_000_000)
        self.ui.multiplicationSpinBox.setValue(1)

        self.ui.featuresListWidget.itemChanged.connect(self.update_apply_state)
        for check_box in (
            self.ui.additioncCheckBox,
            self.ui.multiplicationCheckBox,
            self.ui.lnCheckBox,
        ):
            check_box.toggled.connect(self.update_apply_state)

        self.ui.applyButton.clicked.connect(self.submit_data)
        self.ui.cancelButton.clicked.connect(self.reject)

        self.update_apply_state()

    def collect_request(self) -> MutationRequest:
        ui = self.ui
        return MutationRequest(
            features=checked_rows(ui.featuresListWidget),
            addition=(
                float(ui.additionSpinBox.value())
                if ui.additioncCheckBox.isChecked()
                else None
            ),
            multiplication=(
                float(ui.multiplicationSpinBox.value())
                if ui.multiplicationCheckBox.isChecked()
                else None
            ),
            apply_ln=ui.lnCheckBox.isChecked(),
        )

    def update_apply_state(self, *_):
        request = self.collect_request()
        self.ui.applyButton.setEnabled(bool(request.features) and request.has_mutations)

    def submit_data(self):
        request = self.collect_request()
        if not request.features or not request.has_mutations:
            return

        self.mutations_submitted.emit(request)
        self.accept()
