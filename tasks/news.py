# -*- coding=utf-8 -*-
import invoke
import tomlkit
import uuid
from pathlib import Path


def _get_git_root(ctx):
    return Path(ctx.run('git rev-parse --show-toplevel', hide=True).stdout.strip())


def _get_news_dir(ctx):
    return _get_git_root(ctx) / 'news'


def get_toml_file(ctx):
    return _get_git_root(ctx) / 'pyproject.toml'


def get_random():
    return str(uuid.uuid4())[:8]


@invoke.task
def add(ctx, description, type_='feature', issue=None):
    with get_toml_file(ctx).open() as f:
        tf = tomlkit.parse(f.read_text())
    allowed_types = tf.get('tool', {}).get('towncrier', {}).get('type', [])
    if allowed_types:
        allowed_types = [t.get('directory') for t in allowed_types]
    if not allowed_types or type_ not in allowed_types:
        print("[news.add] Invalid type or no types found: {0}".format(type_))
        print("Valid news types: {0}".format(' '.join(allowed_types)))
        return
    target_dir = _get_news_dir(ctx)
    existing_files = [f.suffix.split('-')[0] for f in target_dir.glob('{0}.*'.format(type_)) if f.suffix.split('-')[0].isdigit()]
    if not existing_files and not issue:
        nextfile = target_dir / '1-{0}.{1}'.format(get_random(), type_)
    elif issue:
        nextfile = target_dir / '{0}.{1}'.format(issue, type_)
    else:
        nextfile = '{0}-{1}.{2}'.format(int(sorted(existing_files).pop()) + 1, get_random(), type_)
        nextfile = target_dir / nextfile
    print("[news.add] Adding newsfile {0} => [{1}] {2}".format(nextfile.name, type_.upper(), description))
    nextfile.write_text(description)


@invoke.task
def generate(ctx, draft=False):
    print("[news.generate] Generating NEWS")

    args = []
    if draft:
        args.append("--draft")

    ctx.run("towncrier {}".format(" ".join(args)))
