def build_parser(subparsers):
    parser = subparsers.add_parser('mongo',
                                   help='push feed data to MongoDB')
    parser.add_argument('feed_source',
                        nargs="*",
                        help='target url or path')
    parser.add_argument('--user', '-U',
                        dest='user',
                        default=None,
                        help='mongodb user')
    parser.add_argument('--password', '-P',
                        dest='password',
                        default=None,
                        help='mongodb password')
    parser.add_argument('--collection', '-C',
                        dest='collection',
                        default="f2e",
                        help='mongo collection')
    parser.add_argument('--database', '-D',
                        dest='database',
                        default="f2e",
                        help='mongo database')
    parser.add_argument('--mongo-url', '-M',
                        dest='mongo_urn',
                        default="mongodb://127.0.0.1:27017/f2e",
                        help='mongo URL. (Default: '
                             'mongodb://127.0.0.1:27017/f2e)')
