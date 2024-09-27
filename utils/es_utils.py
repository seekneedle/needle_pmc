from haystack_integrations.document_stores.elasticsearch import ElasticsearchDocumentStore
from config import config
from typing import List
from elasticsearch import Elasticsearch 
import os


class ESDatabase:
    def __init__(self,index=None):        
        self.index = index
        self.document_store = self.get_es_document_store()
        self.es = Elasticsearch(config['es_hosts']) 
        
    def get_es_document_store(self):
        self.document_store = ElasticsearchDocumentStore(hosts=config['es_hosts'],index=self.index)
        return self.document_store  
    
    def get_documentid_by_filename(self,filename):
        doc_ids = []
        docs=self.document_store.filter_documents({"file_path":filename})
        if(len(docs)!=0):
            for d in docs:
                doc_ids.append(d.id)
        return doc_ids
    
    def delete_documents_by_docid(self,document_ids: List[str]):
        self.document_store.delete_documents(document_ids=document_ids)


    def delete_documents_by_filename(self,filename):
        doc_ids = self.get_documentid_by_filename(filename)
        self.delete_documents_by_docid(doc_ids)
        
    def get_all_filenames(self,max_size=1000):
        """获取index下的所有文件名"""
        body = {
            "size": 0,    
            "aggs": {
                "group_by_filename": {
                    "terms": {
                        "field": "file_path",
                        "size":max_size
                    }
                }
            }
        }  

        response = self.es.search(index=str(self.index), body=body)  
        aggregations = response['aggregations']['group_by_filename']['buckets'] 
        filenames = []
        if(len(aggregations)!=0):
            for bucket in aggregations:  
                filenames.append(bucket['key'].split('/')[-1])
        return filenames
        
    def get_chunks_by_filename(self,filename):
        filepath = os.path.join(config['filestore_root_dir'],str(self.index),filename)
        docs=self.document_store.filter_documents({"file_path":filepath})
        chunks_json = {"chunks":[{"chunk_id": d.id, "chunk_content": d.content} for d in docs]}  
        return chunks_json
    #
    # def delete_documents_by_filename(self,filename):
    #     chunks=self.get_chunks_by_filename(filename)
    #     document_ids=[]
    #     for chunk in chunks['chunks']:
    #         document_ids.append(chunk['chunk_id'])
    #     self.document_store.delete_documents(document_ids)
    
    def delete_document_store_by_index(self,index):
        if self.es.indices.exists(index=index):
            self.es.indices.delete(index=index)
            print(f"Index '{index}' has been deleted.")
        else:
            print(f"Index '{index}' does not exist.")