import sqlalchemy
#from django.db.models.fields.related import ForeignKey
print sqlalchemy.__version__

import gaclient
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey,PickleType
from sqlalchemy.sql import select
from sqlalchemy.sql import and_, or_, not_

import ga
import random

import sys
import types

def str_to_class(field):
    try:
        identifier = getattr(sys.modules[__name__], field)
    except AttributeError:
        raise NameError("%s doesn't exist." % field)
    if isinstance(identifier, (types.ClassType, types.TypeType)):
        return identifier
    raise TypeError("%s is not a class." % field)

    
class DataBase:
    
     
    def __init__(self,db=None,reset=False,echo=False):
        
        if db == None:
            #self.engine = create_engine('sqlite:///:memory:', echo=echo)
            #self.engine = create_engine('mysql://pyouser:12345@localhost:80/pyoga',echo=echo)
            self.engine = create_engine('sqlite:///pyoga.db', echo=True)
        else:
            self.engine = create_engine(db,echo)
            
        self.conn = self.engine.connect()


        self.metadata = MetaData(self.engine)

     
    

        self.genes = Table('genes', self.metadata,
              Column('id', Integer, primary_key=True),
              Column('type', String(32)),
              Column('data',PickleType)              
              )

        self.nomes = Table('nomes', self.metadata,
              Column('id', Integer, primary_key=True),
              Column('title', String(16)),
              Column('composer', String(16)),              
              Column('mum_id',Integer,ForeignKey('nomes.id')),
              Column('dad_id',Integer,ForeignKey('nomes.id'))              
      
              )

        self.nome_genes =Table('nome_genes',self.metadata,
              Column('id', Integer, primary_key=True),
              Column('nome_id',Integer,ForeignKey('nomes.id')),
              Column('gene_id',Integer,ForeignKey('genes.id'))          
              )

 
        if reset:
            self.metadata.drop_all()
        
        self.metadata.create_all(self.engine) 

        self.gene_pool={}
        self.nome_pool={}

    def load_nome(self,nome_id):
        
        """
        Load the nome with nome_id
        If it is already in the nome_pool return cached version
        """
        
        # if it's in the pool return it
        if nome_id in self.nome_pool:
            print " Cached Nome found"
            return self.nome_pool[nome_id]
        
        
        
        s = select([self.nomes],self.nomes.c.id==nome_id)
        result=self.conn.execute(s)
      
      
        row=result.fetchone()
        
        
        if row == None:
            raise NameError('Invalid nome_id='+str(nome_id))
     
        nome=self.load_nome_from_row(row)
        
        result.close()
        return nome
    
    def load_nome_from_row(self,row):
        #print row
        nome=ga.Pheno(row['title'],row['composer'])
        nome.id=row['id']
        nome.mum_id=row['mum_id']
        nome.dad_id=row['dad_id']
        
        self.nome_pool[nome.id]=nome
        
        
        
        s = select([self.genes],
                   and_(self.nome_genes.c.nome_id==nome.id,self.genes.c.id==self.nome_genes.c.gene_id))
        result=self.conn.execute(s)

        for row in result:
            key=row['id']
            if key in self.gene_pool:
                gene=self.gene_pool[key]
            else:
                print "ZZZ",row[1]
                cc=eval("ga."+row['type'])   # create class from the name in type field
                print cc
                gene=cc()
                
                gene.id=row['id']
                
                gene.data=row['data']
                self.gene_pool[gene.id]=gene
                
            nome.genes.append(gene)  
                
        result.close()
        # print nome
        return nome

    def save_nome(self,nome):
        """
        Save the nome and all it's genes in the database.
        
        TODO duplicates etc.
        """
        
        ins=self.nomes.insert().values(title=nome.title,composer=nome.composer,mum_id=nome.mum_ID,dad_id=nome.dad_ID)
        
        result=self.conn.execute(ins)
        
        #print result.inserted_primary_key
        
        key=result.inserted_primary_key[0]
        
        nome.id=key
        
        
        for g in nome.genes:
            print g
            cn=g.__class__.__name__
            ins=self.genes.insert().values(type=cn,data=g.data)
            result=self.conn.execute(ins)
            key=result.inserted_primary_key[0]
            g.id=key
            # print nome.id,g.id
            #ins=genomes.insert().values(nome_id=nome.id,gene_id=g.id)
            ins=self.nome_genes.insert().values(gene_id=g.id,nome_id=nome.id)
            result=self.conn.execute(ins)


    def load_random(self):
        self.load_all_nomes()
        
        keys=self.nome_pool.keys()  
            
        id1=random.choice(keys)
               
        return self.nome_pool[id1]


    def load_all_nomes(self):
        s = select([self.nomes])
        result=self.conn.execute(s)
  
 
        for row in result:
        # if it's in the pool return it
            nome_id=row['id']
            if nome_id in self.nome_pool:
                print " Cached Nome found"
                continue
            
            self.load_nome_from_row(row)
            
                

if __name__ == "__main__":
    

 
    
    def testSave():
        n_delay=3
        n_mod=2
        n_voice=2
        n_envelope=3
       
        
        pheno=ga.Pheno()
        
        pheno.randomize(n_delay=n_delay,n_envelope=n_envelope,n_modulation=n_mod,n_voice=n_voice)
        
        print pheno.nome
        db.save_nome(pheno.nome)
        
        n_delay=5
        n_voice=3
        
        pheno=ga.Pheno()
        pheno.randomize(n_delay=n_delay,n_envelope=n_envelope,n_modulation=n_mod,n_voice=n_voice)
        print pheno.nome
        db.save_nome(pheno.nome)
        
    def testLoad(nome_id):
        return db.load_nome(nome_id)
  
  
             
    db=DataBase(reset=True,echo=False)
   
        
    testSave()
    #testSave()
    
    nome1=testLoad(1)
    #print "1 ",nome1
    
    nome2=testLoad(2)
    
    #print "2 ",nome2    

    breeder=ga.Breeder()
    print "------------------------------------------__"
    nome=breeder.mate(nome1,nome2)
    
    #print nome
    db.save_nome(nome)
    
    c=gaclient.Client()
    
    c.build(nome)             # build Pheno on the server from the clinets nome
    c.send("pheno.play()")
    
    #print nome

    