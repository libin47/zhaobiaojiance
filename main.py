# This is a sample Python script.
from craw import craw
from send import send
import asyncio

async def main():
    await asyncio.gather(craw(), send())

if __name__ == '__main__':
    asyncio.run(main())