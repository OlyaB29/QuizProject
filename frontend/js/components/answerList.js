export const renderAnswers = (answers, index) =>
    answers
        .map((answer) =>
            `
            <li>
                <label>
                    <input class="answer-input" type="radio" name="${index}" value="${answer.id}">
                    ${answer.text}
                </label>
            </li>
            `
        )
        .join('')