from kind import *


def get_vm(name, vm_kind_list):
    """
    寻找某型号的虚拟机
    :param name:         虚拟机名字
    :param vm_kind_list: 虚拟机列表
    :return:             虚拟机
    """
    for vm in vm_kind_list:
        if name == vm.get_name().strip():
            return vm


def is_full(server: ServerKind, vm: VmKind):
    """
    判断服务器是否能够容纳虚拟机
    :param server: 服务器
    :param vm:     虚拟机
    :return:       是否足够分配
    """
    # 单节点
    if vm.get_node_kind() == "0":
        cpu, memory = server.get_anode_info()
        if cpu > vm.get_cpu() and memory > vm.get_memory():
            return True
        else:
            cpu, memory = server.get_bnode_info()
            if cpu > vm.get_cpu() and memory > vm.get_memory():
                return True
            else:
                return False
    # 双节点
    else:
        a_cpu, a_memory = server.get_anode_info()
        b_cpu, b_memory = server.get_bnode_info()
        # 有一组节点满足要求即可
        if (a_cpu >= vm.get_cpu() // 2 and a_memory >= vm.get_memory() // 2) and (
                b_cpu >= vm.get_cpu() // 2 and b_memory >= vm.get_memory() // 2):
            return True
        return False


def cost(server, need_hardware, need_electroic, money):
    """
    计算开销
    :param server:          服务器
    :param need_hardware:   是否加硬件
    :param need_electroic:  是否运行
    :param money:
    :return:
    """
    if need_hardware:
        money += server.hardware_cost
    if need_electroic:
        money += server.electroic_cost
    return money


# 服务器初始cpu 内存之间的倍数差距
def get_key_value(server):
    return server.get_beishu()


# 服务器剩余资源
def get_left_res(server):
    a_cpu, a_memory = server.get_anode_info()
    b_cpu, b_memory = server.get_bnode_info()

    return a_cpu + a_memory + b_cpu + b_memory
