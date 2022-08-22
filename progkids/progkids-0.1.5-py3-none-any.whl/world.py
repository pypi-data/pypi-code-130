from .__progkids__ import sendCommand


def getBlock(x, y, z):
    return sendCommand('world:getBlock', [x, y, z])


def getBlockData(x, y, z):
    return sendCommand('world:getBlockData', [x, y, z])


def getBlocks(x0, y0, z0, x, y, z):
    return sendCommand('world:getBlocks', [x0, y0, z0, x, y, z])


def getHeight(x, y, z=None):
    if z is None:
        z = y
        y = 0
    return sendCommand('world:getHeight', [x, y, z])


def getPlayerId(playerId):
    return sendCommand('world:getPlayerId', [playerId])


def getPlayerIds():
    return sendCommand('world:getPlayerIds', [])


def setBlock(x, y, z, material, data=0):
    if material == 64 and data == 0:
        return sendCommand('world:setBlock', [x, y+1, z, material, 9]), sendCommand('world:setBlock', [x, y, z, material, 3])
    return sendCommand('world:setBlock', [x, y, z, material, data])


def setCuboid(x0, y0, z0, x, y, z, material, data=0):
    return sendCommand('world:setCuboid', [x0, y0, z0, x, y, z, material, data])


def setBlocks(x, y, z, blocks):
    return sendCommand('world:setBlocks', [x, y, z, blocks])


def buildArc(x, y, z, w, h, material, data=0):
    return sendCommand('world:buildArc', [x, y, z, w, h, material, data])


def buildColumn(x, y, z, h, material, data=0):
    return sendCommand('world:buildColumn', [x, y, z, h, material, data])


def buildSphere(x, y, z, r, material, data=0):
    return sendCommand('world:buildSphere', [x, y, z, r, material, data])


def buildHome(x, y, z, h, l, w, material, direction='SOUTH', data=0):
    return sendCommand('world:buildHome', [x, y, z, h, l, w, material, 0, direction, data])


def buildWall(x, y, z, w, h, material, data=0):
    return sendCommand('world:buildWall', [x, y, z, w, h, material, data])


def spawnCreature(x, y, z, creature):
    return sendCommand('world:spawnCreature', [x, y, z, creature])


def setWeather(material):
    return sendCommand('world:setWeather', [material])


def setTime(time):
    return sendCommand('world:setTime', [time])
