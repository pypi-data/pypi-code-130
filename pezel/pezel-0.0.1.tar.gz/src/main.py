import argparse
import fnmatch
import io
import logging
import os
import pathlib
import tarfile

from build.cache import BuildCache
from build.graph import BuildGraph
from helper.artifact import ArtifactTypes
from helper.debug import debug_info
from helper.logging import CriticalException, dev_log_root, user_log_root
from rule.load import build_loader
from rule.rules.file import PathResult


dev_log = dev_log_root.getChild(__name__)
user_log = user_log_root.getChild(__name__)


class ExitCodes(object):
    SUCCESS = 0
    FAILURE = 1


def _save_results(path, results, root_path, path_is_dir):
    save_data = {}
    for rule, data in results.items():
        if not isinstance(data, PathResult):
            raise CriticalException(f'Output for rule {rule} is not a filetype. It can\'t be saved.')

        if len(data.files) == 1:
            save_data[rule] = data.files[0].data
        else:
            file_archive = io.BytesIO()
            with tarfile.open(fileobj=file_archive, mode='w:gz') as tar:
                data.add_to_tar(tar, '/', root_path)
            save_data[f'{rule}.tar'] = file_archive

    if path_is_dir:
        for filename, data in save_data.items():
            path.mkdir(parents=True, exist_ok=True)
            with path.joinpath(filename).open('wb') as f:
                f.write(data)
    else:
        assert len(save_data) == 1, 'Unable to save to single file with multiple rule outputs.'
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('wb') as f:
            f.write(next(iter(save_data.values())))


def run_build(rules, build_graph):
    results = {}
    for rule in rules:
        user_log.info(f'Running rule {rule}')
        results[rule] = build_graph.build_rule(rule)

    return results


def run_test(rules, build_graph, test_max_failures):
    exit_code = ExitCodes.SUCCESS
    tests_failed = 0
    tests_passed = 0
    for rule in rules:
        user_log.info(f'Running test {rule}')
        try:
            build_graph.build_rule(rule)
        except CriticalException as err:
            err.log(user_log, dev_log)
            user_log.info(f'Error with test {rule}')
            tests_failed += 1
        except Exception as err:
            CriticalException(str(err)).log()
            user_log.info(f'Error with test {rule}')
            tests_failed += 1
        else:
            tests_passed += 1

        if test_max_failures is not None and test_max_failures < tests_failed:
            user_log.info(f'Surpassed max test failures. Halting any more tests.')
            exit_code = ExitCodes.FAILURE
            break
    else:
        user_log.info(f'{tests_passed}/{tests_passed + tests_failed} test(s) passed.')

    return exit_code


def run():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('root')
        parser.add_argument('rule')
        parser.add_argument('--cache', default='/tmp/pezel')
        parser.add_argument('--debug_keep_failed_container_alive', action=argparse.BooleanOptionalAction)
        parser.add_argument('--dev_logs', action=argparse.BooleanOptionalAction)
        parser.add_argument('--enable_env_vars', default=True, action=argparse.BooleanOptionalAction)
        parser.add_argument('--host_root')
        parser.add_argument('--log_level', type=str.upper, choices=logging._nameToLevel.keys())
        parser.add_argument('--mode', default='run', choices=['run', 'test'])
        parser.add_argument('--out')
        parser.add_argument('--test_max_failures', type=int)
        parser.add_argument('--var', action='append', default=[])
        args = parser.parse_args()
    except SystemExit:
        exit(ExitCodes.FAILURE)

    try:
        if args.log_level is not None:
            user_log_root.setLevel(args.log_level)
        if args.dev_logs:
            dev_log_root.setLevel(logging.DEBUG)
            user_log_root.setLevel(logging.DEBUG)

        debug_info.keep_failed_container_alive = args.debug_keep_failed_container_alive

        root_path = pathlib.Path(args.root).resolve()
        host_root_path = pathlib.Path(args.host_root) if args.host_root is not None else None
        cache_path = root_path.joinpath(args.cache).resolve()
        out_path = root_path.joinpath(args.out).resolve() if args.out is not None else None
        out_is_dir = args.out is not None and args.out[-1] == pathlib.os.sep

        passed_vars = {}
        for var in args.var:
            var_k, var_v = var.split('=')
            passed_vars[var_k] = var_v
        global_vars = {
            **(os.environ if args.enable_env_vars else {}),
            **passed_vars}

        rule_loader = build_loader(root_path, global_vars=global_vars, host_root_path=host_root_path)
        build_cache = BuildCache(cache_path)
        build_graph = BuildGraph(root_path, rule_loader, build_cache)

        matched_rules = sorted([rule for rule in build_graph.rules if fnmatch.fnmatch(rule, args.rule)])

        if not matched_rules:
            user_log.error(f'Unable to find rule(s) that match "{args.rule}".')
            return

        exit_code = ExitCodes.SUCCESS
        if args.mode == 'run':
            results = run_build(matched_rules, build_graph)

            if out_path is not None:
                _save_results(out_path, results, root_path, out_is_dir)
        elif args.mode == 'test':
            exit_code = run_test(matched_rules, build_graph, args.test_max_failures)

        if build_graph.artifacts[ArtifactTypes.IMAGE_TAG]:
            user_log.info(f'Image tag(s) created: {", ".join(build_graph.artifacts["image_tag"])}')
    except CriticalException as err:
        err.log(user_log, dev_log)
        exit_code = ExitCodes.FAILURE
    except Exception as err:
        CriticalException.build_from_exception(err).log(user_log, dev_log)
        exit_code = ExitCodes.FAILURE

    exit(exit_code)


if __name__ == '__main__':
    run()
