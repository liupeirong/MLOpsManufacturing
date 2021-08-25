# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

jsonKBDetails = {
    "id": "9d091697-fb8c-4ed5-9ac0-35bf8273bfff",
    "hostName": "https://myqnamakerbot.azurewebsites.net",
    "lastAccessedTimestamp": "2018-03-16T10:59:46Z",
    "lastChangedTimestamp": "2018-03-16T10:58:10Z",
    "lastPublishedTimestamp": "2018-03-16T10:59:56Z",
    "name": "My QnA Maker Bot",
    "userId": "03a4f4ce-30a6-4ec6-b436-02bcdf6153e1",
    "urls": [
        "https://docs.microsoft.com/en-in/azure/cognitive-services/qnamaker/faqs",
        "https://docs.microsoft.com/en-us/bot-framework/resources-bot-framework-faq",
    ],
    "sources": ["Custom Editorial", "SurfaceManual.pdf"],
}

jsonKB = {
    "qnaDocuments": [
        {
            "alternateQuestionClusters": [
                {
                    "alternateQuestionList": [
                        {
                            "autoSuggestedCount": 0,
                            "question": "What is This?",
                            "userSuggestedCount": 100,
                        }
                    ],
                    "clusterHead": "What is This?",
                    "totalAutoSuggestedCount": 0,
                    "totalUserSuggestedCount": 100,
                }
            ],
            "answer": "yes! only azure",
            "context": {"isContextOnly": False, "prompts": []},
            "id": 1,
            "isDocumentText": False,
            "lastUpdatedTimestamp": "2021-06-08T11:52:25.286+00:00",
            "metadata": [],
            "questions": ["azure"],
            "source": "Editorial",
        }
    ]
}

jsonKBwOALFeedback = {
    "qnaDocuments": [
        {
            "alternateQuestionClusters": [],
            "answer": "yes! only azure",
            "context": {"isContextOnly": False, "prompts": []},
            "id": 1,
            "isDocumentText": False,
            "lastUpdatedTimestamp": "2021-06-08T11:52:25.286+00:00",
            "metadata": [],
            "questions": ["azure"],
            "source": "Editorial",
        }
    ]
}


alMergeIntoKB = {
    "qnaDocuments": [
        {
            "alternateQuestionClusters": [
                {
                    "alternateQuestionList": [
                        {
                            "autoSuggestedCount": 5,
                            "question": "What is the best Cloud?",
                            "userSuggestedCount": 1001,
                        },
                        {
                            "autoSuggestedCount": 2,
                            "question": "What is the future Cloud?",
                            "userSuggestedCount": 201,
                        },
                    ],
                    "clusterHead": "What is the best Cloud?",
                    "totalAutoSuggestedCount": 7,
                    "totalUserSuggestedCount": 1202,
                }
            ],
            "answer": "yes! only azure",
            "context": {"isContextOnly": False, "prompts": []},
            "id": 1,
            "isDocumentText": False,
            "lastUpdatedTimestamp": "2021-06-08T11:52:25.286+00:00",
            "metadata": [],
            "questions": ["azure"],
            "source": "Editorial",
        },
        {
            "alternateQuestionClusters": [
                {
                    "alternateQuestionList": [
                        {
                            "autoSuggestedCount": 20,
                            "question": "What is an ok cloud?",
                            "userSuggestedCount": 501,
                        }
                    ],
                    "clusterHead": "What is an ok cloud?",
                    "totalAutoSuggestedCount": 20,
                    "totalUserSuggestedCount": 501,
                }
            ],
            "answer": "nooooooooo! use azure",
            "context": {"isContextOnly": False, "prompts": []},
            "id": 2,
            "isDocumentText": False,
            "lastUpdatedTimestamp": "2021-06-08T11:52:25.286+00:00",
            "metadata": [],
            "questions": ["aws"],
            "source": "Editorial",
        },
    ]
}

alMergeFromKB = {
    "qnaDocuments": [
        {
            "alternateQuestionClusters": [
                {
                    "alternateQuestionList": [
                        {
                            "autoSuggestedCount": 8,
                            "question": "What is the nicest Cloud?",
                            "userSuggestedCount": 801,
                        }
                    ],
                    "clusterHead": "What is the best Cloud?",
                    "totalAutoSuggestedCount": 8,
                    "totalUserSuggestedCount": 801,
                },
                {
                    "alternateQuestionList": [
                        {
                            "autoSuggestedCount": 6,
                            "question": "What is the best Enterprise Cloud?",
                            "userSuggestedCount": 601,
                        }
                    ],
                    "clusterHead": "What is the best Enterprise Cloud?",
                    "totalAutoSuggestedCount": 6,
                    "totalUserSuggestedCount": 601,
                },
            ],
            "answer": "yes! only azure",
            "context": {"isContextOnly": False, "prompts": []},
            "id": 1,
            "isDocumentText": False,
            "lastUpdatedTimestamp": "2021-06-08T11:52:25.286+00:00",
            "metadata": [],
            "questions": ["azure"],
            "source": "Editorial",
        },
        {
            "alternateQuestionClusters": [
                {
                    "alternateQuestionList": [
                        {
                            "autoSuggestedCount": 10,
                            "question": "What is an ok cloud?",
                            "userSuggestedCount": 201,
                        }
                    ],
                    "clusterHead": "What is an ok cloud?",
                    "totalAutoSuggestedCount": 10,
                    "totalUserSuggestedCount": 201,
                }
            ],
            "answer": "nooooooooo! use azure",
            "context": {"isContextOnly": False, "prompts": []},
            "id": 2,
            "isDocumentText": False,
            "lastUpdatedTimestamp": "2021-06-08T11:52:25.286+00:00",
            "metadata": [],
            "questions": ["aws"],
            "source": "Editorial",
        },
    ]
}

alMergeExpectedResult = {
    "qnaDocuments": [
        {
            "alternateQuestionClusters": [
                {
                    "alternateQuestionList": [
                        {
                            "autoSuggestedCount": 5,
                            "question": "What is the best Cloud?",
                            "userSuggestedCount": 1001,
                        },
                        {
                            "autoSuggestedCount": 2,
                            "question": "What is the future Cloud?",
                            "userSuggestedCount": 201,
                        },
                        {
                            "autoSuggestedCount": 8,
                            "question": "What is the nicest Cloud?",
                            "userSuggestedCount": 801,
                        },
                    ],
                    "clusterHead": "What is the best Cloud?",
                    "totalAutoSuggestedCount": 15,
                    "totalUserSuggestedCount": 2003,
                },
                {
                    "alternateQuestionList": [
                        {
                            "autoSuggestedCount": 6,
                            "question": "What is the best Enterprise Cloud?",
                            "userSuggestedCount": 601,
                        }
                    ],
                    "clusterHead": "What is the best Enterprise Cloud?",
                    "totalAutoSuggestedCount": 6,
                    "totalUserSuggestedCount": 601,
                },
            ],
            "answer": "yes! only azure",
            "context": {"isContextOnly": False, "prompts": []},
            "id": 1,
            "isDocumentText": False,
            "lastUpdatedTimestamp": "2021-06-08T11:52:25.286+00:00",
            "metadata": [],
            "questions": ["azure"],
            "source": "Editorial",
        },
        {
            "alternateQuestionClusters": [
                {
                    "alternateQuestionList": [
                        {
                            "autoSuggestedCount": 30,
                            "question": "What is an ok cloud?",
                            "userSuggestedCount": 702,
                        }
                    ],
                    "clusterHead": "What is an ok cloud?",
                    "totalAutoSuggestedCount": 30,
                    "totalUserSuggestedCount": 702,
                }
            ],
            "answer": "nooooooooo! use azure",
            "context": {"isContextOnly": False, "prompts": []},
            "id": 2,
            "isDocumentText": False,
            "lastUpdatedTimestamp": "2021-06-08T11:52:25.286+00:00",
            "metadata": [],
            "questions": ["aws"],
            "source": "Editorial",
        },
    ]
}

kbCreateResponse = {"operationId": "1"}

operationStatusResponseRunning = {"operationState": "Running"}

operationStatusResponseCompleted = {
    "operationState": "Completed",
    "resourceLocation": "/knowledgebases/abc",
}
