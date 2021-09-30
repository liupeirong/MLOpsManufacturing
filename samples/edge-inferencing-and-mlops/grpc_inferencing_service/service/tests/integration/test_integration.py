import grpc
import os
import pytest
from protos import inference_pb2, inference_pb2_grpc


@pytest.mark.integration_test
class TestFeaturizer:

    @classmethod
    def setup_class(cls):
        port = os.getenv('GRPC_SERVER_PORT', '50051')
        host = os.getenv('GRPC_SERVER_HOST', 'localhost')
        # instantiate a channel
        cls.channel = grpc.insecure_channel(f"{host}:{port}")

        # bind the client and the server
        cls.stub = inference_pb2_grpc.InferenceStub(cls.channel)

    def test_default_response(self):
        request = inference_pb2.InferenceRequest(x1=1, x2=1)
        result = self.stub.GetRecommendation(request)

        assert hasattr(result, 'prediction')
        assert len(result.warnings) == 0
        assert len(result.errors) == 0
