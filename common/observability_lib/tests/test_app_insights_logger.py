from src.app_insights_logger import AppInsightsLogger


def test_get_run_id_having_online_context(mocker):
    mock_run = mocker.MagicMock()
    mock_run.id = 'FOO'
    mock_run.name = 'FOO1'
    mock_run.experiment.name = 'BAR'
    mock_run.parent.id = 'BAZ'
    mock_run.parent.get_portal_url.return_value = 'portal_url'

    expected_run_id = "FOO"
    expected_custom_dimensions = {
        'custom_dimensions': {
            "parent_run_id": 'BAZ',
            "step_id": 'FOO',
            "step_name": 'FOO1',
            "experiment_name": 'BAR',
            "run_url": 'portal_url',
            "offline_run": False
        }
    }

    # action
    logger = AppInsightsLogger(mock_run)
    actual_run_id = logger.run_id
    actual_custom_dimensions = logger.custom_dimensions

    # logger.custom_dimensions
    assert actual_run_id == expected_run_id
    assert actual_custom_dimensions == expected_custom_dimensions


def test_get_run_id_having_online_context_using_buildid(mocker):
    # arrange
    mock_run = mocker.MagicMock()
    mock_run.id = 'OfflineRun'
    expected_run_id = "BAR"
    mocker.patch(
        'src.app_insights_logger.Env.build_id',
        new_callable=mocker.PropertyMock,
        return_value=expected_run_id
    )

    expected_custom_dimensions = {
        'custom_dimensions': {
            "run_id": expected_run_id,
            "offline_run": True
        }
    }

    # action
    logger = AppInsightsLogger(mock_run)
    actual_run_id = logger.run_id
    actual_custom_dimensions = logger.custom_dimensions

    # logger.custom_dimensions
    assert actual_run_id == expected_run_id
    assert actual_custom_dimensions == expected_custom_dimensions


# def test_constructor():
#     pass


# class RealAppInsightsLogger(AppInsightsLogger):
#     def __init__(self):
#         self.logger = logging.getLogger(__name__)
#         self.env = MockEnv("")
#         self.tracer = Tracer()


# class MockEnv:
#     def __init__(self, run_id):
#         self.build_id = run_id


# class MockSpan:
#     def __init__(self, name):
#         self.span_kind = None
#         self.attributes = {}


# class TestObservability(unittest.TestCase):
#     @patch("src.app_insights_logger.AppInsightsLogger")
#     def setUp(self, mock_app_insights_logger):
#         self.concert_app_insights_logger = RealAppInsightsLogger()
#         self.mock_app_insights_logger = mock_app_insights_logger

#     def test_get_run_id_having_online_context_using_uuid(self):
#         self.concert_app_insights_logger.env.build_id = ""

#         response = self.concert_app_insights_logger.\
#             get_run_id_and_set_context(MockRun("OfflineRun"))

#         self.assertIsNotNone(response)


#     @patch.object(Tracer, "start_span")
#     def test_start_span_having_online_context(self, mock_tracer):
#         name = "foo"
#         mock_tracer.return_value = MockSpan(name)
#         test_span = self.concert_app_insights_logger.start_span(name)
#         mock_tracer.assert_called_with(name)
#         self.assertEqual(test_span.span_kind, SpanKind.SERVER)
#         self.assertEqual(test_span.attributes['http.method'], 'START')
#         self.assertEqual(test_span.attributes['http.route'], name)


# if __name__ == "__main__":
#     unittest.main()
