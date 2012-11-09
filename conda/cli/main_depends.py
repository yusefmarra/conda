
from os.path import abspath, expanduser

from anaconda import anaconda
from config import ROOT_DIR


def configure_parser(sub_parsers):
    p = sub_parsers.add_parser(
        'depends',
        description = "Query Anaconda package dependencies.",
        help        = "Query Anaconda package dependencies.",
    )
    p.add_argument(
        '-m', "--max-depth",
        action  = "store",
        type    = int,
        default = 0,
        help    = "maximum depth to search dependencies, 0 searches all depths (default: 0)",
    )
    p.add_argument(
        "--no-prefix",
        action  = "store_true",
        default = False,
        help    = "return reverse dependencies compatible with any specified environment, overrides --prefix",
    )
    p.add_argument(
        '-p', "--prefix",
        action  = "store",
        default = ROOT_DIR,
        help    = "return dependencies compatible with a specified environment (default: %s)" % ROOT_DIR,
    )
    p.add_argument(
        '-r', "--reverse",
        action  = "store_true",
        default = False,
        help    = "generate reverse dependencies",
    )
    p.add_argument(
        '-v', "--verbose",
        action  = "store_true",
        default = False,
        help    = "display build strings on reverse dependencies",
    )
    p.add_argument(
        'pkg_names',
        action  = "store",
        metavar = 'package_name',
        nargs   = '+',
    )
    p.set_defaults(func=execute)


def execute(args):
    conda = anaconda()

    prefix = abspath(expanduser(args.prefix))
    env = conda.lookup_environment(prefix)

    pkgs = [env.find_activated_package(pkg_name) for pkg_name in args.pkg_names]

    if args.reverse:
        reqs = conda.index.find_compatible_requirements(pkgs)
        rdeps = conda.index.get_reverse_deps(reqs, args.max_depth)

        fmt = '%s' if len(args.pkg_names) == 1 else '{%s}'

        if not args.no_prefix:
            rdeps = rdeps & env.activated

        if len(rdeps) == 0:
            print 'No packages depend on ' + fmt % ', '.join(args.pkg_names)
            return

        if args.verbose:
            names = sorted([pkg.canonical_name for pkg in rdeps])
        else:
            names = [str(pkg) for pkg in rdeps]
            names_count = dict((k, names.count(k)) for k in names)
            names = sorted(list(set(names)))

        activated = '' if args.no_prefix else 'activated '
        print 'The following %spackages depend on ' % activated + fmt % ', '.join(args.pkg_names) + ':'
        for name in names:
            if args.verbose or names_count[name]==1:
                print '    %s' % name
            else:
                print '    %s (%d builds)' % (name, names_count[name])

    else:
        deps = conda.index.get_deps(pkgs, args.max_depth)

        if len(deps) == 0:
            suffix, fmt = ('es', '%s') if len(args.pkg_names) == 1 else ('', '{%s}')
            print (fmt + ' do%s not depend on any packages') % (', '.join(args.pkg_names), suffix)
            return

        names = sorted(['%s %s' % (dep.name, dep.version.vstring) for dep in deps])

        suffix, fmt = ('s', '%s') if len(args.pkg_names) == 1 else ('', '{%s}')
        print (fmt + ' depend%s on the following packages:') % (', '.join(args.pkg_names), suffix)
        for name in names:
            print '    %s' % name

