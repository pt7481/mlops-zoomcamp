from homework.tests import test_batch
from homework import batch

def test_read_data():
    df_input = test_batch.test_prepare_data()
    input_file = batch.get_input_path(2023, 1)
    df_input.to_parquet(
        input_file,
        engine='pyarrow',
        compression=None,
        index=False,
        storage_options=batch.options
    )