from PySide6 import QtWidgets
from PySide6.QtGui import Qt


class TodaysTotalsTable(QtWidgets.QTableWidget):
    def __init__(self):
        super().__init__()

        self.horizontalHeader().setVisible(True)
        self.setShowGrid(True)

        # tag name, total
        self.setColumnCount(2)

        self.verticalHeader().setVisible(False)

    def update_times(self, totals: dict[str, int]):
        self.setRowCount(len(totals))
        self.setHorizontalHeaderLabels(["Tag", "Total"])

        for row_number, (tag_name, total) in enumerate(totals.items()):
            # Add tag
            tag_table_item = QtWidgets.QTableWidgetItem(tag_name)
            tag_table_item.setFlags(
                tag_table_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )
            self.setItem(row_number, 0, tag_table_item)

            # Add total
            time_table_item = QtWidgets.QTableWidgetItem(str(total))
            time_table_item.setFlags(
                time_table_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )
            time_table_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.setItem(row_number, 1, time_table_item)

        self.resizeRowsToContents()
        self.resizeColumnsToContents()

        # Ensure that we never need a vertical scrollbar
        self.setFixedHeight(self.__get_unconstrained_height())

        # Ensure there's no blank gaps within the frame
        self.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )

    def __get_unconstrained_height(self):
        row_total_height = sum(
            self.rowHeight(row_number) for row_number in range(self.rowCount())
        )

        return (
            self.horizontalHeader().height() + row_total_height + self.frameWidth() * 2
        )
