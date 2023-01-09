from math import ceil
import serial
import os
from multiprocessing import Queue
from multiprocessing import Process

def test():
  test_data = 'hello world! today temperature is -12^C. ___'
  sendDataTest(test_data)

def sendDataTest(sendingData: str):
  """
  Send data string by UART. Switching from one UART to another during transaction.
  """
  numOfBytes = ceil(len(sendingData) / 8)
  # split data on bytes
  for i in range(numOfBytes):
    if(i > 2):
      sendByteOfDataPackage(uart3Addr, sendingData[8 * i : 8 * i + 8])
    else:
      sendByteOfDataPackage(uart5Addr, sendingData[8 * i : 8 * i + 8])


def sendData(addr: str, sendingData: str):
  """
  Send data string by UART
  """
  numOfBytes = ceil(len(sendingData) / 8)
  # split data on bytes
  for i in range(numOfBytes):
    sendByteOfDataPackage(addr, sendingData[8 * i : 8 * i + 8])


def sendByteOfDataPackage(uart_addr: str, data: str, test_read = True):
  """
  Sending one byte package by UART. Set test_read to true for auto test.
  """

  package = '0'
  result = False

  receivedData = ''
  data = data.ljust(8)
  package += uart_addr + data + '1'

  queue = Queue() # start queue for sharing data from reading thread
  if test_read:
    queue.put(ret)
    p1 = Process(target=receivePackage, args=(uart_addr, data, queue), daemon=True)
    p1.start()

  print("\nWriting byte...")
  print("---------------")
  print("Send data: ", data)
  while result == False:
    result = sendPackage(package)

  if test_read:
    p1.join()
    receivedData = queue.get()['data'] # get read data from queue
    print("Receive data: ", receivedData)
    print("Current uart address: ", uart_addr)

    # analaze the response
    if receivedData == data:
      print(" \U00002705 Package sent successfully! ")
    else:
      print(" \U0000274C Package failed! ")

def sendOneBit(dataBit: bytes, bitId = -1):
  dataBit = bytes(dataBit, 'utf-8')
  uart4.open()
  
  writeResult = True
  hasAnswer = False

  # Send Bit:
  uart4.write(dataBit)
  ans = uart4.read() # Get answer
  
  if ans != b'':
    hasAnswer = True

  if(bitId == 11 or hasAnswer): # Check answer
    print("--> Answer: ", ans)

    if ans == b'1':
      writeResult = True
    else:
      writeResult = False

  uart4.close()
  return writeResult

def receivePackage(uart_addr: str, data: str, queue):
  data_len = len(data)
  received_len = 0
  receivedData = ''
  bit: bytes = b''

  if uart_addr == uart3Addr:
    uart3.open()
    while True:
      buf = str(uart3.read())
      #print("buf: ", buf)
      
      if buf != "b''":
        receivedData += buf
        #print("received_len: ", received_len)
        if data_len == received_len + 1:
          break
        received_len += 1
    uart3.close()

  if uart_addr == uart5Addr:
    uart5.open()
    while True:
      buf = str(uart5.read())
      #print("buf: ", buf)
      
      if buf != "b''":
        receivedData += buf
        #print("received_len: ", received_len)
        if data_len == received_len + 1:
          break
        received_len += 1
    uart5.close()

  print("sent data:     ", data)
  print("received data: ", receivedData)
  receivedData = receivedData.replace('b', '').replace("'",'')
  r = queue.get()
  r['data'] = receivedData
  queue.put(r)

def sendPackage(package):
  for i in range(len(package)):
      bit: bytes = package[i]
      
      print("Send: ", bit)
      if sendOneBit(bit, i) == False:
        return False
        break
      else:
        return True

uart3Addr = '01'
uart5Addr = '00'

ret = { 'data': '' }

# Clear console
clear = lambda: os.system('cls')
clear()

# UART 4 Writer
uart4 = serial.Serial()
uart4.baudrate = 9600
uart4.port = 'COM5'
uart4.timeout = 1

# UART 5 Reader
uart5 = serial.Serial()
uart5.baudrate = 115200
uart5.port = 'COM3'
uart5.timeout = 1

# UART 5 Reader
uart3 = serial.Serial()
uart3.baudrate = 115200
uart3.port = 'COM4'
uart3.timeout = 1

if __name__ == '__main__':
  test()