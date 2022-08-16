import yaml

from rule.rules.chain import ChainRule
from rule.rules.file import DownloadRule, FolderRule, FileRule, GlobRule, PathRule
from rule.rules.function import FunctionRule, RunRule
from rule.rules.get_item import GetItemRule
from rule.rules.image import ImageRule, ImageBuildRule, ImageTagRule
from rule.rules.string import MustacheRule
from rule.rules.reference import ReferenceRule


RULES = [
    ChainRule, DownloadRule, GetItemRule, FolderRule, FileRule, GlobRule, FunctionRule, ImageRule, ImageBuildRule, ImageTagRule, MustacheRule, PathRule,
    ReferenceRule, RunRule]


def build_loader(root_path, global_vars=None, host_root_path=None):
    class RuleLoader(yaml.SafeLoader):
        global_vars = {}

    if global_vars is not None:
        RuleLoader.global_vars = global_vars

    for rule in RULES:
        rule.register_constructor(RuleLoader, root_path, host_root_path=host_root_path)

    return RuleLoader
