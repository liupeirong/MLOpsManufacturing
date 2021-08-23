// <Dependencies>
import builder from "junit-report-builder";
import fs from "fs";
import * as readline from "readline";
// </Dependencies>


// read args
const args = {
    in: null, out: null
};
const argv = process.argv.slice(2);
for (let i = 0; i < argv.length; i++) {
    const element = argv[i];
    if(element.startsWith('-')) {
        args[element.replace('-', '')] = argv[i + 1];
    }
}
const IN_FILE = args.in ?? "output/out.tsv";
const OUT_FILE = args.out ?? "test-report.xml";
console.log(args);


// generateJUnitReport
async function generateJUnitReport()
{
    const rs = fs.createReadStream(IN_FILE);
    const rl = readline.createInterface(rs);
    const suite = builder.testSuite();

    // readline
    let current_line_no = 0;
    for await (const line of rl) {

        // skip header
        if (current_line_no++ === 0)
            continue;

        const fields = line.split('\t');
        const question = fields[0];
        const answerids = fields[1];
        const success = fields[2] === "true" ? true : false;
        const turn = fields[3];
        // const successid = fields[4];
        // const confidence = fields[5];
        // const answer = fields[6];
        // const preciseAnswer = fields[7];
        const returnedAllIds = fields[8];
        const returnedAllConfidences = fields[9];
        const confidenceDroppedIds = fields[10];
        const similarityDroppedIds = fields[11];

        const testcase = suite.testCase().name(question);
        testcase._attributes['owner'] = turn;
        if (success === false) {
            testcase.failure(
                `Target Answer Ids: ${answerids}
                Turn: ${turn}
                Returned All Ids: ${returnedAllIds}
                Returned All Confidences: ${returnedAllConfidences}
                Confidence Dropped Ids: ${confidenceDroppedIds}
                Similarity Dropped Ids: ${similarityDroppedIds}`
            );
        }
    }

    builder.writeTo(OUT_FILE);
}

generateJUnitReport();
