import json

import psutil as pu
import GPUtil as Gu


def getpercentage(used, total):
    # Get percentage from gpu usage
    percentage = 100 * (float(used) / float(total))
    return round(percentage, 2)


def getlog(disk):
    # Crete GPU var
    gpus = Gu.getGPUs()
    gpu = gpus[0]

    # Taking server logs
    cpu_usage = pu.cpu_percent(4).real
    memory_usage = pu.virtual_memory()[2]
    disk_usage = pu.disk_usage(disk).percent
    disk_available_space = pu.disk_usage(disk).free
    disk_total_space = pu.disk_usage(disk).total
    gpu_id = gpu.id
    gpu_available_space = gpu.memoryFree
    gpu_total_memory = gpu.memoryTotal
    gpu_usage = gpu.memoryUsed
    gpu_temperature = gpu.temperature
    gpu_device = gpu.name
    gpu_driver = gpu.driver

    # Create JSON response
    server_status = {
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
        "disk_usage": disk_usage,
        "disk_available_space": getpercentage(disk_available_space, disk_total_space),
        "disk_total_space": disk_total_space,
        "gpu_id": gpu_id,
        "gpu_available_space": getpercentage(gpu_available_space, gpu_total_memory),
        "gpu_total_memory": gpu_total_memory,
        "gpu_usage": getpercentage(gpu_usage, gpu_total_memory),
        "gpu_temperature": gpu_temperature,
        "gpu_device": gpu_device,
        "gpu_driver": gpu_driver
    }

    return json.dumps(server_status)
