from main import main
from watchgod import run_process
import asyncio

def run_main():
    asyncio.run(main())

if __name__ == "__main__":
    run_process('.', run_main)