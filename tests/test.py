from math import ceil
import serial as serial
from multiprocessing import Queue
import time
import threading
from prettytable import PrettyTable
from prettytable import ALL as ALL

#region Test Functions

receivedTestData = ''

def utf8len(s):
    return len(s.encode('utf-8'))

def test():
  messageFile = open('tests/send_message.txt', 'r')
  test_data = messageFile.read()

  dataSize = utf8len(test_data)
  print("Size: ", dataSize)

  start_time = time.time()
  sendDataTest(test_data)
  ex_time = (time.time() - start_time)

  print("--- Testing Finished ---")

  speed = dataSize / ex_time
  missRate = missesCount / sendAttemps
  packageMissRate = packageMissesCount / packageSendAttemps

  print("Received data:\n%s\n---" % (receivedTestData,))

  t = PrettyTable(header=False)
  t.hrules = ALL
  t.title = 'Results'
  t.add_row(['Size', (str)(dataSize) + ' Bytes'])
  t.add_row(['Time', (str)(round(ex_time, 4)) + ' seconds'])
  t.add_row(['Speed', (str)(round(speed, 4)) + ' B\s'])
  t.add_row(['Package miss rate', packageMissRate])
  t.add_row(['Package misses count', packageMissesCount])
  t.add_row(['Package send attemps', packageSendAttemps])
  t.add_row(['Byte miss rate', missRate])
  t.add_row(['Byte misses count', missesCount])
  t.add_row(['Byte send attemps', sendAttemps])
  print(t)


def sendDataTest(sendingData: str):
  """
  Send data string by UART. Switching from one UART to another during transaction.
  """
  numOfBytes = ceil(len(sendingData) / 8)
  print("Raw data bytes: ", numOfBytes)
  # split data on bytes
  i = 0
  while i < numOfBytes:
    if(i > 5):
      if not sendByteOfDataPackage(uart3Addr, sendingData[8 * i : 8 * i + 8], True):
        i -= 1
    else:
      if not sendByteOfDataPackage(uart5Addr, sendingData[8 * i : 8 * i + 8], True):
        i -= 1
    i += 1

def sendData(addr: str, sendingData: str):
  """
  Send data string by UART
  """
  numOfBytes = ceil(len(sendingData) / 8)
  # split data on bytes
  for i in range(numOfBytes):
    if not sendByteOfDataPackage(addr, sendingData[8 * i : 8 * i + 8], True):
      i -= 1

def sendByteOfDataPackage(uart_addr: str, data: str, test_read = True):
  """
  Sending one byte package by UART. Set test_read to true for auto test.
  """
  global packageSendAttemps
  packageSendAttemps += 1

  package = '0'
  result = False

  data = data.ljust(8)
  package += uart_addr + data + '1'

  queue = Queue() # start queue for sharing data from reading thread
  if test_read:
    queue.put(ret)
    thread = threading.Thread(target=receivePackage, args=(uart_addr, data, queue), daemon=True)
    thread.start()

  
  print("\n> Sending byte...")
  DebugLog("---------------")
  uart4.open()
  while result == False:
    result = sendPackage(package)
  uart4.close()

  if test_read:
    thread.join(3)
    
    receivedData = queue.get()['data'] # get read data from queue
    DebugLog("Send data: ", data)
    DebugLog("Receive data: ", receivedData)
    DebugLog("Current uart address: ", uart_addr)

    # analyze the response
    if receivedData.replace('\\n', '\n') == data:
      global receivedTestData
      receivedTestData += receivedData
      print(" \U00002705 Package sent successfully! ")
      return True
    else:
      global packageMissesCount
      packageMissesCount += 1
      print(" \U0000274C Package failed! ")
      return False
  return True

def sendOneBit(dataBit: bytes, bitId = -1):
  """
  Write one bit to UART stream
  """
  lastBit = bitId == 11
  # Send Bit:
  uart4.write(dataBit)

  start_time = time.time()
  while 1:
    ans = uart4.read() # Get answer

    if(ans != b''):        #If we got data
      DebugLog('Less then ', UART4_TIMEOUT)
      break    
    else:
      if(lastBit):
        if (time.time() - start_time) > UART4_TIMEOUT_LASTBIT:
          DebugLog((time.time() - start_time))
          break
      else:
        if (time.time() - start_time) > UART4_TIMEOUT:
          DebugLog((time.time() - start_time))
          break
      
  if(lastBit or ans != b''): # Check answer
    DebugLog("--> Answer: ", ans)

    if ans == b'1':
      uart4.timeout = UART4_READ_TIMEOUT
      return True # Success
    else:
      if lastBit:
        uart4.timeout = UART4_READ_TIMEOUT_ERROR
      return False


def read_uart():
    uart3.open()
    while True:
      buf = str(uart3.read())
      print("uart3 > Receive bit: ", buf)
      
    uart3.close()

def receivePackage(uart_addr: str, data: str, queue):
  """
  Connect to reader UARTs and get their incoming data to compare with writer data
  """
  data_len = len(data)
  received_len = 0
  receivedData = ''
  bit: bytes = b''

  ad = 0

  if uart_addr == uart3Addr:
    uart3.open()
    while True:
      buf = str(uart3.read())
      
      if buf != "b''":
        receivedData += buf[2:-1]
        DebugLog("uart3 > Receive bit: ", buf, '  receivedData: ', receivedData)
        DebugLog("received_len: ", received_len)
        if data_len == received_len + 1:
          break
        received_len += 1
    uart3.close()

  if uart_addr == uart5Addr:
    uart5.open()
    while True:
      buf = str(uart5.read())
      
      if buf != "b''":
        receivedData += buf[2:-1]
        DebugLog("uart3 > Receive bit: ", buf, '  receivedData: ', receivedData)
        DebugLog("received_len: ", received_len)
        if data_len == received_len + 1:
          break
        received_len += 1
    uart5.close()

  #receivedData = receivedData.replace('b', '').replace("'",'')
  r = queue.get()
  r['data'] = receivedData
  queue.put(r)
  return 0

def sendPackage(package):
  """
  Send package, until has positive answer
  """
  for i in range(len(package)):
      bit: bytes = bytes(package[i], 'utf-8')
      
      DebugLog("Send: ", bit)
      global sendAttemps
      global missesCount
      DebugLog("sendAttemps: ", sendAttemps)
      DebugLog("missesCount: ", missesCount)
      sendAttemps += 1
      if sendOneBit(bit, i) == False:
        # try sending package again
        missesCount += 1
        return False

  uart4.close()
  # package sent successfully
  return True

#endregion

#region Debug
isDebugMode = False

def DebugLog(*args):
  if isDebugMode:
    log = ''
    for arg in args:
      log += str(arg)
    print(log)

#endregion

#region UART Setup
# UART Addresses
uart3Addr = '01'
uart5Addr = '00'

# UART 4 Writer

UART4_TIMEOUT             = 0.0000001
UART4_TIMEOUT_LASTBIT     = 0.03       # default 0.058

UART4_READ_TIMEOUT_ERROR  = 0.011       # default 0.02
UART4_READ_TIMEOUT        = 0.00000001

uart4 = serial.Serial()
uart4.baudrate = 115200
uart4.port = 'COM5'
uart4.timeout = UART4_READ_TIMEOUT

# UART 5 Reader
uart5 = serial.Serial()
uart5.baudrate = 115200
uart5.port = 'COM3'
uart5.timeout = 0.000001

# UART 5 Reader
uart3 = serial.Serial()
uart3.baudrate = 115200
uart3.port = 'COM4'
uart3.timeout = 0.000001
#endregion

#region Main
# return value from read Process
ret = { 'data': '' }

sendAttemps = 0
missesCount = 0
packageSendAttemps = 0
packageMissesCount = 0
missRate = 0

if __name__ == '__main__':
  test()
#endregion