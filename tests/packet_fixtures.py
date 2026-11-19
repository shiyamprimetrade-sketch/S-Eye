from seye.core.storage import checksum

def packet(value):
    schema={'version':'seye-feature-pipeline-v1','components':[{'name':'scalar','version':'numeric-fixture-v1','dimension':1,'offset':0}],'dimension':1}
    return {'schema':schema,'schema_sha256':checksum(schema),'features':[value]}

def row(identifier,value,label,group=None):
    return {'id':identifier,'group':group or identifier,'label':label,'packet':packet(value),
            'content_sha256':checksum({'numeric_fixture':value,'capture':identifier}),'source_kind':'numeric_fixture'}

def data():
    return [row('ta',0,'a'),row('tb',1,'b')],[row('va',.01,'a'),row('vb',1.01,'b')]
