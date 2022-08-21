import re

URL_VALIDATION_REGEX = re.compile(r"\A[\w.-]+(?:\.[\w\.-]+)+[\w\-\._%~:\/?#\[\]@!\$&'\(\)\*\+,;=.]+\Z")


class RegistryTypes:
    CNVRG = "cnvrg"
    INTEL = "intel"
    HABANA = "habana"
    DOCKERHUB = "dockerhub"
    NVIDIA = "nvidia"
    GCR = "gcr"
    ECR = "ecr"
    ACR = "acr"
    OTHER = "other"

    @classmethod
    def validate_type(cls, registry_type):
        if registry_type is None:
            return True

        registry_types = [cls.__dict__[var] for var in vars(cls) if not var.startswith("__")]
        return registry_type in registry_types
