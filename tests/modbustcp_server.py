#!/bin/python

from pyModbusTCP.server import ModbusServer
from time import sleep
from random import uniform
import config_parameters

# Create an instance of ModbusServer
server = ModbusServer("127.0.0.1", 12345, no_block=True)

try:
    print("Start server...")
    server.start()
    print("Server is online")
    state = [0]
    while True:
        # Generate random values for all registers
        random_values = [int(uniform(0, 100)) for _ in range(config_parameters.REG_NB)]

        # Set the last two registers to create a float value of 1.0
        random_values[config_parameters.REG_NB - 1] = 0x3F80  # Set the second last register to 0x3F80
        random_values[config_parameters.REG_NB - 2] = 0x0000  # Set the last register to 0x0000


        # Update the holding registers with the generated values
        server.data_bank.set_holding_registers(
            config_parameters.REG_ADDR, random_values
        )

        current_value = server.data_bank.get_holding_registers(
            config_parameters.REG_ADDR, config_parameters.REG_NB
        )  # Read all registers

        if current_value and state != current_value:  # Check if read was successful
            state = current_value
            print("Values of Registers have changed to: " + str(state))
        sleep(config_parameters.SLEEP_TIME)

except Exception as e:
    print(f"Shutdown server ... {e}")
    server.stop()
    print("Server is offline")
