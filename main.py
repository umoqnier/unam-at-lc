from data_manager import get_institution_codes
from data_manager import xml_processing
from rupa_validation import verifier


def main():
    variants = get_institution_codes()
    year = 2008
    start_record = 1
    print("Start Processing")
    total_records = xml_processing(variants, year, start_record)
    print("Finish... Total records", total_records)
    print("Start Creators validation")
    verifier()
    print("Finish Creators validation")


if __name__ == '__main__':
    main()