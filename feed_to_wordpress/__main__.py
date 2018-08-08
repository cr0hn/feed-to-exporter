import os
import argparse

from feed_to_wordpress.model import AppConfig
from feed_to_wordpress.processors import process_feed


def main():
    parser = argparse.ArgumentParser(
        description='Parse feed and publish Wordpress post')
    parser.add_argument('feed', metavar='FEED_URL', type=str,
                        help='url to feed to parse')

    parser.add_argument('--wordpress-url', '-W',
                        dest='wordpress_url',
                        required=True,
                        help='wordpress url')
    parser.add_argument('--filters-file', '-F',
                        dest='filters_file',
                        help='file with filters')
    parser.add_argument('--mapping', '-m',
                        dest='mapping_path',
                        required=False,
                        help='file path to mapping.json file')
    parser.add_argument('--user', '-U',
                        dest='user',
                        required=True,
                        help='user to access to Wordpress')
    parser.add_argument('--app-auth', '-A',
                        dest='app_auth',
                        required=True,
                        help='app auth code (from "Application '
                             'Passwords" plugin)')
    parser.add_argument('--discover', '-D',
                        dest='discover_mode',
                        action="store_true",
                        default=False,
                        required=False,
                        help='using this mode f2w will try to discover '
                             'mapping and filters')
    args = parser.parse_args()

    #
    # Ensure config
    #
    if args.mapping_path and args.discover_mode:
        print("[!] Options -D and -m are incompatible")
        return

    if args.discover_mode:
        #
        # Discover mode
        #
        find_location = os.path.abspath(os.path.dirname(args.feed))

        for root, dirs, files in os.walk(find_location, topdown=False):
            if all(x in files for x in ("filters.py", "mapping.json")):

                if "f2wSkip" in files:
                    continue

                filters_path = os.path.join(root, "filters.py")
                mapping_path = os.path.join(root, "mapping.json")
                config_args = args.__dict__
                config_args['filters_file'] = filters_path
                config_args['mapping_path'] = mapping_path

                config = AppConfig(**config_args)
                process_feed(config)

    else:
        #
        # Individual mode
        #
        config = AppConfig(**args.__dict__)
        process_feed(config)


if __name__ == '__main__':
    main()


