import asyncio
import shlex


class CommandError(Exception):
    pass


async def run_command(command, cwd=None):
    process = await asyncio.create_subprocess_exec(
        *shlex.split(command),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd,
    )

    return_code = await process.wait()
    if return_code != 0:
        stderr = []
        while True:
            line = await process.stderr.readline()
            if not line:
                break
            stderr.append(line.decode())

        raise CommandError(return_code, " ".join(command), "\n".join(stderr))
