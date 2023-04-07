import {renderAnswersResult} from "./answersResult.js";

export const renderQuestionResult = (question, localResult) =>
    `
        <div class="quiz-result-item">
            <div class="quiz-result-item-question">${question.text}</div>
            <ul class="quiz-result-item-answer">${renderAnswersResult(question.answers, localResult)}</ul>
        </div>
        `