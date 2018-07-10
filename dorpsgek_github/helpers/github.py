import os

from dorpsgek_github.config import REFERENCE_REPOSITORY_FOLDER
from dorpsgek_github.helpers.subprocess import run_command


async def download_github_repository(repository, ref, clone_url, work_folder):
    reference_folder = f"{REFERENCE_REPOSITORY_FOLDER}/{repository}"
    repository_folder = f"{work_folder}/source"
    repository_tarball = f"{work_folder}/artifact/source.tar.gz"

    if not os.path.exists(reference_folder):
        await run_command(
            "git",
            "clone",
            "--mirror",
            clone_url,
            reference_folder,
        )
    else:
        await run_command(
            "git",
            "fetch",
            "--all",
            cwd=reference_folder,
        )

    await run_command(
        "git",
        "clone",
        "--reference",
        reference_folder,
        clone_url,
        repository_folder,
    )

    await run_command(
        "git",
        "checkout",
        ref,
        cwd=repository_folder
    )

    await run_command(
        "tar",
        "zcf",
        repository_tarball,
        ".",
        cwd=repository_folder,
    )
