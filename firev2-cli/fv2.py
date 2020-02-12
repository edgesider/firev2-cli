#! /usr/bin/env python3
import sys


def main():
    import argparse
    parser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument(
        '--config', help='specify configuration file')
    subparsers = parser.add_subparsers(
        required=True, dest='command')

    from .cli import (subscription_add_parser,
                      node_add_parser,
                      inbound_add_parser,
                      routing_add_parser,
                      v2_add_parser,
                      log_add_parser)

    subscription_add_parser(subparsers)
    node_add_parser(subparsers)
    inbound_add_parser(subparsers)
    routing_add_parser(subparsers)
    v2_add_parser(subparsers)
    log_add_parser(subparsers)

    args = parser.parse_args(sys.argv[1:])

    from firev2 import config

    if args.config is not None:
        config.auto_load()

    command = args.command
    if command == 'subscription':
        from .cli import process_subscription
        process_subscription(args)
    elif command == 'node':
        from .cli import process_node
        process_node(args)
    elif command == 'inbound':
        from .cli import process_inbound
        process_inbound(args)
    elif command == 'routing':
        from .cli import process_routing
        process_routing(args)
    elif command == 'v2':
        from .cli import process_v2
        process_v2(args)
    elif command == 'log':
        from .cli import process_log
        process_log(args)


if __name__ == '__main__':
    main()
