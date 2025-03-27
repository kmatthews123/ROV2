import asyncio
import serial_asyncio

class Writer(asyncio.Protocol):
    def connection_made(self, transport):
        """Store the serial transport and schedule the task to send data.
        """
        self.transport = transport
        print('Writer connection created')
        asyncio.ensure_future(self.send())
        print('Writer.send() scheduled')

    def connection_lost(self, exc):
        print('Writer closed')

    async def send(self):
        """Send four newline-terminated messages, one byte at a time.
        """
        message = ['red', 'blue', 'orange', 'yellow', 'pink', 'purple', 'aqua', 'white']
        for item in message:
            await asyncio.sleep(0.5)
            self.transport.serial.write(item.encode())
            print(f'Writer sent: {item}')
        self.transport.close()

class Reader(asyncio.Protocol):
    def connection_made(self, transport):
        """Store the serial transport and prepare to receive data.
        """
        self.transport = transport
        self.buf = bytes()
        self.msgs_recvd = 0
        print('Reader connection created')

    def data_received(self, data):
        """Store characters until a newline is received.
        """
        self.buf += data
        if b'\n' in self.buf:
            lines = self.buf.split(b'\n')
            self.buf = lines[-1]  # whatever was left over
            for line in lines[:-1]:
                print(f'Reader received: {line.decode()}')
                self.msgs_recvd += 1
        if self.msgs_recvd == 4:
            self.transport.close()

    def connection_lost(self, exc):
        print('Reader closed')



# Reader, Writer

loop = asyncio.get_event_loop()
reader = serial_asyncio.create_serial_connection(loop, Reader, '/dev/ttyS0', baudrate=9600)
writer = serial_asyncio.create_serial_connection(loop, Writer, '/dev/ttyACM2', baudrate=115200)
asyncio.ensure_future(reader)
print('Reader scheduled')
asyncio.ensure_future(writer)
print('Writer scheduled')
loop.call_later(10, loop.stop)
loop.run_forever()
print('Done')