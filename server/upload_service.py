from utils.db_utils import ConnectSQL
from utils import files_utils
from utils.es_utils import ESDatabase
from core.preprocessing_pipeline import PreprocessingPipeline
import os
from config import config

def upload_service(body,vector_store_id):
    result = ConnectSQL().check_index_id_exists(int(vector_store_id))
    if(not result):
        #todo：specific exception
        raise Exception(f'不存在id为{vector_store_id}的知识库')
    elif(len(body['files'])==0):
        #todo：specific exception
        raise Exception("文件不能为空")
    else:
        chunk_type = int(body['chunking_strategy']['chunk_type'])
        max_tokens = int(body['chunking_strategy']['max_tokens'])
        overlap =int( body['chunking_strategy']['overlap'])
        separator = str(body['chunking_strategy']['separator'])
        if(chunk_type == 0):
            max_tokens = 200
            overlap = 30
            separator = 'word' 

        for f in body['files']:
            filepath = os.path.join(config['filestore_root_dir'],str(vector_store_id),f['file_name'])
            print(filepath)
            #删除es上的documents
            ESDatabase(index=str(vector_store_id)).delete_documents_by_filename(filepath)
            #删除本地存储的文件
            files_utils.delete_file(filepath)                
            #上传新的files 
            file_path = files_utils.save_file_to_index_path(str(vector_store_id),f['file_name'],f['file_base64'])
            PreprocessingPipeline(separator=separator, max_tokens=max_tokens, overlap=overlap,language=f['language'],index_name=str(vector_store_id)).run(file_path)

        filenames = ESDatabase(index=str(vector_store_id)).get_all_filenames()
    return filenames