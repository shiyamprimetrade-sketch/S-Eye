"""Recorded data/config/source identities and same-host seeded reproducibility."""
import hashlib,platform
from pathlib import Path
from seye.core.storage import checksum
from seye.learning.packet_prototypes import records_digest
from seye.learning.packet_linear import fit


def reproduce(training,validation,config):
    first=fit(training,validation,**config);second=fit(training,validation,**config)
    source=Path(__file__).with_name('packet_linear.py').read_bytes()
    return {'schema_version':1,'training_sha256':records_digest(training),'validation_sha256':records_digest(validation),
            'configuration':dict(config),'algorithm_source_sha256':hashlib.sha256(source).hexdigest(),
            'python':platform.python_version(),'first_model_sha256':checksum(first),'second_model_sha256':checksum(second),
            'identical':first==second,'scope':'same-host same-input run; cross-platform byte identity not guaranteed'}
