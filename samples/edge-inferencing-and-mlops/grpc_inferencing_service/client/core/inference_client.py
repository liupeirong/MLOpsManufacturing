import grpc
from protos import inference_pb2, inference_pb2_grpc


class InferenceClient(inference_pb2_grpc.InferenceServicer):
    def __init__(self, host: str, port: str):
        # instantiate a channel
        self.channel = grpc.insecure_channel(
            '{}:{}'.format(host, port))

        # bind the client and the server
        self.stub = inference_pb2_grpc.InferenceStub(self.channel)

    def send_inference_request(self, x1: int, x2: int) -> object:
        request = inference_pb2.InferenceRequest(x1=x1, x2=x2)
        return self.stub.GetRecommendation(request)
