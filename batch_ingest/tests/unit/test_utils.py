import batch_ingest.utils.tools as ut
import batch_ingest.utils.validate as uv


def test_unixtime_to_yyyymmdd():
    unixtime = 1640995200
    year, month, day = ut.unixtime_to_yyyymmdd(unixtime)
    assert year == "2022"
    assert month == "01"
    assert day == "01"


class TestJobStatusLogger:
    job = "x job"

    def test_log_job_status_success(self):
        success = True
        msg = ut.log_job_status(self.job, success)
        assert msg == f"Successfully ingested all {self.job} data!"

    def test_log_job_status_failure(self):
        success = False
        msg = ut.log_job_status(self.job, success)
        assert msg == f"Failed to ingest all {self.job} data."


class TestValparse:
    def test_try_valparse_success(self, coincap_response):
        response, datamodel = coincap_response
        result_data, valparsed = uv.try_valparse(response, datamodel)
        assert result_data == datamodel.parse_obj(response).dict()
        assert valparsed is True

    def test_try_valparse_invalidtype(self, coincap_response_invalidtype):
        response, datamodel = coincap_response_invalidtype
        result_data, valparsed = uv.try_valparse(response, datamodel)
        assert result_data == response
        assert valparsed is False

    def test_try_valparse_missingfield(self, coincap_response_missingfield):
        response, datamodel = coincap_response_missingfield
        result_data, valparsed = uv.try_valparse(response, datamodel)
        assert result_data == response
        assert valparsed is False

    def test_try_valparse_shallowextra(self, coincap_response_shallowextra):
        response, datamodel = coincap_response_shallowextra
        result_data, valparsed = uv.try_valparse(response, datamodel)
        assert result_data == response
        assert valparsed is False

    def test_try_valparse_deepextra(self, coincap_response_deepextra):
        response, datamodel = coincap_response_deepextra
        result_data, valparsed = uv.try_valparse(response, datamodel)
        assert result_data == response
        assert valparsed is False
