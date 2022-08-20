import cv2

from .parser import get_parser
from scicam.io.cameras.setup import setup

def run(camera, queue=None, preview=False):

    try:
        for timestamp, all_rois in camera:

            for frame in all_rois:
                print(
                    "Basler camera reads: ",
                    timestamp,
                    frame.shape,
                    frame.dtype,
                    camera.computed_framerate,
                )
                if queue is not None:
                    queue.put((timestamp, frame))

                frame = cv2.resize(
                    frame,
                    (frame.shape[1] // 3, frame.shape[0] // 3),
                    cv2.INTER_AREA,
                )
                if preview:
                    cv2.imshow("Basler", frame)
                    if cv2.waitKey(1) == ord("q"):
                        break

    except KeyboardInterrupt:
        return


def setup_and_run(args, **kwargs):

    camera = setup(args)
    maxframes = getattr(args, "maxframes", None)
    run(camera, preview=args.preview, **kwargs)


def main(args=None, ap=None):
    """
    Initialize a BaslerCamera
    """

    if args is None:
        ap = get_parser(ap=ap)
        args = ap.parse_args()

    setup_and_run(args)


if __name__ == "__main__":
    main()
