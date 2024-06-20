from JsonToMarkdown import JsonToMarkdownV3
from JsonToXML import JsonToXML, JsonToXMLV2
import os

# Parent directory where JSON files are stored
input_directory = "../OP"

# Output directory where Markdown files will be saved
output_directory = "../OP_XML"

PROCESS_TYPE = "xml"  # Change to 'xml' to convert to XML instead of Markdown


def main():
    # Ensure the output directory exists, create if it does not
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # List all JSON files in the input directory
    json_files = [
        os.path.join(input_directory, f)
        for f in os.listdir(input_directory)
        if f.endswith(".json")
    ]

    if PROCESS_TYPE == "xml":
        for file in json_files:
            output_file = os.path.join(
                output_directory, os.path.basename(file).replace(".json", ".xml")
            )
            converter = JsonToXMLV2(file)
            converter.convert()
            converter.save_to_file(output_file)
            print(f"Converted {file} to {output_file}")
    else:
        for file in json_files:
            output_file = os.path.join(
                output_directory, os.path.basename(file).replace(".json", ".md")
            )
            converter = JsonToMarkdownV3(file)
            converter.convert()
            converter.save_to_file(output_file)
            print(f"Converted {file} to {output_file}")


if __name__ == "__main__":
    main()
