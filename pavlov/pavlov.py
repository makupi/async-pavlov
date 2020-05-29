import asyncio
import hashlib
import json


class InvalidPassword(Exception):
    pass


class PavlovRCON:
    def __init__(self, ip, port, password):
        self.ip = ip
        self.port = port
        self.password = hashlib.md5(password.encode()).hexdigest()
        self.reader, self.writer = None, None

    async def _connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.ip, self.port)

    async def _disconnect(self):
        self.writer.close()
        await self.writer.wait_closed()

    async def _send(self, data):
        self.writer.write(data.encode())
        await self.writer.drain()

    async def _recv(self):
        try:
            data = await self.reader.readuntil(separator=b"\r\n")
            data = data.decode()
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                pass
            return data
        except Exception as ex:
            print(f"EXCEPTION <_recv>: {ex}")
            return None

    async def _auth(self):
        await self._send(self.password)
        data = await self._recv()
        if "Authenticated=1" not in data:
            raise InvalidPassword

    async def send(self, command, wait_response=True):
        await self._connect()
        await self._auth()
        await self._send(command)
        data = None
        if wait_response:
            data = await self._recv()
        await self._disconnect()
        return data
