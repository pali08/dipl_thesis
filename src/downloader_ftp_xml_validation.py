from src.downloader_ftp import FtpFileDownloader


class XmlValidationDownloader(FtpFileDownloader):
    def __init__(self, molecule, save_filepath):
        self.molecule = molecule
        url = self.get_url()
        super().__init__(url, save_filepath)

    def get_url(self):
        return 'ftp://files.rcsb.org/pub/pdb/validation_reports/' + \
               self.molecule[1:-1] + '/' + self.molecule + '/' + self.molecule + \
               '_validation.xml.gz'

    def get_file(self):
        if not self.file_exists_on_ftp():
            searched_string = self.molecule + '_validation.xml'
