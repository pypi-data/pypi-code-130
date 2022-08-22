from click import group
from kubernetes import config

from sugarloaf_utilities.debug import bastion
from sugarloaf_utilities.deployment import update_image
from sugarloaf_utilities.secrets import secrets
from sugarloaf_utilities.terraform import chain_apply, chain_destroy


config.load_kube_config()

@group()
def main():
    pass

main.add_command(update_image)
main.add_command(bastion)
main.add_command(chain_apply, name="apply")
main.add_command(chain_destroy, name="destroy")
main.add_command(secrets)
