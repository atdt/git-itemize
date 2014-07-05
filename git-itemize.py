#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
  git-itemize: compose commit message interactively

  This script provides an interface similar to 'git commit --interactive'
  for writing commit messages.  It displays each staged hunk and prompts the
  user for a one-line summary. Pressing 'enter' skips the current hunk.
  The set of summarized changes is then opened in $EDITOR so that it may be
  revised or expanded.

  Requires pygit2: <http://www.pygit2.org/>

  Copyright 2014 Ori Livneh <ori@wikimedia.org>

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

"""
from __future__ import print_function

import os
import tempfile

import pygit2


repo = pygit2.Repository(pygit2.discover_repository(os.getcwd()))
temp = tempfile.NamedTemporaryFile(mode='wt', delete=False)

cyan = '\033[96m{}\033[0m'.format
red = '\033[91m{}\033[0m'.format
green = '\033[92m{}\033[0m'.format


def format_line(type, line):
    color = {'+': green, '-': red, ' ': str}.get(type)
    return color('{} {}'.format(type, line.rstrip()))

format_patch = '--- c/{0.old_file_path}\n+++ i/{0.new_file_path}'
format_hunk = cyan(
    '@@ -{0.old_start},{0.old_lines} +{0.new_start},{0.new_lines} @@')

for patch in repo.diff('HEAD'):
    if patch.status == 'D':
        print('* deleted {0.old_file_path}'.format(patch), file=temp)
        continue
    print(format_patch.format(patch))
    for hunk in patch.hunks:
        print(format_hunk.format(hunk))
        for type, line in hunk.lines:
            print(format_line(type, line))
    summary = raw_input('> ')
    if summary:
        print('* {0}'.format(summary), file=temp)

temp.flush()
os.fsync(temp.fileno())
temp.close()

os.execlp('git', 'git', 'commit', '-t', temp.name)
