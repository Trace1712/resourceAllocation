import sys


# 服务器类型
class ServerKind:

    def __init__(self, name, cpu, memory, hardware_cost, electroic_cost):
        # 服务器名字
        self.name = name

        # 服务器硬件成本
        self.hardware_cost = hardware_cost

        # 服务器电费
        self.electroic_cost = electroic_cost

        # 服务器初始资源
        self.cpu = cpu
        self.memory = memory

        # 服务器资源
        self.a_cpu = cpu // 2
        self.a_memory = memory // 2

        self.b_cpu = cpu // 2
        self.b_memory = memory // 2

        # 服务器上运行的虚拟机
        # {_id: vm_name}
        self.vm_running = {}

        # 服务器上运行的单节点虚拟机
        self.single_vm_node = {}

        # 服务器编号
        self.server_code = None

    # 分配服务器编号
    def allocate_server_code(self, num):
        self.server_code = num

    # 获取服务器名字
    def get_server_name(self):
        return self.name.strip()

    # 获取 A节点剩余信息
    def get_anode_info(self):
        return self.a_cpu, self.a_memory

    # 获取B节点剩余信息
    def get_bnode_info(self):
        return self.b_cpu, self.b_memory

    # 资源分配
    def distribute_resource(self, cpu, memory, kind, _id, vm_name, single_install_address):
        # 加入运行节点列表
        self.vm_running[_id] = vm_name
        if kind == "0":
            # 加入单节点列表
            node = self.S_distribute_resource(cpu, memory)
            self.single_vm_node[_id] = node
            single_install_address[_id] = node
        else:
            self.D_distribute_resource(cpu, memory)

    # cpu 和 memory的倍数
    def get_beishu(self):
        if self.a_memory == 0 or self.a_cpu == 0:
            return sys.maxsize
        # return self.cpu + self.memory
        if self.a_cpu >= self.a_memory:
            return self.a_cpu // self.a_memory
        else:
            return self.a_memory // self.a_cpu



    # 单节点资源分配
    def S_distribute_resource(self, cpu: int, memory: int):
        a_cpu, a_memory = self.get_anode_info()
        b_cpu, b_memory = self.get_bnode_info()
        if (a_cpu >= cpu and a_memory >= memory) and (b_cpu >= cpu and b_memory >= memory):
            if a_cpu + a_memory >= b_cpu + b_memory:
                self.a_cpu -= cpu
                self.a_memory -= memory
                return "A"
            else:
                self.b_cpu -= cpu
                self.b_memory -= memory
                return "B"
        elif b_cpu >= cpu and b_memory >= memory:
            self.b_cpu -= cpu
            self.b_memory -= memory
            return "B"
        elif a_cpu >= cpu and a_memory >= memory:
            self.a_cpu -= cpu
            self.a_memory -= memory
            return "A"
        else:
            print("资源不足分配")

    # 双节点资源分配
    def D_distribute_resource(self, cpu: int, memory: int):
        if (self.a_cpu >= cpu // 2 and self.b_cpu >= cpu // 2) and (
                self.a_memory >= memory // 2 and self.b_memory >= memory // 2):
            self.a_cpu -= cpu // 2
            self.a_memory -= memory // 2
            self.b_cpu -= cpu // 2
            self.b_memory -= memory // 2
        else:
            print("资源不足分配")

    # 判断虚拟机是否在此服务器上
    def is_on(self, _id):
        return _id in self.vm_running.keys()

    def release_resource(self, _id, vm_lst):
        """
        释放资源
        :param _id: 需要释放的虚拟机id
        :param vm_lst: 虚拟机列表 用来查看对应种类的资源
        :return: None
        """
        if not self.is_on(_id):
            print("虚拟机不在此服务器上")
        else:
            for vm in vm_lst:
                if self.vm_running[_id] == vm.get_name():
                    # 单节点释放
                    if vm.get_node_kind() == "0":
                        if self.single_vm_node[_id] == "A":
                            self.a_cpu += vm.get_cpu()
                            self.a_memory += vm.get_memory()
                        elif self.single_vm_node[_id] == "B":
                            self.b_cpu += vm.get_cpu()
                            self.b_memory += vm.get_memory()
                        # 删除运行服务器中的节点
                        # 删除单节点服务器的节点
                        del self.single_vm_node[_id]
                    # 双节点释放
                    elif vm.get_node_kind() == "1":
                        self.a_cpu += vm.get_cpu() // 2
                        self.b_cpu += vm.get_cpu() // 2
                        self.a_memory += vm.get_memory() // 2
                        self.b_memory += vm.get_memory() // 2
                        # 删除运行服务器的节点
            del self.vm_running[_id]


# 虚拟机类型
class VmKind:
    def __init__(self, name, cpu: int, memory: int, node_kind):
        self.name = name
        self.cpu = cpu
        self.memory = memory
        # 0 单节点 1 双节点
        self.node_kind = node_kind

    def get_memory(self):
        return self.memory

    def get_cpu(self):
        return self.cpu

    def get_node_kind(self):
        return self.node_kind.strip()

    def get_name(self):
        return self.name.strip()
