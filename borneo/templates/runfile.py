from borneo.parameters import parse_xml, Query


def main(argv):

    try:
        xml_path = argv[0]
    except IndexError:
        print("Please provide an xml paramter file")
        return
