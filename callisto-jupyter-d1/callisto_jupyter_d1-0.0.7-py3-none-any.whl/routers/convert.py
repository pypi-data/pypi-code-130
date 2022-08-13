import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
import traceback

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.logger import logger
from jupytext.cli import jupytext  # type: ignore
from starlette.responses import StreamingResponse

from ..d1_response import D1Response

COPY_BUFSIZE = 64 * 1024

router = APIRouter(default_response_class=D1Response)


@router.post(
    "/rmd_to_ipynb",
    status_code=status.HTTP_200_OK,
)
def convert_rmd_to_ipynb(file: UploadFile = File(...)):

    out_file = NamedTemporaryFile(mode="rb", suffix=".ipynb")
    try:

        with NamedTemporaryFile(mode="wb", suffix=".Rmd") as f:
            shutil.copyfileobj(file.file, f)
            f.seek(0)
            jupytext(
                [
                    f.name,
                    "--from",
                    "rmarkdown",
                    "--to",
                    "notebook",
                    "--output",
                    out_file.name,
                    "--set-kernel",
                    "ir",
                ]
            )
    except Exception as e:
        logger.info(
            f"Failed to convert Rmd file to ipynb {e} \n"
            f"{traceback.format_exc()}"
        )
        msg = "Failed to convert Rmd file to ipynb"
        if isinstance(e, KeyError):
            msg += ", do you have an R kernel installed and added to the kernelspecs?"
        raise HTTPException(400, msg)

    filename = file.filename
    if filename is None or len(filename) < 1:
        filename = "notebook"
    headers = {
        "content-disposition": f'attachment; filename="{Path(filename).stem}.ipynb"'
    }
    out_file.seek(0)

    def iterfile():
        yield from out_file

    return StreamingResponse(
        content=iterfile(),
        headers=headers,
        media_type="application/x-ipynb+json",
    )
