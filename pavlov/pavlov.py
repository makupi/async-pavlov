import asyncio
import hashlib
import json


class InvalidPassword(Exception):
    pass


class PavlovRCON:
    def __init__(self, ip, port, password, timeout=5):
        self.ip = ip
        self.port = port
        self.password = hashlib.md5(password.encode()).hexdigest()
        self.timeout = timeout
        self.reader, self.writer = None, None

    async def open(self):
        if not self.is_connected():
            await self._connect()

    async def close(self):
        if self.is_connected():
            await self._disconnect()

    def is_connected(self):
        if self.writer and not self.writer.is_closing():
            return True
        return False

    async def send(self, command, wait_response=True, auto_close=False):
        if not self.is_connected():
            await self._connect()
        await self._send(command)
        data = None
        if wait_response:
            data = await self._recv()
        if auto_close:
            await self._disconnect()
        return data

    async def _send(self, data):
        self.writer.write(data.encode())
        await asyncio.wait_for(self.writer.drain(), self.timeout)

    async def _auth(self):
        await self._send(self.password)
        data = await self._recv()
        if "Authenticated=1" not in data:
            raise InvalidPassword

    async def _connect(self):
        self.reader, self.writer = await asyncio.wait_for(
            asyncio.open_connection(self.ip, self.port), self.timeout
        )
        await self._auth()

    async def _disconnect(self):
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

    async def _recv(self):
        try:
            data = await asyncio.wait_for(
                self.reader.readuntil(separator=b"\r\n"), self.timeout
            )
            data = data.decode()
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                pass
            return data
        except Exception as ex:
            print(f"EXCEPTION <_recv>: {ex}")
            return None
