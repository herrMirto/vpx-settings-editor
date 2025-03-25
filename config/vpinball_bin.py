from config_utils import get_vpx_binary_path

class VPinballBin:
    def __init__(self, filepath=None):
        if filepath is None:
            filepath = get_vpx_binary_path()
        self.filepath = filepath

    def get_filepath(self):
        return self.filepath     