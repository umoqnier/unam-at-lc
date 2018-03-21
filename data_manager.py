from requester import xml_requester
import xml.etree.ElementTree as ET
from datetime import datetime
from os.path import isfile

NS = {"zs": "http://www.loc.gov/zing/srw/", "srw_dc": "info:srw/schema/1/dc-schema",
      "dc": "http://purl.org/dc/elements/1.1/"}  # For XML tags with namespaces


def process_input_file(file):  # TODO: Create function to process from file the codes of an institution
    data = []
    return data


def get_institution_codes():
    variants = ["Universidad Nacional Autonoma de Mexico", "UNAM",
                "U.N.A.M", "Univ. Nac. Aut. Mex.", "National Autonomous University of Mexico",
                "Univ. Nac. Auton. Mex.", "Univ. Nac. Auton. de México", ]
    try:
        file = open("unam_codes_NOT.txt", 'r')  # Not yet this input
        variants = process_input_file(file)
        file.close()
        return variants
    except FileNotFoundError as err:
        print(err, "returning default variants of UNAM: ", variants)
        return variants


def data_cleaner(data):
    string = "|"
    for record in data.findall("zs:record", NS):  #TODO: Make with an exception
        dc = record.find("./zs:recordData/srw_dc:dc", NS)

        # POSITION
        position = record.find("zs:recordPosition", NS).text + '|'

        # TITLE
        try:
            string += dc.find("dc:title", NS).text + '|'
        except AttributeError:
            print("###Title not found at the " + position + "record")
            string += "|not_found|"

        # CREATOR(S)
        creators = dc.findall("dc:creator", NS)
        if creators:
            for creator in creators:
                try:
                    string += creator.text + '##'
                except TypeError:
                    print("[TAG] Error at Creator(s) at the " + position + "record")
            string = string[:-2]  # Remove the last separators ##
        else:
            print("###Creator(s) not found at the " + position + "record")
            string += 'not_found|'
        string += '|'

        # TYPE
        try:
            string += dc.find("dc:type", NS).text + '|'
        except AttributeError:
            print("###Type not found at the " + position + "record")
            string += 'not_found|'

        # PUBLISHER
        try:
            string += dc.find("dc:publisher", NS).text + '|'
        except AttributeError:
            print("###Publisher not found at the " + position + "record")
            string += "not_found|"

        # DATE
        try:
            string += dc.find("dc:date", NS).text + '|'
        except AttributeError:
            print("###Date not found at the " + position + "record")
            string += "not_found|"

        # LANGUAGE
        try:
            string += dc.find("dc:language", NS).text + '|'
        except AttributeError:
            print("###Publisher not found at the " + position + "record")
            string += "not_found|"

        # DESCRIPTION
        descriptions = dc.findall("dc:description", NS)
        if descriptions:
            for description in descriptions:
                try:
                    string += description.text + '##'
                except TypeError:
                    print("[TAG] Error at description(s) at the " + position + "record")
            string = string[:-2]  # Remove the last separators ##
        else:
            print("###Description(s) not found at the " + position + "record")
            string += 'not_found|'
        string += '|'

        # IDENTIFIER
        identifiers = dc.findall("dc:identifier", NS)
        if identifiers:
            for identifier in identifiers:
                try:
                    string += identifier.text + '##'
                except TypeError:
                    print("[TAG] Error at identifier(s) at the " + position + "record")
            string = string[:-2]  # Remove the last separators ##
        else:
            print("###Identifier(s) not found at the " + position + "record")
            string += 'not_found|'
        string += '|\n|'

    return string[:-1]  # Remove the last pipe "|"


def header_to_file(keyword, year):
    """
    This function create the file and name it with current date. Also set the information header
    :param keyword: Current variant of UNAM
    :param year: Current year fot the query
    :return: The file object
    """
    today = datetime.now()
    file_name = str(today.year) + "_" + str(today.month) + "_" + str(today.day) + ".txt"
    if isfile("./" + file_name):
        f_out = open(file_name, 'a')
        f_out.write("+" * 10 + "For: " + keyword + " at " + str(year) + "+" * 10 + "\n")
    else:
        f_out = open(file_name, 'a')
        f_out.write("|#|title|Creator(s)|type|publisher|date|language|description(s)|identifier(s)|\n")
        f_out.write("+" * 10 + "For: " + keyword + " at " + str(year) + "+"*10 + "\n")

    return f_out


def data_to_file(data, total, file, first_time=0):
    if first_time:
        file.write("total: " + str(total) + "=" * 10 + "\n")
    data_c = data_cleaner(data)
    file.write(data_c)


def scraper(xml, variant, year, file):
    root = ET.fromstring(xml)
    total_records = root.find("zs:numberOfRecords", NS).text
    try:
        next_record_position = root.find("zs:nextRecordPosition", NS).text
    except AttributeError:
        print("## LAST RECORD OF THE YEAR " + str(year))
        next_record_position = False
    records = root.find("zs:records", NS)
    data_to_file(records, total_records, file, 1)
    while next_record_position:
        next_content = xml_requester(variant, str(year), str(next_record_position))
        next_root = ET.fromstring(next_content)
        try:
            next_record_position = next_root.find("zs:nextRecordPosition", NS).text
        except AttributeError:
            records = next_root.find("zs:records", NS)
            data_to_file(records, total_records, file)  # The last data of a year
            break
        records = next_root.find("zs:records", NS)
        data_to_file(records, total_records, file)


def xml_processing(variants, year, start_record):
    """
    This function convert and process the xml data from function xml_requester
    :return:
    """
    for variant in variants:
        while year <= 2018:
            file_output = header_to_file(variant, year)
            print("+"*20 + "For " + str(year) + "+"*20 + " and " + variant)
            xml_content = xml_requester(variant, str(year), str(start_record))
            scraper(xml_content, variant, year, file_output)
            year += 1
        start_record = 1
        year = 2008


def main():
    variants = get_institution_codes()
    year = 2008
    start_record = 1
    print("Start Processing")
    xml_processing(variants, year, start_record)
    print("Finish...")


if __name__ == '__main__':
    main()
