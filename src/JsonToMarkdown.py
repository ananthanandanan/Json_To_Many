import json


class JsonToMarkdown:
    def __init__(self, json_file):
        with open(json_file, "r") as file:
            self.data = json.load(file)
        self.markdown_lines = []

    def convert(self):
        self.parse_element(self.data, 1)

    def parse_element(self, element, level):
        if isinstance(element, dict):
            for key, value in element.items():
                self.add_heading(key, level)
                self.parse_element(value, level + 1)
        elif isinstance(element, list):
            for item in element:
                self.parse_element(item, level)
        else:
            self.add_text(element)

    def add_heading(self, text, level):
        self.markdown_lines.append(f'{"#" * level} {text}\n')

    def add_text(self, text):
        self.markdown_lines.append(f"{text}\n")

    def save_to_file(self, output_file):
        with open(output_file, "w") as file:
            file.writelines(self.markdown_lines)


class JsonToMarkdownV1:
    def __init__(self, json_file):
        with open(json_file, "r") as file:
            self.data = json.load(file)
        self.markdown_lines = []

    def convert(self):
        for item in self.data:
            self.parse_item(item)

    def parse_item(self, item):
        self.add_heading(item.get("code", ""), 1)
        self.add_heading(item.get("name", ""), 2)
        self.add_heading("Description", 3)
        self.add_text(item.get("description", ""))

        self.add_heading("Intended Results", 3)
        self.parse_list(item.get("intended_results", []))

        self.add_heading("Leadership Area", 3)
        self.parse_leadership_area(item.get("leadership_area", []))

        self.add_heading("Compliance Hierarchy", 3)
        self.parse_compliance_hierarchy(item.get("compliance_hierarchy", []))

    def parse_leadership_area(self, areas):
        for area in areas:
            self.add_heading(area.get("name", ""), 4)
            self.add_text(area.get("description", ""))
            self.parse_functional_areas(area.get("functional_areas", []))

    def parse_functional_areas(self, areas):
        for area in areas:
            self.add_heading(f'{area.get("type", "")}: {area.get("name", "")}', 5)
            self.add_text(area.get("description", ""))

    def parse_compliance_hierarchy(self, hierarchy):
        for item in hierarchy:
            self.add_heading(item.get("name", ""), 4)
            self.add_text(item.get("description", ""))
            self.parse_parts(item.get("parts", []))
            self.parse_specs(item.get("specs", []))

    def parse_parts(self, parts):
        for part in parts:
            self.add_heading(part.get("name", ""), 5)
            self.add_text(part.get("description", ""))
            self.parse_parts(part.get("parts", []))
            self.parse_specs(part.get("specs", []))

    def parse_specs(self, specs):
        if specs:
            self.add_heading("Specifications", 6)
            for spec in specs:
                self.add_text(f'- {spec.get("description", "")}')

    def parse_list(self, items):
        for item in items:
            self.add_text(f"- {item}")

    def add_heading(self, text, level):
        if text:
            self.markdown_lines.append(f'{"#" * level} {text}\n')

    def add_text(self, text):
        if text:
            self.markdown_lines.append(f"{text}\n")

    def save_to_file(self, output_file):
        with open(output_file, "w") as file:
            file.writelines(self.markdown_lines)


class JsonToMarkdownV2:
    def __init__(self, json_file):
        with open(json_file, "r") as file:
            self.data = json.load(file)
        self.markdown_lines = []

    def convert(self):
        for item in self.data:
            self.add_metadata(item)
            self.add_heading("Operating Practice", 1)
            self.add_text(item.get("name", ""))
            self.add_heading("Description", 1)
            self.add_text(item.get("description", ""))
            self.add_heading("Intended Results", 1)
            self.parse_list(item.get("intended_results", []))
            self.add_heading("Specification", 1)
            self.parse_compliance_hierarchy(item.get("compliance_hierarchy", []))
            self.add_heading("Accountability", 1)
            self.parse_leadership_area(item.get("leadership_area", []))

    def add_metadata(self, item):
        self.add_heading("METADATA", 1)
        self.add_text(f'- {item.get("code", "")}')
        co_codes = []
        am_codes = []
        if item.get("compliance_hierarchy"):
            for ch in item["compliance_hierarchy"]:
                if ch.get("code", "").startswith("CO"):
                    co_codes.append(ch.get("code", ""))
                if ch.get("parts"):
                    for part in ch["parts"]:
                        if part.get("code", "").startswith("CO"):
                            co_codes.append(part.get("code", ""))
                        if part.get("parts"):
                            for subpart in part["parts"]:
                                if subpart.get("code", "").startswith("CO"):
                                    co_codes.append(subpart.get("code", ""))
        if item.get("leadership_area"):
            for la in item["leadership_area"]:
                if la.get("code", "").startswith("AM"):
                    am_codes.append(la.get("code", ""))
                if la.get("functional_areas"):
                    for fa in la["functional_areas"]:
                        if fa.get("code", "").startswith("AM"):
                            am_codes.append(fa.get("code", ""))
        self.add_text(f'- {", ".join(co_codes)}')
        self.add_text(f'- {", ".join(am_codes)}')

    def parse_leadership_area(self, areas):
        for area in areas:
            self.parse_functional_areas(area.get("functional_areas", []))

    def parse_functional_areas(self, areas):
        for area in areas:
            if area.get("type", "") == "Accountable":
                self.add_text(f'- Accountable: {area.get("name", "")}')
            elif area.get("type", "") == "Responsible":
                self.add_text(f'- Responsible: {area.get("name", "")}')

    def parse_compliance_hierarchy(self, hierarchy):
        for item in hierarchy:
            self.add_text(f'- {item.get("name", "")}')
            codes = self.collect_codes(item)
            if item.get("specs"):
                self.parse_specs(
                    item.get("specs", []), codes
                )  # Pass the collected codes to parse_specs
            else:
                self.add_text(f"  - {codes}")  # Only add codes if there are no specs

    def collect_codes(self, item):
        codes = []
        if item.get("code"):
            codes.append(item.get("code"))
        if item.get("parts"):
            for part in item["parts"]:
                part_codes = self.collect_codes(part)  # Recursively collect codes
                if part_codes:
                    codes.append(
                        part_codes
                    )  # Append the collected codes as a single string
        return " > ".join(codes)  # Join with ' > ' at this level only

    def parse_specs(self, specs, codes):
        specs_descriptions = []
        for spec in specs:
            description = (
                spec.get("description", "").replace("\n", " ").strip()
            )  # Clean new line characters and trim
            specs_descriptions.append(description)
        if specs_descriptions:
            formatted_specs = " - ".join(
                specs_descriptions
            )  # Join all specifications descriptions
            self.add_text(
                f"  - {codes} - {formatted_specs}"
            )  # Append codes followed by specs descriptions
        else:
            self.add_text(f"  - {codes}")  # Just codes if no descriptions available

    def parse_parts(self, parts, level):
        for part in parts:
            self.add_text(f'{" " * level}- {part.get("name", "")}')
            codes = self.collect_codes(part)
            self.add_text(f'{" " * (level + 1)}- {codes}')
            self.parse_specs(part.get("specs", []), level + 2)
            self.parse_parts(part.get("parts", []), level + 2)

    def parse_list(self, items):
        for item in items:
            self.add_text(f"- {item}")

    def add_heading(self, text, level):
        if text:
            self.markdown_lines.append(f'{"#" * level} {text}\n')

    def add_text(self, text):
        if text:
            self.markdown_lines.append(f"{text}\n")

    def save_to_file(self, output_file):
        with open(output_file, "w") as file:
            file.writelines(self.markdown_lines)


import json


class JsonToMarkdownV3:
    def __init__(self, json_file):
        with open(json_file, "r") as file:
            self.data = json.load(file)
        self.markdown_lines = []

    def convert(self):
        for item in self.data:
            self.add_metadata(item)
            self.add_heading("Operating Practice", 1)
            self.add_text(item.get("name", ""))
            self.add_heading("Description", 1)
            self.add_text(item.get("description", ""))
            self.add_heading("Intended Results", 1)
            self.parse_list(item.get("intended_results", []))
            self.add_heading("Specification", 1)
            self.parse_compliance_hierarchy(item.get("compliance_hierarchy", []))
            self.add_heading("Accountability", 1)
            self.parse_leadership_area(item.get("leadership_area", []))

    def add_metadata(self, item):
        self.add_heading("METADATA", 1)
        self.add_text(f'- {item.get("code", "")}')
        co_codes = self.collect_co_codes(item)
        am_codes = self.collect_am_codes(item)
        self.add_text(f'- {", ".join(co_codes)}')
        self.add_text(f'- {", ".join(am_codes)}')

    def collect_co_codes(self, item):
        codes = []
        if item.get("compliance_hierarchy"):
            for ch in item["compliance_hierarchy"]:
                if ch.get("code", "").startswith("CO"):
                    codes.append(ch.get("code", ""))
                if ch.get("parts"):
                    for part in ch["parts"]:
                        codes.extend(self.collect_co_codes(part))
        return codes

    def collect_am_codes(self, item):
        codes = []
        if item.get("leadership_area"):
            for la in item["leadership_area"]:
                if la.get("code", "").startswith("AM"):
                    codes.append(la.get("code", ""))
                if la.get("functional_areas"):
                    for fa in la["functional_areas"]:
                        if fa.get("code", "").startswith("AM"):
                            codes.append(fa.get("code", ""))
        return codes

    def parse_compliance_hierarchy(self, hierarchy):
        for item in hierarchy:
            self.add_text(f'- {item.get("name", "")}')
            self.handle_item(item, "")

    def handle_item(self, item, prefix):
        current_code = item.get("code", "").strip()
        if prefix:
            prefix = f"{prefix} > {current_code}"  # Correctly format with ' > ' for non-root items
        else:
            prefix = current_code  # Direct assignment for root item without leading '>'

        if "parts" in item and item["parts"]:
            # If the item has parts, recursively handle each
            for part in item["parts"]:
                self.handle_item(part, prefix)
        else:
            # If no more parts, print the accumulated codes and specs
            self.add_text(f"  - {prefix}")
            self.parse_specs(item.get("specs", []))

    def parse_specs(self, specs):
        for spec in specs:
            description = spec.get("description", "").replace("\n", "\n      ").strip()
            self.add_text(f"    - {description}")

    def parse_leadership_area(self, areas):
        for area in areas:
            self.parse_functional_areas(area.get("functional_areas", []))

    def parse_functional_areas(self, areas):
        for area in areas:
            if area.get("type", "") == "Accountable":
                self.add_text(f'- Accountable: {area.get("name", "")}')
            elif area.get("type", "") == "Responsible":
                self.add_text(f'- Responsible: {area.get("name", "")}')

    def parse_list(self, items):
        for item in items:
            self.add_text(f"- {item}")

    def add_heading(self, text, level):
        if text:
            self.markdown_lines.append(f'{"#" * level} {text}\n')

    def add_text(self, text):
        if text:
            self.markdown_lines.append(f"{text}\n")

    def save_to_file(self, output_file):
        with open(output_file, "w") as file:
            file.writelines(self.markdown_lines)
