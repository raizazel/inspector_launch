
import sys
import os
import signal
from subprocess import Popen
import time

# ----------------------------------------------------------------------------------------------------

class bcolors:    
    BLUE = '\033[94m'
    PINK = '\033[95m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    
# ----------------------------------------------------------------------------------------------------

def run(cmd, stdout, stderr):
    """Run a given `cmd` in a subprocess, write logs to stdout / stderr.

    Parameters
    ----------
    cmd : list of str
        Command to run.
    stdout : str or subprocess.PIPE object
        Destination of stdout output.
    stderr : str or subprocess.PIPE object
        Destination of stderr output.

    Returns
    -------
    A subprocess.Popen instance.
    """
    return Popen(cmd, stdout=stdout, stderr=stderr, shell=False,
                 preexec_fn=os.setsid)


def get_stdout_stderr(typ, datetime, dir):
    """Create stdout / stderr file paths."""
    out = '%s_%s_stdout.log' % (datetime, typ)
    err = '%s_%s_stderr.log' % (datetime, typ)
    return os.path.join(dir, out), os.path.join(dir, err)


def check_files_exist(files):
    """Check if given list of files exists.

    Parameters
    ----------
    files : list of str
        Files to check for existence.

    Returns
    -------
    None if all files exist. Else raises a ValueError.
    """
    errors = []
    for f in files:
        if not os.path.exists(f):
            errors.append(f)
    if errors:
        raise ValueError('File does not exist: %s' % errors)


def start_process(cmd, typ, start_time, dpath_logs):
    """Start a subprocess with the given command `cmd`.

    Parameters
    ----------
    cmd : list of str
        Command to run.
    typ : str
        Type of subprocess. This will be included in the logs' file names.
    start_time : str
        Datetime string, will be included in the logs' file names as well as
        the resulting bag's name.
    dpath_logs :
        Path to log direcotry.

    Returns
    -------
    A subprocess.Popen instance.
    """
    print(bcolors.BLUE + 'Starting ' + typ.upper() + bcolors.ENDC)
    stdout, stderr = get_stdout_stderr(typ, start_time, dpath_logs)
    with open(stdout, 'wb') as out, open(stderr, 'wb') as err:
        return run(cmd, stdout=out, stderr=err)

# ----------------------------------------------------------------------------------------------------

class InitCmds():
    def __init__(self, args):
        self.args = args
        # check_files_exist([self.args.script_node_telemetry, self.args.script_node_img, self.args.script_node_slam, self.args.dpath_logs])

        self.p_ros_core = None
        self.session_telemetry_node = None
        self.session_img_node = None
        self.session_slam_node = None

        self.start_time = time.strftime('%Y%m%d_%H%M%S')

    def nodeRoscore(self):
        if self.p_ros_core is None:
            self.p_ros_core = start_process(['/opt/ros/noetic/bin/roscore'], 
                                            'ros', self.start_time, self.args.dpath_logs)
            print(bcolors.GREEN + 'PGID ROS: ' + str(os.getpgid(self.p_ros_core.pid)) + bcolors.ENDC)
        else:
            print(bcolors.WARNING + 'Closing ROSCORE' + bcolors.ENDC)
            os.killpg(os.getpgid(self.p_ros_core.pid), signal.SIGTERM)
            self.p_ros_core = None

    def nodeTelemetry(self):
        if self.session_telemetry_node is None:
            self.session_telemetry_node = start_process(['/bin/bash', self.args.script_node_telemetry],
                                                'telemetry_node', self.start_time,
                                                self.args.dpath_logs)
            print(bcolors.GREEN + 'PGID TELEMETRY: ' + str(os.getpgid(self.session_telemetry_node.pid)) + bcolors.ENDC)
        else:
            print(bcolors.WARNING + 'Closing TELEMETRY' + bcolors.ENDC)
            os.killpg(os.getpgid(self.session_telemetry_node.pid), signal.SIGTERM)
            self.session_telemetry_node = None

    def nodeImg(self):
        if self.session_img_node is None:
            self.session_img_node = start_process(['/bin/bash', self.args.script_node_img],
                                                'img_node', self.start_time,
                                                self.args.dpath_logs)
            print(bcolors.GREEN + 'PGID IMG: ' + str(os.getpgid(self.session_img_node.pid)) + bcolors.ENDC)
        else:
            print(bcolors.WARNING + 'Closing IMG' + bcolors.ENDC)
            os.killpg(os.getpgid(self.session_img_node.pid), signal.SIGTERM)
            self.session_img_node = None

    def nodeSLAM(self):
        if self.session_slam_node is None:
            self.session_slam_node = start_process(['/bin/bash', self.args.script_node_slam],
                                                'slam_node', self.start_time,
                                                self.args.dpath_logs)
            print(bcolors.GREEN + 'PGID SLAM: ' + str(os.getpgid(self.session_slam_node.pid)) + bcolors.ENDC)
        else:
            print(bcolors.WARNING + 'Closing SLAM' + bcolors.ENDC)
            os.killpg(os.getpgid(self.session_slam_node.pid), signal.SIGTERM)
            self.session_slam_node = None

    def close(self):
        print(bcolors.WARNING + 'Closing all programs' + bcolors.ENDC)
        if self.p_ros_core is not None:
            os.killpg(os.getpgid(self.p_ros_core.pid), signal.SIGTERM)
            self.p_ros_core = None

        if self.session_telemetry_node is not None:
            os.killpg(os.getpgid(self.session_telemetry_node.pid), signal.SIGTERM)
            self.session_telemetry_node = None
        
        if self.session_img_node is not None:
            os.killpg(os.getpgid(self.session_img_node.pid), signal.SIGTERM)
            self.session_img_node = None

        if self.session_slam_node is not None:
            os.killpg(os.getpgid(self.session_slam_node.pid), signal.SIGTERM)
            self.session_slam_node = None

    def __del__(self):
        print(bcolors.WARNING + 'Closing all programs' + bcolors.ENDC)
        if self.p_ros_core is not None:
            os.killpg(os.getpgid(self.p_ros_core.pid), signal.SIGTERM)

        if self.session_telemetry_node is not None:
            os.killpg(os.getpgid(self.session_telemetry_node.pid), signal.SIGTERM)
        
        if self.session_img_node is not None:
            os.killpg(os.getpgid(self.session_img_node.pid), signal.SIGTERM)
            
        if self.session_slam_node is not None:
            os.killpg(os.getpgid(self.session_slam_node.pid), signal.SIGTERM)
            
# ----------------------------------------------------------------------------------------------------

def main(args):

    dummies_init = InitCmds(args)

    print(bcolors.BLUE + 'Init Script for launch nodes in remote.' + bcolors.ENDC)
    dummies_init.nodeRoscore()

    print(bcolors.PINK + 'Use 1 for launch Telemetry node.' + bcolors.ENDC)
    print(bcolors.PINK + 'Use 2 for launch Camera node.' + bcolors.ENDC)
    print(bcolors.PINK + 'Use 3 for launch SLAM node.' + bcolors.ENDC)
    print(bcolors.PINK + 'Use 9 for close existing nodes and relaunch Roscore.' + bcolors.ENDC)
    print(bcolors.PINK + 'Use 0 for script exit.' + bcolors.ENDC)

    finishRead = False
    for line in sys.stdin:
        for var in line.split():
            var = int(var)
            if var == 1:
                dummies_init.nodeTelemetry()
            elif var == 2:
                dummies_init.nodeImg()
            elif var == 3:
                dummies_init.nodeSLAM()
            elif var == 9:
                dummies_init.close()
                dummies_init.nodeRoscore()
            elif var == 0:
                finishRead = True
            else:
                print(bcolors.WARNING + 'Number error, please use 1 or 0. Thanks' + bcolors.ENDC)
        if finishRead:
            break
    
    print(bcolors.FAIL + 'Exiting...' + bcolors.ENDC)
    
# ----------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--script_node_telemetry', '-t', type=str,
                        default='/home/gunter/programming/catkin_dji/telemetry.sh')

    parser.add_argument('--script_node_img', '-i', type=str,
                        default='/home/gunter/programming/inspector_ws_2/img.sh')

    parser.add_argument('--script_node_slam', '-s', type=str,
                        default='/home/gunter/programming/inspector_ws_2/slam.sh')

    parser.add_argument('--dpath_logs', '-l', type=str,
                        default='/home/manuoso/programming/inspector_launch/logs')
    
    args = parser.parse_args()
    main(args)
