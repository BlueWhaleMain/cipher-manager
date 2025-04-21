import json
import logging
import re

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt6.QtWidgets import QWidget
from markdown import markdown

import gui
from gui.common.env import report_with_exception
from gui.designer.check_for_updates_form import Ui_check_for_updates_form

_LOG = logging.getLogger(__name__)
_EMOJI_PATTERN = re.compile(r'(<img alt=")(.)(.+" />)')


class CheckForUpdatesForm(QWidget, Ui_check_for_updates_form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.check_for_update_push_button.clicked.connect(self._check_for_updates)
        self.open_url_push_button.clicked.connect(self._open_url_push_button)
        self.browser_download_push_button.clicked.connect(self._browser_download)
        self._nam: QNetworkAccessManager = QNetworkAccessManager(self)
        self._nam.finished.connect(self._check_for_updates_finished)
        self._browser_download_url: str | None = None

    @report_with_exception
    def _check_for_updates(self, _):
        self.check_for_update_push_button.setEnabled(False)
        if self.pre_release_check_box.isChecked():
            self._nam.get(QNetworkRequest(QUrl('https://api.github.com/repos/BlueWhaleMain/cipher-manager/releases')))
            return
        self._nam.get(QNetworkRequest(QUrl(
            'https://api.github.com/repos/BlueWhaleMain/cipher-manager/releases/latest')))

    @report_with_exception
    def _open_url_push_button(self, _):
        if self.pre_release_check_box.isChecked():
            QDesktopServices.openUrl(QUrl('https://github.com/BlueWhaleMain/cipher-manager/releases'))
            return
        QDesktopServices.openUrl(QUrl('https://github.com/BlueWhaleMain/cipher-manager/releases/latest'))

    @report_with_exception
    def _browser_download(self, _):
        if self._browser_download_url is None:
            return
        QDesktopServices.openUrl(QUrl(self._browser_download_url))

    @report_with_exception
    def _check_for_updates_finished(self, reply: QNetworkReply):
        data = self._load_json(reply.readAll().data())
        if isinstance(data, list) and len(data) > 0:
            data = data[0]
        try:
            # 替换不受支持的html标签，直接显示Unicode Emoji
            self.update_details_text_browser.setHtml(
                _EMOJI_PATTERN.sub(r'\2', markdown(data['body'], extensions=['extra', 'py''m''down''x.emoji'])))
            self._browser_download_url = data['assets'][0]['browser_download_url']
            name, ver, *_ = data['tag_name'].split('-')
            if name == 'CipherManagerGUI':
                if ver > gui.__version__:
                    self.setWindowTitle(self.tr('*发现新版本 - {}').format(data['published_at']))
                    self.browser_download_push_button.setEnabled(True)
                    return
                self.setWindowTitle(self.tr('当前已经是最新版本'))
            self.browser_download_push_button.setEnabled(False)
        finally:
            self.check_for_update_push_button.setEnabled(True)

    @classmethod
    def _load_json(cls, data: bytes) -> dict:
        _LOG.debug(data)
        return json.loads(data)
