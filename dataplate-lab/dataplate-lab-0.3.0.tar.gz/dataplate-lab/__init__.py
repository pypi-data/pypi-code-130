import json
from pathlib import Path

from ._version import __version__
from .handlers import setup_handlers



# HERE = Path(__file__).parent.resolve()

# with (HERE / "labextension" / "package.json")

# with (HERE / "package.json").open() as fid:
#     data = json.load(fid)

package_json = '''{
  "name": "dataplate-lab",
  "version": "0.1.0",
  "description": "DataPlate ML Platform extension for easy notebook operations",
  "keywords": [
    "jupyter",
    "jupyterlab",
    "jupyterlab-extension"
  ],
  "homepage": "https://github.com/Dataplate/dataplate-labextension",
  "bugs": {
    "url": "https://github.com/Dataplate/dataplate-labextension/issues"
  },
  "license": "BSD-3-Clause",
  "author": {
    "name": "DataPlate",
    "email": "noreply@dataplate.io"
  },
  "files": [
    "lib/**/*.{d.ts,eot,gif,html,jpg,js,js.map,json,png,svg,woff2,ttf}",
    "style/**/*.{css,js,eot,gif,html,jpg,json,png,svg,woff2,ttf}"
  ],
  "main": "lib/index.js",
  "types": "lib/index.d.ts",
  "style": "style/index.css",
  "repository": {
    "type": "git",
    "url": "https://github.com/Dataplate/dataplate-labextension.git"
  },
  "scripts": {
    "build": "jlpm build:lib && jlpm build:labextension:dev",
    "build:prod": "jlpm clean && jlpm build:lib && npm pack .",
    "build:labextension": "jupyter labextension build .",
    "build:labextension:dev": "jupyter labextension build --development True .",
    "build:lib": "tsc",
    "clean": "jlpm clean:lib",
    "clean:lib": "rimraf lib tsconfig.tsbuildinfo",
    "clean:lintcache": "rimraf .eslintcache .stylelintcache",
    "clean:labextension": "rimraf dataplate-lab/labextension",
    "clean:all": "jlpm clean:lib && jlpm clean:labextension && jlpm clean:lintcache",
    "eslint": "jlpm eslint:check --fix",
    "eslint:check": "eslint . --cache --ext .ts,.tsx",
    "install:extension": "jlpm build",
    "lint": "jlpm stylelint && jlpm prettier && jlpm eslint",
    "lint:check": "jlpm stylelint:check && jlpm prettier:check && jlpm eslint:check",
    "prettier": "jlpm prettier:base --write --list-different",
    "prettier:base": "prettier \\"**/*{.ts,.tsx,.js,.jsx,.css,.json,.md}\\"",
    "prettier:check": "jlpm prettier:base --check",
    "stylelint": "jlpm stylelint:check --fix",
    "stylelint:check": "stylelint --cache \\"style/**/*.css\\"",
    "watch": "run-p watch:src watch:labextension",
    "watch:src": "tsc -w",
    "watch:labextension": "jupyter labextension watch ."
  },
  "dependencies": {
    "@jupyterlab/application": "^3.4.3",
    "@jupyterlab/apputils": "^3.4.3",
    "@jupyterlab/notebook": "^3.4.3",
    "@lumino/coreutils": "^1.11.0",
    "@lumino/messaging": "^1.10.0",
    "classnames": "^2.2.6",
    "codemirror": "5.63",
    "react": "^17.0.1",
    "react-router-dom": "^5.1.2",
    "sanitize-html": "2.5.3",
    "url-parse": "1.5.3"
  },
  "devDependencies": {
    "@babel/core": "^7.0.0",
    "@babel/preset-env": "^7.0.0",
    "@jupyterlab/builder": "^3.1.0",
    "@jupyterlab/testutils": "^3.0.0",
    "@types/classnames": "^2.3.0",
    "@types/codemirror": "^0.0.109",
    "@typescript-eslint/eslint-plugin": "^4.8.1",
    "@typescript-eslint/parser": "^4.8.1",
    "eslint": "^7.14.0",
    "eslint-config-prettier": "^6.15.0",
    "eslint-plugin-import": "^2.24.2",
    "eslint-plugin-json": "^2.1.1",
    "eslint-plugin-prettier": "^3.1.4",
    "eslint-plugin-react": "^7.26.1",
    "eslint-plugin-react-hooks": "^4.2.0",
    "mkdirp": "^1.0.3",
    "npm-run-all": "^4.1.5",
    "prettier": "^2.1.1",
    "rimraf": "^3.0.2",
    "strip-ansi": "^6.0.1",
    "typescript": "~4.1.3"
  },
  "resolutions": {
    "codemirror": "5.63",
    "sanitize-html": "2.5.3",
    "strip-ansi": "6.0.1",
    "url-parse": "1.5.3"
  },
  "sideEffects": [
    "style/*.css",
    "style/index.js"
  ],
  "styleModule": "style/index.js",
  "publishConfig": {
    "access": "public"
  },
  "jupyterlab": {
    "discovery": {
      "server": {
        "managers": [
          "pip"
        ],
        "base": {
          "name": "dataplate-lab"
        }
      }
    },
    "extension": true,
    "outputDir": "dataplate-lab/labextension"
  }
}'''

data = json.loads(package_json)

def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": data["name"]
    }]



def _jupyter_server_extension_points():
    return [{
        "module": "dataplate-lab"
    }]


def _load_jupyter_server_extension(server_app):
    """Registers the API handler to receive HTTP requests from the frontend extension.

    Parameters
    ----------
    server_app: jupyterlab.labapp.LabApp
        JupyterLab application instance
    """
    setup_handlers(server_app.web_app)
    server_app.log.info("Registered {name} server extension".format(**data))


# For backward compatibility with notebook server - useful for Binder/JupyterHub
load_jupyter_server_extension = _load_jupyter_server_extension

