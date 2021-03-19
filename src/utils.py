from kind import *
import collections

def get_vm(name, vm_kind_list):
    """
    寻找某型号的虚拟机
    :param name:         虚拟机名字
    :param vm_kind_list: 虚拟机列表
    :return:             虚拟机
    """
    for vm in vm_kind_list:
        if name.strip() == vm.get_name().strip():
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


# sort
def get_min_resource(server):
    min_ = min(server.a_cpu, server.a_memory, server.b_cpu, server.b_memory)
    return min_


# 服务器剩余资源
def get_left_res(server):
    a_cpu, a_memory = server.get_anode_info()
    b_cpu, b_memory = server.get_bnode_info()

    return a_cpu + a_memory + b_cpu + b_memory


def add_server(server_lst,vm,start_num,single_install_address,install_address,_id,vm_dic,vm_name):
    """
    分配服务器
    :param server_lst: 可选服务器列表
    :param vm: 虚拟机
    :param start_num: 虚拟机编号
    :param single_install_address: 单节点信息
    :param install_address: 所有信息
    :param _id: 虚拟机ID
    :param vm_dic: 虚拟机地址存储
    :param vm_name: 虚拟机名称
    :return:
    """
    for server in server_lst:
        server = server.copy_server()
        if is_full(server, vm):
            # 服务器分配ID
            server.allocate_server_code(start_num)
            server.distribute_resource(vm.get_cpu(), vm.get_memory(), vm.get_node_kind(), _id, vm_name,
                                       single_install_address, vm_dic)
            # 服务器编码
            install_address[_id] = server.server_code
            return server

def print_info(temp_server,install_address,single_install_address):
    """
    打印信息
    :param temp_server:
    :param install_address:
    :param single_install_address:
    :return:
    """
    servers = collections.Counter(temp_server)
    print("(purchase," + str(len(servers)) + ")")
    for item in servers.items():
        print("(" + item[0].get_server_name() + "," + str(item[1]) + ")")
    print("(migration,0)")
    for item in install_address.items():
        if item[0] not in single_install_address:
            print("("+str(item[0]).strip()+","+str(item[1])+")")
        else:
            print("("+str(item[0]).strip()+","+str(item[1])+","+single_install_address[item[0]]+")")
