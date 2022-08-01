# Copyright (c) MegFlow. All rights reserved.

import argparse
import os
import os.path as osp
import re

pattern = re.compile(r'\[.*?\]\(.*?\)')


def analyze_doc(cur_dir: str, path: str, check_http: bool,
                debug: bool) -> bool:
    if debug:
        print(f'analyzing {path}')

    problem_list = []
    code_block = False
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith('```'):
                code_block = not code_block
                continue

            if code_block is True:
                continue

            if '[' in line and ']' in line and '(' in line and ')' in line:
                for item in pattern.findall(line):
                    start = item.find('(')
                    end = item.find(')')
                    ref = item[start + 1:end]

                    if not check_http and ref.startswith(
                            'http') or ref.startswith('#'):
                        continue

                    if '.md#' in ref:
                        ref = ref[ref.find('#'):]
                    fullpath = osp.join(cur_dir, ref)
                    if not osp.exists(fullpath):
                        problem_list.append(ref)
            else:
                continue

    if len(problem_list) > 0:
        print(f'{path}:')
        for item in problem_list:
            print(f'\t {item}')
        print('\n')
        return False

    return True


def check_doc_link(filepath: str,
                   check_http: bool = False,
                   debug: bool = False) -> int:
    """"""
    retv = 0
    if not osp.exists(filepath):
        print(f'filepath {filepath} not exists')
        retv = 1

    if os.path.isfile(filepath):
        if not analyze_doc('./', filepath, check_http, debug):
            retv = 1

    for cur_dir, _, filenames in os.walk(filepath):
        for filename in filenames:
            if filename.endswith('.md'):
                path = osp.join(cur_dir, filename)
                if not osp.islink(path):
                    if not analyze_doc(cur_dir, path, check_http, debug):
                        retv = 1

    return retv


def main():
    parser = argparse.ArgumentParser(description='Doc link checker')
    parser.add_argument(
        'filepath', type=str, help='the directory or file to check')
    parser.add_argument(
        '--check-http', action='store_true', help='check http or not ')
    parser.add_argument(
        '--debug', action='store_true', help='Print debug info')

    args = parser.parse_args()
    return check_doc_link(args.filepath, args.check_http, args.debug)


if __name__ == '__main__':
    raise SystemExit(main())
