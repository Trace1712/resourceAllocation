from utils import *
import random
import collections
import sys
import time

train_path = "training-1.txt"
running_server = []


def main():
    vm_dic = {}
    f = open(train_path, "r")
    # 服务器数量
    server_num = int(f.readline().strip())
    server_list = []
    # 存储服务器类型
    for _ in range(server_num):
        name, cpu, memory, hardware_cost, electroic_cost = f.readline().strip().strip("(").strip(")").split(",")
        server_list.append(ServerKind(name, int(cpu), int(memory), int(hardware_cost), int(electroic_cost)))
    # 虚拟机类型
    vm_num = int(f.readline().strip())
    vm_list = []
    for _ in range(vm_num):
        name, cpu, memory, node_kind = f.readline().strip().strip("(").strip(")").split(",")
        vm_list.append(VmKind(name, int(cpu), int(memory), node_kind))
    # 总共请求天数
    day_num = int(f.readline().strip())
    # 第一天请求
    request_num = int(f.readline().strip())
    list_request = []
    for _ in range(request_num):
        list_request.append(f.readline().strip())
    # 处理第一天请求 返回现在的费用
    price, start_num = MCMC(list_request, server_list, vm_list, running_server, vm_dic)
    # running_server 排序
    running_lst = sorted(running_server, key=get_left_res)

    server_list1, server_list2 = sort_server(server_list)

    # 之后的请求
    for _ in range(day_num - 1):
        # start = time.time()
        day_num = int(f.readline().strip())
        list_request = []
        for _ in range(day_num):
            list_request.append(f.readline().strip())
        one_price, start_num = request_policy(running_lst, server_list1, server_list2, vm_list, list_request, start_num,
                                              vm_dic)


# 第一天请求策略
def MCMC(request_lst, server_lst, vm_list, running_server=None, vm_dic=None):
    """

    :param vm_dic:
    :param start_num:  服务器开始编号
    :param running_server:
    :param request_lst: 请求列表
    :param server_lst:  可用服务器列表
    :param vm_list:     可用虚拟机列表
    :return: 当天的费用
    """
    if vm_dic is None:
        vm_dic = {}
    all_prices = 9999999
    temp_server = []
    final_server = []
    count = 0
    # 分配位置
    install_address = {}
    # 单节点额外信息
    single_address = {}
    while count < 500:
        start_num = 0
        temp_server = []
        lst = request_lst
        temp_prices = 0
        # 初始化服务器
        server = server_lst[random.randint(0, len(server_lst) - 1)]
        server.allocate_server_code(start_num)
        start_num += 1
        # 增加成本
        temp_prices += cost(server, need_hardware=True, need_electroic=True, money=temp_prices)
        temp_server.append(server)
        while len(lst) > 0:
            request = lst.pop()
            op, vm_name, _id = request.strip("(").strip(")").split(",")
            _id = _id.strip()
            # dic_ = {_id: vm_name}
            vm = get_vm(vm_name.strip(), vm_list)

            changed = False
            # 判断资源是否足够 不够需要再申请一个服务器
            while not is_full(server, vm):
                # 申请服务器
                server = server_lst[random.randint(0, len(server_lst) - 1)]
                changed = True
            # 增加成本
            if changed:
                temp_prices += cost(server, need_hardware=True, need_electroic=True, money=temp_prices)
                temp_server.append(server)
                # 设置编号
                server.allocate_server_code(start_num)
                start_num += 1

            server.distribute_resource(vm.get_cpu(), vm.get_memory(), vm.get_node_kind(), _id, vm_name, single_address,
                                       vm_dic)
            # 存储分配信息
            install_address[_id] = server.server_code
            # 构建虚拟机信息
            # 服务器中放入虚拟机信息
        if temp_prices < all_prices:
            final_server = temp_server
            all_prices = temp_prices
            final_number = start_num

        count += 1
    running_server += final_server

    print_info(temp_server, install_address, single_address)
    return all_prices, final_number


def request_policy(running_server, server_list1, server_list2, vm_lst, request_lst, start_num, vm_dic):
    """
    请求处理策略
    init 获取两种排序之后的服务器列表
    1.判断现有服务中是否有空余位置给虚拟机
    2.判断虚拟机类型(cpu > memory or memory > cpu)
    3.从两个服务器列表中 选择服务器类型与虚拟机一样的最大的型号
    4.填入服务器
    所有请求全部完成后,判断所有有空闲容量的服务器，判断更小的服务器能否替代
    :param vm_dic:
    :param start_num: 起始编号
    :param server_list1:    cpu > memory 的服务器列表
    :param server_list2:    memory > cpu 的服务器列表
    :param running_server:  正在运行的服务器
    :param vm_lst:          虚拟机信息
    :param request_lst:     请求列表
    :return: 当天的加装费用
    """
    prices = 0
    # 需要扩容的数量
    all_add_server = 0
    # 扩容的虚拟机列表
    temp_server = []
    # 分配位置
    install_address = {}
    # 单节点更多信息
    single_install_address = {}
    for request in request_lst:
        op_lst = request.strip("(").strip(")").split(",")
        # add操作
        if len(op_lst) == 3:
            # start = time.time()
            op, vm_name, _id = request.strip("(").strip(")").split(",")
            _id = _id.strip()
            # 判断现有服务器中是否有空位
            vm = get_vm(vm_name, vm_lst)
            # 有位子直接分配
            # 无位子需要加装虚拟机
            if all_add_server % 20 == 0:
                running_server.sort(key=get_min_resource, reverse=True)
            result, _time_ = find_empty_space(running_server, vm, _id, install_address, single_install_address, vm_dic)
            if not result:
                # 加装
                all_add_server += 1
                server = None
                if vm.get_cpu() >= vm.get_memory():
                    # 加装服务器
                    server = add_server(server_list1, vm, start_num, single_install_address, install_address, _id,
                                        vm_dic,
                                        vm_name)
                else:
                    server = add_server(server_list2, vm, start_num, single_install_address, install_address, _id,
                                        vm_dic,
                                        vm_name)
                # 加一台服务器 最好加在头部
                running_server.insert(0, server)

                start_num += 1
                # 统计这一天加装的服务器
                temp_server.append(server)
                prices += server.hardware_cost

        # del操作
        elif len(op_lst) == 2:
            op, _id = op_lst
            # 去除空格
            _id = _id.strip()
            server = vm_dic[_id]
            # 释放服务器
            server.release_resource(_id, vm_lst)

    print_info(temp_server, install_address, single_install_address)
    return prices, start_num


def find_empty_space(running_server, vm, vm_id, install_address, single_address, vm_dic):
    """
    判断现有服务器中是否有位子放入现有虚拟机
    :param vm_dic:
    :param single_address: 单节点额外信息
    :param install_address: 分配信息
    :param vm_id: 虚拟机ID
    :param running_server: 运行着虚拟机的服务器
    :param vm: 需要加装的虚拟机
    :return: 是否可以加装
    """
    # start = time.time()
    count = 0
    for server in running_server:
        if count == 20:
            break
        if is_full(server, vm):
            # 分配资源
            server.distribute_resource(vm.get_cpu(), vm.get_memory(), vm.get_node_kind(), vm_id, vm.get_name(),
                                       single_address, vm_dic)
            # 服务器编码
            install_address[vm_id] = server.server_code
            # end = time.time()
            return True, 0
        count += 1
    # end = time.time()
    return False, 0


def sort_server(server_lst):
    """
    服务器排序 分为两种 CPU > 内存 or 内存 > CPU
    :param server_lst: 服务器列表
    :return:
    """
    server_list1 = []
    server_list2 = []
    for server in server_lst:
        a_cpu, a_memory = server.get_anode_info()
        if a_cpu >= a_memory:
            server_list1.append(server)
        else:
            server_list2.append(server)
    server_list1 = sorted(server_list1, key=get_key_value, reverse=True)
    server_list2 = sorted(server_list2, key=get_key_value, reverse=True)
    return server_list1, server_list2


# 迁移策略
def transfer():
    pass


if __name__ == "__main__":
    main()
