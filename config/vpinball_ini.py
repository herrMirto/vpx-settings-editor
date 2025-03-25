import re
from collections import OrderedDict
from config_utils import get_vpx_ini_path

class VPinballINI:
    def __init__(self, filepath=None):
        if filepath is None:
            filepath = get_vpx_ini_path()
        self.filepath = filepath
        self.lines = []  
        self.sections = OrderedDict()
        self._load()
    
    def _load(self):
        """Load the .init file preserving order and comments."""
        current_section = None
        section_content = []
        
        with open(self.filepath, 'r', encoding='utf-8') as f:
            for line in f:
                self.lines.append(line)  
                
                match = re.match(r'\[(.+?)\]', line)
                if match:
                    if current_section:
                        self.sections[current_section] = section_content  
                    current_section = match.group(1)
                    section_content = []
                
                if current_section:
                    section_content.append(line)
                
        if current_section:
            self.sections[current_section] = section_content  
    
    def get_section_subset(self, section, keys):
        """Retorna dict with specific options from a give section"""
        if section not in self.sections:
            return {}
        
        subset = OrderedDict()
        for line in self.sections[section]:
            match = re.match(r'([^#;\[]\S+)\s*=\s*(.*)', line)  
            if match:
                key, value = match.groups()
                if key in keys:
                    subset[key] = value
        
        return subset
    
    def get_section_value(self, section, key, fallback=0):
        subset = self.get_section_subset(section, [key])
        return subset.get(key, fallback)

    def update_section_subset(self, section, updates):
        """Update subset values in a given section, adding missing keys."""
        if section not in self.sections:
            return

        new_section_content = []
        updated_keys = set()

        for line in self.sections[section]:
            match = re.match(r'([^#;\[]\S+)\s*=\s*(.*)', line)
            if match:
                key, value = match.groups()
                if key in updates:
                    new_line = f"{key} = {updates[key]}\n"
                    new_section_content.append(new_line)
                    updated_keys.add(key)
                else:
                    new_section_content.append(line)
            else:
                new_section_content.append(line)

        for key, value in updates.items():
            if key not in updated_keys:
                new_section_content.append(f"{key} = {value}\n")

        self.sections[section] = new_section_content
    
    def save(self, output_path=None):
        """Save the .ini file keeping format."""
        output_path = self.filepath  
        with open(output_path, 'w', encoding='utf-8') as f:
            for section, content in self.sections.items():
                for line in content:
                    f.write(line)