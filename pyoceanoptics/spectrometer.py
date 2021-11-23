import usb.core
import usb.util
import array
import numpy as np

VENDOR_ID = 0x2457
PRODUCT_ID = 0x1012


def get_spectrometers():
    """ Searches for possible HR4000 devices


    :return: list of HR4000 devices found (Spectrometer Objects)
    """
    device = usb.core.find(find_all=True, idVendor=VENDOR_ID,
                           idProduct=PRODUCT_ID)
    spectrometers = []
    for d in device:
        s = Spectrometer(d)
        spectrometers.append(s)
    return spectrometers


def get_spectrometer_by_id(id_string):
    """ Gets Spectrometer by identification string

    :param id_string: identification string
    :return: Spectrometer object
    """
    spectrometers = get_spectrometers()
    for s in spectrometers:
        if s.id_string == id_string:
            return s
    return None


class Spectrometer:
    def __init__(self, device):
        """
        Generates spectrometer object from device object and gets the device serial number for identification
        """

        self._device = device
        self._device.set_configuration()
        self._write_ep = self._device[0][(0, 0)][0]
        self._endpoint2 = self._device[0][(0, 0)][1]
        self._endpoint6 = self._device[0][(0, 0)][2]
        self._main_read_ep = self._device[0][(0, 0)][3]

        self._device.write(self._write_ep.bEndpointAddress, b'\x01')
        self.id_string = self._query(b'\x05\x00')
        self.a = 0
        self.b = 0
        self.c = 0
        self.d = 0
        self.stray_light = 0
        self.nl_order = 0
        self.grating_config = 0
        self.usb4000_config = 0
        self.auto_null = 0
        self.power_up_board = 0
        self.nonlinearity = []
        self.get_ccd_config()
        usb.util.dispose_resources(self._device)

    def free(self):
        """
        Unloads the USB device, this is usually not necessary but can be useful in interactive shells

        """
        usb.util.dispose_resources(self._device)

    def _read_packet(self, endpoint):
        """ read packet utility function for internal use, should be refactored
        """
        attempts = 1
        data = None
        while data is None and attempts > 0:
            try:
                data = self._device.read(endpoint.bEndpointAddress,
                                         endpoint.wMaxPacketSize)
            except usb.core.USBError as e:
                data = None
                if e.args == ('Operation timed out',):
                    attempts -= 1
                    continue
        return data

    def __str__(self):
        return self.id_string

    def __repr__(self):
        return self.id_string

    def _query(self, command):
        self._device.write(self._write_ep.bEndpointAddress, command)
        return (self._read_packet(self._main_read_ep)[2:].tobytes().split(b'\0')[0]).decode('utf-8', 'ignore')


    def _query_float(self, command):
        return float(self._query(command))

    def get_ccd_config(self):
        """
        Reads Spectrometer config from device and stores in object

        """
        self.a = self._query_float(b'\x05\x01')
        self.b = self._query_float(b'\x05\x02')
        self.c = self._query_float(b'\x05\x03')
        self.d = self._query_float(b'\x05\x04')

        self.stray_light = self._query_float(b'\x05\x05')

        self.nonlinearity = []
        self.nonlinearity.append(self._query_float(b'\x05\x06'))
        self.nonlinearity.append(self._query_float(b'\x05\x07'))
        self.nonlinearity.append(self._query_float(b'\x05\x08'))
        self.nonlinearity.append(self._query_float(b'\x05\x09'))
        self.nonlinearity.append(self._query_float(b'\x05\x0a'))
        self.nonlinearity.append(self._query_float(b'\x05\x0b'))
        self.nonlinearity.append(self._query_float(b'\x05\x0c'))
        self.nonlinearity.append(self._query_float(b'\x05\x0d'))

        self.nl_order = self._query_float(b'\x05\x0e')
        self.grating_config = self._query(b'\x05\x0f')
        self.usb4000_config = self._query(b'\x05\x10')
        self.auto_null = self._query(b'\x05\x11')
        self.power_up_board = self._query(b'\x05\x12')

    def get_ccd_data(self):
        """
        Reads the current spectrum 3840 pixels
        :return: ccd_data, numpy array of the raw read values
        """

        spectrum = []
        self._device.write(self._write_ep.bEndpointAddress, '\x09')
        for i in range(4):
            spectrum.append(array.array('h', self._read_packet(self._endpoint6).tobytes()))
        for i in range(16-4-1):
            spectrum.append(array.array('h', self._read_packet(self._endpoint2).tobytes()))

        end_data = self._read_packet(self._endpoint2)
        if end_data.tobytes() != b"\x69":
            raise ValueError('Cannot get data from CCD')

        ccd_data = np.array(spectrum).flatten() ^ 0x2000
        return ccd_data

    def get_x(self):
        """
        Calculates the Wavelength axis from configuration data
        :return: Wavelength axis
        """
        n = np.arange(0, 3840, 1.0)
        x = self.a + self.b*n + self.c*n**2 + self.d*n**3
        return x