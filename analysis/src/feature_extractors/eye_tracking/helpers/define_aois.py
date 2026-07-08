"""
Interactive AOI annotation tool.

Step 02 of the eye tracking pipeline.

Draw rectangular AOIs on a stimulus image and export
normalized coordinates to CSV.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import cv2

from configs.paths import METADATA_DIR

# ==========================================================
# AOIs
# ==========================================================

OLD_AOIS = [

    "mother" ,
    "children"

]

NEW_AOIS = [
    "father",
    "mother",
    "children",
    "dog",
]

# ==========================================================
# Globals
# ==========================================================

drawing = False

ix = -1
iy = -1

cx = -1
cy = -1

current_index = 0

aois = []
image = None
canvas = None
image_name = None
aoi_names = []

# ==========================================================
# Helpers
# ==========================================================

def current_aoi():
    if current_index >= len(aoi_names):
        return None
    return aoi_names[current_index]


def redraw():
    global canvas
    canvas = image.copy()
    for row in aois:
        h, w = image.shape[:2]

        x1 = int(row["x_min"] * w)
        y1 = int(row["y_min"] * h)

        x2 = int(row["x_max"] * w)
        y2 = int(row["y_max"] * h)

        cv2.rectangle(
            canvas,
            (x1, y1),
            (x2, y2),
            (0,255,0),
            2,
        )

        cv2.putText(
            canvas,
            row["aoi"],
            (x1,y1-5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0,255,0),
            2,
        )

    title = current_aoi()

    if title is None:

        title = "Finished - Press ESC"

    cv2.putText(

        canvas,

        f"Draw: {title}",

        (20,40),

        cv2.FONT_HERSHEY_SIMPLEX,

        1,

        (255,0,0),

        2,

    )

    # ==========================================================
# Mouse callback
# ==========================================================

def mouse_callback(event, x, y, flags, param):

    global drawing
    global ix
    global iy
    global cx
    global cy
    global current_index

    if current_aoi() is None:

        return

    if event == cv2.EVENT_LBUTTONDOWN:

        drawing = True

        ix = x
        iy = y

        cx = x
        cy = y

    elif event == cv2.EVENT_MOUSEMOVE and drawing:

        cx = x
        cy = y

        redraw()

        cv2.rectangle(

            canvas,

            (ix, iy),

            (cx, cy),

            (0, 0, 255),

            2,

        )

    elif event == cv2.EVENT_LBUTTONUP:

        drawing = False

        cx = x
        cy = y

        redraw()

        cv2.rectangle(

            canvas,

            (ix, iy),

            (cx, cy),

            (0, 0, 255),

            2,
        )
        h, w = image.shape[:2]

        x1 = min(ix, cx)
        x2 = max(ix, cx)

        y1 = min(iy, cy)
        y2 = max(iy, cy)

        aois.append(
            {
                "image": image_name,
                "aoi": current_aoi(),
                "x_min": x1 / w,
                "y_min": y1 / h,
                "x_max": x2 / w,
                "y_max": y2 / h,
            }
        )

        current_index += 1
        redraw()


# ==========================================================
# Save
# ==========================================================

def save_csv():

    METADATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output = (
        METADATA_DIR /
        f"aois_{image_name}.csv"
    )

    with open(
        output,
        "w",
        newline="",
        encoding="utf-8",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "image",
                "aoi",
                "x_min",
                "y_min",
                "x_max",
                "y_max",
            ],

        )

        writer.writeheader()
        writer.writerows(
            aois

        )

    print()
    print(f"Saved {len(aois)} AOIs")
    print(output)

    # ==========================================================
# Main
# ==========================================================

def main():
    global image
    global canvas
    global image_name
    global aoi_names
    global current_index

    parser = argparse.ArgumentParser(

        description="Interactive AOI annotation tool."

    )

    parser.add_argument(

        "image",

        type=Path,

        help="Path to stimulus image.",

    )

    args = parser.parse_args()

    image_path = args.image

    if not image_path.exists():

        raise FileNotFoundError(image_path)

    stem = image_path.stem.lower()

    if "nueva" in stem:

        image_name = "lamina_nueva"

        aoi_names = NEW_AOIS

    elif "vieja" in stem:

        image_name = "lamina_vieja"

        aoi_names = OLD_AOIS

    else:

        raise ValueError(

            "Image name must contain 'nueva' or 'vieja'."

        )

    image = cv2.imread(

        str(image_path)

    )

    if image is None:

        raise RuntimeError(

            f"Could not load {image_path}"

        )

    redraw()

    cv2.namedWindow(

        "AOI Annotator",

        cv2.WINDOW_NORMAL,

    )

    cv2.setMouseCallback(

        "AOI Annotator",

        mouse_callback,

    )

    print()

    print("=" * 60)

    print("AOI ANNOTATOR")

    print("=" * 60)

    print()

    print(f"Image : {image_name}")

    print()

    print("Controls")

    print("--------")

    print("Draw rectangle with the mouse")

    print("Backspace -> delete last AOI")

    print("ESC -> save and exit")

    print()

    while True:

        cv2.imshow(

            "AOI Annotator",

            canvas,

        )

        key = cv2.waitKey(20) & 0xFF

        if key == 27:

            break

        elif key in (8, 127):

            if len(aois) > 0:

                aois.pop()

                current_index -= 1

                redraw()

    cv2.destroyAllWindows()

    save_csv()


if __name__ == "__main__":

    main()

