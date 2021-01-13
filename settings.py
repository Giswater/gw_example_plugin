import os, sys, glob, importlib

# Pointer to the module object instance itself
this = sys.modules[__name__]

# we can explicitly make assignments on it
this.giswater_folder = None
this.global_vars = None
this.tools_qgis = None
this.tools_qt = None
this.tools_gw = None


def init_plugin():

    if this.giswater_folder is not None:
        print("Variable giswater_folder already set")
        return

    this.giswater_folder = get_giswater_folder()
    if this.giswater_folder is None:
        print("Giswater plugin folder not found")
        return

    # Define imports to Giswater modules
    this.tools_qgis = importlib.import_module('.tools_qgis', package=f'{giswater_folder}.lib')
    this.tools_qt = importlib.import_module('.tools_qt', package=f'{giswater_folder}.lib')
    this.tools_gw = importlib.import_module('.tools_gw', package=f'{giswater_folder}.core.utils')


def get_giswater_folder(filename_to_find='tools_qgis.py'):
    """ Find and return Giswater plugin folder name """

    # Get QGIS plugin root folder
    qgis_plugin_root_folder = os.path.dirname(os.path.dirname(__file__))

    # Find @filename recursively inside this folder
    for filename in glob.glob(f"{qgis_plugin_root_folder}/**/{filename_to_find}", recursive=True):
        giswater_folder_name = os.path.basename(os.path.dirname(os.path.dirname(filename)))
        print(f"giswater_folder_name: {giswater_folder_name}")
        return giswater_folder_name

    return None


def init_global():

    print(f"init_global: {this.giswater_folder}")
    this.global_vars = importlib.import_module('.global_vars', package=f'{this.giswater_folder}')
