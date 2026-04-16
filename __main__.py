# -*- coding: utf-8 -*-
"""
@author: Grace Iroagalachi
"""

from periodicTable import PeriodicTable
import sys
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PeriodicTable()
    window.show()
    #sys.exit(app.exec_())

