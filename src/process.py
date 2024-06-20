from JsonToMarkdown import JsonToMarkdown, JsonToMarkdownV3


json_file = "../single-op.json"
output_file = "output.md"


def main():
    converter = JsonToMarkdownV3(json_file)
    converter.convert()
    converter.save_to_file(output_file)


if __name__ == "__main__":
    main()
