def split_list_into_3_key_dict(l):
    l_dict = {}
    l_dict['l1'] = []
    l_dict['l2'] = []
    l_dict['l3'] = []
    l_dict['leftovers'] = []
    if (len(l) >= 3):
        l1 = l[0:(len(l)//3)]
        l2 = l[(len(l)//3):((len(l)//3)*2)]
        l3 = l[((len(l)//3)*2):]

        mod3 = len(l) % 3

        if (mod3 == 0):
            pass
        elif (mod3 == 1):
            l_dict['leftovers'].append(l3.pop())
        else:
            l_dict['leftovers'].append(l3.pop())
            l_dict['leftovers'].append(l3.pop())

        l_dict['l1'] = l1
        l_dict['l2'] = l2
        l_dict['l3'] = l3

    elif (len(l) == 1):
        l_dict['leftovers'] = l
    elif (len(l) == 2):
        l_dict['leftovers'].append(l[0])
        l_dict['leftovers'].append(l[1])
    return l_dict

