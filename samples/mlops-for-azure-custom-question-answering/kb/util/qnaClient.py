# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
Helper class to make REST API calls to the QnA Maker service.

The official Python SDK handles much of this, but currently does not
support Active Learning feedback extraction in download.

This utility class was created to provide that support.

"""

import requests
import json
from http import HTTPStatus


class QnaClient:
    def __init__(self, endpoint, subscription_key, kb_id):
        self.endpoint = endpoint
        self.subscription_key = subscription_key
        self.kb_id = kb_id

    def get_kb_details(self):
        url = f'{self.endpoint}/knowledgebases/{self.kb_id}'
        headers = {'Ocp-Apim-Subscription-Key': self.subscription_key}

        response = requests.request("GET", url, headers=headers)

        if(response.status_code == HTTPStatus.OK):
            kb_details = response.text
            kb_details_json = json.loads(kb_details)
            return kb_details_json
        else:
            raise Exception('Get KB details (qnaClient.py get_kb_details) failed with: ' + response.text)

    def download(self, environment):
        url = f'{self.endpoint}/knowledgebases/{self.kb_id}/{environment}/qna'
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key
        }
        response = requests.request("GET", url, headers=headers)

        if(response.status_code == HTTPStatus.OK):
            qnas = response.text
            qnas_json = json.loads(qnas)
            return qnas_json['qnaDocuments']
        else:
            raise Exception('Replace KB (qnaClient.py download) failed with: ' + response.text)

    def replace_knowledgebase(self, qnas):
        url = f'{self.endpoint}/knowledgebases/{self.kb_id}'
        payload = json.dumps({
            "qnAList": qnas
        })
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key,
            'Content-Type': 'application/json'
        }

        response = requests.request("PUT", url, headers=headers, data=payload)
        if(response.status_code != HTTPStatus.NO_CONTENT):
            raise Exception('Replace KB (qnaClient.py replace_knowledgebase) failed with: ' + response.text)

    def publish_knowledgebase(self):
        url = f'{self.endpoint}/knowledgebases/{self.kb_id}'
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key,
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers)
        if(response.status_code != HTTPStatus.NO_CONTENT):
            raise Exception('Publish KB (qnaClient.py publish_knowledgebase) failed with: ' + response.text)

    def sync_feedback(self, source_qnas, timespan):
        # Get questions with changes since timestamp in destination env
        #   (e.g. PROD), which is only Active Learning feedback in
        #   non-authoring environments (e.g. PROD).

        #  Note: This must be from the 'Test' index since that is where
        #   Active Learning Feedback is stored.
        dest_url = f'{self.endpoint}/knowledgebases/{self.kb_id}/Test/qna?changedSince={timespan}'
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key
        }
        response = requests.request("GET", dest_url, headers=headers)
        destination_qnas = response.text
        if(response.status_code == HTTPStatus.OK):
            dest_qnas_json = json.loads(destination_qnas)['qnaDocuments']
        else:
            raise Exception('Syncing of Feedback (qnaClient.py sync_feedback) failed with: ' + response.text)

        # Iterate through IDs of updated questions (these should
        #   be the only ones that have been changed in non-authoring
        #   environments like PROD) due to new Active Learning Feedback.
        #   Then, add that feedback to the matching questions in the source.
        for q in dest_qnas_json:
            # Only deal with ones that contain alternateQuestionClusters
            #   (i.e. Active Learning data).
            if len(q['alternateQuestionClusters']) > 0:
                source_q_index = next((index for (index, d) in enumerate(source_qnas) if d["id"] == q["id"]), None)
                updated_q = source_qnas[source_q_index]
                updated_q['alternateQuestionClusters'] = q['alternateQuestionClusters']
                source_qnas[source_q_index] = updated_q
        return source_qnas

    def merge_feedback(self, incoming_qnas):
        # Get questions destination env  (e.g. QA)
        # merge only Active Learning feedback incoming from
        #   non-authoring environments (e.g. PROD).

        #  Note: This must be from the 'Test' index since that is where
        #   Active Learning Feedback is stored.
        dest_url = f'{self.endpoint}/knowledgebases/{self.kb_id}/Test/qna'
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key
        }
        response = requests.request("GET", dest_url, headers=headers)
        destination_qnas = response.text
        if(response.status_code == HTTPStatus.OK):
            dest_qnas_json = json.loads(destination_qnas)['qnaDocuments']
        else:
            raise Exception('Syncing of Feedback (qnaClient.py merge_feedback) failed with: ' + response.text)

        # Iterate through IDs of incoming questions (these should
        #   be the only ones that have been changed in non-authoring
        #   environments like PROD) due to new Active Learning Feedback.
        #   Then, add that feedback to the matching questions in the destination.
        for q in incoming_qnas:
            # Only deal with ones that contain alternateQuestionClusters
            #   (i.e. Active Learning data).
            if len(q['alternateQuestionClusters']) > 0:
                dest_q_index = next((index for (index, d) in enumerate(dest_qnas_json) if d["id"] == q["id"]), None)
                updated_q = dest_qnas_json[dest_q_index]
                updated_q['alternateQuestionClusters'] = self.merge_alternateQuestionClusters(
                                                                q['alternateQuestionClusters'],
                                                                updated_q['alternateQuestionClusters']
                                                                )
                dest_qnas_json[dest_q_index] = updated_q
        return dest_qnas_json

    def merge_alternateQuestionClusters(self, incoming_cluster, destination_cluster):

        for i_cluster_head in incoming_cluster:
            clusterHeadFound = False
            for d_cluster_head in destination_cluster:
                if i_cluster_head['clusterHead'] == d_cluster_head['clusterHead']:
                    clusterHeadFound = True
                    d_cluster_head['alternateQuestionList'] = self.merge_alternateQuestionLists(
                                                                i_cluster_head['alternateQuestionList'],
                                                                d_cluster_head['alternateQuestionList']
                                                                )
                # recount
                totalAutoSuggestedCount = 0
                totalUserSuggestedCount = 0
                for question in d_cluster_head['alternateQuestionList']:
                    totalAutoSuggestedCount += question['autoSuggestedCount']
                    totalUserSuggestedCount += question['userSuggestedCount']
                d_cluster_head['totalAutoSuggestedCount'] = totalAutoSuggestedCount
                d_cluster_head['totalUserSuggestedCount'] = totalUserSuggestedCount

            if not clusterHeadFound:
                destination_cluster.append(i_cluster_head)

        return destination_cluster

    def merge_alternateQuestionLists(self, incoming_questionlist, destination_questionlist):
        for i_question in incoming_questionlist:
            questionFound = False
            for d_question in destination_questionlist:
                if i_question['question'] == d_question['question']:
                    questionFound = True
                    d_question['autoSuggestedCount'] += i_question['autoSuggestedCount']
                    d_question['userSuggestedCount'] += i_question['userSuggestedCount']

            if not questionFound:
                destination_questionlist.append(i_question)

        return destination_questionlist
