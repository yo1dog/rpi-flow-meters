# Cistern

## Reading Flowmeters
The flowmeters we use output a high voltage for 1/2 of the pinwheel's rotation and a low voltage for the other 1/2. Here's an example of what the signal would look like after 3 complete rotations:

```
     Rotation 1    Rotation 2    Rotation 3
   /-----------\ /-----------\ /-----------\
   ______        ______        ______        ___
  |      |      |      |      |      |      |
__|      |______|      |______|      |______|
  ^             ^             ^             ^
 Rise          Rise          Rise          Rise
```

Thefefore, we can know the pinwheel has completed a full rotation everytime the single changes from a low state to a high state (a rise).


## Calculate Flow Rate

The pinwheel in the flow meter rotates at a rate consistant with the flow rate. Meaning, if the flow rate doubles in speed, the pinwheel will double in speed. Therefore, there exists a constant relationship between the rotation of the pinwheel and the volume of liquid passed through the flow meter. This constant is given by the flow meter manufacturer. Example: `2ml/rot`.

Given this constant we can calculate the volume of liquid that has flowed through the flow meter based on the number of pinwheel rotations: `volume = volumne/rotation * rotation`. Once we know the volumne, we can calcualte the average flow rate over a period time: `flow_rate = volume/time`.

Example: The volume per rotation for the flowmeter is `2ml/rot`. The flowmeter's pinwheel rotated 6 times in 4 seconds.

```
(6rot * 2ml/rot)/4s = (12ml)/4s = 3ml/s
```


## Wiring

Based on [Raspberry Pi B Rev 2 (Q4 2012)](https://elinux.org/RPi_Low-level_peripherals#Model_A_and_B_.28Original.29) and Adafruit i2c 16x2 RGB LCD Pi Plate.

All pin numbers are GPIO pin numbers, not the PCB pin numbers.

The LCD plate should be connected to the Raspberry Pi normally. This will use only the 2 I2C pins (GPIO 14 and 15).

The flow meters' V+ and ground should be connected to one of the Raspberry Pi 5V pins and ground pins. The flow meters' signal should connect to any GPIO pin except 14 & 15.


## Configuring

Edit `config.py` to configure.


## Running

```
python cistern.py
```