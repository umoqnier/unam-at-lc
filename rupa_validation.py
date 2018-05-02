import csv
from string import punctuation, digits
from difflib import SequenceMatcher
import unicodedata
from time import clock

# TODO: Solucionar problema con escritura de archivo de salida. Provicional impresion en pantalla

def get_file():
    loc_file = open("info_unam_loc.txt", "r")
    return loc_file


def get_line(file):
    line = file.readline()
    while line:
        if line[0] is not '|':
            line = file.readline()
            continue
        else:
            line = line.split('|')
            return line
    file.close()
    return False  # End of file


def strip_special_chars(string):
    return ''.join(ch for ch in string if ch not in punctuation + digits)


def replace_accents(string):
    return ''.join((c for c in unicodedata.normalize('NFD', string) if unicodedata.category(c) != 'Mn'))


def perfect_match(rupa, loc_name):
    rupa_info = rupa.__next__()
    loc_name = strip_special_chars(loc_name)
    loc_name = loc_name.upper()
    loc_name = replace_accents(loc_name)
    if ("UNIVERSIDAD" in loc_name) or ("MEXICO" in loc_name):
        return False
    while rupa_info:
        rupa_name = ' '.join(rupa_info[2:5])
        if loc_name == rupa_name:
            print("PERFECT MATCH-->", loc_name, "=", rupa_name)
            return True
        else:
            try:
                rupa_info = rupa.__next__()
            except StopIteration:
                return False  # try with all rupa workers names


def adjust_ratio(loc_name, rupa_name, ratio):
    delta = 0
    loc_atoms = loc_name.split(' ')
    rupa_atoms = rupa_name.split(' ')
    for atom in loc_atoms:
        if len(atom) >= 3:
            for rupa_item in rupa_atoms:
                if atom == rupa_item:
                    delta += 0.15
                elif atom != rupa_item:
                    new_ratio = SequenceMatcher(None, atom, rupa_item).ratio()
                    if new_ratio >= 0.899999999:
                        delta += 0.1
                    elif new_ratio >= 0.799999999:
                        delta += 0.05
                    else:
                        delta += -0.02
    return ratio + delta


def proximity(rupa, loc_name):
    count = 0
    candidates = {}
    rupa_info = rupa.__next__()
    loc_name = strip_special_chars(loc_name)
    loc_name = loc_name.upper()
    loc_name = replace_accents(loc_name)
    if ("UNIVERSIDAD" in loc_name) or ("MEXICO" in loc_name):
        return "0"
    while rupa_info:
        rupa_name = ' '.join(rupa_info[2:5])
        seq = SequenceMatcher(None, loc_name, rupa_name)
        ratio = seq.ratio()
        # ratio = adjust_ratio(loc_name, rupa_name, ratio)
        if ratio >= 0.8999999999:
            print(str(count) + " PROXIMITY (>= 0.89): " + loc_name + " ~ " + rupa_name)
            candidates[rupa_name] = "2"
            try:
                rupa_info = rupa.__next__()
                count += 1
            except StopIteration:
                if len(candidates):
                    return candidates  # Dictionary of candidates
                else:
                    return '0'  # Try all rupa workers names and nothing is found
        elif ratio >= 0.7999999999:
            print(str(count) + " PROXIMITY (>= 0.79): " + loc_name + " ~ " + rupa_name)
            candidates[rupa_name] = "3"
            try:
                rupa_info = rupa.__next__()
                count += 1
            except StopIteration:
                if len(candidates):
                    return candidates  # Dictionary of candidates
                else:
                    return '0'  # Try all rupa workers names and nothing is found
        else:
            try:
                rupa_info = rupa.__next__()
                count += 1
            except StopIteration:
                if len(candidates):
                    return candidates  # Dictionary of candidates
                else:
                    return '0'  # Try all rupa workers names and nothing is found


def verifier():
    print("<count> ALGORITHM: LOC NAMES <> RUPA NAMES")
    info_unam = get_file()
    output_file = open("salida.txt", "a")
    rupa_file = open("rupa.csv", "r")
    # HEADER: NumeroEmpleado,CodigoEntidad,ApellidoPaterno,ApellidoMaterno,Nombre,Entidad
    while True:
        line = get_line(info_unam)
        if not line:
            break
        workers = line[2]
        workers = workers.split("##")
        rupa_iterator = iter(csv.reader(rupa_file))
        for i, worker in enumerate(workers):
            if perfect_match(rupa_iterator, worker):
                rupa_file.seek(0)
                if i:
                    line[2] += "##" + worker + "(1)"
                    if i == len(workers) - 1:  # The last worker
                        line = "|".join(line)
                        line += '\n'
                        print(line)
                        output_file.write(line)
                elif i == 0:
                    line.pop()  # Remove the last \n
                    line[2] = worker + "(1)"  # First worker
            else:
                rupa_file.seek(0)
                rupa_iterator = iter(csv.reader(rupa_file))
                tic = clock()
                candidates = proximity(rupa_iterator, worker)
                toc = clock()
                print("Time spend ~ ", (toc-tic)/60, "minutes")
                rupa_file.seek(0)
                if candidates != '0':
                    min_level = min([int(level) for level in candidates.values()])
                    if i == len(workers) - 1:  # Last worker
                        line[2] += "##" + worker + "(" + str(min_level) + ")"
                        line = '|'.join(line)
                        line += '|' + str(candidates) + '\n'
                        print(line)
                        output_file.write(line)
                    elif i == 0:  # First worker
                        line.pop()  # Remove the last \n
                        line[2] = worker + "(" + str(min_level) + ")"
                        line = '|'.join(line)
                        line += '|' + str(candidates) + '##'
                        line = line.split('|')
                    else:  # Worker in the middle
                        line[2] += "##" + worker + "(" + str(min_level) + ")"
                        line = '|'.join(line)
                        line += '|' + str(candidates) + '##'
                        line = line.split('|')
                else:
                    print("Worker not found at RUPA-->", worker)
                    if i == len(workers) - 1:  # Last worker
                        line = '|'.join(line)
                        line += '\n'
                        print(line)
                        output_file.write(line)
                    elif i == 0:  # First worker
                        line.pop()  # Remove the last \n
                        line[2] = worker + "(NF)"
                    else:  # Worker in the middle
                        line[2] += "##" + worker + "(NF)"
    rupa_file.close()
    output_file.close()


verifier()
