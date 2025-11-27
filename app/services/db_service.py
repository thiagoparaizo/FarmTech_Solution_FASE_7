from pymongo import MongoClient
from bson import ObjectId
from app.models.cultura import Cultura
from app.models.campo import Campo

class DatabaseService:
    def __init__(self, mongo_uri):
        self.client = MongoClient(mongo_uri)
        self.db = self.client.get_database()
        
        # Coleções
        self.culturas = self.db.culturas
        self.campos = self.db.campos
        
        # Inicializar as culturas padrão se não existirem
        self._inicializar_culturas_padrao()
    
    def _inicializar_culturas_padrao(self):
        """Inicializa as culturas padrão no banco de dados se não existirem"""
        if self.culturas.count_documents({}) == 0:
            # Adicionar cultura da mandioca
            mandioca = Cultura.from_dict(Cultura.get_mandioca_default())
            self.culturas.insert_one(mandioca.to_dict())
            
            # Adicionar cultura do feijão-caupi
            feijao = Cultura.from_dict(Cultura.get_feijao_caupi_default())
            self.culturas.insert_one(feijao.to_dict())
    
    # Métodos para culturas
    def obter_todas_culturas(self):
        """Retorna todas as culturas do banco de dados"""
        return list(self.culturas.find())
    
    def obter_cultura_por_id(self, cultura_id):
        """Retorna uma cultura específica pelo ID"""
        cultura = self.culturas.find_one({"_id": cultura_id})
        return cultura if cultura else None
    
    def obter_cultura_por_nome(self, nome_cultura):
        """Retorna uma cultura específica pelo nome"""
        cultura = self.culturas.find_one({"nome_cultura": nome_cultura})
        return cultura if cultura else None
    
    def adicionar_cultura(self, cultura):
        """Adiciona uma nova cultura ao banco de dados"""
        if isinstance(cultura, Cultura):
            return self.culturas.insert_one(cultura.to_dict()).inserted_id
        return self.culturas.insert_one(cultura).inserted_id
    
    def atualizar_cultura(self, cultura_id, dados_atualizados):
        """Atualiza uma cultura existente"""
        return self.culturas.update_one(
            {"_id": cultura_id},
            {"$set": dados_atualizados}
        ).modified_count
    
    def remover_cultura(self, cultura_id):
        """Remove uma cultura do banco de dados"""
        return self.culturas.delete_one({"_id": cultura_id}).deleted_count
    
    # Métodos para campos
    def obter_todos_campos(self):
        """Retorna todos os campos do banco de dados"""
        return list(self.campos.find())
    
    def obter_campo_por_id(self, campo_id):
        """Retorna um campo específico pelo ID"""
        campo = self.campos.find_one({"_id": campo_id})
        return campo if campo else None
    
    def obter_campos_por_produtor(self, nome_produtor):
        """Retorna todos os campos de um produtor específico"""
        return list(self.campos.find({"nome_produtor": nome_produtor}))
    
    def adicionar_campo(self, campo):
        """Adiciona um novo campo ao banco de dados"""
        if isinstance(campo, Campo):
            return self.campos.insert_one(campo.to_dict()).inserted_id
        return self.campos.insert_one(campo).inserted_id
    
    def atualizar_campo(self, campo_id, dados_atualizados):
        """Atualiza um campo existente"""
        return self.campos.update_one(
            {"_id": campo_id},
            {"$set": dados_atualizados}
        ).modified_count
    
    def remover_campo(self, campo_id):
        """Remove um campo do banco de dados"""
        return self.campos.delete_one({"_id": campo_id}).deleted_count