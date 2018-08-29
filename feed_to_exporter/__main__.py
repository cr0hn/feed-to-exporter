import os
import argparse

from feed_to_exporter.processors import process_feed
from feed_to_exporter.mongodb.cli import build_parser as bp_mongo
from feed_to_exporter.wordpress.cli import build_parser as bp_wp


def main():
    parser = argparse.ArgumentParser(
        description='Parse feed and publish Wordpress post')
    parser.add_argument('--filters-file', '-F',
                        dest='filter_file',
                        required=False,
                        help='file with filters')
    parser.add_argument('--mapping', '-m',
                        dest='mapping_path',
                        required=False,
                        help='file path to mapping.json file')

    subparsers = parser.add_subparsers(dest="option", help='available options')

    # -------------------------------------------------------------------------
    # Add subparsers
    # -------------------------------------------------------------------------
    bp_mongo(subparsers)
    bp_wp(subparsers)

    args = parser.parse_args()

    if not args.option:
        parser.print_help()
        return

    # -------------------------------------------------------------------------
    # Check if target is a remote URL or a directory
    # -------------------------------------------------------------------------
    if not args.feed_source:
        args.feed_source = os.path.dirname(__file__)
    else:
        _t = args.feed_source[0]
        args.feed_source = os.path.join(os.getcwd(), _t) \
            if not _t.startswith("http") \
            else _t

    if os.path.isdir(args.feed_source):
        mode = "path"
    elif args.feed_source.startswith("http"):
        mode = "url"
    else:
        print("[!] Invalid target. Allowed targets are: directory path or URL")
        return

    print(f"[*] Using feed source: '{args.feed_source}'")

    # -------------------------------------------------------------------------
    # Check class for config
    # -------------------------------------------------------------------------
    if args.option == "mongo":
        from feed_to_exporter.mongodb.model import AppConfigMongo
        klass = AppConfigMongo

    elif args.option == "wordpress":
        from feed_to_exporter.wordpress.model import AppConfigWordpress
        klass = AppConfigWordpress
    else:
        print("[!] Invalid option. Allowed: mongo|wordpress")
        return

    #
    # Ensure config
    #
    if mode == "path":
        #
        # Discover mode
        #
        for root, dirs, files in os.walk(args.feed_source, topdown=False):
            if all(x in files for x in ("filters.py", "mapping.json")):

                if "f2eSkip" in files:
                    continue

                filters_path = os.path.join(root, "filters.py")
                mapping_path = os.path.join(root, "mapping.json")
                config_args = args.__dict__
                config_args['filter_file'] = filters_path
                config_args['mapping_path'] = mapping_path

                if "option" in config_args:
                    del config_args["option"]

                config = klass(**config_args)
                process_feed(config)

    else:
        #
        # Individual mode
        #
        config = klass(**args.__dict__)
        process_feed(config)


if __name__ == '__main__':
    main()


