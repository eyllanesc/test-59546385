#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from PyQt5 import QtCore, QtWidgets, QtTest

import mock

import pytest
from pytestqt.plugin import QtBot, capture_exceptions


def get_messagebox(t=100, max_attemps=-1):
    messagebox = None
    attempt = 0
    loop = QtCore.QEventLoop()

    def on_timeout():
        nonlocal attempt, messagebox

        attempt += 1
        active_window = QtWidgets.QApplication.activeWindow()

        if isinstance(active_window, QtWidgets.QMessageBox):
            messagebox = active_window
            loop.quit()
        elif max_attemps > 0:
            if attempt > max_attemps:
                loop.quit()
        else:
            QtCore.QTimer.singleShot(t, on_timeout)

    QtCore.QTimer.singleShot(t, on_timeout)
    loop.exec_()
    return messagebox


@pytest.fixture(scope="module")
def Viewer(request):
    print("  SETUP GUI")
    GUI = __import__("GUI")
    app, imageViewer = GUI.main_GUI()
    with capture_exceptions():
        qtbotbis = QtBot(app)
        QtTest.QTest.qWait(0.5 * 1000)
        yield app, imageViewer, qtbotbis

        app.quitOnLastWindowClosed()

        def handle_dialog():
            messagebox = get_messagebox()
            yes_button = messagebox.button(QtWidgets.QMessageBox.Yes)
            qtbotbis.mouseClick(yes_button, QtCore.Qt.LeftButton, delay=1)

        QtCore.QTimer.singleShot(10, handle_dialog)
        qtbotbis.mouseClick(imageViewer.btn_quit, QtCore.Qt.LeftButton, delay=1)
        assert imageViewer.isHidden()

        app.closeAllWindows()
        app.quit()
        app.exit()
        app.closingDown()
        QtTest.QTest.qWait(0.5 * 1000)
        with mock.patch.object(QtWidgets.QApplication, "exit"):
            app.exit()
            assert QtWidgets.QApplication.exit.call_count == 1
            print("[Notice] So a mock.patch is used to count if the signal is emitted.")
        print("  TEARDOWN GUI")


class Test_GUI_CXS:
    def test_buttons(self, Viewer, caplog):
        app, mainWindow, qtbot = Viewer

        qtbot.mouseClick(mainWindow.btn_prt, QtCore.Qt.LeftButton)

