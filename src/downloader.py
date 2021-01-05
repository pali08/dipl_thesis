class FileDownloader:
    FTP_SERVER = 'ftp://ftp.ebi.ac.uk'
    FTP_PATH_TO_A_M_O_FILES = '/pub/databases/msd/status/'
    FTP_PATH_TO_PDB_FILES = '/pub/databases/pdb/data/structures/divided/mmCIF/'
    FTP_PATH_TO_VALIDATION_REPORT_FILES = '/pub/databases/pdb/validation_reports/'
    HTTP_SERVER = 'https://www.ebi.ac.uk'
    HTTP_PATH_TO_REST_FILES = '/pdbe/api/pdb/entry/'
    HTTP_SERVER_WEBCHEM = 'http://webchem.ncbr.muni.cz'
    HTTP_WEBCHEM_PATH_TO_VDB_FILES = '/Platform/ValidatorDb/Data/'
    HTTP_WEBCHEM_SOURCE_BY_STRUCTURES = '?source=ByStructure'
    HTTP_PATH_TO_PDB_UPDATED = '/pdbe/entry-files/download/'

    def __init__(self, url, save_filepath):
        self.url = url
        self.save_filepath = save_filepath
