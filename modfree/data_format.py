import re
import numpy as np


def swap(dic, k1, k2):
    "swap keys in complex dictionnary and conserves the integrity of its content"
    # ex: swap(dic[res][field][temp][conc], 1, 3) = dic[res][conc][temp][field]
    if k1 == 0 and k2 == 1:
        print("minimum key number is 1 here")
        return None
    if k1 == 1 and k2 == 2:
        output = dict()
        for k in dic.keys():
            for kk in dic[k].keys():
                if kk not in output.keys():
                    output[kk] = dict()
                output[kk][k] = dic[k][kk]
        return output
    elif k2 - k1 == 1:
        return {k: swap(dic[k], k1-1, k2-1) for k in dic.keys()}
    else:
        output = dic
        temp_k = k1
        while temp_k < k2:
            #print("swap", temp_k, temp_k+1)
            output = swap(output, temp_k, temp_k+1)
            temp_k += 1
        temp_k -= 1
        while temp_k > k1:
            #print("swap", temp_k-1, temp_k)
            output = swap(output, temp_k-1, temp_k)
            temp_k -= 1
        return output


def assign(value, dic, key_list):
    if len(key_list) == 1:
        dic[key_list[0]] = value
        return dic
    else:
        return {k: dic[k] if k != key_list[0] else assign(value, dic[k], key_list[1:]) for k in dic.keys()}


class Reader:
    """In practice should read dictionnaries. example below"""
    """;dict
    ;key:int:1
    ;dict
    ;key:str:R1
    ;list:float
    1.0
    1.2
    1.4
    1.5
    ;key:str:R2
    ;list:str
    10.0
    7.5
    8.34
    9.23
    10.1
    ;endic
    ;key:int:2
    ;dict
    ;key:str:R1
    float:2.03
    ;key:str:R2
    ;list:float
    10.02
    9.22
    ;endic
    ;endic"""
    def __init__(self, textfile):
        self.output = None
        with open(textfile, 'r') as f:
            self.text = [el.rstrip("\n") for el in f.readlines()]
        self.read()
            
    @staticmethod
    def function(line):
        if re.search("dict", line):
            return "dict"
        elif re.search("endic", line):
            return "endic"
        elif re.search("key", line):
            return "key"
        elif re.search("list", line):
            return "list"
        elif re.search("endlis", line):
            return "endlis"
        
    @staticmethod
    def Type(statement):
        if statement == "int":
            return int
        elif statement == "float":
            return float
        elif statement == "str":
            return str
    
    def element(self, key_list, dic=None):
        if dic is None:
            dic = self.output
        if len(key_list) > 1:
            return self.element(key_list[1:], dic[key_list[0]])
        else:
            return dic[key_list[0]]
        
    @staticmethod
    def list_element(l, idxs):
        if idxs == []:
            return l
        elif len(idxs) == 1:
            return l[idxs[0]]
        else:
            return list_element(l[idxs[0]], idxs[1:])
        
    def assign(self, value, dic=None, key_list=[]):
        if dic is None:
            dic = self.output
        if key_list == []:
            return dic
        if len(key_list) == 1:
            dic[key_list[0]] = value
            return dic
        else:
            return {k: dic[k] if k != key_list[0] else self.assign(value, dic[k], key_list[1:]) for k in dic.keys()}
        
    @staticmethod
    def assign_to_list(value, l, idxs):
        output = l
        if idxs == []:
            return output
        elif len(idxs) == 1:
            output[idxs[0]] = value
        else:
            output = [el if i != idxs[0] else self.assign_to_list(value, l[i], idxs[1:]) for i, el in enumerate(output)]
        return output
    
    @staticmethod
    def append_to_list(value, l, idxs):
        output = l
        if idxs == []:
            output.append(value)
        elif len(idxs) == 1:
            output[idxs[0]].append(value)
        else:
            output = [el if i != idxs[0] else append(value, l[i], idxs[1:]) for i, el in enumerate(output)]
        return output
    
    def read(self, text=None):
        current_keys = []
        current_list_idx = []
        state = "None"
        current_type = "None"
        if text is None:
            text = self.text
        for line in self.text:
            if line[0] == ";":
                if self.function(line) == "dict":
                    if current_keys == []:
                        self.output = dict()
                    else:
                        self.output = self.assign(dict(), key_list=current_keys)
                    state = "dict"
                elif self.function(line) == "endic":
                    current_keys = current_keys[:-1]
                elif self.function(line) == "key":
                    if state != "dict":
                        current_keys = current_keys[:-1]
                    temp = line[1:].split(":")
                    current_keys.append(self.Type(temp[1])(temp[2]))
                    state = "key"
                elif self.function(line) == "list":
                    try:
                        current_list = self.element(current_keys)
                    except KeyError:
                        current_list = []
                    current_type = line[1:].split(":")[1]                   
                    if state == "list":
                        current_list = self.append_to_list([], current_list, current_list_idx[:-1])
                        self.output = self.assign(current_list, key_list=current_keys)
                    else:
                        self.output = self.assign(current_list, key_list=current_keys)
                    state = "list"
                    current_list_idx.append(0)
                elif self.function(line) == "endlis":
                    current_list_idx = current_list_idx[:-1]
                    if current_list_idx != []:
                        current_list_idx[-1] += 1
            else:
                if state == "list":
                    current_list = self.element(current_keys)
                    current_list = self.append_to_list(self.Type(current_type)(line), current_list, current_list_idx[:-1])
                    self.output = self.assign(current_list, key_list=current_keys)
                    current_list_idx[-1] += 1
                elif state == "key":
                    temp = line.split(":")
                    self.output = self.assign(self.Type(temp[0])(temp[1]), key_list=current_keys)


class Save:
    def __init__(self, dic, textfile):
        self.savefile = textfile
        self.dic = dic
        self.lines = self.wlines()
        self.save()
    
    @staticmethod
    def Type(val):
        if type(val) == int:
            return "int"
        elif type(val) == float:
            return "float"
        elif type(val) == str:
            return "str"
        elif type(val) == list:
            return "list"
        elif type(val) == np.float64:
            return "float"
        else:
            return "str"
        
    def wlist(self, l):
        output = []
        if l != []:
            output.append(";list:"+str(self.Type(l[0]))+"\n")
            if self.Type(l[0]) != "list":
                for el in l:
                    output.append(str(el)+"\n")
            else:
                for el in l:
                    output = output + self.wlist(el)
        else:
            output.append(";list:str\n")
        output.append(";endlis\n")
        return output
        
    def wlines(self, dic=None):
        if dic is None:
            dic = self.dic
        output = [";dict\n"]
        for k in dic.keys():
            output.append(";key:"+self.Type(k)+":"+str(k)+"\n")
            if type(dic[k]) == dict:
                output = output + self.wlines(dic[k])
            elif type(dic[k]) == list:
                output = output + self.wlist(dic[k])
            else:
                output.append(str(self.Type(dic[k]))+":"+str(dic[k])+"\n")
        output.append(";endic\n")
        return output

    def save(self, lines=None):
        if lines is None:
            lines = self.lines
        with open(self.savefile, 'w') as f:
            for line in lines:
                f.write(line)


def list2dic(x, y):
    return {k: y[i] for i, k in enumerate(x)}


def dic2list(dic):
    return list(dic.keys()), list(dic.values())


def common(dic1, dic2):
    output = dict()
    for k in dic1.keys():
        if k in dic2.keys():
            output[k] = dic1[k]
    return output


def commons(x1, y1, x2, y2):
    d1 = list2dic(x1, y1)
    d2 = list2dic(x2, y2)
    d1 = common(d1, d2)
    d2 = common(d2, d1)
    x1, y1 = dic2list(d1)
    x2, y2 = dic2list(d2)
    return x1, y1, x2, y2
