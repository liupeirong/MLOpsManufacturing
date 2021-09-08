/* eslint-disable @typescript-eslint/no-explicit-any */
// <Dependencies>
import "dotenv/config";
import * as fs from "fs";
import * as readline from "readline";
import fetch from 'node-fetch';
// </Dependencies>

// <GlobalParams>
const QNA_ENDPOINT_HOST_NAME = String(process.env.QNA_ENDPOINT_HOST_NAME);
const QNA_ENDPOINT_KEY = String(process.env.QNA_ENDPOINT_KEY);
const QNA_KNOWLEDGEBASE_ID = String(process.env.QNA_KNOWLEDGEBASE_ID);

const TOP_ANSWER = Number(process.env.TOP_ANSWER);
const TOP_PROMPT = Number(process.env.TOP_PROMPT);
const SCORE_THRESHOLD = Number(process.env.SCORE_THRESHOLD) * 100;
const SCORE_SIMILARITY = Number(process.env.SCORE_SIMILARITY) * 100;
const MULTI_TURN_DEPTH = Number(process.env.MULTI_TURN_DEPTH);

const TEST_FILE = String(process.env.TEST_FILE);
const OUTPUT_FILE = String(process.env.OUTPUT_FILE);

const UNKNOWN_ANSWER_ID = -1;
const PRECISE_ANSWERING = Boolean(process.env.PRECISE_ANSWERING);

const QNA_REST_API_URI = QNA_ENDPOINT_HOST_NAME + "/knowledgebases/" + QNA_KNOWLEDGEBASE_ID + "/generateAnswer";
const OUTPUT_HEADER = "Test Question\tTarget Answer Ids\tSuccess\tTurn\tSuccess Id\tConfidence\tAnswer\tPrecise Answer\tReturned All Ids\tReturned All Confidences\tConfidence Dropped Ids\tSimilarity Dropped Ids\r\n";
// </GlobalParams>

class Accuracy {
    //qnamakerClient!: QnAMakerRuntimeClient;
    rs!: fs.ReadStream;
    totalCount!: number;
    trueTurn: Array<number> = [];
    output!: fs.PathLike;
    ws!: number;
    found = false;
    
    // additional metrics for analytics and improvement..
    successId!: number;
    successConfidence!: number;
    successAnswer!: any;
    successPreciseAnswer!: any;
    answerIds: Array<number[]> = [];
    answerConfidences: Array<number[]> = [];
    similarityDroppedSIds: number[] = [];
    confidenceDroppedSIds: number[] = [];

    // elapsed time calc..
    startTime:Date = null;

    init() {
        console.log("0. init...");

        this.totalCount = 0;

        for (let inx = 0; inx < MULTI_TURN_DEPTH; inx++) {
            this.trueTurn[inx] = 0;
        }

        console.log("---- Global Variables ----");
        console.log(`QNA_ENDPOINT_HOST_NAME=${QNA_ENDPOINT_HOST_NAME}`);
        console.log(`QNA_ENDPOINT_KEY=${QNA_ENDPOINT_KEY}`);
        console.log(`QNA_KNOWLEDGEBASE_ID=${QNA_KNOWLEDGEBASE_ID}`);

        console.log(`TOP_ANSWER=${TOP_ANSWER}`);
        console.log(`TOP_PROMPT=${TOP_PROMPT}`);
        console.log(`SCORE_THRESHOLD=${SCORE_THRESHOLD}`);
        console.log(`MULTI_TURN_DEPTH=${MULTI_TURN_DEPTH}`);
        console.log(`PRECISE_ANSWERING=${PRECISE_ANSWERING}`);
        
        console.log(`TEST_FILE=${TEST_FILE}`);
        console.log(`OUTPUT_FILE=${OUTPUT_FILE}`);
        console.log("---- Global Variables ----");
    }

    initRuntime() {
        console.log("1. initRuntime...");

        // 0. connect to KB..
        console.log("  - QnA Maker REST API URI : " + QNA_REST_API_URI);

        // 1. load test data file..
        this.rs = fs.createReadStream(TEST_FILE);
        console.log("  - load test data file : " + TEST_FILE);

        // 2. create output file..
        this.output = OUTPUT_FILE;
        console.log("  - create output file : " + OUTPUT_FILE);
        this.ws = fs.openSync(this.output, 'w');

        // 3. write output headers..
        fs.writeSync(this.ws, OUTPUT_HEADER);
    }

    async startTest() {
        console.log("2. startTest..");
        this.startTime = new Date();
        console.log("  - start time: " + this.startTime);

        // create reader from reader stream..
        const rd = readline.createInterface(this.rs);

        // readline..
        for await (const line of rd) {
            ++this.totalCount;
            const testData = line.split('\t');

            // call accuracy test.. 
            // testData[0] = test question, testData[1] = target qnaid
            await this.calcAccuracy(testData[0], testData[1]);
        }

        // endTest..
        this.endTest();
    }

    // iterates to find the anwser..
    async calcAccuracy(question: string, answerId: string) {
        try {
            console.log(this.totalCount, " '" + question + "' -> " + answerId);
            
            // init controls.. 
            this.found = false;
            this.answerIds = [];
            for (let inx = 0; inx < MULTI_TURN_DEPTH; inx++) {
                this.answerIds[inx] = [];
            }

            this.answerConfidences = [];
            for (let inx = 0; inx < MULTI_TURN_DEPTH; inx++) {
                this.answerConfidences[inx] = [];
            }

            // metrics init..
            this.successId = -1;
            this.successConfidence = 0;
            this.successAnswer = null;
            this.successPreciseAnswer =  null;
            this.similarityDroppedSIds = [];
            this.confidenceDroppedSIds = [];

            // 1. get answers and check similarity..
            const answers = this.checkConfidenceSimilarity(await this.getAnswers(question));

            // 2. calc multi-turn aware accuracy..
            const turn = await this.calcMultiturn(0, answers, answerId.split(','));

            console.log("Returned All Ids : " + JSON.stringify(this.answerIds));

            // 3. write test result..
            // "Test Question\tTarget Answer Ids\tSuccess\tTurn
            // \tSuccess Id\tConfidence
            // \tAnswer\tPrecise Answer
            // \tReturned All Ids\ttReturned All Confidences
            // \tConfidence Dropped Ids\tSimularity Dropped Ids\r\n"
            const outputLine = question + '\t' + answerId + '\t' + this.found + '\t' + turn 
                            + '\t' + this.successId + '\t' + this.successConfidence 
                            + '\t' + JSON.stringify(this.successAnswer) + '\t' + JSON.stringify(this.successPreciseAnswer)
                            + '\t' + JSON.stringify(this.answerIds) + '\t' + JSON.stringify(this.answerConfidences)
                            + '\t' + JSON.stringify(this.confidenceDroppedSIds) + '\t' + JSON.stringify(this.similarityDroppedSIds) + '\r\n';

            fs.writeSync(this.ws, outputLine);
        } catch (err) {
            console.log(err);
            throw err;
        }
    }

    async calcMultiturn(turnCnt: number, answers: Array<any>, answerId: Array<string>) {
        // escape condition..
        if (this.found || answers.length === 0 || turnCnt >= MULTI_TURN_DEPTH)
            return turnCnt;

        try {
            // 1. check answers..
            console.log("TURN : " + (turnCnt + 1));
            let foundTurn = -1;

            foundTurn = await this.checkAnswers(turnCnt, answers, answerId);

            if (foundTurn >= 0)
                return foundTurn;
            
            // 2. check prompts of answers..
            turnCnt++;
            console.log("TURN : " + (turnCnt + 1));
            foundTurn = await this.checkPrompts(turnCnt, answers, answerId);

            if (foundTurn > 0)
                return foundTurn;

            // 3. drill down to prompts.. 
            if (++turnCnt >= MULTI_TURN_DEPTH) {
                return turnCnt - 1;
            }

            for (const answer of answers) {
                // prompt click event --> recursion
                for (const prompt of answer.context['prompts']) {
                    const _answers = this.checkConfidenceSimilarity(await this.getAnswersByQnaId(String(prompt.qnaId)));
                    await this.calcMultiturn(turnCnt - 1, _answers, answerId);
                    
                    if (this.found)
                        return turnCnt + 1;
                }
            }
        } catch (err) {
            console.error(err);
            throw err;
        }

        return turnCnt + 1;
    }


    async checkAnswers(turnCnt: number, answers: Array<any>, answerId: Array<string>) {
        for (const answer of answers) {
            console.log("  answer.id = " + answer.id);
            this.answerIds[turnCnt].push(answer.id);
            this.answerConfidences[turnCnt].push(answer.score);


            // no proper answer found..
            if (answer.id === UNKNOWN_ANSWER_ID)
                return turnCnt + 1;

            for (const id of answerId) {
                if (answer.id === Number(id)) {
                    this.trueTurn[turnCnt] += 1;
                    this.found = true;
                    console.log("  -> answer found : " + answer.id + " - turn : " + (turnCnt + 1));

                    // metrics..
                    this.successId = answer.id;
                    this.successConfidence = answer.score;
                    this.successAnswer = answer.answer;
                    if (answer.answerSpan != null)
                        this.successPreciseAnswer = answer.answerSpan.text;

                    return turnCnt + 1;
                }
            }
        }
        // -1 means continue to the next turn as there are answers but there's not the right one.
        return -1;
    }

    async checkPrompts(turnCnt: number, answers: Array<any>, answerId: Array<string>) {
        for (const answer of answers) {
            for (const prompt of answer.context.prompts) {
                console.log("\tprompt.qnaId=" + prompt.qnaId);
                this.answerIds[turnCnt].push(prompt.qnaId);

                // 3. check prompts..
                for (const id of answerId) {
                    if (prompt.qnaId === Number(id)) {
                        this.trueTurn[turnCnt] += 1;
                        this.found = true;
                        console.log("\t-> prompt found : " + id + " - turn : " + (turnCnt + 1));

                        // metrics..
                        await this.getPromptResult(prompt.qnaId);

                        return turnCnt + 1;
                    }
                }
            }
        }
        // -1 means continue to the next turn as there are prompts but there's not the right one.
        return -1;
    }

    async getPromptResult(qnaId:number){
        const _answers = await this.getAnswersByQnaId(String(qnaId));
        const answer = _answers.answers[0];

        this.successId = answer.id;
        this.successConfidence = answer.score;
        this.successAnswer = answer.answer;

        if (answer.answerSpan != null)
            this.successPreciseAnswer = answer.answerSpan.text;
    }

    // get answer by question..
    async getAnswers(_question: string): Promise<any> {
        const _body = {
            'question': _question,
            'top': TOP_ANSWER,
            'scoreThreshold': 0,
            //"rankerType": "QuestionOnly",
            'answerSpanRequest': {'enable': PRECISE_ANSWERING, 'scoreThreshold': 0, 'topAnswersWithSpan': 1}
        };

        // console.log(JSON.stringify(_body));
            
        try {
            return await fetch(QNA_REST_API_URI, 
                {
                    method: 'POST',
                    headers: {
                        'Content-type': 'application/json; charset=utf-8',
                        'Ocp-Apim-Subscription-Key': QNA_ENDPOINT_KEY
                    },
                    body: JSON.stringify(_body)
                })
                .then(response => response.json());
        } catch (err) {
            console.error(err);
            throw err;
        }
    }
    
    // get answer by qnaId..
    async getAnswersByQnaId(_qnaID: string): Promise<any> {
        try {
            return await fetch(QNA_REST_API_URI, 
                {
                    method: 'POST',
                    headers: {
                        'Content-type': 'application/json; charset=utf-8',
                        'Ocp-Apim-Subscription-Key': QNA_ENDPOINT_KEY
                    },
                    body: JSON.stringify({
                        'qnaId': _qnaID,
                        'top': TOP_ANSWER,
                        'scoreThreshold': 0,
                        'answerSpanRequest': {'enable': PRECISE_ANSWERING, 'scoreThreshold': 0, 'topAnswersWithSpan': 1}
                    })
                })
                .then(response => response.json());
        } catch (err) {
            console.error(err);
            throw err;
        }   
    }

    checkConfidenceSimilarity(answers: any): Array<any> {
        if (answers.error != null){
            console.log(answers.err);
            throw new Error("Error occured during calling generateAnswer API. Check .env or connection to QnA Maker..");
        }
        
        const _answers: Array<any> = [];
        let firstScore = 0;
        let inx = 0;

        //console.log(answers);

        for (const answer of answers.answers) {
            if (inx === 0) {
                if (answer.score >= SCORE_THRESHOLD){
                     firstScore = answer.score;
                    _answers[inx] = answer;
                } else {
                    this.confidenceDroppedSIds.push(answer.id);
                }

            } else {
                if (answer.score >= SCORE_THRESHOLD){
                    if (firstScore - answer.score <= SCORE_SIMILARITY) {
                        _answers[inx] = answer;
                    } else {
                        this.similarityDroppedSIds.push(answer.id);
                    }
               } else {
                   this.confidenceDroppedSIds.push(answer.id);
               }
            }

            inx++;
        }

        return _answers;
    }

    // call back for end of file..
    endTest() {
        console.log("3. endTest..");

        // 4. dump accuracy result..
        this.dumpResult();
    }

    dumpResult() {
        const endTime = new Date();
        console.log("4. dumpResult...\n");
        console.log("*** Accuracy Test Result");
        console.log("  - Total Test Count : " + this.totalCount);
        console.log("  - Test input file : " + this.rs.path);
        console.log("  - Test output file : " + this.output);
        console.log("  - Start Time : " + this.startTime);
        console.log("  - End Time : " + endTime);
        console.log("  - Elapsed Time: " + (endTime.getTime()- this.startTime.getTime())/1000) + " secs";
        console.log("  - Multi-Turn Accuracy Result");

        let sum = 0;
        for (let inx = 1; inx < MULTI_TURN_DEPTH + 1; inx++) {
            sum += this.trueTurn[inx - 1];
            console.log(`    > True Turn[${inx}] = ` + this.trueTurn[inx - 1] + `  \t| True Total[${inx}] =` + sum + `  \t| Accuracy[${inx}] = ` + (sum / this.totalCount));
        }
        console.log("***");
    }

    async main() {
        try {
            // 0. init..
            console.log("* Accuracy Test Starts..");
            this.init();

            // 1. init QnA Maker runtime..
            this.initRuntime();

            // 2. start Test..
            await this.startTest();

            // 3. testing will be done though call backs : readData(), endTest(), dumpResult()

        } catch (err) {
            console.warn(`Accuracy Evaluation Exception: ${err}`);
        }
    }
}

const acc = new Accuracy();
acc.main();
