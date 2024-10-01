from pathlib import Path

import vcr
from vcr import VCR

my_vcr = vcr.VCR(
    cassette_library_dir=str(Path(__file__).parent.absolute()) + '/fixtures/cassettes',
    path_transformer=VCR.ensure_suffix('.yml'),
    # see https://vcrpy.readthedocs.io/en/latest/usage.html for further details; e.g. 'once' (for just at the beginning) or 'all' (for always)
    record_mode='new_episodes',
    decode_compressed_response=True,
)
