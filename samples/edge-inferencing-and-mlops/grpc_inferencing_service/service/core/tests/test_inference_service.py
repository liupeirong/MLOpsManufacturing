from unittest.mock import MagicMock, patch
import grpc

from protos import inference_pb2
from core.inference_service import InferenceService

default_predict_response = [1]
# Computed values from the default_predict_response above
default_inference_response = inference_pb2.InferenceResponse(
    prediction=1,
    warnings=[],
    errors=[]
)


# Mock init of InferenceService (cuts out loading in model in RecommendationInference)
def mock_init(self):
    mclf = MagicMock()
    mclf.predict.return_value = default_predict_response
    self.clf = mclf
    self.is_integration_test = False
    print('mock init')


class TestGetRecommendation:
    """Unit tests for GetRecommendation function"""
    request = inference_pb2.InferenceRequest(
                x1=-0.697672367,
                x2=79.73386858,
            )

    def test_default_response(self):
        with patch.object(InferenceService, '__init__', mock_init):
            service = InferenceService()
            response = service.GetRecommendation(self.request, None)
            assert response is not None
            assert response == default_inference_response

    def test_empty_default_proto_input(self):
        with patch.object(InferenceService, '__init__', mock_init):
            service = InferenceService()
            response = service.GetRecommendation(inference_pb2.InferenceRequest(), None)
            assert response is not None
            assert response == default_inference_response

    def test_empty_input(self):
        with patch.object(InferenceService, '__init__', mock_init):
            service = InferenceService()
            response = service.GetRecommendation({}, None)
            assert response is not None
            assert response.errors is not None
            assert len(response.errors) == 1

    def test_none_input(self):
        with patch.object(InferenceService, '__init__', mock_init):
            service = InferenceService()
            response = service.GetRecommendation(None, None)
            assert response is not None
            assert response.errors is not None
            assert len(response.errors) == 1

    def test_handles_exception(self):
        with patch.object(InferenceService, '__init__', mock_init):
            service = InferenceService()
            service.clf.predict.side_effect = Exception('Some runtime error occurred')
            mock_context = MagicMock()
            response = service.GetRecommendation(self.request, mock_context)
            mock_context.set_code.assert_called_with(grpc.StatusCode.INTERNAL)
            assert response is not None
