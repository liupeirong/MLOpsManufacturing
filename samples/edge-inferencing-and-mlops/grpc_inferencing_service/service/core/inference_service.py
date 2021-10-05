import grpc
from protos import inference_pb2, inference_pb2_grpc


# This class can be used for validating any parameters in the grpc request
# Any sort of input checking can live as part of init or something else here
class RequestData:
    x1 = float()
    x2 = float()

    def __init__(self, request: inference_pb2.InferenceRequest):
        self.x1 = request.x1
        self.x2 = request.x2


class InferenceService(inference_pb2_grpc.InferenceServicer):
    def __init__(self, clf):
        self.clf = clf

    def _send_result(self, prediction: int, warnings, errors):
        result = {
            "prediction": prediction,
            "warnings": warnings,
            "errors": errors
        }

        return inference_pb2.InferenceResponse(**result)

    def _get_prediction(self, requestData: RequestData):
        # This function allows for more complex preprocessing to be done if needed
        return self.clf.predict([[requestData.x1, requestData.x2]])[0]

    def GetRecommendation(self, request, context):
        if request is None or not request:  # not request checks if request is an empty object
            return inference_pb2.InferenceResponse(errors=["Input cannot be None"])

        try:
            y_pred = -1
            errors = []
            requestData = RequestData(request)

            if self.clf is None:
                errors = ["Error: There is no model"]
                return self._send_result(y_pred, [], errors)

            y_pred = self._get_prediction(requestData)
            return self._send_result(y_pred, [], errors)

        except Exception as ex:
            msg = f"Runtime error occurred during inferencing: {ex}"
            context.set_details(msg)
            context.set_code(grpc.StatusCode.INTERNAL)

            return inference_pb2.InferenceResponse()
