from openfigi import (
    IdType,
    MappingJob,
    OpenFIGIDataSource,
)


def test_smoke():
    assert OpenFIGIDataSource is not None
    assert MappingJob is not None
    assert IdType is not None
