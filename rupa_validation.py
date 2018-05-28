import csv
from string import punctuation, digits
from difflib import SequenceMatcher
import unicodedata
from time import clock
TOTAL_TIME = 0

# TODO: Falla importante con articulos que tienen autores repetidos
# TODO: Falla menor cuando el artículo solo tiene un autor
# TODO: Modificar función proximity para agregar número de empleado al diccionario
# Ej: {"nombre": [proximidad, numero de emplado], ...}


def get_files():
    """
    Get files with Library of Congress data, output data, output authors and rupa database
    :return tuple of files objects
    """
    loc_file = open("info_unam_loc.txt", "r")
    data_file = open("data.txt", "a")
    authors_file = open("authors.txt", "a")
    rupa_file = open("rupa.csv", "r")
    return loc_file, data_file, authors_file, rupa_file


def get_info_line(file):
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
    :return: String number of employer if name is at RUPA or Boolean false if name is not at rupa
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
            return rupa_info[0], rupa_info[5]
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
            candidates[rupa_name] = ["2", rupa_info[0], rupa_info[5]]
            try:
                rupa_info = rupa.__next__()
                count += 1
            except StopIteration:
                if len(candidates):
                    return candidates  # Dictionary of candidates
                else:
                    return '0'  # Try all rupa workers names and nothing is found
        elif ratio >= 0.7399999999:
            if len(candidates) < 4:
                print(str(count) + " PROXIMITY (>= 0.739): " + loc_name + " ~ " + rupa_name)
                candidates[rupa_name] = ["3", rupa_info[0], rupa_info[5]]
            else:  # Maximum 3 candidates that has 0.739... SecuenceMatcher value
                print("Maximum PROXIMITY (>= 0.739) candidates has rebase")
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


def authors_manager(worker_data, worker, c_id, mode, candidates=None):
    """
    Manage author information and make string line for authors_out file
    :param worker_data: Information from RUPA Data Base. Number and institution
    :param worker: Name of creator of article from LOC
    :param c_id: Current Personal id for authors_out file
    :param mode: Flag for perfect match or proximity case
    :param candidates: Dictionary of candidates for proximity case
    :return: String line with author information
    """
    if mode:  # Perfect Math case
        line = str(c_id) + '|' + worker + "|1|" + worker_data[0] + '|' + worker_data[1] + '\n'  # First worker
    else:  # Proximity case
        line = str(c_id) + '|' + worker + "|2|" + str(candidates) + '\n'  # First worker
    print(line)
    return line


def verifier():
    global TOTAL_TIME
    ids = 0
    print("<count> ALGORITHM: LOC NAMES <> RUPA NAMES")
    info_unam, data_out, authors_out, rupa_file = get_files()
    # HEADER: NumeroEmpleado,CodigoEntidad,ApellidoPaterno,ApellidoMaterno,Nombre,Entidad
    while True:
        line = get_info_line(info_unam)
        if not line:
            break
        workers = line.pop(2)
        workers = workers.split("##")
        line[0] = ids
        rupa_iterator = iter(csv.reader(rupa_file))
        for i, worker in enumerate(workers):
            rupa_info = perfect_match(rupa_iterator, worker)
            if rupa_info:
                rupa_file.seek(0)  # Rewind RUPA iterator
                author_line = authors_manager(rupa_info, worker, ids, 1)
                authors_out.write(author_line)
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
        ids += 1
    print("TOTAL TIME: ", TOTAL_TIME/60, "minutes", (TOTAL_TIME/60)/60, "hours", ((TOTAL_TIME/60)/60)/24, "days")
    rupa_file.close()
    authors_out.close()
    data_out.close()


verifier()
