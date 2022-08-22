import flit_core.buildapi

def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    return flit_core.buildapi.build_wheel(wheel_directory, config_settings, metadata_directory)

def build_sdist(sdist_directory, config_settings=None):
    return flit_core.buildapi.build_sdist(sdist_directory, config_settings)

