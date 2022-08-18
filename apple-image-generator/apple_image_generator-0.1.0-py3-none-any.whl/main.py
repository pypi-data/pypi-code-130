from genericpath import isdir
import typer
import os
import shutil
from PIL import Image

"""
    Fonctions :
    - Create directories and subdirectories
    image_name
        -> ios and ipados
        -> watchos
        -> macos
        -> appletv
        -> applecar
"""

def create_directories(name: str, architecture: str = "all"):
    """
        create directories based on architecture
    """
    realname = os.path.splitext(name)[0]
    if not os.path.exists(f"{realname}/"):
        architecture = ["mac", "iphone", "ipad", "watchos", "tvos", "carplay", "ios-marketing"]
        for directory in architecture:
            os.makedirs(f"{realname}/{directory}")

def verify_image(name: str) -> bool:
    """
        The master image need to be 1024x1024 size.
    """
    im = Image.open(f"{name}")
    width, height = im.size
    if not width == 1024:
        return False
    if not height == 1024:
        return False
    return True

def create_images(name: str):
    """
        Create images to different size based and the original image
        https://developer.apple.com/design/human-interface-guidelines/foundations/app-icons/

        TODO:
            - TvOS : 400x240@1x, 800x480@2x
            - Intégrer la génération automatique du Contents.json :
              https://developer.apple.com/library/archive/documentation/Xcode/Reference/xcode_ref-Asset_Catalog_Format/index.html#//apple_ref/doc/uid/TP40015170-CH18-SW1
            
    """
    resize_image(name, size=512, multiplier="1x", architecture="mac")
    resize_image(name, size=1024, multiplier="2x", architecture="mac")
    resize_image(name, size=1024, multiplier="3x", architecture="mac")
    resize_image(name, size=256, multiplier="1x", architecture="mac")
    resize_image(name, size=512, multiplier="2x", architecture="mac")
    resize_image(name, size=128, multiplier="1x", architecture="mac")
    resize_image(name, size=256, multiplier="2x", architecture="mac")
    resize_image(name, size=32, multiplier="1x", architecture="mac")
    resize_image(name, size=64, multiplier="2x", architecture="mac")
    resize_image(name, size=16, multiplier="1x", architecture="mac")
    resize_image(name, size=32, multiplier="2x", architecture="mac")

    resize_image(name, size=20, multiplier="1x", architecture="iphone")
    resize_image(name, size=29, multiplier="1x", architecture="iphone")
    resize_image(name, size=60, multiplier="1x", architecture="iphone")
    resize_image(name, size=60, multiplier="3x", architecture="iphone")
    resize_image(name, size=120, multiplier="2x", architecture="iphone")
    resize_image(name, size=180, multiplier="3x", architecture="iphone")
    resize_image(name, size=40, multiplier="1x", architecture="iphone")
    resize_image(name, size=40, multiplier="2x", architecture="iphone")
    resize_image(name, size=80, multiplier="2x", architecture="iphone")
    resize_image(name, size=120, multiplier="3x", architecture="iphone")
    resize_image(name, size=58, multiplier="2x", architecture="iphone")
    resize_image(name, size=87, multiplier="3x", architecture="iphone")
    resize_image(name, size=76, multiplier="1x", architecture="iphone")
    resize_image(name, size=76, multiplier="2x", architecture="iphone")
    resize_image(name, size=114, multiplier="3x", architecture="iphone")

    resize_image(name, size=80, multiplier="2x", architecture="ipad")
    resize_image(name, size=120, multiplier="3x", architecture="ipad")
    resize_image(name, size=167, multiplier="2x", architecture="ipad")
    resize_image(name, size=76, multiplier="1x", architecture="ipad")
    resize_image(name, size=152, multiplier="2x", architecture="ipad")
    resize_image(name, size=58, multiplier="2x", architecture="ipad")
    resize_image(name, size=76, multiplier="2x", architecture="ipad")
    resize_image(name, size=114, multiplier="3x", architecture="ipad")
    
    # Watch
    resize_image(name, size=87, multiplier="3x", architecture="watchos")

    # Watch 38
    resize_image(name, size=80, multiplier="2x", architecture="watchos")
    resize_image(name, size=48, multiplier="2x", architecture="watchos")
    resize_image(name, size=172, multiplier="2x", architecture="watchos")
    # Watch 40
    resize_image(name, size=88, multiplier="2x", architecture="watchos")
    resize_image(name, size=55, multiplier="2x", architecture="watchos")
    resize_image(name, size=196, multiplier="2x", architecture="watchos")
    # Watch 41
    resize_image(name, size=92, multiplier="2x", architecture="watchos")
    resize_image(name, size=58, multiplier="2x", architecture="watchos")
    resize_image(name, size=196, multiplier="2x", architecture="watchos")
    # Watch 42
    resize_image(name, size=80, multiplier="2x", architecture="watchos")
    resize_image(name, size=55, multiplier="2x", architecture="watchos")
    resize_image(name, size=196, multiplier="2x", architecture="watchos")
    # Watch 44
    resize_image(name, size=100, multiplier="2x", architecture="watchos")
    resize_image(name, size=58, multiplier="2x", architecture="watchos")
    resize_image(name, size=216, multiplier="2x", architecture="watchos")
    # Watch 45
    resize_image(name, size=102, multiplier="2x", architecture="watchos")
    resize_image(name, size=66, multiplier="2x", architecture="watchos")
    resize_image(name, size=234, multiplier="2x", architecture="watchos")

    # Apple Car
    resize_image(name, size=120, multiplier="2x", architecture="carplay")
    resize_image(name, size=180, multiplier="2x", architecture="carplay")
    resize_image(name, size=72, multiplier="3x", architecture="carplay")
    resize_image(name, size=108, multiplier="3x", architecture="carplay")


    resize_image(name, size=1024, multiplier="1x", architecture="ios-marketing")

def resize_image(name: str, size: int, multiplier: str, architecture: str):
    """
        resize images
    """
    im = Image.open(f"{name}")
    im_realname = os.path.splitext(name)[0]
    im_extension = os.path.splitext(name)[1]

    new_im = im.resize((size,size))
    new_im.save(f'{im_realname}/{architecture}/Icon-App-{size}x{size}@{multiplier}{im_extension}')

def generate_images(name: str) -> bool:
    if verify_image(name) is True:
        create_directories(name, "all")
        create_images(name)
    else:
        print("Sorry your image is not 1024x1024 size")
    
    
app = typer.Typer()

@app.command()
def generate(image: str):
    print(f"Generate {image}")
    generate_images(image)

@app.command()
def clear():
    print(f"Clear environment")
    
    for listobject in os.listdir("."):
        if os.path.isdir(f"{listobject}"):
            print(f"Deleting {listobject}")
            shutil.rmtree(f"{listobject}")

def run() -> None:
    app()

if __name__ == "__main__":
    app()
