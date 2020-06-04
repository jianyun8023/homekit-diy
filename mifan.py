#! python3

import logging

from miio.fan import FanP5, OperationMode
from pyhap.accessory import Accessory
from pyhap.const import CATEGORY_FAN

logger = logging.getLogger(__name__)


class MiFan(Accessory):
    """代理小米风扇，实现homekit风扇设备"""

    category = CATEGORY_FAN

    def __init__(self, param, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fan = FanP5(
            ip=param.host,
            token=param.token
        )

        mi_fan = self.add_preload_service('Fanv2',
                                          chars=['Name', 'Active', 'RotationSpeed', 'SwingMode', 'LockPhysicalControls',
                                                 'RotationDirection'])
        info = self.fan.info()
        logger.info(info)
        self.set_info_service(
            manufacturer='Xiaomi',
            model=info.model,
            firmware_revision=info.firmware_version,
            serial_number='1'
        )

        mi_fan.configure_char('Name', value='Mi Fan')
        # 设备开关
        mi_fan.configure_char('Active', setter_callback=self.set_power, getter_callback=self.get_power)
        # 风扇速度
        mi_fan.configure_char('RotationSpeed', setter_callback=self.set_speed, getter_callback=self.get_speed)
        # homekit定义是旋转方向，这个配置成直吹风\自然风
        mi_fan.configure_char('RotationDirection', setter_callback=self.set_mode, getter_callback=self.get_mode)
        # 是否摇头
        mi_fan.configure_char('SwingMode', setter_callback=self.set_oscillate, getter_callback=self.get_oscillate)
        # 童锁
        mi_fan.configure_char('LockPhysicalControls', setter_callback=self.set_child_lock,
                              getter_callback=self.get_child_lock)

    def set_mode(self, value):
        if value == 1:
            self.fan.set_mode(OperationMode.Nature)
        else:
            self.fan.set_mode(OperationMode.Normal)

    def get_mode(self):
        return int(self.fan.status().mode == OperationMode.Nature)

    def set_speed(self, value):
        self.fan.set_speed(value)

    def get_speed(self):
        return self.fan.status().speed

    def set_oscillate(self, value):
        self.fan.set_oscillate(bool(value))

    def get_oscillate(self):
        return int(self.fan.status().oscillate)

    def get_power(self):
        return int(self.fan.status().is_on)

    def set_power(self, value: int):
        if value == 1:
            self.fan.on()
        else:
            self.fan.off()

    def set_child_lock(self, value):
        self.fan.set_child_lock(bool(value))

    def get_child_lock(self):
        return int(self.fan.status().child_lock)


def build_param():
    import argparse
    import os
    parser = argparse.ArgumentParser(description='miFan tool')
    parser.add_argument('--host', type=str, default=os.getenv("MIIO_HOST"), help="小米设备的ip地址")
    parser.add_argument('--token', type=str, default=os.getenv("MIIO_TOKEN"), help="小米设备的token")
    parser.add_argument('--port', type=int, default=51826, help="homekit对外的端口")
    args = parser.parse_args()
    assert args.host
    assert args.token
    return args


def main(args):
    import logging
    import signal
    from pyhap.accessory_driver import AccessoryDriver

    logging.basicConfig(level=logging.INFO)

    driver = AccessoryDriver(port=args.port)
    accessory = MiFan(args, driver, 'Fanv2')
    driver.add_accessory(accessory=accessory)

    signal.signal(signal.SIGTERM, driver.signal_handler)
    driver.start()


if __name__ == '__main__':
    main(build_param())
