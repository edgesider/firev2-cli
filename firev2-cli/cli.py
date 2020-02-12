import json

from firev2 import v2_config
from firev2 import Inbound, Routing, DataManager


def subscription_add_parser(subparsers):
    parser = subparsers.add_parser(
        'subscription', help='manage subscriptions')
    cmds = parser.add_subparsers(
        required=True, dest='sub_cmd')
    cmd_add = cmds.add_parser('add', help='add a new subscription')
    cmd_add.add_argument('name')
    cmd_add.add_argument('url')
    cmd_update = cmds.add_parser('update', help='update a subscription')
    cmd_update.add_argument('name')
    cmd_list = cmds.add_parser('list', help='list all subscriptions')
    cmd_remove = cmds.add_parser('remove', help='remove a subscription')
    cmd_remove.add_argument('name')


# TODO colorful ui
def process_subscription(args):
    cmd = args.sub_cmd
    mgr = DataManager()
    sm = mgr.subscription_mgr
    if cmd == 'add':
        sm.add_url(args.name, args.url)
        mgr.save()
    elif cmd == 'update':
        sm.update(args.name)
        mgr.save()
    elif cmd == 'remove':
        sm.remove(args.name)
        mgr.save()
    elif cmd == 'list':
        for name, s in sm.get_all().items():
            print(f'{name} [{s.url}]')


def node_add_parser(subparsers):
    parser = subparsers.add_parser('node', help='manage nodes')
    cmds = parser.add_subparsers(required=True, dest='sub_cmd')
    cmd_list = cmds.add_parser('list', help='list all nodes')


def process_node(args):
    cmd = args.sub_cmd
    mgr = DataManager()
    nm = mgr.node_mgr
    sm = mgr.subscription_mgr
    if cmd == 'list':
        for name, s in sm.get_all().items():
            print(f'Subscription {name} [{s.url}]:')
            for i, n in enumerate(s.nodes):
                if isinstance(n, v2_config.VmessNode):
                    print(f'\t[{i}] {n.remark} - {n.address}')
                elif isinstance(n, (v2_config.DirectNode, v2_config.BlockedNode)):
                    print(f'\t[{i}] {n.tag}')


def inbound_add_parser(subparsers):
    parser = subparsers.add_parser('inbound', help='manage inbounds')
    cmds = parser.add_subparsers(required=True, dest='sub_cmd')
    cmd_list = cmds.add_parser('list', help='list all inbounds')
    cmd_add = cmds.add_parser('add', help='add a new inbound')
    cmd_add.add_argument('name')
    # cmd_add.add_argument('protocol')
    cmd_add.add_argument('port')


def process_inbound(args):
    cmd = args.sub_cmd
    mgr = DataManager()
    im = mgr.inbound_mgr
    if cmd == 'list':
        inbound: Inbound
        i = 0
        for name, inbound in im.get_all().items():
            print(f'[{i}] {name} - localhost:{inbound.port} [{inbound.protocol}]')
            i += 1
    elif cmd == 'add':
        name = args.name
        port = args.port
        im.add(name, Inbound('', 'socks', port))
        mgr.save()


def routing_add_parser(subparsers):
    parser = subparsers.add_parser('routing', help='manage routings')
    cmds = parser.add_subparsers(required=True, dest='sub_cmd')

    cmd_list = cmds.add_parser('list', help='list all routing')
    cmd_add = cmds.add_parser('add', help='add a new routing')
    cmd_add.add_argument('name')
    cmd_remove = cmds.add_parser('remove', help='remove a routing')
    cmd_remove.add_argument('name')
    cmd_set_master = cmds.add_parser('set-master', help='set master node')
    cmd_set_master.add_argument('name')
    cmd_set_master.add_argument('master-node')

    cmd_remove_rule = cmds.add_parser('remove-rule',
                                      help='remove a rule from routing')
    cmd_remove_rule.add_argument('name')
    cmd_remove_rule.add_argument('-m', '--matchers')
    cmd_remove_rule.add_argument('-i', '--inbound', required=True)
    cmd_remove_rule.add_argument('-n', '--node', required=True)

    cmd_add_rule = cmds.add_parser('add-rule', help='add rule(s) to a routing')
    cmd_add_rule.add_argument('name')
    cmd_add_rule.add_argument('-m', '--matchers')
    cmd_add_rule.add_argument('-i', '--inbound', required=True)
    cmd_add_rule.add_argument('-n', '--node', required=True)

    cmd_list_rule = cmds.add_parser('list-rules', help='list rules in routing')
    cmd_list_rule.add_argument('name')


def process_routing(args):
    cmd = args.sub_cmd
    mgr = DataManager()
    rm = mgr.routing_mgr
    im = mgr.inbound_mgr
    sm = mgr.subscription_mgr
    nm = mgr.node_mgr
    if cmd == 'list':
        routings = rm.get_all()
        r: Routing
        for n, r in routings.items():
            l = len(r.rules)
            print(f'{n} [{l} rule{"s" if l > 1 else ""}]')
    elif cmd == 'add':
        name = args.name
        rm.add(name, Routing())
        mgr.save()
    elif cmd == 'remove':
        name = args.name
        rm.remove(name)
        mgr.save()
    elif cmd == 'set-master':
        name = args.name
        node = getattr(args, 'master-node')
        r: Routing = rm.get_by_name(name)
        r.master = node
        mgr.save()
    elif cmd == 'add-rule':
        name = args.name
        matchers = args.matchers
        node_name: str = args.node
        inbound_name: str = args.inbound

        inbound = im.get_by_name(inbound_name)
        assert inbound, f'no such inbound {inbound_name}'
        node = sm.get_node(node_name)
        assert node, f'no such node {node_name}'
        r: Routing = rm.get_by_name(name)
        r.add_rule(inbound_name, node_name, matchers)
        mgr.save()
    elif cmd == 'remove-rule':
        name = args.name
        matchers = args.matchers
        node_name: str = args.node
        inbound_name: str = args.inbound

        r: Routing = rm.get_by_name(name)
        r.remove_rule(inbound_name, node_name, matchers)
        mgr.save()
    elif cmd == 'list-rules':
        name = args.name
        r: Routing = rm.get_by_name(name)
        for tags, matchers in r.rules.items():
            print(f'{tags[0]} ----> {", ".join(matchers)} ----> {tags[1]}')


def v2_add_parser(subparsers):
    parser = subparsers.add_parser('v2', help='manage v2ray process')
    cmds = parser.add_subparsers(required=True, dest='sub_cmd')
    cmd_start = cmds.add_parser('start', help='start v2ray process')
    cmd_start.add_argument('-r', '--routing', required=True,
                           help='select a routing')
    cmd_stop = cmds.add_parser('stop', help='stop v2ray process')
    cmd_restart = cmds.add_parser('restart', help='restart v2ray process')

    cmd_status = cmds.add_parser('status', help='show monitor status')

    cmd_dump_config = cmds.add_parser('dump-config',
                                      help='dump v2ray config in json format')
    cmd_dump_config.add_argument('-r', '--routing', required=True,
                                 help='select a routing')


def process_v2(args):
    cmd = args.sub_cmd

    from firev2 import v2ray
    data_mgr = DataManager()
    rm = data_mgr.routing_mgr
    im = data_mgr.inbound_mgr
    sm = data_mgr.subscription_mgr
    v2_mgr = v2ray.V2rayManager()
    if cmd == 'start':
        routing_name = args.routing
        routing: Routing = rm.get_by_name(routing_name)
        assert routing, f'no such routing {routing_name}'
        v2_mgr.start(routing.make_config(im, sm))
    elif cmd == 'stop':
        v2_mgr.stop()
    elif cmd == 'restart':
        v2_mgr.restart()
    elif cmd == 'status':
        if v2_mgr.is_running():
            print("running")
        else:
            print('stopped')
    elif cmd == 'dump-config':
        routing_name = args.routing
        routing: Routing = rm.get_by_name(routing_name)
        assert routing, f'no such routing {routing_name}'
        print(json.dumps(routing.make_config(im, sm),
                         indent=4, ensure_ascii=False))


def log_add_parser(subparsers):
    parser = subparsers.add_parser('log', help='manage v2ray logs')
    cmds = parser.add_subparsers(required=True, dest='log_cmd')
    cmd_set_level = cmds.add_parser('set-level', help='set log level')
    cmd_set_level.add_argument('level', choices=['debug', 'info', 'warning',
                                                 'error', 'none'])
    cmd_attach = cmds.add_parser('attach', help='fetch v2ray logs')
    cmd_attach.add_argument('-t', '--type', choices=['access', 'error'],
                            help='select type of logs to fetch')


def process_log(args):
    cmd = args.log_cmd

    from firev2 import v2ray
    v2_mgr = v2ray.V2rayManager()
    if cmd == 'set-level':
        pass
    elif cmd == 'attach':
        log_type = args.type
        fp = None
        if log_type == 'access':
            fp = v2_mgr.get_access_log_file()
        elif log_type == 'error':
            fp = v2_mgr.get_error_log_file()
        elif log_type == 'monitor':
            # TODO
            pass
        else:
            raise ValueError
        import select
        import fcntl
        import os
        import io
        fcntl.fcntl(fp.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
        eof = False
        while True:
            # TODO remove select()
            rfds, _, _ = select.select([fp], [], [])
            assert len(rfds) == 1
            rfd: io.FileIO = rfds[0]
            while True:
                d = rfd.read()
                if d is None:
                    break
                elif d == b'':
                    eof = True
                print(d.decode('utf8'), end='')
            if eof:
                break


if __name__ == '__main__':
    from firev2 import config

    config.auto_load()


    class A:
        pass


    a = A()
    a.sub_cmd = 'add'
    a.name = 'r'
    process_routing(a)

    a = A()
    a.sub_cmd = 'add'
    a.name = 'auto'
    a.port = '3000'
    process_inbound(a)

    a = A()
    a.sub_cmd = 'add-rule'
    a.name = 'r'
    a.matchers = None
    a.node = 'direct'
    a.inbound = 'auto'
    process_routing(a)

    a = A()
    a.sub_cmd = 'remove-rule'
    a.name = 'r'
    a.matchers = None
    a.node = 'direct'
    a.inbound = 'auto'
    process_routing(a)
