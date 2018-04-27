import csv
from string import punctuation, digits
from difflib import SequenceMatcher


# TODO: Modificara para probar todos los autores de cada publicacion
# TODO: Solucionar problema con escritura de archivo de salida
# TODO: Agregar verificación por tokens
# TODO: Agregar pesos propios dada la verificacion por tokens

def get_file():
    f = open("info_unam_loc.txt", "r")
    return f


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
    d = {"Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U"}
    for c in string:
        if c in d.keys():
            string = string.replace(c, d[c])
    return string


def verifier():
    print("<count> ALGORITHM: LOC NAMES <> RUPA NAMES")
    info_unam = get_file()
    output_f = open("salida.txt", "a")
    f =  open("rupa.csv", "r")
    # HEADER: NumeroEmpleado,CodigoEntidad,ApellidoPaterno,ApellidoMaterno,Nombre,Entidad
    while True:
        line = get_line(info_unam)
        workers = line[2]
        if not workers:
            break
        workers = workers.split("##")
        rupa_iterator = iter(csv.reader(f))
        if perfect_match(rupa_iterator, workers, f):
            line.pop()  # Remove the last \n
            line = "|".join(line)
            line += '|1\n'
            print(line)
            output_f.write(line)
            f.seek(0)
            continue  # At least one worker is at RUPA
        else:
            f.seek(0)
            rupa_iterator = iter(csv.reader(f))
            level = proximity(rupa_iterator, workers, f)
            if level in ['2', '3']:
                line.pop()  # Remove the last \n
                line = '|'.join(line)
                line += '|' + level
                print(line)
                output_f.write(line)
                f.seek(0)
                continue  # At least one worker is at RUPA
            else:
                print("Workers not found at RUPA-->", workers)
                f.seek(0)
                continue
    f.close()
    output_f.close()


def perfect_match(rupa, loc_names, file):
    rupa_info = rupa.__next__()
    for loc_name in loc_names:
        loc_name = strip_special_chars(loc_name)
        loc_name = replace_accents(loc_name)
        loc_name = loc_name.upper()
        if ("UNIVERSIDAD" in loc_name) or ("MEXICO" in loc_name):
            continue
        while rupa_info:
            rupa_name = ' '.join(rupa_info[2:5])
            if loc_name == rupa_name:
                print("PERFECT MATCH-->", loc_name, "=", rupa_name)
                return True
            else:
                try:
                    rupa_info = rupa.__next__()
                except StopIteration:
                    file.seek(0)
                    rupa = iter(csv.reader(file))
                    rupa_info = rupa.__next__()
                    break
    return False


def proximity(rupa, loc_names, file):
    count = 0
    rupa_info = rupa.__next__()
    for loc_name in loc_names:
        loc_name = ''.join(ch for ch in loc_name if ch not in punctuation + digits)
        loc_name = loc_name.upper()
        if "UNIVERSIDAD" in loc_name:
            continue
        while rupa_info:
            rupa_name = ' '.join(rupa_info[2:5])
            seq = SequenceMatcher(None, loc_name, rupa_name)
            ratio = seq.ratio()
            if ratio >= 0.8999999999:
                print(str(count) + " PROXIMITY (>= 0.89): " + loc_name + " ~ " + rupa_name)
                return '2'
            elif ratio >= 0.7999999999:
                print(str(count) + " PROXIMITY (>= 0.79): " + loc_name + " ~ " + rupa_name)
                return '3'
            else:
                try:
                    rupa_info = rupa.__next__()
                    count += 1
                except StopIteration:
                    file.seek(0)
                    rupa = iter(csv.reader(file))
                    rupa_info = rupa.__next__()
                    count = 0
                    break

    return '0'


verifier()
