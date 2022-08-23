import pathlib
class Buildpack:
    def __init__(self, project):
        self.project = project

    def parseScript(self, shonkufile):
        file = open(shonkufile)
        lines = file.read().split("\n")
        script = ""
        '''
            For web
        '''
        for i in lines:
            split = i.split(" ", 1)
            if split[0] == "web:":
                script = split[1]
        return script

    def dockerfiles(self, entrypoint):
        python = f'''FROM ubuntu:20.04\nWORKDIR /app\nRUN apt-get update && apt-get install -y python3-pip\nCOPY requirements.txt .\nRUN yes | pip install -r requirements.txt\nCOPY . .\nEXPOSE 8000\nCMD {entrypoint}'''
        return python

    def generateDockerfile(self, file, save_location):
        script = self.parseScript(file)
        dockerfile = self.dockerfiles(script)
        file = open(f"{save_location}/Dockerfile", "w")
        with file as f:
            f.write(dockerfile)

