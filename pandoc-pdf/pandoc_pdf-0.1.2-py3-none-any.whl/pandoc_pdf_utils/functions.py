from .env import CONFIG_DIR, CACHE_DIR, DEFAULT_CONFIG_DIR
import yaml
from pathlib import Path
import shutil


def _touch_files(key: str, obj: dict) -> None:
    if key in obj:
        values: dict[str] = []
        for filepath_i in [value_i.split('/') for value_i in obj[key]]:
            if filepath_i[0] == r'${.}':
                values.append('/'.join(filepath_i[1:]))
            else:
                continue
        for filepath_i in values:
            filepath_i = CONFIG_DIR / filepath_i
            if not filepath_i.exists():
                filepath_i.touch()
                with open(Path(__file__).parent / 'default_config' / filepath_i.name) as f:
                    content_raw = f.read()
                filepath_i.write_text(content_raw)
            shutil.copy(CONFIG_DIR / filepath_i, CACHE_DIR / filepath_i)


def init_config() -> None:
    """genegete default config files to CACHE_DIR and CONFIG_DIR if the cofig files don't exist.
    """
    if not CONFIG_DIR.exists():
        shutil.copytree(DEFAULT_CONFIG_DIR, CONFIG_DIR, dirs_exist_ok=False)
    # for dir_i in [CACHE_DIR, CONFIG_DIR]:
    #     if not dir_i.exists():
    #         dir_i.mkdir()
    # for file_name in ['setting.yml', 'defaults.yml']:
    #     config_file_path = (CONFIG_DIR / file_name)
    #     if not config_file_path.exists():
    #         config_file_path.touch()
    #         with open(Path(__file__).parent / 'default_config' / file_name) as f:
    #             content_raw = f.read()
    #             content_obj = yaml.safe_load(content_raw)
    #         config_file_path.write_text(content_raw)
    #         del content_raw
    #         if file_name == 'defaults.yml':
    #             _touch_files('include-in-header', content_obj[preset_i])
    # del file_name


# TODO: CONFIG_DIRフォルダを、CONFIG_DIRに再帰コピーする。
def init_cache() -> None:
    """Copy the CONFIG_DIR folder to CONFIG_DIR recursively. Generate the defaults_{preset}.yml separeted by preset.
    """
    if not CACHE_DIR.exists():
        CACHE_DIR.mkdir()
    shutil.copytree(CONFIG_DIR, CACHE_DIR, dirs_exist_ok=True)
    with open(CONFIG_DIR / 'defaults.yml') as f:
        defaults_obj: dict = yaml.safe_load(f)
    for preset_i in defaults_obj:
        defaults_by_preset: Path = CACHE_DIR / f'defaults_{preset_i}.yml'
        if not defaults_by_preset.exists():
            defaults_by_preset.touch()
        with open(defaults_by_preset, 'w') as f:
            yaml.dump(defaults_obj[preset_i], f,
                      encoding='utf-8', allow_unicode=True)
        # _touch_files('include-in-header', defaults_obj[preset_i])
        # _touch_files('filters', defaults_obj[preset_i])


def init_setting(opt_docker, opt_volumes) -> dict:
    """Load setting.yml and apply the command's options to the loaded object.

    Args:
        opt_docker (str): docker image name
        opt_volumes (str): the volume to mount to docker container

    Returns:
        dict: ~/.config/setting.yml object
    """
    setting_file_path = CONFIG_DIR / 'setting.yml'
    with open(setting_file_path, 'r') as f:
        setting_obj = yaml.safe_load(f)

    setting_obj['docker'].setdefault('volumes', [])
    setting_obj['docker'].setdefault('other_option', "")
    if opt_docker:
        setting_obj['docker']['use_docker'] = True
        setting_obj['docker']['docker_image'] = opt_docker
    if opt_volumes:
        if opt_docker:
            setting_obj['docker']['volumes'] = opt_volumes
        else:
            setting_obj['docker']['volumes'].extend(opt_volumes)

    return setting_obj


def generate_command_docker(setting_obj) -> list[str]:
    """Generate docker commands from the given settings.

    Args:
        setting_obj (dict): Object of pandoc_pdf command settings (~/.config/setting.yml)

    Returns:
        list[str]: docker command with arguments
    """
    setting_obj['docker'].setdefault('volumes', [])
    setting_obj['docker'].setdefault('other_option', "")
    args_docker = ['docker', 'run', '--rm', '--volume',
                   f'{CACHE_DIR}:/cache', '--entrypoint', '/bin/bash']
    if setting_obj['docker']['use_docker'] == True:
        for volume_i in setting_obj['docker']['volumes']:
            args_docker.extend(['--volume', volume_i])
        args_docker.append(setting_obj['docker']['other_option'])
        args_docker.append(setting_obj['docker']['docker_image'])
        args_docker.append('-c')
    else:
        args_docker = []
    return args_docker


def generate_command_pandoc(setting_obj, defaults_file, input_file, output_file, opt_preset, opt_variables, opt_metadatas) -> list[str]:
    """Generate pandoc commands from the given defaults_file's object and options of pandoc_pdf command.

    Args:
        setting_obj (dict): Object of pandoc_pdf command settings.
        defaults_file (Path): Path to the pandoc defaults file (defaults.yml) generated for each preset.
        input_file (Path): Path to the file to be converted to PDF, given as an argument to the pandoc_pdf command.
        output_file (Path): Path of the file to output to. Value of --output option.
        opt_preset (str): Preset name to be used. By default, html5 and latex are set.
        opt_variables (str): Arguments for LaTeX files.
        opt_metadatas (str): A set of keys and values to be registered as metadata.

    Returns:
        list[str]: pandoc command with arguments
    """
    args_pandoc = ['pandoc', str(input_file), '-t', opt_preset, '-o',
                   str(output_file), '-d', str(defaults_file)]
    for variable in opt_variables:
        args_pandoc.extend(['-V', variable])
    for metadata in opt_metadatas:
        args_pandoc.extend(['-M', metadata])
    return args_pandoc
