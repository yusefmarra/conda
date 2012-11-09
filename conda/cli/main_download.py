
from anaconda import anaconda
from package_plan import create_download_plan


def configure_parser(sub_parsers):
    p = sub_parsers.add_parser(
        'download',
        description     = "Download Anaconda packages and their dependencies.",
        help            = "Download Anaconda packages and their dependencies. (ADVANCED)",
    )
    p.add_argument(
        "--confirm",
        action  = "store",
        default = "yes",
        choices = ["yes", "no"],
        help    = "ask for confirmation before downloading packages (default: yes)",
    )
    p.add_argument(
        "--dry-run",
        action  = "store_true",
        default = False,
        help    = "display packages to be downloaded, without actually executing",
    )
    p.add_argument(
        '-f', "--force",
        action  = "store_true",
        default = False,
        help    = "force package downloads even when specific package is already available",
    )
    p.add_argument(
        "--progress-bar",
        action  = "store",
        default = "yes",
        choices = ["yes", "no"],
        help    = "display progress bar for package downloads (default: yes)",
    )
    p.add_argument(
        'canonical_names',
        action  = "store",
        metavar = 'canonical_name',
        nargs   = '+',
        help    = "canonical name of package to download and make locally available",
    )
    p.set_defaults(func=execute)


def execute(args):
    conda = anaconda()

    plan = create_download_plan(conda, args.canonical_names, args.force)

    if plan.empty():
        print 'All packages already downloaded, nothing to do'
        return

    print plan

    if args.dry_run:
        return

    if args.confirm == "yes":
        proceed = raw_input("Proceed (y/n)? ")
        if proceed.lower() not in ['y', 'yes']: return

    # pass default environment because some env is required, but it is unused here
    plan.execute(conda.default_environment, args.progress_bar=="yes")
