from utils.db_utils import ConnectSQL
from utils import files_utils
from utils.es_utils import ESDatabase
from core.preprocessing_pipeline import PreprocessingPipeline

def create_service(body):
    index_name = body['name']
    result = ConnectSQL().get_index_id_by_name(index_name)
    if(result):
        #todo：specific exception
        raise Exception("知识库名字已存在")
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

        index_id = ConnectSQL().insert_index_name(index_name)
        for f in body['files']:
            file_path = files_utils.save_file_to_index_path(str(index_id),f['file_name'],f['file_base64'])
            preprocessing_pipeline = PreprocessingPipeline(separator=separator, max_tokens=max_tokens, overlap=overlap,language=f['language'],index_name=index_id)
            preprocessing_pipeline.run(file_path)

        filenames = ESDatabase(index=str(index_id)).get_all_filenames()
    return index_id,filenames