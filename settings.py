import configparser, os, sys, glob, importlib

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
    this.tools_qgis = importlib.import_module('.tools_qgis', package=f'{this.giswater_folder}.lib')
    this.tools_qt = importlib.import_module('.tools_qt', package=f'{this.giswater_folder}.lib')
    this.tools_gw = importlib.import_module('.tools_gw', package=f'{this.giswater_folder}.core.utils')


def get_giswater_folder(filename_to_find='metadata.txt'):
    """ Find and return Giswater plugin folder name """

    # Get QGIS plugin root folder from environment variables
    qgis_plugin_root_folder = None
    try:
        if sys.platform == "win32":
            qgis_plugin_root_folder = os.environ['QGIS_PLUGINPATH']
        elif sys.platform == "linux":
            qgis_plugin_root_folder = os.environ['QGIS_PLUGINPATH']
        elif sys.platform == "darwin":
            qgis_plugin_root_folder = os.environ['QGIS_PLUGINPATH']
    except KeyError:
        # Key not found
        pass

    # Get QGIS plugin root folder from qgis plugin path
    if qgis_plugin_root_folder is None:
        qgis_plugin_root_folder = os.path.dirname(os.path.dirname(__file__))

    # Find @filename recursively inside this folder
    for filename in glob.glob(f"{qgis_plugin_root_folder}/**/{filename_to_find}", recursive=True):
        parser = configparser.ConfigParser()
        parser.read(filename)
        if not parser.has_section('general'): continue
        if not parser.has_option('general', 'name'): continue
        if parser['general']['name'] == 'giswater':
            giswater_folder_name = os.path.basename(os.path.dirname(filename))
            return giswater_folder_name

    return None


def init_global():

    print(f"init_global: {this.giswater_folder}")
    this.global_vars = importlib.import_module('.global_vars', package=f'{this.giswater_folder}')


