import re
import time
import logging

from virttest import error_context, utils_test


LOG = logging.getLogger(__name__)

@error_context.context_aware
def run(test, params, env):
    """
    Qemu reboot test:
    1) Log into a guest
    3) Send a reboot command or a system_reset monitor command (optional)
    4) Wait until the guest is up again
    5) Log into the guest to verify it's up again

    :param test: QEMU test object
    :param params: Dictionary with the test parameters
    :param env: Dictionary with test environment.
    """
    regexp_vbs_enabled = re.compile("VirtualizationBasedSecurityStatus\s*:\s*2")
    def runningVBS(session):
        output = session.cmd_output('powershell -command "get-CimInstance -classname win32_deviceguard -namespace root\microsoft\windows\deviceguard"')
        LOG.info(output)
        return regexp_vbs_enabled.search(output) is not None

    timeout = float(params.get("login_timeout", 240))
    serial_login = params.get("serial_login", "no") == "yes"
    vms = env.get_all_vms()
    assert len(vms) == 1, "Only one VM supported on this test"
    vm = vms[0]
    error_context.context("Try to log into guest '%s'." % vm.name, test.log.info)
    if serial_login:
        session = vm.wait_for_serial_login(timeout=timeout)
    else:
        session = vm.wait_for_login(timeout=timeout)
    if not runningVBS(session):
        test.fail("VBS not running")
    session.close()
