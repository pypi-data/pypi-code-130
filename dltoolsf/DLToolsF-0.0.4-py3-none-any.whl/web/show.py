import tornado, os, asyncio, sys
from tornado.web import RequestHandler, StaticFileHandler

def get_images(root):
    li_string = '<ul class="pictures">\n'
    for each_image in os.listdir(root):
        if each_image.endswith(('.jpg', '.png', '.bmp')):
            one_image = '\t\t\t\t<li><img data-original="images/{}" src="images/{}" alt="{}"></li>\n'.format(each_image, each_image, each_image)
            li_string += one_image
    li_string += "\t\t\t</ul>"
    return li_string

class IndexHandler(RequestHandler):
    def get(self):
        self.render('index.html',
        webtitle=os.path.realpath(os.curdir),
        images=get_images(os.path.realpath(os.curdir)))

app = tornado.web.Application(
    [
    (r"/", IndexHandler),
    (r'^/images/(.*)$', StaticFileHandler, {"path": os.path.realpath(os.curdir)}),
    (r'^/css/(.*)$', StaticFileHandler, {"path": os.path.realpath(os.path.dirname(__file__)) + "/css/"}),
    (r'^/js/(.*)$', StaticFileHandler, {"path": os.path.realpath(os.path.dirname(__file__)) + "/js/"}),
    ],
)

async def main():
    app.listen(int(sys.argv[-1]))
    print("Server is running on ip:port 127.0.0.1:{}".format(sys.argv[-1]))
    await asyncio.Event().wait()

def run():
    asyncio.run(main())

if __name__ == "__main__":
    try:
        if not (0 <= int(sys.argv[-1]) <= 65535):
            raise ValueError("Port number is not valid")
    except:
        print("Port number is not valid or not given")
        sys.exit(1)

    run()