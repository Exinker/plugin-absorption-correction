import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from itertools import chain
from pathlib import Path
from typing import Callable, NewType

import numpy as np
from PySide6 import QtCore, QtGui, QtWidgets
from matplotlib.backend_bases import KeyEvent, MouseEvent, PickEvent
from matplotlib.figure import Figure

import plugin
from plugin.dto import AtomDatum
from spectrumapp.configs import TELEGRAM_CONFIG
from spectrumapp.helpers import find_tab, find_window, getdefault_object_name
from spectrumapp.types import Lims
from spectrumapp.widgets.graph_widget import MplCanvas
from spectrumapp.windows.report_issue_window import ReportIssueWindow
from spectrumapp.windows.report_issue_window.archive_managers import ZipArchiveManager
from spectrumapp.windows.report_issue_window.archive_managers.utils import explore
from spectrumapp.windows.report_issue_window.report_managers import TelegramReportManager
from spectrumlab.picture.alphas import ALPHA
from spectrumlab.picture.colors import COLOR
from spectrumlab.types import Frame, R


Index = NewType('Index', str)

DEFAULT_SIZE = QtCore.QSize(640, 480)
DEFAULT_LIMS = ((0, 1), (0, 1))


@dataclass
class AxisLabel:
    xlabel: str
    ylabel: str


class BaseGraphWidget(QtWidgets.QWidget):

    def __init__(
        self,
        *args,
        object_name: str | None = None,
        size: QtCore.QSize = DEFAULT_SIZE,
        tight_layout: bool = True,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self._widget_size = size

        self._frame = None
        self._point_labels = None
        self._axis_labels = None
        self._point_annotation = None
        self._zoom_region = None
        self._full_lims = None
        self._cropped_lims = None

        # object name
        object_name = object_name or getdefault_object_name(self)
        self.setObjectName(object_name)

        # focus
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.setFocus()

        # layout and canvas
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.canvas = MplCanvas(
            tight_layout=tight_layout,
        )
        self.canvas.mpl_connect('pick_event', self._pick_event)
        self.canvas.mpl_connect('button_press_event', self._button_press_event)
        self.canvas.mpl_connect('button_release_event', self._button_release_event)
        self.canvas.mpl_connect('motion_notify_event', self._motion_notify_event)
        layout.addWidget(self.canvas)

        # pressed mouse and keys events
        self._mouse_event: MouseEvent | None = None
        self._ctrl_modified = False
        self._shift_modified = False

        # geometry
        self.setFixedSize(self._widget_size)

    @property
    def point_labels(self) -> Mapping[Index, tuple[str, ...]] | None:
        return self._point_labels

    @property
    def axis_labels(self) -> AxisLabel | None:
        return self._axis_labels

    @property
    def default_lims(self) -> Lims:
        return DEFAULT_LIMS

    @property
    def full_lims(self) -> Lims | None:
        return self._full_lims

    @property
    def cropped_lims(self) -> Lims | None:
        return self._cropped_lims

    @property
    def ctrl_modified(self) -> bool:
        return self._ctrl_modified

    @property
    def shift_modified(self) -> bool:
        return self._shift_modified

    def update(
        self,
        frame: AtomDatum,
    ) -> None:

        self._frame = frame.groupby(level=0, sort=False).mean().apply(lambda x: np.log10(x))

    def update_zoom(self, lims: Lims | None = None) -> None:
        """Update zoom to given `lims`."""

        xlim, ylim = lims or self.full_lims or self.default_lims

        self.canvas.axes.set_xlim(xlim)
        self.canvas.axes.set_ylim(ylim)
        self.canvas.draw_idle()

    def set_full_lims(self, lims: Lims) -> None:
        """Set full lims (maximum) to given `lims`."""

        if self._full_lims is None:
            self._full_lims = lims

    def set_cropped_lims(self, lims: Lims | None) -> None:
        """Set cropped lims to given `lims`."""

        self._cropped_lims = lims

    def set_shift_modified(self, __state: bool) -> None:
        self._shift_modified = __state

    def set_ctrl_modified(self, __state: bool) -> None:
        self._ctrl_modified = __state

    def sizeHint(self) -> QtCore.QSize:  # noqa: N802
        return self._widget_size

    def keyPressEvent(  # noqa: N802
        self,
        event: KeyEvent,
    ) -> None:

        match event.key():
            case QtCore.Qt.Key.Key_Control:
                self.set_ctrl_modified(True)
            case QtCore.Qt.Key.Key_Shift:
                self.set_shift_modified(True)
            case _:
                return None

    def keyReleaseEvent(  # noqa: N802
        self,
        event: KeyEvent,
    ) -> None:

        match event.key():
            case QtCore.Qt.Key.Key_Control:
                self.set_ctrl_modified(False)
            case QtCore.Qt.Key.Key_Shift:
                self.set_shift_modified(False)
            case _:
                return None

    def _pick_event(
        self,
        event: PickEvent,
    ) -> None:
        return None

    def _check_point(
        self,
        event: MouseEvent,
        epsilon: float = .05,
    ) -> bool:
        ax = self.figure.gca()

        condition = (np.abs((self._frame['concentration'] - np.log10(event.xdata))) < epsilon) & (np.abs((self._frame['intensity'] - np.log10(event.ydata))) < epsilon)
        matches = self._frame.index[condition]
        if len(matches) > 0:

            for match in matches:
                self._point_annotation = ax.text(
                    event.xdata, event.ydata,
                    match,
                    fontsize=10,
                    ha='center',
                    va='bottom',
                )
                self._point_annotation.set_in_layout(False)
            self.canvas.draw_idle()

    def _button_press_event(
        self,
        event: MouseEvent,
    ) -> None:
        self._mouse_event = event

        # update zoom and pan
        if self.ctrl_modified and self.shift_modified:
            return None

        if self.ctrl_modified:
            return None

        if self.shift_modified:
            return None

        if event.button == 2:
            if event.inaxes is not None:
                self._check_point(
                    event=event,
                )
        if event.button == 3 and event.dblclick:
            self._mouse_event = None
            self.set_cropped_lims(lims=None)
            self.update_zoom(lims=self.full_lims)

    def _button_release_event(
        self,
        event: MouseEvent,
    ) -> None:
        raise NotImplementedError

    def _motion_notify_event(
        self,
        event: MouseEvent,
    ) -> None:

        # update zoom and pan
        if self.ctrl_modified and self.shift_modified:
            return None

        if self.ctrl_modified:
            return None

        if self.shift_modified:
            if event.button == 1:
                self._pan_event(
                    self._mouse_event,
                    event,
                )
                return None

    def _zoom_event(
        self,
        press_event: MouseEvent | None,
        release_event: MouseEvent | None,
    ) -> None:

        if (press_event is None) or (release_event is None):
            return None
        if any(
            getattr(obj, attr) is None
            for obj in [press_event, release_event]
            for attr in ['xdata', 'ydata']
        ):
            return None

        # update full lims
        self.set_full_lims(
            lims=(
                self.canvas.axes.get_xlim(),
                self.canvas.axes.get_ylim(),
            ),
        )

        # update crop lims
        xlim = tuple(sorted(
            (event.xdata for event in (press_event, release_event)),
        ))
        ylim = tuple(sorted(
            (event.ydata for event in (press_event, release_event)),
        ))
        self.set_cropped_lims(
            lims=(xlim, ylim),
        )

        # update zoom
        self.update_zoom(
            lims=self.cropped_lims,
        )

    def _pan_event(
        self,
        press_event: MouseEvent | None,
        release_event: MouseEvent | None,
    ) -> None:

        if (press_event is None) or (release_event is None):
            return None
        if any(
            getattr(obj, attr) is None
            for obj in [press_event, release_event]
            for attr in ['xdata', 'ydata']
        ):
            return None

        # update crop lims
        xlim, ylim = self.canvas.axes.get_xlim(), self.canvas.axes.get_ylim()
        xshift, yshift = release_event.xdata - press_event.xdata, release_event.ydata - press_event.ydata
        self.set_cropped_lims(
            lims=(
                [value - xshift for value in xlim],
                [value - yshift for value in ylim],
            ),
        )

        # update zoom
        self.update_zoom(
            lims=self._cropped_lims,
        )

    @property
    def figure(self) -> Figure:
        return self.canvas.figure


class RetriverViewWidget(BaseGraphWidget):

    def __init__(self, column_id: str) -> None:
        super().__init__(size=QtCore.QSize(480, 480))

        self.column_id = column_id

        self._frame = None
        self._selection_start = None
        self._selection = None

    def update(
        self,
        frame: AtomDatum,
        bounds: tuple[R, R] | None,
    ) -> None:
        super().update(frame=frame)

        ax = self.figure.gca()
        ax.clear()

        x = frame['concentration']
        y = frame['intensity']
        ax.scatter(
            x, y,
            s=20,
            marker='s',
            facecolors='none',
            edgecolors=[0, 0, 0, 0],
            alpha=ALPHA['parallel'],
        )
        x = frame['concentration'].groupby(level=0, sort=False).mean()
        y = frame['intensity'].groupby(level=0, sort=False).mean()
        ax.scatter(
            x, y,
            s=40,
            marker='s',
            facecolors=COLOR['green'],
            edgecolors=COLOR['green'],
            alpha=.5,
            label='recorded',
        )

        x = frame['concentration']
        y = frame['intensity_linearized']
        ax.scatter(
            x, y,
            s=20,
            marker='s',
            facecolors='none',
            edgecolors=[0, 0, 0, 0],
            alpha=ALPHA['parallel'],
        )
        x = frame['concentration'].groupby(level=0, sort=False).mean()
        y = frame['intensity_linearized'].groupby(level=0, sort=False).mean()
        ax.scatter(
            x, y,
            s=40,
            marker='s',
            facecolors=COLOR['red'],
            edgecolors=COLOR['red'],
            alpha=.5,
            label='recorded',
        )

        x, y = frame['concentration'], frame['intensity_true']
        ax.plot(
            x, y,
            color='black', linestyle=':',
            alpha=.5,
        )

        if bounds is not None:
            lb, ub = bounds
            ax.axhspan(
                lb, ub,
                alpha=.125, color=COLOR['red'],
            )

        ax.set_xscale('log')
        ax.set_yscale('log')

        ax.set_xlabel('$\log_{10}{C}$')
        ax.set_ylabel('$\log_{10}{R}$')
        ax.grid(True, color='grey', linestyle=':')

        self.canvas.draw_idle()

    def _button_press_event(
        self,
        event: MouseEvent,
    ) -> None:
        super()._button_press_event(event=event)

        if self.ctrl_modified and self.shift_modified:
            return None

        if self.ctrl_modified:
            return None

        if self.shift_modified:
            return None

        if event.button == 1:
            ax = self.figure.gca()

            self._selection_start = event.ydata
            self._selection = ax.axhspan(
                event.ydata, event.ydata,
                alpha=.125, color=COLOR['red'],
                visible=True,
            )
            self.canvas.draw_idle()

    def _motion_notify_event(
        self,
        event: MouseEvent,
    ) -> None:
        super()._motion_notify_event(event=event)

        if event.button == 1:
            if self._selection_start is not None:
                y_min = min(self._selection_start, event.ydata)
                y_max = max(self._selection_start, event.ydata)

                self._selection.set_bounds(0, y_min, 1, y_max - y_min)
                self.canvas.draw_idle()

    def _button_release_event(
        self,
        event: MouseEvent,
    ) -> None:

        # update annotate
        if self._point_annotation:
            self._point_annotation.set_visible(False)
            self.canvas.draw_idle()

        # update zoom and pan
        if self.ctrl_modified and self.shift_modified:
            return None

        if self.ctrl_modified:
            return None

        if self.shift_modified:
            if event.button == 1:
                self._pan_event(
                    self._mouse_event,
                    event,
                )
            return None

        if event.button == 1:
            self._selection_start = None
            self._selection = None

            self._select_event(
                self._mouse_event,
                event,
            )
        if event.button == 3:
            self._zoom_event(
                self._mouse_event,
                event,
            )

    def _select_event(
        self,
        press_event: MouseEvent | None,
        release_event: MouseEvent | None,
    ) -> None:

        if (press_event is None) or (release_event is None):
            return None
        if any(
            getattr(obj, attr) is None
            for obj in [press_event, release_event]
            for attr in ['xdata', 'ydata']
        ):
            return None

        # update zoom
        bounds = tuple(sorted([press_event.ydata, release_event.ydata]))

        self.parent().parent().parent().parent().update(
            column_id=self.column_id,
            bounds=bounds,
        )


class ResidualViewWidget(BaseGraphWidget):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, size=QtCore.QSize(480, 480), **kwargs)

    def _button_release_event(
        self,
        event: MouseEvent,
    ) -> None:

        # update annotate
        if self._point_annotation:
            self._point_annotation.set_visible(False)
            self.canvas.draw_idle()

        # update zoom and pan
        if self.ctrl_modified and self.shift_modified:
            return None

        if self.ctrl_modified:
            return None

        if self.shift_modified:
            if event.button == 1:
                self._pan_event(
                    self._mouse_event,
                    event,
                )
            return None

        if event.button == 3:
            self._zoom_event(
                self._mouse_event,
                event,
            )

    def update(
        self,
        frame: Frame,
    ) -> None:
        super().update(frame=frame)

        ax = self.figure.gca()
        ax.clear()

        x = frame['concentration']
        y = 100 * (frame['intensity'] - frame['intensity_true']) / frame['intensity_true']
        ax.scatter(
            x, y,
            s=20,
            marker='s',
            facecolors='none',
            edgecolors=[0, 0, 0, 0],
            alpha=ALPHA['parallel'],
        )
        x = frame['concentration'].groupby(level=0, sort=False).mean()
        y = 100 * (frame['intensity'].groupby(level=0, sort=False).mean() - frame['intensity_true'].groupby(level=0, sort=False).mean()) / frame['intensity_true'].groupby(level=0, sort=False).mean()
        ax.scatter(
            x, y,
            s=40,
            marker='s',
            facecolors=COLOR['green'],
            edgecolors=COLOR['green'],
            alpha=.5,
            label='recorded',
        )

        x = frame['concentration']
        y = 100 * (frame['intensity_linearized'] - frame['intensity_true']) / frame['intensity_true']
        ax.scatter(
            x, y,
            s=20,
            marker='s',
            facecolors='none',
            edgecolors=[0, 0, 0, 0],
            alpha=ALPHA['parallel'],
        )
        x = frame['concentration'].groupby(level=0, sort=False).mean()
        y = 100 * (frame['intensity_linearized'].groupby(level=0, sort=False).mean() - frame['intensity_true'].groupby(level=0, sort=False).mean()) / frame['intensity_true'].groupby(level=0, sort=False).mean()
        ax.scatter(
            x, y,
            s=40,
            marker='s',
            facecolors='red',
            edgecolors='red',
            alpha=.5,
            label='recorded',
        )

        ax.set_ylim([-100, +100])  # FIXME: add env

        ax.set_xscale('log')

        ax.set_xlabel('$\log_{10}{C}$')
        ax.set_ylabel('Систематическая погрешность, $\%$')
        ax.grid(True, color='grey', linestyle=':')

        self.canvas.draw_idle()


class TabWidget(QtWidgets.QWidget):

    def __init__(self, *args, column_id: str, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.retriver_view_widget = RetriverViewWidget(
            column_id=column_id,
        )
        layout.addWidget(self.retriver_view_widget)

        self.residual_view_widget = ResidualViewWidget()
        layout.addWidget(self.residual_view_widget)

    def update(
        self,
        frame: Frame,
        bounds: tuple[R, R] | None,
    ) -> None:

        self.retriver_view_widget.update(
            frame=frame,
            bounds=bounds,
        )
        self.residual_view_widget.update(
            frame=frame,
        )


class ContentWidget(QtWidgets.QTabWidget):

    def __init__(self, *args, column_ids: Sequence[str], nicknames: Sequence[str], **kwargs) -> None:
        super().__init__(*args, **kwargs)

        for column_id, nickname in zip(column_ids, nicknames):
            self.addTab(TabWidget(column_id=column_id), nickname)


class PreviewWindow(QtWidgets.QWidget):

    def __init__(
        self,
        *args,
        data: Mapping[str, AtomDatum],
        update_callback: Callable[[tuple[R, R], Frame], Frame],
        dump_callback: Callable[[], None],
        flags: Mapping[QtCore.Qt.WindowType, bool] | None = None,
        **kwargs,
    ) -> None:
        super().__init__()

        self._data = data
        self._update_callback = update_callback
        self._dump_callback = dump_callback

        self.setObjectName('previewWindow')

        # title
        self.setWindowTitle(' '.join(map(lambda x: x.capitalize(), plugin.__name__.split('-'))))

        # actions
        action = QtGui.QAction('&Save', self)
        action.setShortcut(QtGui.QKeySequence('Ctrl+S'))
        action.setShortcutContext(QtCore.Qt.ApplicationShortcut)
        action.triggered.connect(self.on_saved)
        self.addAction(action)

        action = QtGui.QAction('&Report Issue', self)
        action.setShortcut(QtGui.QKeySequence('Ctrl+Shift+I'))
        action.setShortcutContext(QtCore.Qt.ApplicationShortcut)
        action.triggered.connect(self.on_report_issue_window_opened)
        self.addAction(action)

        # flags
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.CustomizeWindowHint)

        flags = flags or {
            # QtCore.Qt.WindowType.WindowStaysOnTopHint: False,
            # QtCore.Qt.WindowType.WindowCloseButtonHint: False,
            QtCore.Qt.WindowType.Window: True,
        }
        for key, value in flags.items():
            self.setWindowFlag(key, value)

        # style
        filepath = Path().resolve() / 'static' / 'view-window.css'
        if os.path.exists(filepath):
            style = open(filepath, 'r').read()
            self.setStyleSheet(style)

        # icon
        filepath = Path().resolve() / 'static' / 'icon.ico'
        if os.path.exists(filepath):
            icon = QtGui.QIcon(str(filepath))
            self.setWindowIcon(icon)

        # layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.content_widget = ContentWidget(
            column_ids=[
                datum.column_id
                for datum in data.values()
            ],
            nicknames=[
                datum.nickname
                for datum in data.values()
            ],
        )
        layout.addWidget(self.content_widget)

        # geometry
        self.setFixedSize(self.sizeHint())

        # show window
        self.show()

    def on_saved(self, *args, **kwargs):
        """Save a dump."""

        self._dump_callback()

    def on_report_issue_window_opened(self, *args, **kwargs):
        """Report an issue."""

        # dump
        self.on_saved()

        # window
        window = find_window('reportIssueWindow')
        if window is not None:
            window.show()
        else:

            timestamp = datetime.timestamp(datetime.now())
            window = ReportIssueWindow(
                application_name=plugin.__name__,
                application_version=plugin.__version__,
                timestamp=timestamp,
                archive_manager=ZipArchiveManager(
                    files=chain(
                        explore([
                            Path.cwd() / '.env',
                            Path.cwd() / '.log',
                            Path.cwd() / 'pyproject.toml',
                            Path.cwd() / 'results.xml',
                            Path.cwd() / 'uv.lock',
                        ], prefix=Path.cwd()),
                        explore([
                            Path.cwd().parents[2] / 'Temp' / 'py_table.xml',
                        ], prefix=Path.cwd().parents[2] / 'Temp'),
                    ),
                    archive_name='{}'.format(int(timestamp)),
                ),
                report_manager=TelegramReportManager.create(
                    application_name=plugin.__name__,
                    application_version=plugin.__version__,
                    timestamp=timestamp,
                    token=TELEGRAM_CONFIG.token.get_secret_value(),
                    chat_id=TELEGRAM_CONFIG.chat_id,
                ),
                parent=self,
                flags=QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint,
            )

    def update(
        self,
        column_id: int,
        bounds: tuple[R, R] | None,
    ) -> None:
        datum = self._data[column_id]
        bounds, frame = self._update_callback(
            column_id=column_id,
            frame=datum.frame,
            bounds=bounds,
        )

        widget = find_tab(self.content_widget, text=datum.nickname)
        widget.update(
            frame=frame,
            bounds=bounds,
        )

    def closeEvent(self, event):  # noqa: N802

        self.setParent(None)
        event.accept()
