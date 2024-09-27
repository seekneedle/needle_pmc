from haystack.components.writers import DocumentWriter
from haystack.components.converters import PyPDFToDocument, TextFileToDocument, DOCXToDocument
from haystack.components.preprocessors import DocumentCleaner
from custom_components.document_splitter_cn import DocumentSplitterCN
from haystack.components.routers import FileTypeRouter
from haystack.components.joiners import DocumentJoiner
from haystack.components.embedders import OpenAIDocumentEmbedder
from haystack_integrations.document_stores.elasticsearch import ElasticsearchDocumentStore
from haystack import Pipeline
from pathlib import Path
from utils.es_utils import ESDatabase


class PreprocessingPipeline:
    def __init__(
        self,
        separator: str = "word",
        max_tokens: int = 200,
        overlap: int = 0,
        language: str = 'cn',
        index_name: str = 'default',
        emb_model: str = 'bge-m3',
    ):

        self.separator = separator
        self.max_tokens = max_tokens
        self.overlap = overlap
        self.language = language
        self.index_name = index_name
        self.emb_model = emb_model
        

    def get_es_preprocessing_pipeline(self):
        ## 初始化
        document_store = ESDatabase(index=self.index_name).get_es_document_store()
        file_type_router = FileTypeRouter(mime_types=["text/plain", "application/pdf","application/vnd.openxmlformats-officedocument.wordprocessingml.document"])
        text_file_converter = TextFileToDocument()
        pdf_converter = PyPDFToDocument()
        docx_converter = DOCXToDocument()
        document_joiner = DocumentJoiner() #将所有文档作为一个文档列表
        document_cleaner = DocumentCleaner() #删除空格  
        document_splitter_cn = DocumentSplitterCN(split_by=self.separator, split_length=self.max_tokens, split_overlap=self.overlap,language=self.language) 
        document_embedder = OpenAIDocumentEmbedder(model=self.emb_model)
        document_writer = DocumentWriter(document_store)
        
        ## 添加组件
        preprocessing_pipeline = Pipeline()
        preprocessing_pipeline.add_component(instance=file_type_router, name="file_type_router")
        preprocessing_pipeline.add_component(instance=text_file_converter, name="text_file_converter")
        preprocessing_pipeline.add_component(instance=pdf_converter, name="pypdf_converter")
        preprocessing_pipeline.add_component(instance=docx_converter, name="docx_converter")
        preprocessing_pipeline.add_component(instance=document_joiner, name="document_joiner")
        preprocessing_pipeline.add_component(instance=document_cleaner, name="document_cleaner")
        preprocessing_pipeline.add_component(instance=document_splitter_cn, name="document_splitter_cn")
        preprocessing_pipeline.add_component(instance=document_embedder, name="document_embedder")
        preprocessing_pipeline.add_component(instance=document_writer, name="document_writer")     

        ## 连接组件
        preprocessing_pipeline.connect("file_type_router.text/plain", "text_file_converter.sources")
        preprocessing_pipeline.connect("file_type_router.application/pdf", "pypdf_converter.sources")
        preprocessing_pipeline.connect("file_type_router.application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                   "docx_converter.sources")
        preprocessing_pipeline.connect("text_file_converter", "document_joiner")
        preprocessing_pipeline.connect("pypdf_converter", "document_joiner")
        preprocessing_pipeline.connect("docx_converter", "document_joiner")
        preprocessing_pipeline.connect("document_joiner", "document_cleaner")
        preprocessing_pipeline.connect("document_cleaner", "document_splitter_cn")
        preprocessing_pipeline.connect("document_splitter_cn", "document_embedder")
        preprocessing_pipeline.connect("document_embedder", "document_writer")

        return preprocessing_pipeline
    
    
    def run(self,file_path):
        preprocessing_pipeline = self.get_es_preprocessing_pipeline()
        #preprocessing_pipeline.run({"file_type_router": {"sources": list(Path(file_path).glob("**/*"))}}) 
        preprocessing_pipeline.run({"file_type_router": {"sources": [file_path]}}) 
    
