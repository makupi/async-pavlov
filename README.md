# async-pavlov
Async wrapper for pavlov RCON commands

# Requirements
Python 3.7+

# Install

```shell
pip install async-pavlov
```

# Usage
```py
import asyncio
from pavlov import PavlovRCON

async def main():
    pavlov = PavlovRCON("127.0.0.1", 9104, "password")
    data = await pavlov.send("ServerInfo")
    print(data)

asyncio.run(main())
```