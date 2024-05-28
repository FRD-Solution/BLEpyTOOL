# 
# 
# 
# GITHUB release
# THIS DOCUMENT IS PUBLIC
# ANYONE IS FREE TO USE AND MODIFY IT
# 
# 
# 
# 


import asyncio
import time
import os
import datetime as dt
from bleak import BleakScanner
from bleak import BleakClient



UUID_SN_CHARACTERISTIC                             ="00002a24-0000-1000-8000-00805f9b34fb"
UUID_MANUFACTURER_CHARACTERISTIC                   ="00002a29-0000-1000-8000-00805f9b34fb"
UUID_SYSTEM_ID_CHARACTERISTIC                      ="00002a23-0000-1000-8000-00805f9b34fb"
UUID_SW_VERSION_CHARACTERISTIC                     ="00002a28-0000-1000-8000-00805f9b34fb"
UUID_FW_VERSION_CHARACTERISTIC                     ="00002a26-0000-1000-8000-00805f9b34fb"
UUID_BATTERY_LEVEL_CHARACTERISTIC                  ="00002a19-0000-1000-8000-00805f9b34fb"

List_UUID = [
    ["UUID_SN_CHARACTERISTIC", UUID_SN_CHARACTERISTIC],
    ["UUID_MANUFACTURER_CHARACTERISTIC", UUID_MANUFACTURER_CHARACTERISTIC],
    ["UUID_SYSTEM_ID_CHARACTERISTIC", UUID_SYSTEM_ID_CHARACTERISTIC],
    ["UUID_SW_VERSION_CHARACTERISTIC", UUID_SW_VERSION_CHARACTERISTIC],
    ["UUID_FW_VERSION_CHARACTERISTIC", UUID_FW_VERSION_CHARACTERISTIC],
    ["UUID_BATTERY_LEVEL_CHARACTERISTIC", UUID_BATTERY_LEVEL_CHARACTERISTIC],
]

Devices_List = []


def getdate():
    #getting the date for the logfile
    date, time = str(dt.datetime.now()).split(" ")
    return date

def gettime():
    #getting the time in the format hh : mm : ss
    date, time = str(dt.datetime.now()).split(" ")
    time, millisec = time.split(".")
    return time

def clockformat(sec):
    #tranforming a number of second into a clock format --> hh : mm : ss
    s = sec
    m = 0
    h = 0
    while s>59:
        if s > 59:
            m += 1
            s -= 60
        if m > 59:
            h += 1
            m -= 60
    return (str(h)+" : "+str(m)+" : "+str(s))

def startLog(tolog):
    #creating a folder named log and then creating a .csv and a .txt log files
    #use this fonction again to right the data to log in both of the logfiles
    main_repo = os.getcwd()
    try:
        os.chdir('logs')
    except FileNotFoundError:
        os.mkdir('logs')
        os.chdir('logs')
    try:
        date = getdate()
        csvname = "BLEpyTOOL"+date+".csv"
        txtname = "BLEpyTOOL"+date+".txt"
        logcsv = open(csvname, "a")
        logcsv.write(tolog)
        logtxt = open(txtname, "a")
        logtxt.write(tolog)
    except Exception as e:
        print(e)
    os.chdir(main_repo)

class BLE_Device:
    #to store the device info like address, name and signal strength
    #TO DO make a fonction to get the signal strength
    def __init__(self, address, name, signal = 0):
        self.address = address
        self.name = name
        self.signal = signal

async def Scan_Discover():
    #scan for BLE devices and show the one that meet the specified names
    #to be use for the rest of the script
    devices = await BleakScanner.discover()
    for d in devices:
        address, name = str(d).split(": ")
        if True:  #you can add filter by address or name by replacing True by your filter parameter
            print("found this device")
            print(address, "-", name)
            Devices_List.append(BLE_Device(address, name))
            startLog(";{time};{text};{device};\n".format(time = gettime(), text = "", device = str(d))) #you can add text to help read the log afterwards
    if len(Devices_List) > 1:
        os.system('cls')
        print("\n\n\n!!! found more than 1 device to monitor !!!\n\n\n")
        while True:
            try:
                print("select which device you want to monitor by pressing the corresponding number")
                for i in range(len(Devices_List)):
                    print("{device_num} - {address} - {name} - signal = {signal}".format(device_num = i, address = Devices_List[i].address, name = Devices_List[i].name, signal = Devices_List[i].signal))
                user_input = input("waiting for user input\n: ")
                if user_input == "":
                    print("all devices selected")
                else:
                        use_device = Devices_List[int(user_input)]
                        Devices_List.clear()
                        Devices_List.append(use_device)
                        print("starting to log data from this device :\n {device_num} - {address} - {name} - signal = {signal}".format(device_num = 0, address = Devices_List[0].address, name = Devices_List[0].name, signal = Devices_List[0].signal))
                break
            except IndexError:
                os.system('cls')
                print("device selected doesn't exist, please select a device from the list below")
    if len(Devices_List) < 1:
        os.system('cls')
        print("\n\n\n!!! no devices found to monitor !!!\n\n\n")
        devices = await BleakScanner.discover()
        for d in devices:
            print(d)

async def List_Services(address):
    #ask the BLE device for it's services and try many often used services ID to get info on the device
    while True:
        try:
            async with BleakClient(address) as client:
                svcs = await client.get_services()
                print("Services:")
                for service in svcs:
                    service = str(service)
                    uuid = service.split(" ")
                    uuid = uuid.pop(0)
                    List_UUID.append([service, uuid])
                    print(service)
                startLog("\n\n" + address + "\n")
                for i in List_UUID:
                    try:
                        read_gatt = await client.read_gatt_char(i[1])
                        print(i[0], read_gatt)
                        startLog(i[0] + ";" + str(read_gatt) + "\n")
                    except Exception as e:
                        print("execption : ", e)
                break
        except Exception as e:
            print(e)

async def Get_Data(address, timespent, clock):
    #ask data of the BLE device from the specified sevices
    #you must modify this part to get other data from your device
    while True:
        async with BleakClient(address) as client:
            # Change the UUID to suit your needs
            Value = await client.read_gatt_char(UUID_BATTERY_LEVEL_CHARACTERISTIC)
            Value_int = (int.from_bytes(Value,byteorder='big'))
            startLog(";{time};;{timespent};{address};{Value_int};;".format(time = gettime(), timespent = timespent, address = address, Value_int = Value_int)) 
            print("{clock} -- {address} -- {b}".format(clock = clock, address = address, b = Value_int))
            break

def main():
    #a while loop to get data periodically from ervery BLE devices selected before
    asyncio.run(Scan_Discover())
    for Device in Devices_List:
            asyncio.run(List_Services(Device.address))
    sec_counter = time.time()
    while True:
        try:
            for Device in Devices_List:
                timespent = int(time.time() - sec_counter)
                clock = clockformat(timespent)
                asyncio.run(Get_Data(Device.address, timespent, clock))
        except Exception as e:
            startLog(";{time};{error};\n".format(time = gettime(), error = e))
            print(e)
        startLog("\n")

main()