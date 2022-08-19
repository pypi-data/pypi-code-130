from .set_tf_config import set_dist_train_config
from kfp.v2.dsl import component
from typing import Optional

def distmm_train_component(func: Optional[Callable] = None,
                           *,
                           rank: Optional[int] = 0,
                           nranks: Optional[int] = 1,
                           base_image: Optional[str] = None,
                           target_image: Optional[str] = None,
                           packages_to_install: List[str] = None,
                           pip_index_urls: Optional[List[str]] = None,
                           output_component_file: Optional[str] = None,
                           install_kfp_package: bool = True,
                           kfp_package_path: Optional[str] = None):
    '''
    configure TF_CONFIG env so that the pipeline component is recognized as
    an distribued multi-worker mirrored training step.
    '''
    step_name = getattr(func, '__name__', repr(func))

    class _Inner:
        __name__ = step_name
        def __call__(*args, **kwargs):
            print("step template name: %s" % step_name)
            set_dist_train_config(rank, nranks, step_name)
            func(*args, **kwargs)

    return component(_Inner,
        base_image=base_image,
        target_image=target_image,
        packages_to_install=packages_to_install,
        pip_index_urls=pip_index_urls,
        output_component_file=output_component_file,
        install_kfp_package=install_kfp_package,
        kfp_package_path=kfp_package_path)
    
