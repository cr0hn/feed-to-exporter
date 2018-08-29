def build_parser(argparser):
    parser = argparser.add_parser('wordpress',
                                  help='push feed data to Wordpress')

    parser.add_argument('feed_source',
                        nargs="*",
                        help='target url or path')
    parser.add_argument('--wordpress-url', '-W',
                        dest='wordpress_url',
                        required=True,
                        help='wordpress url')
    parser.add_argument('--user', '-U',
                        dest='user',
                        required=True,
                        help='user to access to Wordpress')
    parser.add_argument('--app-auth', '-A',
                        dest='app_auth',
                        required=True,
                        help='app auth code (from "Application '
                             'Passwords" plugin)')
    parser.add_argument('--devel',
                        dest='develop_mode',
                        action="store_true",
                        default=False,
                        required=False,
                        help="running in develop mode doesn't publish "
                             "Wordpress Post")