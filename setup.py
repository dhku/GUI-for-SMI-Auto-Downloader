import sys
import os
import platform
from cx_Freeze import setup, Executable

# ADD FILES
files = ['icon.ico', 'themes/', 'anime.yml', 'settings.yml', 'downloads/', 'log']

# ADD PACKAGE
build_exe_options = {
    "excludes": [
        "tkinter", "matplotlib",
        # 불필요한 Qt 모듈 (프로젝트는 QtCore, QtGui, QtWidgets만 사용)
        "PySide6.QtPdf", "PySide6.QtPdfWidgets",
        "PySide6.QtQuick", "PySide6.QtQuickWidgets", "PySide6.QtQuick3D",
        "PySide6.QtQml", "PySide6.QtQmlModels",
        "PySide6.QtQmlMeta", "PySide6.QtQmlWorkerScript",
        "PySide6.QtVirtualKeyboard",
        "PySide6.QtOpenGL", "PySide6.QtOpenGLWidgets",
        "PySide6.QtDBus",
        "PySide6.QtSvg", "PySide6.QtSvgWidgets",
        "PySide6.QtMultimedia", "PySide6.QtMultimediaWidgets",
        "PySide6.QtBluetooth",
        "PySide6.QtNfc",
        "PySide6.QtPositioning",
        "PySide6.QtLocation",
        "PySide6.QtSensors",
        "PySide6.QtSerialPort", "PySide6.QtSerialBus",
        "PySide6.QtWebEngine", "PySide6.QtWebEngineCore",
        "PySide6.QtWebEngineWidgets",
        "PySide6.QtWebChannel", "PySide6.QtWebSockets",
        "PySide6.QtRemoteObjects",
        "PySide6.QtSql",
        "PySide6.QtTest",
        "PySide6.QtXml",
        "PySide6.QtDesigner",
        "PySide6.QtHelp",
        "PySide6.QtCharts",
        "PySide6.QtDataVisualization",
        "PySide6.QtStateMachine",
        "PySide6.QtScxml",
        "PySide6.Qt3DCore", "PySide6.Qt3DRender",
        "PySide6.Qt3DInput", "PySide6.Qt3DLogic",
        "PySide6.Qt3DAnimation", "PySide6.Qt3DExtras",
        "PySide6.QtNetworkAuth",
        "PySide6.QtHttpServer",
        "PySide6.QtConcurrent",
        "PySide6.QtTextToSpeech",
        "PySide6.QtSpatialAudio",
        "PySide6.QtAsyncio",
        # 불필요한 표준 라이브러리
        "unittest", "test", "email", "http.server",
        "xmlrpc", "pydoc", "doctest",
        "sqlite3", "difflib",
        "lib2to3", "ensurepip", "venv",
        "idlelib", "distutils",
        "curses", "dbm", "ftplib", "imaplib",
        "mailbox", "nntplib", "poplib", "smtplib",
        "telnetlib", "turtle", "turtledemo",
        "antigravity", "this",
        # 빌드 로그에서 확인된 불필요한 optional 의존성
        "IPython", "ipywidgets",
        "OpenSSL", "cryptography",
        "brotli", "brotlicffi",
        "backports.zstd", "compression",
        "h2",
        "html5lib",
        "lxml",
        "pandas",
        "colorama",
        "simplejson",
        "socks",
        "cchardet", "chardet",
        "setuptools_scm", "setuptools", "pkg_resources",
        "annotationlib",
        "fastnumbers", "icu",
        "pyodide", "js",
    ],
    "include_files": files,
    "optimize": 2,
    "zip_include_packages": ["*"],
    "zip_exclude_packages": ["PySide6", "certifi"]
}

# TARGET (플랫폼별 분기)
if platform.system() == "Windows":
    base = "Win32GUI"
    target_name = "SMI-Auto-Downloader.exe"
    icon = "icon.ico"
else:
    base = None
    target_name = "SMI-Auto-Downloader"
    icon = "icon.ico"

target = Executable(
    script="main.py",
    base=base,
    icon=icon,
    target_name=target_name
)

# macOS .app 번들 옵션 (콘솔 창 없이 실행)
bdist_mac_options = {
    "bundle_name": "SMI-Auto-Downloader",
    "iconfile": "icon.ico",
}

# SETUP CX FREEZE
setup(
    name="SMI-AUTO-DOWNLOADER",
    version="1.0",
    description="SMI-AUTO-DOWNLOADER",
    author="KUDONG",
    options={
        'build_exe': build_exe_options,
        'bdist_mac': bdist_mac_options,
    },
    executables=[target]
)
