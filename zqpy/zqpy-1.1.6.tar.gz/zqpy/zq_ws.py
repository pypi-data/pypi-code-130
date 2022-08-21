import asyncio
import websockets
import websockets_routes
import threading
import zq_log

''' 示例 https://www.jianshu.com/p/b7df44b7c7f7
#region server
async def echo(websocket, path):
    #fetch msg
    async for message in websocket:
        zq_log.log_debug('%s get message:%s'%(path, message))
        await websocket.send('server recv: %s'%message)

async def main():
    # start a websocket server
    async with websockets.serve(echo, 'localhost', 8800):
        await asyncio.Future()  # run forever

asyncio.run(main())
#endregion

#region client
async def hello():
    async with websockets.connect('ws://localhost:8800') as websocket:
        await websocket.send('Hello world!')
        await websocket.recv()

asyncio.run(hello())
#endregion
'''

#region 服务器
# 初始化一个router对象，路由装饰器
ws_server_router = websockets_routes.Router()

async def ws_server_main(ip='localhost', port=8800):
    async with websockets.serve(lambda x, y: ws_server_router(x, y), ip, port):
        zq_log.log_debug('ws:', ip, port)
        await asyncio.Future()  # run forever

@ws_server_router.route('/v1/test/{status}') #添加router的route装饰器，它会路由uri。
async def test_status(websocket, path):
    async for message in websocket:
        zq_log.log_debug('server recv message:%s,%s,%s'%(path, path.params['status'], message))
        if (path.params['status'] == 'ok'):
            await  websocket.send('server recv status:%s message:%s'%(path.params['status'], message))
        elif path.params['status'] == 'no':
            await  websocket.send('server recv status:%s message:%s'%(path.params['status'], message))
        else:
            await  websocket.send('server recv invalid params')

def ws_server_open_sync(ip='localhost', port=8800):
    '''
    打开websocket server 监听 同步
    router 是路由
    '''
    asyncio.run(ws_server_main(ip, port))

def ws_server_open_async(ip='localhost', port=8800):
    '''
    打开websocket server 监听 异步
    router 是路由
    '''
    thread = threading.Thread(target=ws_server_open_sync, kwargs={'ip':ip, 'port':port})
    thread.start()
    return thread

#endregion



#region 客户端

async def ws_client_test(ip='localhost', port=8800, path='v1/test/ok', data='也许世界就这样'):
    '''
    ws 客户端测试
    # await ws_client_test()
    '''
    try:
        async with websockets.connect('ws://%s:%s/%s'%(ip, port, path)) as websocket:
            await websocket.send(data)
            recv_msg = await websocket.recv()
            zq_log.log_debug(recv_msg)
    except websockets.exceptions.ConnectionClosedError as e:
        zq_log.log_debug('connection closed error')
    except Exception as e:
        zq_log.log_error(e)

#endregion