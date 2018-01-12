import click
from microservices_framework.core.management.migrate import init as _init
from microservices_framework.core.management.migrate import revision as _revision
from microservices_framework.core.management.migrate import migrate as _migrate
from microservices_framework.core.management.migrate import edit as _edit
from microservices_framework.core.management.migrate import merge as _merge
from microservices_framework.core.management.migrate import upgrade as _upgrade
from microservices_framework.core.management.migrate import downgrade as _downgrade
from microservices_framework.core.management.migrate import show as _show
from microservices_framework.core.management.migrate import history as _history
from microservices_framework.core.management.migrate import heads as _heads
from microservices_framework.core.management.migrate import branches as _branches
from microservices_framework.core.management.migrate import current as _current
from microservices_framework.core.management.migrate import stamp as _stamp


@click.group()
def db():
    """Perform database migrations."""
    pass


@db.command()
@click.option('-d', '--directory', default=None, help='migration script directory (default is "migrations")')
@click.option('--multidb', is_flag=True, help='Support multiple databases')
def init(directory, multidb):
    """Creates a new migration repository."""
    _init(directory, multidb)


@db.command()
@click.option('-d', '--directory', default=None, help='migration script directory (default is "migrations")')
@click.option('-m', '--message', default=None, help='Revision message')
@click.option('--autogenerate', is_flag=True,
              help=('Populate revision script with candidate migration '
                    'operations, based on comparison of database to model'))
@click.option('--sql', is_flag=True, help='Don\'t emit SQL to database - dump to standard output instead')
@click.option('--head', default='head', help='Specify head revision or <branchname>@head to base new revision on')
@click.option('--splice', is_flag=True, help='Allow a non-head revision as the "head" to splice onto')
@click.option('--branch-label', default=None, help='Specify a branch label to apply to the new revision')
@click.option('--version-path', default=None, help='Specify specific path from config for version file')
@click.option('--rev-id', default=None, help='Specify a hardcoded revision id instead of generating one')
def revision(directory, message, autogenerate, sql, head, splice, branch_label,
             version_path, rev_id):
    """Create a new revision file."""
    _revision(directory, message, autogenerate, sql, head, splice,
              branch_label, version_path, rev_id)


@db.command()
@click.option('-d', '--directory', default=None, help='migration script directory (default is "migrations")')
@click.option('-m', '--message', default=None, help='Revision message')
@click.option('--sql', is_flag=True, help='Don\'t emit SQL to database - dump to standard output instead')
@click.option('--head', default='head', help='Specify head revision or <branchname>@head to base new revision on')
@click.option('--splice', is_flag=True, help='Allow a non-head revision as the "head" to splice onto')
@click.option('--branch-label', default=None, help='Specify a branch label to apply to the new revision')
@click.option('--version-path', default=None, help='Specify specific path from config for version file')
@click.option('--rev-id', default=None, help='Specify a hardcoded revision id instead of generating one')
@click.option('-x', '--x-arg', multiple=True, help='Additional arguments consumed by custom env.py scripts')
def migrate(directory, message, sql, head, splice, branch_label, version_path,
            rev_id, x_arg):
    """Autogenerate a new revision file (Alias for 'revision --autogenerate')"""
    _migrate(directory, message, sql, head, splice, branch_label, version_path,
             rev_id, x_arg)


@db.command()
@click.option('-d', '--directory', default=None, help='migration script directory (default is "migrations")')
@click.argument('revision', default='head')
def edit(directory, revision):
    """Edit a revision file"""
    _edit(directory, revision)


@db.command()
@click.option('-d', '--directory', default=None, help='migration script directory (default is "migrations")')
@click.option('-m', '--message', default=None, help='Merge revision message')
@click.option('--branch-label', default=None, help='Specify a branch label to apply to the new revision')
@click.option('--rev-id', default=None, help='Specify a hardcoded revision id instead of generating one')
@click.argument('revisions', nargs=-1)
def merge(directory, message, branch_label, rev_id, revisions):
    """Merge two revisions together, creating a new revision file"""
    _merge(directory, revisions, message, branch_label, rev_id)


@db.command()
@click.option('-d', '--directory', default=None, help='migration script directory (default is "migrations")')
@click.option('--sql', is_flag=True, help='Don\'t emit SQL to database - dump to standard output instead')
@click.option('--tag', default=None, help='Arbitrary "tag" name - can be used by custom "env.py" scripts')
@click.option('-x', '--x-arg', multiple=True, help='Additional arguments consumed by custom env.py scripts')
@click.argument('revision', default='head')
def upgrade(directory, sql, tag, x_arg, revision):
    """Upgrade to a later version"""
    _upgrade(directory, revision, sql, tag, x_arg)


@db.command()
@click.option('-d', '--directory', default=None, help='migration script directory (default is "migrations")')
@click.option('--sql', is_flag=True, help='Don\'t emit SQL to database - dump to standard output instead')
@click.option('--tag', default=None, help='Arbitrary "tag" name - can be used by custom "env.py" scripts')
@click.option('-x', '--x-arg', multiple=True, help='Additional arguments consumed by custom env.py scripts')
@click.argument('revision', default='-1')
def downgrade(directory, sql, tag, x_arg, revision):
    """Revert to a previous version"""
    _downgrade(directory, revision, sql, tag, x_arg)


@db.command()
@click.option('-d', '--directory', default=None, help='migration script directory (default is "migrations")')
@click.argument('revision', default='head')
def show(directory, revision):
    """Show the revision denoted by the given symbol."""
    _show(directory, revision)


@db.command()
@click.option('-d', '--directory', default=None, help='migration script directory (default is "migrations")')
@click.option('-r', '--rev-range', default=None, help='Specify a revision range; format is [start]:[end]')
@click.option('-v', '--verbose', is_flag=True, help='Use more verbose output')
def history(directory, rev_range, verbose):
    """List changeset scripts in chronological order."""
    _history(directory, rev_range, verbose)


@db.command()
@click.option('-d', '--directory', default=None, help='migration script directory (default is "migrations")')
@click.option('-v', '--verbose', is_flag=True, help='Use more verbose output')
@click.option('--resolve-dependencies', is_flag=True, help='Treat dependency versions as down revisions')
def heads(directory, verbose, resolve_dependencies):
    """Show current available heads in the script directory"""
    _heads(directory, verbose, resolve_dependencies)


@db.command()
@click.option('-d', '--directory', default=None, help='migration script directory (default is "migrations")')
@click.option('-v', '--verbose', is_flag=True, help='Use more verbose output')
def branches(directory, verbose):
    """Show current branch points"""
    _branches(directory, verbose)


@db.command()
@click.option('-d', '--directory', default=None, help='migration script directory (default is "migrations")')
@click.option('-v', '--verbose', is_flag=True, help='Use more verbose output')
@click.option('--head-only', is_flag=True, help='Deprecated. Use --verbose for additional output')
def current(directory, verbose, head_only):
    """Display the current revision for each database."""
    _current(directory, verbose, head_only)


@db.command()
@click.option('-d', '--directory', default=None, help='migration script directory (default is "migrations")')
@click.option('--sql', is_flag=True, help='Don\'t emit SQL to database - dump to standard output instead')
@click.option('--tag', default=None, help='Arbitrary "tag" name - can be used by custom "env.py" scripts')
@click.argument('revision', default='head')
def stamp(directory, sql, tag, revision):
    """'stamp' the revision table with the given revision; don't run any
    migrations"""
    _stamp(directory, revision, sql, tag)
