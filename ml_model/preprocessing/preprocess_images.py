import os
import shutil
import numpy as np
from PIL import Image


def resize_image(img, size):
    # resize the image so the longest dimension matches our target size
    img.thumbnail(size, Image.ANTIALIAS)

    # Create a new square white background image
    newimg = Image.new("RGB", size, (255, 255, 255))

    # Paste the resized image into the center of the square background
    if np.array(img).shape[2] == 4:
        # If the source is in RGBA format,
        # use a mask to eliminate the transparency
        newimg.paste(
            img,
            (int((size[0] - img.size[0]) / 2),
             int((size[1] - img.size[1]) / 2)),
            mask=img.split()[3])
    else:
        newimg.paste(
            img,
            (int((size[0] - img.size[0]) / 2),
             int((size[1] - img.size[1]) / 2)))

    return newimg


# Create resized copies of all of the source images
def resize_images(indir, outdir, preprocessing_args):
    size = (preprocessing_args['image_size']['x'],
            preprocessing_args['image_size']['y'])
    print(f"indir: {indir}")
    print(f"outdir: {outdir}")
    if (os.path.exists(indir)):
        print("indir exists")
    else:
        print("indir doesn't exit")

    if os.path.exists(outdir):
        print("outdir exists, delete all files")
        for filename in os.listdir(outdir):
            file_path = os.path.join(outdir, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

    # Loop through each subfolder in the input dir
    for root, dirs, filenames in os.walk(indir):
        for d in dirs:
            print('processing folder ' + d)
            # Create a matching subfolder in the output dir
            saveFolder = os.path.join(outdir, d)
            if not os.path.exists(saveFolder):
                os.makedirs(saveFolder)
            # Loop through the files in the subfolder
            files = os.listdir(os.path.join(root, d))
            for f in files:
                # Open the file
                imgFile = os.path.join(root, d, f)
                print("reading " + imgFile)
                img = Image.open(imgFile)
                # Create a resized version and save it
                proc_img = resize_image(img, size)
                saveAs = os.path.join(saveFolder, f)
                print("writing " + saveAs)
                proc_img.save(saveAs)


def main():
    in_dir = 'data/gear_images/raw'
    out_dir = 'data/processed'
    preprocessing_args = {
        'image_size': {'x': 128, 'y': 128},
        'batch_size': 30
    }
    resize_images(in_dir, out_dir, preprocessing_args)  # NOQA: E501


if __name__ == '__main__':
    main()
