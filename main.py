import psycopg2
from psycopg2 import Error
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
import random
import datetime
from random import randrange

try:
    connection = psycopg2.connect(user="gabriel",
                                  password="abcd1234",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="topicos")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM owners;")
    owners = cursor.fetchall()
    for owner_id, name, last_name in owners:
        cursor.execute(
            "SELECT * FROM servers WHERE owner_id = %s", (owner_id,))
        servers = cursor.fetchall()

        for server_id, owner_id, ipv4, port, server_address, device_name in servers:
            cursor.execute(
                "SELECT * FROM resources WHERE server_id = %s;", (server_id,))
            resources = cursor.fetchall()

            with ModbusClient(ipv4, port=port) as client:
                for res_id, server_id, address, is_coil, read_only in resources:
                    if is_coil:
                        # always read
                        response = client.read_coils(
                            address, 1, unit=server_address
                        )
                        assert(not response.isError())
                        value = response.bits[0]
                        cursor.execute(
                            "INSERT INTO coil_rw (res_id, function_code, value, timestamp) VALUES (%s, %s, %s, %s);",
                            (res_id, 1, value, datetime.datetime.now())
                        )
                        connection.commit()
                        if not read_only:
                            # write
                            value = bool(random.getrandbits(1))
                            response = client.write_coil(
                                address, value, unit=server_address
                            )
                            assert(not response.isError())
                            cursor.execute(
                                "INSERT INTO coil_rw (res_id, function_code, value, timestamp) VALUES (%s, %s, %s, %s);",
                                (res_id, 5, value, datetime.datetime.now())
                            )
                            connection.commit()
                    else:
                        if read_only:
                            # only read
                            response = client.read_input_registers(
                                address, 1, unit=server_address)
                            assert(not response.isError())
                            value = response.registers[0]
                            cursor.execute(
                                "INSERT INTO register_rw (res_id, function_code, value, timestamp) VALUES (%s, %s, %s, %s);",
                                (res_id, 4, value, datetime.datetime.now())
                            )
                            connection.commit()
                            pass
                        else:
                            # read
                            response = client.read_holding_registers(
                                address, 1, unit=server_address)
                            assert(not response.isError())
                            value = response.registers[0]
                            cursor.execute(
                                "INSERT INTO register_rw (res_id, function_code, value, timestamp) VALUES (%s, %s, %s, %s);",
                                (res_id, 3, value, datetime.datetime.now())
                            )
                            connection.commit()
                            # write
                            value = randrange(256)
                            response = client.write_register(
                                address, value, unit=server_address)
                            assert(not response.isError())
                            cursor.execute(
                                "INSERT INTO register_rw (res_id, function_code, value, timestamp) VALUES (%s, %s, %s, %s);",
                                (res_id, 6, value, datetime.datetime.now())
                            )
                            connection.commit()
except (Exception, Error) as error:
    print(error)
finally:
    if (connection):
        cursor.close()
        connection.close()
