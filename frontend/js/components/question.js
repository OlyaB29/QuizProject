import {renderAnswers} from "./answerList.js";

export const renderQuestion = (question, index) =>
    `
    <div class="quiz-question-item">
        <div class="quiz-question-item-question">${question.text}</div>
        <ul class="quiz-question-item-answers">${renderAnswers(question.answers, index)}</ul>
    </div>    
    `