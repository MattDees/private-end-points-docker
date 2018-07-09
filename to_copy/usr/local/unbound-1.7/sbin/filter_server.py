#!/usr/bin/python

from contextlib import closing
import socket
import os
import sys
import grp
import pwd
import json

from daemon import Daemon


# daemon configuration
FILTERS_DIR = "/etc/encryptme/filters"
SOCKET_PATH = "/usr/local/unbound-1.7/etc/unbound/dns_filter.sock"
PID_FILE = "/usr/local/unbound-1.7/etc/unbound/var/run/dns-filter.pid"


class FilterList():
    def __init__(self, filter_dir):
        """
        Build entries from file.
        """
        self.blacklist = set()
        self.load(filters_dir)

    @staticmethod
    def _yield_lines(path):
        with open(path) as list_file:
            for item in list_file:
                yield item.strip()

    def load(self, filters_dir):
        if not os.path.isdir(filters_dir):
            return
        for name in os.listdir(filters_dir):
            if not name.endswith('.blacklist'):
                continue
            for domain in self._yield_lines(os.path.join([filters_dir, name])):
                self.blacklist.add(domain)

    def is_blocked(self, domain):
        '''
        Returns whether this domain is blocked or is a sub-domain of a blocked
        domain.
        '''
        name = domain
        while '.' in name:
            if name in self.blacklist:
                return True
            name = name[name.find('.') + 1:]
        return False


class FilterDaemon(Daemon):
    def __init__(self, pid_file
    def run(self):
        filter_list = FilterList())
        # create the socket
        try:
            os.unlink(socket_path)
        except OSError:
            if os.path.exists(socket_path):
                raise
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        with closing(sock):
            sock.bind(socket_path)
            sock.listen(1)
            if not os.path.exists(run_dir):
                os.makedirs(run_dir)
            uid = pwd.getpwnam("unbound").pw_uid
            gid = grp.getgrnam("unbound").gr_gid
            os.chown(socket_path, uid, gid)
            self._run_loop(sock, filter_list)

    def _run_loop(self, sock, filter_list):
        while True:
            connection, address = sock.accept()
            with closing(connection):
                data = connection.recv(2048)
                data = json.loads(data)
                for list_obj in [blacklist]:
                    connection.sendall(
                    resp = list_obj.query(data['domain'].strip())
                    if resp:
                        break




if __name__ == "__main__":
    daemon = FilterDaemon(
        pid_file=pid_file,
        socket_path=SOCKET_PATH,
        filters_dir=FILTERS_DIR
    )
    if len(sys.argv) != 2:
        print "Unknown command"
        sys.exit(2)

    if 'start' == sys.argv[1]:
        try:
            daemon.start()
        except Exception as e:
            pass
    elif 'stop' == sys.argv[1]:
        daemon.stop()
        os.unlink(socket_path)
    elif 'restart' == sys.argv[1]:
        daemon.restart()
    elif 'status' == sys.argv[1]:
        try:
            pf = file(pid_file, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        except SystemExit:
            pid = None
        if pid:
            print 'dns-filter is running with pid %s' % pid
        else:
            print 'dns-filter is not running.'
    else:
        print "usage: %s start|stop|restart|status" % sys.argv[0]
        sys.exit(2)
