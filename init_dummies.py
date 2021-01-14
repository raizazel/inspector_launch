
from PyQt5 import QtWidgets
from dummies import Ui_MainWindow 
import sys

import os
import signal
from subprocess import Popen
import time

# ----------------------------------------------------------------------------------------------------

class bcolors:    
    BLUE = '\033[94m'
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

class InitGUI(QtWidgets.QMainWindow):
    def __init__(self, args):
        super(InitGUI, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.ui.button_roscore.clicked.connect(self.btnClickedRoscore)
        self.ui.button_telemetry.clicked.connect(self.btnClickedTelemetry)
        self.ui.button_gui.clicked.connect(self.btnClickedGUI)
        self.ui.button_slam.clicked.connect(self.btnClickedSLAM)
        self.ui.button_close.clicked.connect(self.btnClickedClose)

        self.ui.button_roscore.setStyleSheet("background-color: blue")
        self.ui.button_telemetry.setStyleSheet("background-color: blue")
        self.ui.button_gui.setStyleSheet("background-color: blue")
        self.ui.button_slam.setStyleSheet("background-color: blue")
        self.ui.button_close.setStyleSheet("background-color: red")

        self.args = args
        check_files_exist([self.args.script_node_telemetry, self.args.script_node_gui, self.args.script_node_slam, self.args.dpath_logs])

        self.p_ros_core = None
        self.session_telemetry_node = None
        self.session_gui_node = None
        self.session_slam_node = None

        self.start_time = time.strftime('%Y%m%d_%H%M%S')

    def btnClickedRoscore(self):
        if self.p_ros_core is None:
            self.p_ros_core = start_process(['/opt/ros/melodic/bin/roscore'], 
                                            'ros', self.start_time, self.args.dpath_logs)
            print(bcolors.GREEN + 'PGID ROS: ' + str(os.getpgid(self.p_ros_core.pid)) + bcolors.ENDC)
            self.ui.button_roscore.setStyleSheet("background-color: green")
        else:
            print(bcolors.WARNING + 'Closing ROSCORE' + bcolors.ENDC)
            os.killpg(os.getpgid(self.p_ros_core.pid), signal.SIGTERM)
            self.p_ros_core = None
            self.ui.button_roscore.setStyleSheet("background-color: blue")

    def btnClickedTelemetry(self):
        if self.session_telemetry_node is None:
            self.session_telemetry_node = start_process(['/bin/bash', self.args.script_node_telemetry],
                                                'telemetry_node', self.start_time,
                                                self.args.dpath_logs)
            print(bcolors.GREEN + 'PGID TELEMETRY: ' + str(os.getpgid(self.session_telemetry_node.pid)) + bcolors.ENDC)
            self.ui.button_telemetry.setStyleSheet("background-color: green")
        else:
            print(bcolors.WARNING + 'Closing TELEMETRY' + bcolors.ENDC)
            os.killpg(os.getpgid(self.session_telemetry_node.pid), signal.SIGTERM)
            self.session_telemetry_node = None
            self.ui.button_telemetry.setStyleSheet("background-color: blue")

    def btnClickedGUI(self):
        if self.session_gui_node is None:
            self.session_gui_node = start_process(['/bin/bash', self.args.script_node_gui],
                                                'gui_node', self.start_time,
                                                self.args.dpath_logs)
            print(bcolors.GREEN + 'PGID GUI: ' + str(os.getpgid(self.session_gui_node.pid)) + bcolors.ENDC)
            self.ui.button_gui.setStyleSheet("background-color: green")
        else:
            print(bcolors.WARNING + 'Closing GUI' + bcolors.ENDC)
            os.killpg(os.getpgid(self.session_gui_node.pid), signal.SIGTERM)
            self.session_gui_node = None
            self.ui.button_gui.setStyleSheet("background-color: blue")

    def btnClickedSLAM(self):
        if self.session_slam_node is None:
            self.session_slam_node = start_process(['/bin/bash', self.args.script_node_slam],
                                                'slam_node', self.start_time,
                                                self.args.dpath_logs)
            print(bcolors.GREEN + 'PGID SLAM: ' + str(os.getpgid(self.session_slam_node.pid)) + bcolors.ENDC)
            self.ui.button_slam.setStyleSheet("background-color: green")
        else:
            print(bcolors.WARNING + 'Closing SLAM' + bcolors.ENDC)
            os.killpg(os.getpgid(self.session_slam_node.pid), signal.SIGTERM)
            self.session_slam_node = None
            self.ui.button_slam.setStyleSheet("background-color: blue")

    def btnClickedClose(self):
        print(bcolors.WARNING + 'Closing all programs' + bcolors.ENDC)
        if self.p_ros_core is not None:
            os.killpg(os.getpgid(self.p_ros_core.pid), signal.SIGTERM)
            self.p_ros_core = None
        
        if self.session_telemetry_node is not None:
            os.killpg(os.getpgid(self.session_telemetry_node.pid), signal.SIGTERM)
            self.session_telemetry_node = None

        if self.session_gui_node is not None:
            os.killpg(os.getpgid(self.session_gui_node.pid), signal.SIGTERM)
            self.session_gui_node = None
        
        if self.session_slam_node is not None:
            os.killpg(os.getpgid(self.session_slam_node.pid), signal.SIGTERM)
            self.session_slam_node = None

# ----------------------------------------------------------------------------------------------------

def main(args):
    app = QtWidgets.QApplication([])

    dummies_gui = InitGUI(args)
    dummies_gui.show()

    sys.exit(app.exec())

# ----------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--script_node_telemetry', '-t', type=str,
                        default='/home/aphrodite/programming/dji/catkin_local_control/test.sh')

    parser.add_argument('--script_node_gui', '-g', type=str,
                        default='/home/aphrodite/programming/dji/catkin_local_control/test.sh')

    parser.add_argument('--script_node_slam', '-s', type=str,
                        default='/home/aphrodite/programming/dji/catkin_local_control/test2.sh')

    parser.add_argument('--dpath_logs', '-l', type=str,
                        default='/home/aphrodite/programming/inspector_launch')

    args = parser.parse_args()
    main(args)
