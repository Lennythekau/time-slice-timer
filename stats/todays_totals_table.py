from PySide6 import QtWidgets
from PySide6.QtGui import Qt

from db.repository import Repository


class TodaysTotalsTable(QtWidgets.QTableWidget):

    def __init__(self, repo: Repository):
        self.__repo = repo

        super().__init__()
        self.__make_ui()
        self.__update_times()

        self.__repo.time_slice_added += lambda _: self.__update_times()
        self.__repo.tags_changed += lambda _: self.__update_times()

    def __make_ui(self):
        self.horizontalHeader().setVisible(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # tag name, total
        self.setColumnCount(2)
        self.verticalHeader().setVisible(False)

    def __update_times(self):
        times = self.__repo.get_times_by_tag()
        self.setRowCount(len(times))
        self.setHorizontalHeaderLabels(["Tag", "Total"])

        for row_number, (tag, total) in enumerate(times):
            # Add tag
            tag_table_item = QtWidgets.QTableWidgetItem(tag.name)
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
