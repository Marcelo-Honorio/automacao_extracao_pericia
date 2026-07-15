from PyInstaller.utils.hooks import collect_submodules

hiddenimports = []

# Bibliotecas que às vezes precisam ser forçadas no PyInstaller
hiddenimports += collect_submodules("pandas")
hiddenimports += collect_submodules("openpyxl")
hiddenimports += collect_submodules("docxtpl")
hiddenimports += collect_submodules("docx")
hiddenimports += collect_submodules("jinja2")

datas = [
    ("laudo/templates", "laudo/templates"),
    ("indices/dados/bcb", "indices/dados/bcb"),
    ("extrator/regras/regras.yaml", "extrator/regras"),
    ("assets/auto_pericia.ico", "assets")
]

a = Analysis(
    ["app.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None,
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="AutoPericia",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/auto_pericia.ico",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="AutoPericia",
)