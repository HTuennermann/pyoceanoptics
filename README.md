pyoceanoptics
=============

Python Driver for OceanOptics HR4000 v0.1

Since OceanOptics does not provide a python driver and I did not want to use their JAVA based driver I wrote
my my own minimal driver.

As it relies on libusb you will need to install the libusb driver on windows instead of the driver oceanoptics provides.
This means you will not be able to use the OceanOptics software either - which is a shame but at this point cannot be
helped.

This first version does not have an installer, it requires pyusb, numpy.
Feel free to contribute!

Henrik