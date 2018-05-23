import csv
from string import punctuation, digits
from difflib import SequenceMatcher
import unicodedata
from time import clock
TOTAL_TIME = 0

# TODO: Falla importante con articulos que tienen autores repetidos
# TODO: Falla menor cuando el artículo solo tiene un autor

def get_file():
    """
    Get file with Library of Congress data
    :return file object
    """
    loc_file = open("info_unam_loc.txt", "r")
    return loc_file


def get_line(file):
    """
    Get line by line of file with LOC data
    :return List of data by line
    """
    line = file.readline()
    while line:
        if line[0] is not '|':  # Discard all lines that not start with '|'
            line = file.readline()  # Read next
            continue
        else:
            line = line.split('|')
            return line  # Return list of data fields
    file.close()
    return False  # End of file


def strip_special_chars(string):
    """
    Remove special chars from an string
    :param string: Name of worker
    :return: Name of worker without special chars
    """
    return ''.join(ch for ch in string if ch not in punctuation + digits)


def replace_accents(string):
    """
    Remove accents from a string
    :param string: Name of worker
    :return: Name of worker without accents
    """
    return ''.join((c for c in unicodedata.normalize('NFD', string) if unicodedata.category(c) != 'Mn'))


def perfect_match(rupa, loc_name):
    """
    Verify if a worker name is on RUPA database
    :param rupa: Iterator that enable RUPA search
    :param loc_name: Name of worker en LOC file
    :return: Boolean. True if worker is on RUPA and false if not
    """
    rupa_info = rupa.__next__()
    loc_name = strip_special_chars(loc_name)
    loc_name = loc_name.upper()
    loc_name = replace_accents(loc_name)
    if ("UNIVERSIDAD" in loc_name) or ("MEXICO" in loc_name):  # To avoid names like "UNIVERSIAD NACIONAL..."
        return False
    while rupa_info:
        rupa_name = ' '.join(rupa_info[2:5])  # Transform RUPA name from list to string
        if loc_name == rupa_name:
            print("PERFECT MATCH-->", loc_name, "==", rupa_name)
            return True
        else:
            try:
                rupa_info = rupa.__next__()
            except StopIteration:
                return False  # try with all RUPA workers names


def adjust_ratio(loc_name, rupa_name, ratio):
    """
    Algorithm to adjust the ratio of certainty of the name at RUPA
    :param loc_name: Name of worker at LOC
    :param rupa_name: Name of worker at RUPA
    :param ratio: Current ratio of certainty
    :return: Adjust ratio
    """
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
        if ratio >= 0.8399999999:
            print(str(count) + " PROXIMITY (>= 0.839): " + loc_name + " ~ " + rupa_name)
            candidates[rupa_name] = "2"
            try:
                rupa_info = rupa.__next__()
                count += 1
            except StopIteration:
                if len(candidates):
                    return candidates  # Dictionary of candidates
                else:
                    return '0'  # Try all rupa workers names and nothing is found
        elif ratio >= 0.7399999999:
            print(str(count) + " PROXIMITY (>= 0.739): " + loc_name + " ~ " + rupa_name)
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
    global TOTAL_TIME
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
                TOTAL_TIME += toc-tic
                rupa_file.seek(0)
                if candidates != '0':
                    min_level = min([int(level) for level in candidates.values()])
                    if (i == len(workers) - 1) or (len(workers) == 1):  # Last worker or only one worker
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
                        line[2] = worker + "(NF)"
                        line = '|'.join(line)
                        line += '\n'
                        print(line)
                        output_file.write(line)
                    elif i == 0:  # First worker
                        line.pop()  # Remove the last \n
                        line[2] = worker + "(NF)"
                    else:  # Worker in the middle
                        line[2] += "##" + worker + "(NF)"
    print("TOTAL TIME: ", TOTAL_TIME/60, "minutes", (TOTAL_TIME/60)/60, "hours", ((TOTAL_TIME/60)/60)/24, "days")
    rupa_file.close()
    output_file.close()


verifier()
