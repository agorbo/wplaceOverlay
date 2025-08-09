import http.server
import socketserver
from curl_cffi import requests
from PIL import Image
import json
import os.path
import shutil

PORT = 8000

def updateImage():

    with open("config.json") as f:
        tiles = json.load(f)

    missing_pix = 0

    for tile in tiles:

        basepath = 'files/s0/tiles/{}/{}.png'.format(tile[0], tile[1])
        blueprintpath = 'blueprints/{}/{}blueprint.png'.format(tile[0], tile[1])

        image_url = "https://backend.wplace.live/files/s0/tiles/{}/{}.png".format(tile[0], tile[1])
        img_data = requests.get(image_url, impersonate="chrome").content

        os.makedirs(os.path.dirname(basepath), exist_ok=True)
        with open(basepath, 'wb') as handler:
            handler.write(img_data)

        if not (os.path.isfile(blueprintpath)):
            os.makedirs(os.path.dirname(blueprintpath), exist_ok=True)
            shutil.copyfile(basepath, blueprintpath)

        basepic = Image.open(basepath).convert('RGBA')
        basepix = basepic.load()

        blueprint = Image.open(blueprintpath).convert('RGBA')
        blueprintpix = blueprint.load()

        width, height = basepic.size
        identical = True
        xmin = 999
        xmax = 0
        ymin = 999
        ymax = 0
        diff = []

        for x in range(width):
            for y in range(height):
                if blueprintpix[x, y] != (0,0,0,0) and blueprintpix[x,y] != basepix[x,y]:
                    missing_pix += 1
                    bppix = blueprintpix[x,y]
                    identical = False
                    xmin = min(x, xmin)
                    xmax = max(x, xmax)
                    ymin = min(y, ymin)
                    ymax = max(y, ymax)
                    diff.append([(x, y), (bppix[0], bppix[1], bppix[2], 255)])

        if not identical:
            for x in range(xmin-4,xmax+5):
                for y in range(ymin-4,ymax+5):
                    if x < 0 or y < 0 or x > 999 or y > 999:
                        continue
                    basepix[x, y] = (255, 0, 255, 80)
            for el in diff:
                basepix[el[0]] = el[1]
            basepic.save(basepath, 'PNG')
    print("Updated diff. Missing pixels: {} ~ {} hours to regenerate".format(missing_pix, round(missing_pix / 2 / 60,1)))

# Override server class to send allow-CORS header
class CORSHandler(http.server.SimpleHTTPRequestHandler):
    def send_response(self, *args, **kwargs):
        http.server.SimpleHTTPRequestHandler.send_response(self, *args, **kwargs)
        self.send_header('Access-Control-Allow-Origin', '*')

with socketserver.TCPServer(("", PORT), CORSHandler) as httpd:
    try:
        while True:
            updateImage()
            httpd.timeout = 60
            httpd.handle_request()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, exiting.")
        httpd.server_close()

